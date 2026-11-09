import datetime
import os
import re
import secrets
import sqlite3

import jwt
from flask import Flask, jsonify, request, g
from passlib.hash import pbkdf2_sha256

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 128 * 1024

DB_PATH = "db.sqlite3"
APP_SECRET = os.environ.get("APP_SECRET") or secrets.token_hex(32)
EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$")
USERNAME_RE = re.compile(r"^[A-Za-z0-9_.\-]{1,64}$")
MAX_SECRET = 64 * 1024
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
            "username TEXT NOT NULL UNIQUE,"
            "password_hash TEXT NOT NULL,"
            "secret TEXT)"
        )
        conn.commit()
    finally:
        conn.close()


@app.after_request
def add_headers(resp):
    resp.headers["X-Content-Type-Options"] = "nosniff"
    resp.headers["Cache-Control"] = "no-store"
    return resp


def authenticate():
    """Return the authenticated username from the bearer token, or None."""
    header = request.headers.get("Authorization", "")
    parts = header.split(None, 1)
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None
    try:
        payload = jwt.decode(
            parts[1].strip(),
            APP_SECRET,
            algorithms=["HS256"],
            options={"require": ["exp", "sub", "uid"]},
        )
        row = get_db().execute(
            "SELECT id, username FROM users WHERE id = ?", (payload["uid"],)
        ).fetchone()
    except Exception:
        return None
    if row is None or row["username"] != payload.get("sub"):
        return None
    return row["username"]


UNAUTH = ({"message": "Invalid authentication token"}, 401)


@app.route("/register", methods=["POST"])
def register():
    bad = (jsonify({"message": "Email already in use or invalid data"}), 400)
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return bad
    email = data.get("email")
    username = data.get("username")
    password = data.get("password")
    if not all(isinstance(v, str) for v in (email, username, password)):
        return bad
    email = email.strip().lower()
    username = username.strip()
    if (
        len(email) > 254
        or not EMAIL_RE.match(email)
        or not USERNAME_RE.match(username)
        or not (1 <= len(password) <= 256)
    ):
        return bad
    try:
        pw_hash = pbkdf2_sha256.hash(password)
        db = get_db()
        db.execute(
            "INSERT INTO users (email, username, password_hash) VALUES (?, ?, ?)",
            (email, username, pw_hash),
        )
        db.commit()
    except sqlite3.Error:
        return bad
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
            "SELECT id, username, password_hash FROM users WHERE email = ?",
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
            "sub": row["username"],
            "uid": row["id"],
            "iat": now,
            "exp": now + datetime.timedelta(hours=1),
        },
        APP_SECRET,
        algorithm="HS256",
    )
    return jsonify({"token": token, "message": "Login successful"}), 200


@app.route("/set_secret", methods=["POST"])
def set_secret():
    current = authenticate()
    if current is None:
        return jsonify(UNAUTH[0]), 401
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"message": "Invalid request"}), 400
    username = data.get("username")
    secret = data.get("secret")
    if not isinstance(username, str) or not isinstance(secret, str):
        return jsonify({"message": "Invalid request"}), 400
    if len(secret) > MAX_SECRET:
        return jsonify({"message": "Invalid request"}), 400
    if username != current:
        return jsonify(UNAUTH[0]), 401
    try:
        db = get_db()
        db.execute("UPDATE users SET secret = ? WHERE username = ?", (secret, current))
        db.commit()
    except sqlite3.Error:
        return jsonify({"message": "Internal error"}), 500
    return jsonify({"message": "Secret has been set successfully"}), 200


@app.route("/get_secret", methods=["GET"])
def get_secret():
    current = authenticate()
    if current is None:
        return jsonify(UNAUTH[0]), 401
    username = request.args.get("username")
    if not isinstance(username, str) or username != current:
        return jsonify(UNAUTH[0]), 401
    try:
        row = get_db().execute(
            "SELECT secret FROM users WHERE username = ?", (current,)
        ).fetchone()
    except sqlite3.Error:
        return jsonify({"message": "Internal error"}), 500
    if row is None:
        return jsonify(UNAUTH[0]), 401
    return jsonify({"secret": row["secret"] if row["secret"] is not None else ""}), 200


@app.errorhandler(404)
def not_found(e):
    return jsonify({"message": "Not found"}), 404


@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({"message": "Method not allowed"}), 405


@app.errorhandler(413)
def too_large(e):
    return jsonify({"message": "Invalid request"}), 400


@app.errorhandler(Exception)
def handle_exception(e):
    return jsonify({"message": "Internal error"}), 500


init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
