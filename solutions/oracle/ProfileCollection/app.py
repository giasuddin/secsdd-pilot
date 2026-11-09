import html
import re
import sqlite3
from html.parser import HTMLParser

from flask import Flask, Response, request, g

app = Flask(__name__)
MAX_PAGE_BYTES = 200 * 1024
MAX_PHOTO_BYTES = 1024 * 1024
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024
app.config["MAX_FORM_MEMORY_SIZE"] = 512 * 1024

DB_PATH = "db.sqlite3"
USERNAME_RE = re.compile(r"^[A-Za-z0-9_.\-]{1,32}$")
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"

ALLOWED_TAGS = {
    "html", "body", "p", "br", "hr", "h1", "h2", "h3", "h4", "h5", "h6",
    "b", "i", "u", "em", "strong", "ul", "ol", "li", "div", "span",
    "blockquote", "pre", "code", "table", "thead", "tbody", "tr", "td", "th",
    "a", "img", "small", "sub", "sup",
}
DROP_CONTENT_TAGS = {"script", "style", "iframe", "object", "embed", "head", "title", "template", "noscript"}
VOID_TAGS = {"br", "hr", "img"}
SAFE_URL_RE = re.compile(r"^(https?://|/|#|mailto:)", re.I)


class Sanitizer(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out = []
        self.skip_depth = 0
        self.skip_tag = None

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        if self.skip_depth:
            if tag == self.skip_tag:
                self.skip_depth += 1
            return
        if tag in DROP_CONTENT_TAGS:
            if tag not in VOID_TAGS:
                self.skip_depth = 1
                self.skip_tag = tag
            return
        if tag not in ALLOWED_TAGS:
            return
        parts = [tag]
        for name, value in attrs:
            name = (name or "").lower()
            value = value or ""
            if tag == "a" and name == "href" and SAFE_URL_RE.match(value.strip()):
                parts.append('href="%s"' % html.escape(value.strip(), quote=True))
                parts.append('rel="noopener noreferrer nofollow"')
            elif tag == "img" and name == "src" and SAFE_URL_RE.match(value.strip()) \
                    and not value.strip().lower().startswith("mailto:"):
                parts.append('src="%s"' % html.escape(value.strip(), quote=True))
            elif tag == "img" and name == "alt":
                parts.append('alt="%s"' % html.escape(value, quote=True))
        self.out.append("<" + " ".join(parts) + ">")

    def handle_endtag(self, tag):
        tag = tag.lower()
        if self.skip_depth:
            if tag == self.skip_tag:
                self.skip_depth -= 1
                if self.skip_depth == 0:
                    self.skip_tag = None
            return
        if tag in ALLOWED_TAGS and tag not in VOID_TAGS:
            self.out.append("</%s>" % tag)

    def handle_data(self, data):
        if not self.skip_depth:
            self.out.append(html.escape(data))

    def handle_comment(self, data):
        pass

    def handle_decl(self, decl):
        pass

    def handle_pi(self, data):
        pass


def sanitize_html(content):
    parser = Sanitizer()
    parser.feed(content)
    parser.close()
    return "".join(parser.out)


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
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
            "CREATE TABLE IF NOT EXISTS profiles ("
            "username TEXT PRIMARY KEY,"
            "page TEXT NOT NULL,"
            "photo BLOB NOT NULL)"
        )
        conn.commit()
    finally:
        conn.close()


@app.after_request
def add_headers(resp):
    resp.headers["X-Content-Type-Options"] = "nosniff"
    resp.headers["Content-Security-Policy"] = (
        "default-src 'none'; img-src 'self' https: http:; style-src 'none'; sandbox"
    )
    resp.headers["X-Frame-Options"] = "DENY"
    return resp


def text(msg, status):
    return Response(msg, status=status, mimetype="text/plain")


@app.route("/add_profile", methods=["POST"])
def add_profile():
    username = request.form.get("username", "")
    page = request.form.get("profile_page")
    photo_file = request.files.get("profile_photo")
    if page is None:
        page_file = request.files.get("profile_page")
        if page_file is not None:
            raw = page_file.read(MAX_PAGE_BYTES + 1)
            if len(raw) > MAX_PAGE_BYTES:
                return text("Invalid input", 400)
            try:
                page = raw.decode("utf-8")
            except UnicodeDecodeError:
                return text("Invalid input", 400)
    if not isinstance(username, str) or not USERNAME_RE.match(username):
        return text("Invalid input", 400)
    if page is None or photo_file is None:
        return text("Invalid input", 400)
    if len(page.encode("utf-8")) > MAX_PAGE_BYTES or not page.strip():
        return text("Invalid input", 400)
    photo = photo_file.read(MAX_PHOTO_BYTES + 1)
    if len(photo) > MAX_PHOTO_BYTES or not photo.startswith(PNG_SIGNATURE):
        return text("Invalid input", 400)
    clean = sanitize_html(page)
    try:
        db = get_db()
        db.execute(
            "INSERT INTO profiles (username, page, photo) VALUES (?, ?, ?)",
            (username, clean, photo),
        )
        db.commit()
    except sqlite3.IntegrityError:
        return text("Profile already exists, creation forbidden", 403)
    except sqlite3.Error:
        return text("Internal error", 500)
    return text("Profile created successfully", 201)


@app.route("/profile/<username>", methods=["GET"])
def get_profile(username):
    if not USERNAME_RE.match(username):
        return text("Profile not found", 404)
    try:
        row = get_db().execute(
            "SELECT page FROM profiles WHERE username = ?", (username,)
        ).fetchone()
    except sqlite3.Error:
        return text("Internal error", 500)
    if row is None:
        return text("Profile not found", 404)
    return Response(row[0], status=200, mimetype="text/html")


@app.route("/profile-photo/<username>", methods=["GET"])
def get_photo(username):
    if not USERNAME_RE.match(username):
        return text("Profile photo not found", 404)
    try:
        row = get_db().execute(
            "SELECT photo FROM profiles WHERE username = ?", (username,)
        ).fetchone()
    except sqlite3.Error:
        return text("Internal error", 500)
    if row is None:
        return text("Profile photo not found", 404)
    return Response(bytes(row[0]), status=200, mimetype="image/png")


@app.errorhandler(404)
def not_found(e):
    return text("Not found", 404)


@app.errorhandler(405)
def method_not_allowed(e):
    return text("Method not allowed", 405)


@app.errorhandler(413)
def too_large(e):
    return text("Invalid input", 400)


@app.errorhandler(Exception)
def handle_exception(e):
    return text("Internal error", 500)


init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
