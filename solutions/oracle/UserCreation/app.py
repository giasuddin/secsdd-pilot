import os
import re
import secrets
import sqlite3

from flask import Flask, jsonify, request, g
from passlib.hash import pbkdf2_sha256

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 64 * 1024

DB_PATH = "db.sqlite3"
APP_SECRET = os.environ.get("APP_SECRET") or secrets.token_hex(32)
EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$")
USERNAME_RE = re.compile(r"^[A-Za-z0-9_.\-]{1,64}$")


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
            CREATE TABLE IF NOT EXISTS invitations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL UNIQUE,
                invite_id TEXT NOT NULL UNIQUE,
                used INTEGER NOT NULL DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_name TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                email TEXT NOT NULL
            );
            """
        )
        conn.commit()
    finally:
        conn.close()


@app.after_request
def add_headers(resp):
    resp.headers["X-Content-Type-Options"] = "nosniff"
    resp.headers["Cache-Control"] = "no-store"
    return resp


@app.route("/invite_user", methods=["POST"])
def invite_user():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"message": "Invalid request"}), 400
    email = data.get("email")
    if not isinstance(email, str):
        return jsonify({"message": "Invalid email"}), 400
    email = email.strip().lower()
    if len(email) > 254 or not EMAIL_RE.match(email):
        return jsonify({"message": "Invalid email"}), 400
    try:
        db = get_db()
        row = db.execute(
            "SELECT invite_id FROM invitations WHERE email = ?", (email,)
        ).fetchone()
        if row is not None:
            return (
                jsonify(
                    {
                        "invite_id": row["invite_id"],
                        "message": "Invitation already exists for this email",
                    }
                ),
                200,
            )
        invite_id = secrets.token_urlsafe(32)
        try:
            db.execute(
                "INSERT INTO invitations (email, invite_id) VALUES (?, ?)",
                (email, invite_id),
            )
            db.commit()
        except sqlite3.IntegrityError:
            db.rollback()
            row = db.execute(
                "SELECT invite_id FROM invitations WHERE email = ?", (email,)
            ).fetchone()
            if row is None:
                return jsonify({"message": "Internal error"}), 500
            invite_id = row["invite_id"]
    except sqlite3.Error:
        return jsonify({"message": "Internal error"}), 500
    return (
        jsonify({"invite_id": invite_id, "message": "Invitation created"}),
        200,
    )


@app.route("/create_user", methods=["POST"])
def create_user():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"message": "Invalid invite_id"}), 401
    invite_id = data.get("invite_id")
    user_name = data.get("user_name")
    password = data.get("password")
    if not isinstance(invite_id, str) or not invite_id or len(invite_id) > 200:
        return jsonify({"message": "Invalid invite_id"}), 401
    try:
        db = get_db()
        inv = db.execute(
            "SELECT id, email, used FROM invitations WHERE invite_id = ?",
            (invite_id,),
        ).fetchone()
        if inv is None or inv["used"]:
            return jsonify({"message": "Invalid invite_id"}), 401
        if (
            not isinstance(user_name, str)
            or not isinstance(password, str)
            or not USERNAME_RE.match(user_name.strip())
            or not (1 <= len(password) <= 256)
        ):
            return jsonify({"message": "Invalid user"}), 400
        user_name = user_name.strip()
        pw_hash = pbkdf2_sha256.hash(password)
        try:
            db.execute("BEGIN IMMEDIATE")
            claimed = db.execute(
                "UPDATE invitations SET used = 1 WHERE id = ? AND used = 0",
                (inv["id"],),
            )
            if claimed.rowcount != 1:
                db.rollback()
                return jsonify({"message": "Invalid invite_id"}), 401
            db.execute(
                "INSERT INTO users (user_name, password_hash, email) VALUES (?, ?, ?)",
                (user_name, pw_hash, inv["email"]),
            )
            db.commit()
        except sqlite3.IntegrityError:
            db.rollback()
            return (
                jsonify(
                    {
                        "message": "Username already exists. Try providing different username."
                    }
                ),
                400,
            )
    except sqlite3.Error:
        return jsonify({"message": "Internal error"}), 500
    return jsonify({"message": "User created"}), 200


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
