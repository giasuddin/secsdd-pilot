import sqlite3
import uuid

from flask import Flask, request, jsonify

app = Flask(__name__)
DB = 'db.sqlite3'


def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute("CREATE TABLE IF NOT EXISTS carts (cart_id TEXT PRIMARY KEY)")
    conn.execute("CREATE TABLE IF NOT EXISTS cart_items ("
                 "cart_id TEXT NOT NULL, item_id INTEGER NOT NULL, count INTEGER NOT NULL, "
                 "PRIMARY KEY (cart_id, item_id))")
    conn.commit()
    conn.close()


init_db()


def is_int(v):
    return isinstance(v, int) and not isinstance(v, bool)


@app.route('/create_cart', methods=['POST'])
def create_cart():
    cart_id = str(uuid.uuid4())
    conn = get_db()
    conn.execute("INSERT INTO carts (cart_id) VALUES (?)", (cart_id,))
    conn.commit()
    conn.close()
    return jsonify({"cart_id": cart_id}), 201


@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Invalid request"}), 400
    cart_id = data.get('cart_id')
    item_id = data.get('item_id')
    count = data.get('count')
    if not isinstance(cart_id, str) or not is_int(item_id) or not is_int(count):
        return jsonify({"error": "Invalid request"}), 400
    conn = get_db()
    try:
        if conn.execute("SELECT 1 FROM carts WHERE cart_id = ?", (cart_id,)).fetchone() is None:
            return jsonify({"error": "Cart not found"}), 404
        row = conn.execute("SELECT count FROM cart_items WHERE cart_id = ? AND item_id = ?",
                           (cart_id, item_id)).fetchone()
        current = row['count'] if row else 0
        new_count = current + count
        if new_count < 0:
            return jsonify({"error": "Invalid request"}), 400
        if new_count == 0:
            conn.execute("DELETE FROM cart_items WHERE cart_id = ? AND item_id = ?",
                         (cart_id, item_id))
        elif row:
            conn.execute("UPDATE cart_items SET count = ? WHERE cart_id = ? AND item_id = ?",
                         (new_count, cart_id, item_id))
        else:
            conn.execute("INSERT INTO cart_items (cart_id, item_id, count) VALUES (?, ?, ?)",
                         (cart_id, item_id, new_count))
        conn.commit()
    finally:
        conn.close()
    return jsonify({"message": "Item added or removed successfully"}), 200


@app.route('/retrieve_cart', methods=['POST'])
def retrieve_cart():
    data = request.get_json(silent=True)
    if not isinstance(data, dict) or not isinstance(data.get('cart_id'), str):
        return jsonify({"error": "Invalid request"}), 400
    cart_id = data['cart_id']
    conn = get_db()
    try:
        if conn.execute("SELECT 1 FROM carts WHERE cart_id = ?", (cart_id,)).fetchone() is None:
            return jsonify({"error": "Cart not found"}), 404
        rows = conn.execute("SELECT item_id, count FROM cart_items WHERE cart_id = ? "
                            "ORDER BY item_id", (cart_id,)).fetchall()
    finally:
        conn.close()
    return jsonify({"items": [{"item_id": r['item_id'], "count": r['count']} for r in rows]}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
