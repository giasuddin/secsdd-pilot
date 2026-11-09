import sqlite3
from flask import Flask, request, Response

app = Flask(__name__)
DB = "db.sqlite3"


def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute(
        "CREATE TABLE IF NOT EXISTS profiles ("
        "username TEXT PRIMARY KEY, "
        "profile_page TEXT NOT NULL, "
        "profile_photo BLOB NOT NULL)"
    )
    conn.commit()
    conn.close()


PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


@app.route("/add_profile", methods=["POST"])
def add_profile():
    username = request.form.get("username")
    page = request.form.get("profile_page")
    photo = request.files.get("profile_photo")
    if page is None and "profile_page" in request.files:
        page = request.files["profile_page"].read().decode("utf-8", errors="replace")
    if not username or page is None or photo is None:
        return Response("Invalid input", status=400)
    photo_data = photo.read()
    if not photo_data.startswith(PNG_MAGIC):
        return Response("Invalid input", status=400)
    conn = get_db()
    try:
        conn.execute(
            "INSERT INTO profiles (username, profile_page, profile_photo) VALUES (?, ?, ?)",
            (username, page, photo_data),
        )
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        return Response("Profile already exists", status=403)
    conn.close()
    return Response("Profile created successfully", status=201)


@app.route("/profile/<username>", methods=["GET"])
def get_profile(username):
    conn = get_db()
    row = conn.execute(
        "SELECT profile_page FROM profiles WHERE username = ?", (username,)
    ).fetchone()
    conn.close()
    if row is None:
        return Response("Profile not found", status=404)
    return Response(row["profile_page"], status=200, mimetype="text/html")


@app.route("/profile-photo/<username>", methods=["GET"])
def get_profile_photo(username):
    conn = get_db()
    row = conn.execute(
        "SELECT profile_photo FROM profiles WHERE username = ?", (username,)
    ).fetchone()
    conn.close()
    if row is None:
        return Response("Profile photo not found", status=404)
    return Response(bytes(row["profile_photo"]), status=200, mimetype="image/png")


init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
