import os
import re
import secrets
import sqlite3
import datetime

import jwt
from flask import Flask, jsonify, request, g
from passlib.hash import pbkdf2_sha256

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 64 * 1024

DB_PATH = "db.sqlite3"
APP_SECRET = os.environ.get("APP_SECRET") or secrets.token_hex(32)
EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$")
DUMMY_HASH = pbkdf2_sha256.hash("dummy-password-for-timing")


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
        conn.execute(
            "CREATE TABLE IF NOT EXISTS users ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT,"
            "email TEXT NOT NULL UNIQUE,"
            "name TEXT NOT NULL,"
            "password_hash TEXT NOT NULL)"
        )
        conn.commit()
    finally:
        conn.close()


@app.after_request
def add_headers(resp):
    resp.headers["X-Content-Type-Options"] = "nosniff"
    resp.headers["Cache-Control"] = "no-store"
    return resp


@app.route("/register", methods=["POST"])
def register():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"message": "Email already in use or invalid data"}), 400
    email = data.get("email")
    password = data.get("password")
    name = data.get("name")
    if not (
        isinstance(email, str)
        and isinstance(password, str)
        and isinstance(name, str)
    ):
        return jsonify({"message": "Email already in use or invalid data"}), 400
    email = email.strip().lower()
    name = name.strip()
    if (
        len(email) > 254
        or not EMAIL_RE.match(email)
        or not (1 <= len(name) <= 100)
        or not (1 <= len(password) <= 256)
    ):
        return jsonify({"message": "Email already in use or invalid data"}), 400
    try:
        pw_hash = pbkdf2_sha256.hash(password)
        db = get_db()
        db.execute(
            "INSERT INTO users (email, name, password_hash) VALUES (?, ?, ?)",
            (email, name, pw_hash),
        )
        db.commit()
    except sqlite3.IntegrityError:
        return jsonify({"message": "Email already in use or invalid data"}), 400
    except Exception:
        return jsonify({"message": "Email already in use or invalid data"}), 400
    return jsonify({"message": "Registration successful"}), 201


@app.route("/login", methods=["POST"])
def login():
    invalid = (jsonify({"message": "Invalid email or password"}), 401)
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
            "SELECT id, email, password_hash FROM users WHERE email = ?",
            (email,),
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
        {
            "sub": str(row["id"]),
            "email": row["email"],
            "iat": now,
            "exp": now + datetime.timedelta(hours=1),
        },
        APP_SECRET,
        algorithm="HS256",
    )
    return jsonify({"token": token, "message": "Login successful"}), 200


@app.errorhandler(404)
def not_found(e):
    return jsonify({"message": "Not found"}), 404


@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({"message": "Method not allowed"}), 405


@app.errorhandler(413)
def too_large(e):
    return jsonify({"message": "Email already in use or invalid data"}), 400


@app.errorhandler(Exception)
def handle_exception(e):
    return jsonify({"message": "Internal error"}), 500


init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
