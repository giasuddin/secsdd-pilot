import io
import zipfile

from flask import Flask, request, jsonify, Response

app = Flask(__name__)

MAX_UPLOAD = 20 * 1024 * 1024
MAX_ENTRIES = 1000
MAX_ENTRY_SIZE = 10 * 1024 * 1024
MAX_TOTAL_SIZE = 50 * 1024 * 1024
app.config["MAX_CONTENT_LENGTH"] = MAX_UPLOAD + 1024 * 1024


def error(message, status):
    return jsonify({"error": message}), status


@app.errorhandler(413)
def too_large(e):
    return error("Invalid input: file too large", 400)


@app.errorhandler(404)
def not_found(e):
    return error("Not found", 404)


@app.errorhandler(405)
def not_allowed(e):
    return error("Method not allowed", 405)


@app.errorhandler(Exception)
def unexpected(e):
    return error("Invalid input", 400)


def looks_like_text(data):
    if b"\x00" in data:
        return None
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return None


@app.route("/convert", methods=["POST"])
def convert():
    f = request.files.get("file")
    if f is None or not f.filename:
        return error("Invalid input: missing file", 400)
    raw = f.read(MAX_UPLOAD + 1)
    if len(raw) > MAX_UPLOAD:
        return error("Invalid input: file too large", 400)
    if not zipfile.is_zipfile(io.BytesIO(raw)):
        return error("Invalid input: not a zip file", 400)

    parts = []
    total = 0
    try:
        with zipfile.ZipFile(io.BytesIO(raw)) as zf:
            infos = zf.infolist()
            if len(infos) > MAX_ENTRIES:
                return error("Invalid input: too many entries", 400)
            for info in infos:
                if info.is_dir():
                    continue
                if info.flag_bits & 0x1:
                    # encrypted entry cannot be read
                    continue
                if info.file_size > MAX_ENTRY_SIZE:
                    return error("Invalid input: entry too large", 400)
                # entries are only read in memory; their names are never used as paths
                with zf.open(info) as entry:
                    data = entry.read(MAX_ENTRY_SIZE + 1)
                if len(data) > MAX_ENTRY_SIZE:
                    return error("Invalid input: entry too large", 400)
                total += len(data)
                if total > MAX_TOTAL_SIZE:
                    return error("Invalid input: content too large", 400)
                text = looks_like_text(data)
                if text is None:
                    continue
                parts.append(text)
    except (zipfile.BadZipFile, zipfile.LargeZipFile, RuntimeError, NotImplementedError, EOFError, OSError, ValueError):
        return error("Invalid input: corrupt zip file", 400)

    result = "".join(p if p.endswith("\n") else p + "\n" for p in parts)
    resp = Response(result, mimetype="text/plain")
    resp.headers["X-Content-Type-Options"] = "nosniff"
    return resp


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
