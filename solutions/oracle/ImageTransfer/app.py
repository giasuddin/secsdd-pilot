import os
import re
import uuid

from flask import Flask, Response, jsonify, request

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

ID_RE = re.compile(r"^[0-9a-f]{32}$")

# detected format -> (extension, mimetype). SVG/HTML are deliberately excluded (script execution risk).
FORMATS = {
    "png": ("png", "image/png"),
    "jpeg": ("jpg", "image/jpeg"),
    "gif": ("gif", "image/gif"),
    "bmp": ("bmp", "image/bmp"),
    "webp": ("webp", "image/webp"),
    "tiff": ("tiff", "image/tiff"),
    "ico": ("ico", "image/x-icon"),
}
EXT_TO_MIME = {ext: mime for ext, mime in FORMATS.values()}


def err(msg, code):
    return jsonify({"error": msg}), code


def detect_format(head):
    if head.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png"
    if head.startswith(b"\xff\xd8\xff"):
        return "jpeg"
    if head.startswith(b"GIF87a") or head.startswith(b"GIF89a"):
        return "gif"
    if head.startswith(b"BM"):
        return "bmp"
    if head[:4] == b"RIFF" and head[8:12] == b"WEBP":
        return "webp"
    if head.startswith(b"II*\x00") or head.startswith(b"MM\x00*"):
        return "tiff"
    if head.startswith(b"\x00\x00\x01\x00"):
        return "ico"
    return None


@app.after_request
def headers(resp):
    resp.headers["X-Content-Type-Options"] = "nosniff"
    return resp


@app.route("/upload", methods=["POST"])
def upload():
    try:
        f = request.files.get("file")
        if f is None:
            return err("No file provided", 400)
        data = f.stream.read(app.config["MAX_CONTENT_LENGTH"] + 1)
        if not data or len(data) > app.config["MAX_CONTENT_LENGTH"]:
            return err("Invalid file", 400)
        fmt = detect_format(data[:16])
        if fmt is None:
            return err("File is not a supported image", 400)
        ext = FORMATS[fmt][0]
        image_id = uuid.uuid4().hex
        path = os.path.join(UPLOAD_DIR, "%s.%s" % (image_id, ext))
        with open(path, "xb") as out:
            out.write(data)
        return jsonify({"id": image_id}), 200
    except Exception:
        return err("Internal server error", 500)


@app.route("/images/<image_id>", methods=["GET"])
def get_image(image_id):
    try:
        if not ID_RE.match(image_id):
            return err("Image not found", 404)
        for ext, mime in EXT_TO_MIME.items():
            path = os.path.join(UPLOAD_DIR, "%s.%s" % (image_id, ext))
            if os.path.isfile(path) and not os.path.islink(path):
                with open(path, "rb") as fh:
                    data = fh.read()
                resp = Response(data, status=200, mimetype=mime)
                resp.headers["Content-Disposition"] = "inline"
                resp.headers["Content-Security-Policy"] = "default-src 'none'; sandbox"
                resp.headers["Cache-Control"] = "private, max-age=3600"
                return resp
        return err("Image not found", 404)
    except Exception:
        return err("Internal server error", 500)


@app.errorhandler(413)
def too_large(e):
    return err("File too large", 400)


@app.errorhandler(404)
def not_found(e):
    return err("Not found", 404)


@app.errorhandler(405)
def not_allowed(e):
    return err("Method not allowed", 405)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
