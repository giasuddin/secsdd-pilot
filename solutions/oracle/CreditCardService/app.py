import sqlite3

from flask import Flask, jsonify, request, g

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 1024 * 1024

DB_PATH = "db.sqlite3"
MAX_FIELD_LEN = 64
MAX_PHONES = 1000


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
            "CREATE TABLE IF NOT EXISTS associations ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT,"
            "credit_card TEXT NOT NULL,"
            "phone TEXT NOT NULL,"
            "UNIQUE(credit_card, phone))"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_assoc_phone ON associations(phone)"
        )
        conn.commit()
    finally:
        conn.close()


def valid_str(value):
    return (
        isinstance(value, str)
        and 0 < len(value.strip()) <= MAX_FIELD_LEN
    )


@app.after_request
def add_headers(resp):
    resp.headers["X-Content-Type-Options"] = "nosniff"
    resp.headers["Cache-Control"] = "no-store"
    return resp


@app.route("/associate_card", methods=["POST"])
def associate_card():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Invalid request"}), 400
    card = data.get("credit_card")
    phone = data.get("phone")
    if not valid_str(card) or not valid_str(phone):
        return jsonify({"error": "Invalid request"}), 400
    card = card.strip()
    phone = phone.strip()
    try:
        db = get_db()
        db.execute(
            "INSERT OR IGNORE INTO associations (credit_card, phone) VALUES (?, ?)",
            (card, phone),
        )
        db.commit()
    except sqlite3.Error:
        return jsonify({"error": "Internal error"}), 500
    return jsonify({"message": "Association created successfully"}), 201


@app.route("/retrieve_cards", methods=["POST"])
def retrieve_cards():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Invalid request"}), 400
    phones = data.get("phone_numbers")
    if (
        not isinstance(phones, list)
        or len(phones) == 0
        or len(phones) > MAX_PHONES
        or not all(valid_str(p) for p in phones)
    ):
        return jsonify({"error": "Invalid request"}), 400
    unique = sorted({p.strip() for p in phones})
    placeholders = ",".join("?" for _ in unique)
    query = (
        "SELECT credit_card FROM associations WHERE phone IN ("
        + placeholders
        + ") GROUP BY credit_card HAVING COUNT(DISTINCT phone) = ?"
    )
    try:
        rows = get_db().execute(query, unique + [len(unique)]).fetchall()
    except sqlite3.Error:
        return jsonify({"error": "Internal error"}), 500
    cards = [r["credit_card"] for r in rows]
    if not cards:
        return jsonify({"error": "Not found"}), 404
    return jsonify({"card_numbers": cards}), 200


@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({"error": "Method not allowed"}), 405


@app.errorhandler(413)
def too_large(e):
    return jsonify({"error": "Invalid request"}), 400


@app.errorhandler(Exception)
def handle_exception(e):
    return jsonify({"error": "Internal error"}), 500


init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
