import os

from flask import Flask, request, jsonify, Response

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024

SONG_DIR = os.path.realpath("/var/songs")
CHUNK = 64 * 1024


def error(message, status):
    return jsonify({"error": message}), status


@app.errorhandler(413)
def too_large(e):
    return error("Invalid input", 400)


@app.errorhandler(404)
def not_found(e):
    return error("Not found", 404)


@app.errorhandler(405)
def not_allowed(e):
    return error("Method not allowed", 405)


@app.errorhandler(Exception)
def unexpected(e):
    return error("Internal server error", 500)


def stream_file(fh):
    try:
        while True:
            chunk = fh.read(CHUNK)
            if not chunk:
                break
            yield chunk
    finally:
        fh.close()


@app.route("/download", methods=["POST"])
def download():
    body = request.get_json(silent=True)
    if not isinstance(body, dict):
        return error("Invalid input", 400)
    filename = body.get("filename")
    if not isinstance(filename, str) or not filename or len(filename) > 255:
        return error("Invalid input", 400)
    if (
        "\x00" in filename
        or "/" in filename
        or "\\" in filename
        or filename in (".", "..")
        or os.path.basename(filename) != filename
    ):
        return error("Invalid input", 400)

    path = os.path.realpath(os.path.join(SONG_DIR, filename))
    try:
        inside = os.path.commonpath([SONG_DIR, path]) == SONG_DIR and path != SONG_DIR
    except ValueError:
        inside = False
    if not inside:
        return error("Invalid input", 400)
    if not os.path.isfile(path):
        return error("File does not exist", 404)

    try:
        fh = open(path, "rb")
        size = os.fstat(fh.fileno()).st_size
    except OSError:
        return error("File does not exist", 404)

    resp = Response(stream_file(fh), mimetype="audio/mpeg")
    resp.headers["Content-Length"] = str(size)
    resp.headers["X-Content-Type-Options"] = "nosniff"
    return resp


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
