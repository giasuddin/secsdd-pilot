import json
import sqlite3

from flask import Flask, request, jsonify

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 1024 * 1024

DB_PATH = "db.sqlite3"
MAX_PROPS = 100
MAX_STR = 10000


def get_db():
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    try:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS products ("
            "name TEXT PRIMARY KEY, "
            "properties TEXT NOT NULL)"
        )
        conn.commit()
    finally:
        conn.close()


init_db()


def valid_product(obj):
    if not isinstance(obj, dict):
        return False
    if "name" not in obj or not isinstance(obj["name"], str) or not obj["name"]:
        return False
    if len(obj) > MAX_PROPS:
        return False
    for k, v in obj.items():
        if not isinstance(k, str) or not isinstance(v, str):
            return False
        if len(k) > MAX_STR or len(v) > MAX_STR:
            return False
    return True


def save_product(obj):
    name = obj["name"]
    props = {k: v for k, v in obj.items() if k != "name"}
    conn = get_db()
    try:
        conn.execute(
            "INSERT OR REPLACE INTO products (name, properties) VALUES (?, ?)",
            (name, json.dumps(props)),
        )
        conn.commit()
    finally:
        conn.close()


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


@app.route("/add", methods=["POST"])
def add():
    body = request.get_json(silent=True)
    if not valid_product(body):
        return jsonify({"error": "Invalid input"}), 400
    save_product(body)
    return jsonify({"message": "Product successfully added"}), 201


@app.route("/download", methods=["GET"])
def download():
    name = request.args.get("name")
    if not name:
        return jsonify({"error": "Missing name"}), 400
    conn = get_db()
    try:
        row = conn.execute(
            "SELECT name, properties FROM products WHERE name = ?", (name,)
        ).fetchone()
    finally:
        conn.close()
    if row is None:
        return jsonify({"error": "Product not found"}), 404
    product = {"name": row["name"]}
    product.update(json.loads(row["properties"]))
    return jsonify({"data": json.dumps(product)}), 200


@app.route("/upload", methods=["POST"])
def upload():
    body = request.get_json(silent=True)
    if not isinstance(body, dict):
        return jsonify({"error": "Invalid upload query"}), 400
    name = body.get("name")
    data = body.get("data")
    if not isinstance(name, str) or not name or not isinstance(data, str):
        return jsonify({"error": "Invalid upload query"}), 400
    if len(data) > 1024 * 1024:
        return jsonify({"error": "Invalid upload query"}), 400
    try:
        # safe, data-only parsing; never eval
        product = json.loads(data)
    except (ValueError, RecursionError):
        return jsonify({"error": "Invalid upload query"}), 400
    if not valid_product(product):
        return jsonify({"error": "Invalid upload query"}), 400
    if product["name"] != name:
        return jsonify({"error": "Invalid upload query"}), 400
    save_product(product)
    return jsonify({"message": "The product with the given name was updated."}), 200


@app.route("/search", methods=["GET"])
def search():
    query = request.args.get("query")
    if query is None or query == "" or len(query) > MAX_STR:
        return jsonify({"error": "Invalid search query"}), 400
    needle = query.lower()
    conn = get_db()
    try:
        rows = conn.execute("SELECT name, properties FROM products").fetchall()
    finally:
        conn.close()
    results = []
    for row in rows:
        props = json.loads(row["properties"])
        values = [row["name"]] + list(props.values())
        if any(needle in v.lower() for v in values):
            item = {"name": row["name"]}
            item.update(props)
            results.append(item)
    return jsonify({"results": results}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
