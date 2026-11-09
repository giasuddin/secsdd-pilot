import os
import sqlite3
import datetime
import jwt
from flask import Flask, request, jsonify
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
        "CREATE TABLE IF NOT EXISTS users ("
        "id INTEGER PRIMARY KEY AUTOINCREMENT, "
        "email TEXT UNIQUE NOT NULL, "
        "username TEXT UNIQUE NOT NULL, "
        "password_hash TEXT NOT NULL, "
        "secret TEXT)"
    )
    conn.commit()
    conn.close()


def current_username():
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return None
    token = auth[len("Bearer "):].strip()
    try:
        payload = jwt.decode(token, APP_SECRET, algorithms=["HS256"])
    except jwt.PyJWTError:
        return None
    return payload.get("username")


@app.route("/register", methods=["POST"])
def register():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"message": "Email already in use or invalid data"}), 400
    email = data.get("email")
    username = data.get("username")
    password = data.get("password")
    if (
        not isinstance(email, str)
        or not isinstance(username, str)
        or not isinstance(password, str)
        or not email
        or not username
        or not password
        or "@" not in email
    ):
        return jsonify({"message": "Email already in use or invalid data"}), 400
    conn = get_db()
    try:
        conn.execute(
            "INSERT INTO users (email, username, password_hash) VALUES (?, ?, ?)",
            (email, username, pbkdf2_sha256.hash(password)),
        )
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({"message": "Email already in use or invalid data"}), 400
    conn.close()
    return jsonify({"message": "Registration successful"}), 201


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"message": "Invalid email or password"}), 401
    email = data.get("email")
    password = data.get("password")
    if not isinstance(email, str) or not isinstance(password, str):
        return jsonify({"message": "Invalid email or password"}), 401
    conn = get_db()
    row = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    conn.close()
    if row is None or not pbkdf2_sha256.verify(password, row["password_hash"]):
        return jsonify({"message": "Invalid email or password"}), 401
    token = jwt.encode(
        {
            "username": row["username"],
            "exp": datetime.datetime.now(datetime.timezone.utc)
            + datetime.timedelta(hours=1),
        },
        APP_SECRET,
        algorithm="HS256",
    )
    return jsonify({"token": token, "message": "Login successful"}), 200


@app.route("/set_secret", methods=["POST"])
def set_secret():
    token_user = current_username()
    if token_user is None:
        return jsonify({"message": "Invalid authentication token"}), 401
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"message": "Invalid authentication token"}), 401
    username = data.get("username")
    secret = data.get("secret")
    if username != token_user or not isinstance(secret, str):
        return jsonify({"message": "Invalid authentication token"}), 401
    conn = get_db()
    conn.execute("UPDATE users SET secret = ? WHERE username = ?", (secret, username))
    conn.commit()
    conn.close()
    return jsonify({"message": "Secret has been set successfully"}), 200


@app.route("/get_secret", methods=["GET"])
def get_secret():
    token_user = current_username()
    username = request.args.get("username")
    if token_user is None or username != token_user:
        return jsonify({"message": "Invalid authentication token"}), 401
    conn = get_db()
    row = conn.execute(
        "SELECT secret FROM users WHERE username = ?", (username,)
    ).fetchone()
    conn.close()
    if row is None:
        return jsonify({"message": "Invalid authentication token"}), 401
    return jsonify({"secret": row["secret"] or ""}), 200


init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
