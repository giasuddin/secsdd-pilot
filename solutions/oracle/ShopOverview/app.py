import csv
import datetime
import io
import math
import os
import re
import secrets
import sqlite3
from decimal import Decimal, InvalidOperation

import jwt
from flask import Flask, jsonify, request, g, make_response, render_template_string
from passlib.hash import pbkdf2_sha256

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 1024 * 1024

DB_PATH = "db.sqlite3"
APP_SECRET = os.environ.get("APP_SECRET") or secrets.token_hex(32)
COOKIE_NAME = "AUTH_COOKIE"
EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$")
DUMMY_HASH = pbkdf2_sha256.hash("dummy-password-for-timing")
MAX_ROWS = 5000
MAX_PRICE = 1e12


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exc):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS merchants (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL,
                password_hash TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS wares (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                merchant_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                description TEXT NOT NULL,
                price REAL NOT NULL,
                FOREIGN KEY(merchant_id) REFERENCES merchants(id)
            );
            """
        )
        conn.commit()
    finally:
        conn.close()


@app.after_request
def add_headers(resp):
    resp.headers["X-Content-Type-Options"] = "nosniff"
    resp.headers["Content-Security-Policy"] = "default-src 'none'; style-src 'unsafe-inline'"
    resp.headers["X-Frame-Options"] = "DENY"
    return resp


def current_merchant():
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        return None
    try:
        payload = jwt.decode(
            token,
            APP_SECRET,
            algorithms=["HS256"],
            options={"require": ["exp", "mid"]},
        )
        row = get_db().execute(
            "SELECT id, email FROM merchants WHERE id = ?", (payload["mid"],)
        ).fetchone()
    except Exception:
        return None
    return row


@app.route("/merchants/register", methods=["POST"])
def register():
    bad = (jsonify({"error": "Invalid input"}), 400)
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return bad
    email = data.get("email")
    name = data.get("name")
    password = data.get("password")
    if not all(isinstance(v, str) for v in (email, name, password)):
        return bad
    email = email.strip().lower()
    name = name.strip()
    if (
        len(email) > 254
        or not EMAIL_RE.match(email)
        or not (1 <= len(name) <= 100)
        or not (1 <= len(password) <= 256)
    ):
        return bad
    try:
        pw_hash = pbkdf2_sha256.hash(password)
        db = get_db()
        db.execute(
            "INSERT INTO merchants (email, name, password_hash) VALUES (?, ?, ?)",
            (email, name, pw_hash),
        )
        db.commit()
    except sqlite3.Error:
        return bad
    return jsonify({"message": "Merchant registered successfully"}), 201


@app.route("/merchants/login", methods=["POST"])
def login():
    invalid = (jsonify({"error": "Invalid email or password"}), 401)
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return invalid
    email = data.get("email")
    password = data.get("password")
    if not isinstance(email, str) or not isinstance(password, str):
        return invalid
    email = email.strip().lower()
    try:
        row = get_db().execute(
            "SELECT id, password_hash FROM merchants WHERE email = ?", (email,)
        ).fetchone()
        if row is None:
            pbkdf2_sha256.verify(password, DUMMY_HASH)
            return invalid
        if not pbkdf2_sha256.verify(password, row["password_hash"]):
            return invalid
    except Exception:
        return invalid
    now = datetime.datetime.now(datetime.timezone.utc)
    token = jwt.encode(
        {"mid": row["id"], "iat": now, "exp": now + datetime.timedelta(hours=1)},
        APP_SECRET,
        algorithm="HS256",
    )
    resp = make_response(jsonify("Login successful"), 200)
    resp.set_cookie(
        COOKIE_NAME,
        token,
        max_age=3600,
        httponly=True,
        samesite="Strict",
    )
    return resp


def parse_price(text):
    try:
        value = Decimal(text.strip())
    except (InvalidOperation, ValueError):
        return None
    if not value.is_finite():
        return None
    value = float(value)
    if math.isnan(value) or math.isinf(value) or value < 0 or value > MAX_PRICE:
        return None
    return value


@app.route("/merchants/upload-wares", methods=["POST"])
def upload_wares():
    merchant = current_merchant()
    if merchant is None:
        return jsonify({"error": "Unauthorized"}), 401
    bad = (jsonify({"error": "Invalid CSV format"}), 400)
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return bad
    csv_text = data.get("csv")
    if not isinstance(csv_text, str) or not csv_text.strip():
        return bad
    try:
        rows = list(csv.reader(io.StringIO(csv_text, newline=""), strict=True))
    except csv.Error:
        return bad
    rows = [r for r in rows if r]
    if rows and [c.strip().lower() for c in rows[0]] == ["name", "description", "price"]:
        rows = rows[1:]
    if not rows or len(rows) > MAX_ROWS:
        return bad
    parsed = []
    for r in rows:
        if len(r) != 3:
            return bad
        name, desc, price_text = r
        name = name.strip()
        if not name or len(name) > 200 or len(desc) > 2000:
            return bad
        price = parse_price(price_text)
        if price is None:
            return bad
        parsed.append((merchant["id"], name, desc, price))
    try:
        db = get_db()
        db.executemany(
            "INSERT INTO wares (merchant_id, name, description, price) VALUES (?, ?, ?, ?)",
            parsed,
        )
        db.commit()
    except sqlite3.Error:
        return jsonify({"error": "Internal error"}), 500
    return jsonify({"message": "Wares uploaded successfully"}), 200


WARES_TMPL = """<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Wares</title></head>
<body>
<table border="1">
<thead><tr><th>Name</th><th>Price</th><th>Description</th><th>Merchant</th></tr></thead>
<tbody>
{% for w in wares %}<tr><td>{{ w['name'] }}</td><td>{{ '%.2f' % w['price'] }}</td><td>{{ w['description'] }}</td><td>{{ w['email'] }}</td></tr>
{% endfor %}</tbody>
</table>
</body></html>"""


def parse_bound(name):
    raw = request.args.get(name)
    if raw is None or raw == "":
        return None, True
    try:
        value = float(raw)
    except ValueError:
        return None, False
    if math.isnan(value) or math.isinf(value):
        return None, False
    return value, True


@app.route("/wares", methods=["GET"])
def wares():
    if current_merchant() is None:
        return jsonify({"error": "Unauthorized"}), 401
    min_price, ok1 = parse_bound("minPrice")
    max_price, ok2 = parse_bound("maxPrice")
    if not ok1 or not ok2:
        return jsonify({"error": "Invalid input"}), 400
    query = (
        "SELECT w.name AS name, w.description AS description, w.price AS price, "
        "m.email AS email FROM wares w JOIN merchants m ON m.id = w.merchant_id"
    )
    conds = []
    params = []
    if min_price is not None:
        conds.append("w.price >= ?")
        params.append(min_price)
    if max_price is not None:
        conds.append("w.price <= ?")
        params.append(max_price)
    if conds:
        query += " WHERE " + " AND ".join(conds)
    query += " ORDER BY w.id"
    try:
        rows = get_db().execute(query, params).fetchall()
    except sqlite3.Error:
        return jsonify({"error": "Internal error"}), 500
    resp = make_response(render_template_string(WARES_TMPL, wares=rows), 200)
    resp.headers["Content-Type"] = "text/html; charset=utf-8"
    return resp


@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({"error": "Method not allowed"}), 405


@app.errorhandler(413)
def too_large(e):
    return jsonify({"error": "Invalid input"}), 400


@app.errorhandler(Exception)
def handle_exception(e):
    return jsonify({"error": "Internal error"}), 500


init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
