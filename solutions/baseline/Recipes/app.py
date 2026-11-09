import json
import sqlite3
from flask import Flask, request, jsonify, Response
from markupsafe import escape

app = Flask(__name__)
DB = "db.sqlite3"


def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute(
        "CREATE TABLE IF NOT EXISTS recipes ("
        "id INTEGER PRIMARY KEY AUTOINCREMENT, "
        "title TEXT NOT NULL, "
        "ingredients TEXT NOT NULL, "
        "instructions TEXT NOT NULL)"
    )
    conn.execute(
        "CREATE TABLE IF NOT EXISTS comments ("
        "id INTEGER PRIMARY KEY AUTOINCREMENT, "
        "recipe_id INTEGER NOT NULL, "
        "comment TEXT NOT NULL)"
    )
    conn.execute(
        "CREATE TABLE IF NOT EXISTS ratings ("
        "id INTEGER PRIMARY KEY AUTOINCREMENT, "
        "recipe_id INTEGER NOT NULL, "
        "rating INTEGER NOT NULL)"
    )
    conn.commit()
    conn.close()


def parse_id(recipe_id):
    try:
        return int(recipe_id)
    except (ValueError, TypeError):
        return None


def recipe_exists(conn, rid):
    if rid is None:
        return False
    return conn.execute("SELECT 1 FROM recipes WHERE id = ?", (rid,)).fetchone() is not None


def avg_rating(conn, rid):
    row = conn.execute(
        "SELECT AVG(rating) AS a FROM ratings WHERE recipe_id = ?", (rid,)
    ).fetchone()
    return row["a"]


@app.route("/recipes", methods=["GET"])
def overview():
    try:
        conn = get_db()
        recent = conn.execute(
            "SELECT id, title FROM recipes ORDER BY id DESC LIMIT 10"
        ).fetchall()
        top = conn.execute(
            "SELECT r.id, r.title, AVG(rt.rating) AS a FROM recipes r "
            "JOIN ratings rt ON rt.recipe_id = r.id "
            "GROUP BY r.id ORDER BY a DESC LIMIT 10"
        ).fetchall()
        conn.close()
        html = "<html><body><h1>Recipes</h1><h2>Recent</h2><ul>"
        for r in recent:
            html += '<li><a href="/recipes/%d">%s</a></li>' % (r["id"], escape(r["title"]))
        html += "</ul><h2>Top rated</h2><ul>"
        for r in top:
            html += '<li><a href="/recipes/%d">%s</a> (%.2f)</li>' % (
                r["id"],
                escape(r["title"]),
                r["a"],
            )
        html += "</ul></body></html>"
        return Response(html, mimetype="text/html")
    except Exception:
        return Response("Server error", status=500)


@app.route("/recipes/upload", methods=["POST"])
def upload():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Invalid input"}), 400
    title = data.get("title")
    ingredients = data.get("ingredients")
    instructions = data.get("instructions")
    if (
        not isinstance(title, str)
        or not title.strip()
        or not isinstance(ingredients, list)
        or not all(isinstance(i, str) for i in ingredients)
        or not isinstance(instructions, str)
        or not instructions.strip()
    ):
        return jsonify({"error": "Invalid input"}), 400
    conn = get_db()
    cur = conn.execute(
        "INSERT INTO recipes (title, ingredients, instructions) VALUES (?, ?, ?)",
        (title, json.dumps(ingredients), instructions),
    )
    conn.commit()
    rid = cur.lastrowid
    conn.close()
    return (
        jsonify(
            {
                "id": str(rid),
                "title": title,
                "ingredients": ingredients,
                "instructions": instructions,
                "comments": [],
                "avgRating": None,
            }
        ),
        201,
    )


@app.route("/recipes/<recipe_id>", methods=["GET"])
def get_recipe(recipe_id):
    rid = parse_id(recipe_id)
    conn = get_db()
    if not recipe_exists(conn, rid):
        conn.close()
        return Response("Recipe not found", status=404)
    r = conn.execute("SELECT * FROM recipes WHERE id = ?", (rid,)).fetchone()
    comments = conn.execute(
        "SELECT comment FROM comments WHERE recipe_id = ? ORDER BY id", (rid,)
    ).fetchall()
    avg = avg_rating(conn, rid)
    conn.close()
    html = "<html><body><h1>%s</h1><h2>Ingredients</h2><ul>" % escape(r["title"])
    for i in json.loads(r["ingredients"]):
        html += "<li>%s</li>" % escape(i)
    html += "</ul><h2>Instructions</h2><p>%s</p>" % escape(r["instructions"])
    html += "<h2>Average rating</h2><p>%s</p>" % (
        "%.2f" % avg if avg is not None else "No ratings yet"
    )
    html += "<h2>Comments</h2><ul>"
    for c in comments:
        html += "<li>%s</li>" % escape(c["comment"])
    html += "</ul></body></html>"
    return Response(html, mimetype="text/html")


@app.route("/recipes/<recipe_id>/comments", methods=["POST"])
def add_comment(recipe_id):
    rid = parse_id(recipe_id)
    conn = get_db()
    if not recipe_exists(conn, rid):
        conn.close()
        return jsonify({"error": "Recipe not found"}), 404
    data = request.get_json(silent=True)
    comment = data.get("comment") if isinstance(data, dict) else None
    if not isinstance(comment, str) or not comment.strip():
        conn.close()
        return jsonify({"error": "Invalid input"}), 400
    conn.execute(
        "INSERT INTO comments (recipe_id, comment) VALUES (?, ?)", (rid, comment)
    )
    conn.commit()
    conn.close()
    return jsonify({"message": "Comment added successfully"}), 201


@app.route("/recipes/<recipe_id>/ratings", methods=["POST"])
def add_rating(recipe_id):
    rid = parse_id(recipe_id)
    conn = get_db()
    if not recipe_exists(conn, rid):
        conn.close()
        return jsonify({"error": "Recipe not found"}), 404
    data = request.get_json(silent=True)
    rating = data.get("rating") if isinstance(data, dict) else None
    if isinstance(rating, bool) or not isinstance(rating, int) or not 1 <= rating <= 5:
        conn.close()
        return jsonify({"error": "Invalid input"}), 400
    conn.execute(
        "INSERT INTO ratings (recipe_id, rating) VALUES (?, ?)", (rid, rating)
    )
    conn.commit()
    conn.close()
    return jsonify({"message": "Rating added successfully"}), 201


init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
