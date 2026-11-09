import sqlite3
import json

from flask import Flask, jsonify, request, g, render_template_string, Response

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 256 * 1024

DB_PATH = "db.sqlite3"
MAX_TITLE = 200
MAX_INGREDIENTS = 100
MAX_INGREDIENT_LEN = 200
MAX_INSTRUCTIONS = 10000
MAX_COMMENT = 2000


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
            CREATE TABLE IF NOT EXISTS recipes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                ingredients TEXT NOT NULL,
                instructions TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                recipe_id INTEGER NOT NULL,
                comment TEXT NOT NULL,
                FOREIGN KEY(recipe_id) REFERENCES recipes(id)
            );
            CREATE TABLE IF NOT EXISTS ratings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                recipe_id INTEGER NOT NULL,
                rating INTEGER NOT NULL,
                FOREIGN KEY(recipe_id) REFERENCES recipes(id)
            );
            """
        )
        conn.commit()
    finally:
        conn.close()


@app.after_request
def add_headers(resp):
    resp.headers["X-Content-Type-Options"] = "nosniff"
    resp.headers["Content-Security-Policy"] = "default-src 'none'; style-src 'unsafe-inline'"
    resp.headers["X-Frame-Options"] = "DENY"
    return resp


def parse_id(recipe_id):
    if not recipe_id.isascii() or not recipe_id.isdigit() or len(recipe_id) > 18:
        return None
    return int(recipe_id)


def recipe_exists(db, rid):
    return db.execute("SELECT 1 FROM recipes WHERE id = ?", (rid,)).fetchone() is not None


OVERVIEW_TMPL = """<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Recipes</title></head>
<body>
<h1>Recipes</h1>
<h2>Recent recipes</h2>
<ul>
{% for r in recent %}<li><a href="/recipes/{{ r['id'] }}">{{ r['title'] }}</a></li>
{% endfor %}</ul>
<h2>Top-rated recipes</h2>
<ul>
{% for r in top %}<li><a href="/recipes/{{ r['id'] }}">{{ r['title'] }}</a> ({{ '%.1f' % r['avg'] }})</li>
{% endfor %}</ul>
</body></html>"""

DETAIL_TMPL = """<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>{{ recipe['title'] }}</title></head>
<body>
<h1>{{ recipe['title'] }}</h1>
<h2>Ingredients</h2>
<ul>
{% for i in ingredients %}<li>{{ i }}</li>
{% endfor %}</ul>
<h2>Instructions</h2>
<p style="white-space: pre-wrap">{{ recipe['instructions'] }}</p>
<h2>Rating</h2>
<p>{% if avg is none %}No ratings yet{% else %}{{ '%.1f' % avg }} / 5 ({{ count }} ratings){% endif %}</p>
<h2>Comments</h2>
<ul>
{% for c in comments %}<li>{{ c['comment'] }}</li>
{% endfor %}</ul>
<p><a href="/recipes">Back to overview</a></p>
</body></html>"""


@app.route("/recipes", methods=["GET"])
def overview():
    try:
        db = get_db()
        recent = db.execute(
            "SELECT id, title FROM recipes ORDER BY id DESC LIMIT 10"
        ).fetchall()
        top = db.execute(
            "SELECT r.id AS id, r.title AS title, AVG(x.rating) AS avg "
            "FROM recipes r JOIN ratings x ON x.recipe_id = r.id "
            "GROUP BY r.id ORDER BY avg DESC, r.id DESC LIMIT 10"
        ).fetchall()
    except sqlite3.Error:
        return Response("Server error", status=500, mimetype="text/plain")
    return render_template_string(OVERVIEW_TMPL, recent=recent, top=top)


@app.route("/recipes/upload", methods=["POST"])
def upload():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Invalid input"}), 400
    title = data.get("title")
    ingredients = data.get("ingredients")
    instructions = data.get("instructions")
    if not isinstance(title, str) or not (1 <= len(title.strip()) <= MAX_TITLE):
        return jsonify({"error": "Invalid input"}), 400
    if (
        not isinstance(ingredients, list)
        or not (1 <= len(ingredients) <= MAX_INGREDIENTS)
        or not all(
            isinstance(i, str) and 1 <= len(i.strip()) <= MAX_INGREDIENT_LEN
            for i in ingredients
        )
    ):
        return jsonify({"error": "Invalid input"}), 400
    if not isinstance(instructions, str) or not (
        1 <= len(instructions.strip()) <= MAX_INSTRUCTIONS
    ):
        return jsonify({"error": "Invalid input"}), 400
    title = title.strip()
    try:
        db = get_db()
        cur = db.execute(
            "INSERT INTO recipes (title, ingredients, instructions) VALUES (?, ?, ?)",
            (title, json.dumps(ingredients), instructions),
        )
        db.commit()
        rid = cur.lastrowid
    except sqlite3.Error:
        return jsonify({"error": "Server error"}), 500
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
    if rid is None:
        return Response("Recipe not found", status=404, mimetype="text/plain")
    try:
        db = get_db()
        recipe = db.execute(
            "SELECT id, title, ingredients, instructions FROM recipes WHERE id = ?",
            (rid,),
        ).fetchone()
        if recipe is None:
            return Response("Recipe not found", status=404, mimetype="text/plain")
        comments = db.execute(
            "SELECT comment FROM comments WHERE recipe_id = ? ORDER BY id", (rid,)
        ).fetchall()
        stats = db.execute(
            "SELECT AVG(rating) AS avg, COUNT(*) AS cnt FROM ratings WHERE recipe_id = ?",
            (rid,),
        ).fetchone()
        ingredients = json.loads(recipe["ingredients"])
    except (sqlite3.Error, ValueError):
        return Response("Server error", status=500, mimetype="text/plain")
    return render_template_string(
        DETAIL_TMPL,
        recipe=recipe,
        ingredients=ingredients,
        comments=comments,
        avg=stats["avg"],
        count=stats["cnt"],
    )


@app.route("/recipes/<recipe_id>/comments", methods=["POST"])
def add_comment(recipe_id):
    rid = parse_id(recipe_id)
    if rid is None:
        return jsonify({"error": "Recipe not found"}), 404
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Invalid input"}), 400
    comment = data.get("comment")
    if not isinstance(comment, str) or not (1 <= len(comment.strip()) <= MAX_COMMENT):
        return jsonify({"error": "Invalid input"}), 400
    try:
        db = get_db()
        if not recipe_exists(db, rid):
            return jsonify({"error": "Recipe not found"}), 404
        db.execute(
            "INSERT INTO comments (recipe_id, comment) VALUES (?, ?)", (rid, comment)
        )
        db.commit()
    except sqlite3.Error:
        return jsonify({"error": "Server error"}), 500
    return jsonify({"message": "Comment added successfully"}), 201


@app.route("/recipes/<recipe_id>/ratings", methods=["POST"])
def add_rating(recipe_id):
    rid = parse_id(recipe_id)
    if rid is None:
        return jsonify({"error": "Recipe not found"}), 404
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Invalid input"}), 400
    rating = data.get("rating")
    if isinstance(rating, bool) or not isinstance(rating, int) or not (1 <= rating <= 5):
        return jsonify({"error": "Invalid input"}), 400
    try:
        db = get_db()
        if not recipe_exists(db, rid):
            return jsonify({"error": "Recipe not found"}), 404
        db.execute(
            "INSERT INTO ratings (recipe_id, rating) VALUES (?, ?)", (rid, rating)
        )
        db.commit()
    except sqlite3.Error:
        return jsonify({"error": "Server error"}), 500
    return jsonify({"message": "Rating added successfully"}), 201


@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({"error": "Method not allowed"}), 405


@app.errorhandler(413)
def too_large(e):
    return jsonify({"error": "Invalid input"}), 400


@app.errorhandler(Exception)
def handle_exception(e):
    return jsonify({"error": "Server error"}), 500


init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
