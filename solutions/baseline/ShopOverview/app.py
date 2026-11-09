import os
import csv
import io
import sqlite3
import datetime
import jwt
from flask import Flask, request, jsonify, Response, make_response
from markupsafe import escape
from passlib.hash import pbkdf2_sha256

app = Flask(__name__)
APP_SECRET = os.environ.get("APP_SECRET", "default-secret")
DB = "db.sqlite3"


def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute(
        "CREATE TABLE IF NOT EXISTS merchants ("
        "id INTEGER PRIMARY KEY AUTOINCREMENT, "
        "email TEXT UNIQUE NOT NULL, "
        "name TEXT NOT NULL, "
        "password_hash TEXT NOT NULL)"
    )
    conn.execute(
        "CREATE TABLE IF NOT EXISTS wares ("
        "id INTEGER PRIMARY KEY AUTOINCREMENT, "
        "merchant_id INTEGER NOT NULL, "
        "name TEXT NOT NULL, "
        "description TEXT NOT NULL, "
        "price REAL NOT NULL)"
    )
    conn.commit()
    conn.close()


def current_merchant_id():
    token = request.cookies.get("AUTH_COOKIE")
    if not token:
        return None
    try:
        payload = jwt.decode(token, APP_SECRET, algorithms=["HS256"])
        return int(payload["sub"])
    except Exception:
        return None


@app.route("/merchants/register", methods=["POST"])
def register():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Invalid input"}), 400
    email = data.get("email")
    name = data.get("name")
    password = data.get("password")
    if (
        not isinstance(email, str)
        or not isinstance(name, str)
        or not isinstance(password, str)
        or not email
        or not name
        or not password
        or "@" not in email
    ):
        return jsonify({"error": "Invalid input"}), 400
    conn = get_db()
    try:
        conn.execute(
            "INSERT INTO merchants (email, name, password_hash) VALUES (?, ?, ?)",
            (email, name, pbkdf2_sha256.hash(password)),
        )
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({"error": "Invalid input"}), 400
    conn.close()
    return jsonify({"message": "Merchant registered successfully"}), 201


@app.route("/merchants/login", methods=["POST"])
def login():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Invalid email or password"}), 401
    email = data.get("email")
    password = data.get("password")
    if not isinstance(email, str) or not isinstance(password, str):
        return jsonify({"error": "Invalid email or password"}), 401
    conn = get_db()
    row = conn.execute("SELECT * FROM merchants WHERE email = ?", (email,)).fetchone()
    conn.close()
    if row is None or not pbkdf2_sha256.verify(password, row["password_hash"]):
        return jsonify({"error": "Invalid email or password"}), 401
    token = jwt.encode(
        {
            "sub": str(row["id"]),
            "exp": datetime.datetime.now(datetime.timezone.utc)
            + datetime.timedelta(hours=1),
        },
        APP_SECRET,
        algorithm="HS256",
    )
    resp = make_response(jsonify("Login successful"), 200)
    resp.set_cookie("AUTH_COOKIE", token, httponly=True, samesite="Lax")
    return resp


@app.route("/merchants/upload-wares", methods=["POST"])
def upload_wares():
    mid = current_merchant_id()
    if mid is None:
        return jsonify({"error": "Unauthorized"}), 401
    data = request.get_json(silent=True)
    if not isinstance(data, dict) or not isinstance(data.get("csv"), str):
        return jsonify({"error": "Invalid CSV format"}), 400
    try:
        reader = csv.reader(io.StringIO(data["csv"]))
        rows = [r for r in reader if r]
    except csv.Error:
        return jsonify({"error": "Invalid CSV format"}), 400
    if rows and [c.strip().lower() for c in rows[0]] == ["name", "description", "price"]:
        rows = rows[1:]
    parsed = []
    for r in rows:
        if len(r) != 3:
            return jsonify({"error": "Invalid CSV format"}), 400
        try:
            price = float(r[2])
        except ValueError:
            return jsonify({"error": "Invalid CSV format"}), 400
        parsed.append((mid, r[0], r[1], price))
    conn = get_db()
    conn.execute("DELETE FROM wares WHERE merchant_id = ?", (mid,))
    conn.executemany(
        "INSERT INTO wares (merchant_id, name, description, price) VALUES (?, ?, ?, ?)",
        parsed,
    )
    conn.commit()
    conn.close()
    return jsonify({"message": "Wares uploaded successfully"}), 200


@app.route("/wares", methods=["GET"])
def wares():
    if current_merchant_id() is None:
        return jsonify({"error": "Unauthorized"}), 401
    query = (
        "SELECT w.name, w.description, w.price, m.email FROM wares w "
        "JOIN merchants m ON m.id = w.merchant_id WHERE 1=1"
    )
    params = []
    min_price = request.args.get("minPrice")
    max_price = request.args.get("maxPrice")
    try:
        if min_price not in (None, ""):
            query += " AND w.price >= ?"
            params.append(float(min_price))
        if max_price not in (None, ""):
            query += " AND w.price <= ?"
            params.append(float(max_price))
    except ValueError:
        return jsonify({"error": "Invalid price"}), 400
    conn = get_db()
    rows = conn.execute(query, params).fetchall()
    conn.close()
    html = (
        "<html><body><table border='1'>"
        "<tr><th>Name</th><th>Price</th><th>Description</th><th>Merchant</th></tr>"
    )
    for r in rows:
        html += "<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>" % (
            escape(r["name"]),
            escape(r["price"]),
            escape(r["description"]),
            escape(r["email"]),
        )
    html += "</table></body></html>"
    return Response(html, mimetype="text/html")


init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
