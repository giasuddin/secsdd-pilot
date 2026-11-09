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
        "password_hash TEXT NOT NULL, "
        "name TEXT NOT NULL)"
    )
    conn.commit()
    conn.close()


@app.route("/register", methods=["POST"])
def register():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"message": "Email already in use or invalid data"}), 400
    email = data.get("email")
    password = data.get("password")
    name = data.get("name")
    if (
        not isinstance(email, str)
        or not isinstance(password, str)
        or not isinstance(name, str)
        or not email
        or not password
        or not name
        or "@" not in email
    ):
        return jsonify({"message": "Email already in use or invalid data"}), 400
    conn = get_db()
    try:
        conn.execute(
            "INSERT INTO users (email, password_hash, name) VALUES (?, ?, ?)",
            (email, pbkdf2_sha256.hash(password), name),
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
            "sub": str(row["id"]),
            "email": row["email"],
            "exp": datetime.datetime.now(datetime.timezone.utc)
            + datetime.timedelta(hours=1),
        },
        APP_SECRET,
        algorithm="HS256",
    )
    return jsonify({"token": token, "message": "Login successful"}), 200


init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
