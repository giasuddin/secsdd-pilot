import secrets
import sqlite3

from flask import Flask, request, jsonify

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 64 * 1024

DB_PATH = "db.sqlite3"
MAX_COUNT = 1000000
MAX_ITEM_ID = 2 ** 53
MAX_ITEMS_PER_CART = 1000


def get_db():
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    try:
        conn.execute("CREATE TABLE IF NOT EXISTS carts (cart_id TEXT PRIMARY KEY)")
        conn.execute(
            "CREATE TABLE IF NOT EXISTS cart_items ("
            "cart_id TEXT NOT NULL, item_id INTEGER NOT NULL, count INTEGER NOT NULL, "
            "PRIMARY KEY (cart_id, item_id), "
            "FOREIGN KEY (cart_id) REFERENCES carts(cart_id))"
        )
        conn.commit()
    finally:
        conn.close()


init_db()


def is_int(v):
    return isinstance(v, int) and not isinstance(v, bool)


def valid_cart_id(v):
    return isinstance(v, str) and 0 < len(v) <= 128


@app.errorhandler(413)
def too_large(e):
    return jsonify({"error": "Request too large"}), 400


@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(405)
def not_allowed(e):
    return jsonify({"error": "Method not allowed"}), 405


@app.errorhandler(Exception)
def unexpected(e):
    return jsonify({"error": "Internal server error"}), 500


@app.route("/create_cart", methods=["POST"])
def create_cart():
    # unguessable identifier acts as the capability to access the cart
    cart_id = secrets.token_urlsafe(32)
    conn = get_db()
    try:
        conn.execute("INSERT INTO carts (cart_id) VALUES (?)", (cart_id,))
        conn.commit()
    finally:
        conn.close()
    return jsonify({"cart_id": cart_id}), 201


@app.route("/add_to_cart", methods=["POST"])
def add_to_cart():
    body = request.get_json(silent=True)
    if not isinstance(body, dict):
        return jsonify({"error": "Invalid request"}), 400
    cart_id = body.get("cart_id")
    item_id = body.get("item_id")
    count = body.get("count")
    if not valid_cart_id(cart_id) or not is_int(item_id) or not is_int(count):
        return jsonify({"error": "Invalid request"}), 400
    if item_id < 0 or item_id > MAX_ITEM_ID or abs(count) > MAX_COUNT:
        return jsonify({"error": "Invalid request"}), 400

    conn = get_db()
    try:
        conn.execute("BEGIN IMMEDIATE")
        if conn.execute("SELECT 1 FROM carts WHERE cart_id = ?", (cart_id,)).fetchone() is None:
            conn.rollback()
            return jsonify({"error": "Cart not found"}), 404
        row = conn.execute(
            "SELECT count FROM cart_items WHERE cart_id = ? AND item_id = ?",
            (cart_id, item_id),
        ).fetchone()
        current = row["count"] if row else 0
        new = current + count
        if new < 0 or new > MAX_COUNT:
            conn.rollback()
            return jsonify({"error": "Invalid request"}), 400
        if row is None:
            n = conn.execute(
                "SELECT COUNT(*) AS n FROM cart_items WHERE cart_id = ?", (cart_id,)
            ).fetchone()["n"]
            if new > 0 and n >= MAX_ITEMS_PER_CART:
                conn.rollback()
                return jsonify({"error": "Invalid request"}), 400
        if new == 0:
            conn.execute(
                "DELETE FROM cart_items WHERE cart_id = ? AND item_id = ?",
                (cart_id, item_id),
            )
        elif row is None:
            conn.execute(
                "INSERT INTO cart_items (cart_id, item_id, count) VALUES (?, ?, ?)",
                (cart_id, item_id, new),
            )
        else:
            conn.execute(
                "UPDATE cart_items SET count = ? WHERE cart_id = ? AND item_id = ?",
                (new, cart_id, item_id),
            )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
    return jsonify({"message": "Item added or removed successfully"}), 200


@app.route("/retrieve_cart", methods=["POST"])
def retrieve_cart():
    body = request.get_json(silent=True)
    if not isinstance(body, dict) or not valid_cart_id(body.get("cart_id")):
        return jsonify({"error": "Invalid request"}), 400
    cart_id = body["cart_id"]
    conn = get_db()
    try:
        if conn.execute("SELECT 1 FROM carts WHERE cart_id = ?", (cart_id,)).fetchone() is None:
            return jsonify({"error": "Cart not found"}), 404
        rows = conn.execute(
            "SELECT item_id, count FROM cart_items WHERE cart_id = ? ORDER BY item_id",
            (cart_id,),
        ).fetchall()
    finally:
        conn.close()
    return jsonify({"items": [{"item_id": r["item_id"], "count": r["count"]} for r in rows]}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
