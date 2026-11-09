import sqlite3
from flask import Flask, request, jsonify

app = Flask(__name__)
DB = "db.sqlite3"


def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute(
        "CREATE TABLE IF NOT EXISTS associations ("
        "credit_card TEXT NOT NULL, phone TEXT NOT NULL, "
        "PRIMARY KEY (credit_card, phone))"
    )
    conn.commit()
    conn.close()


@app.route("/associate_card", methods=["POST"])
def associate_card():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"message": "Invalid request"}), 400
    card = data.get("credit_card")
    phone = data.get("phone")
    if not isinstance(card, str) or not isinstance(phone, str) or not card or not phone:
        return jsonify({"message": "Invalid request"}), 400
    conn = get_db()
    conn.execute(
        "INSERT OR IGNORE INTO associations (credit_card, phone) VALUES (?, ?)",
        (card, phone),
    )
    conn.commit()
    conn.close()
    return jsonify({"message": "Association created successfully"}), 201


@app.route("/retrieve_cards", methods=["POST"])
def retrieve_cards():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"message": "Invalid request"}), 400
    phones = data.get("phone_numbers")
    if (
        not isinstance(phones, list)
        or not phones
        or not all(isinstance(p, str) for p in phones)
    ):
        return jsonify({"message": "Invalid request"}), 400
    phones = list(set(phones))
    placeholders = ",".join("?" * len(phones))
    conn = get_db()
    rows = conn.execute(
        "SELECT credit_card FROM associations WHERE phone IN (%s) "
        "GROUP BY credit_card HAVING COUNT(DISTINCT phone) = ?" % placeholders,
        phones + [len(phones)],
    ).fetchall()
    conn.close()
    cards = [r["credit_card"] for r in rows]
    if not cards:
        return jsonify({"message": "Not found"}), 404
    return jsonify({"card_numbers": cards}), 200


init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
