import os

from flask import Flask, jsonify, request

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 64 * 1024

DATA_DIR = os.path.realpath("/data")
MAX_FILE_BYTES = 10 * 1024 * 1024
MAX_RESULTS = 1000
MAX_FILES_SCANNED = 20000
MAX_FIELD_LEN = 1000


def bad(msg="Invalid input"):
    return jsonify({"error": msg}), 400


def resolve_dir(search_dir):
    if search_dir is None or search_dir == "":
        return DATA_DIR
    if "\x00" in search_dir:
        return None
    rel = search_dir.lstrip("/\\")
    candidate = os.path.realpath(os.path.join(DATA_DIR, rel))
    if candidate != DATA_DIR and not candidate.startswith(DATA_DIR + os.sep):
        return None
    if not os.path.isdir(candidate):
        return None
    return candidate


def content_matches(path, needle_bytes):
    try:
        if os.path.getsize(path) > MAX_FILE_BYTES:
            return False
        with open(path, "rb") as f:
            return needle_bytes in f.read(MAX_FILE_BYTES)
    except OSError:
        return False


@app.route("/search", methods=["POST"])
def search():
    try:
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return bad()
        content = data.get("search_content")
        filename = data.get("search_filename")
        search_dir = data.get("search_dir")
        for v in (content, filename, search_dir):
            if v is not None and (not isinstance(v, str) or len(v) > MAX_FIELD_LEN):
                return bad()
        if not content and not filename:
            return bad()
        if filename and ("/" in filename or "\\" in filename or "\x00" in filename):
            return bad()
        if content and "\x00" in content:
            return bad()

        base = resolve_dir(search_dir)
        if base is None:
            return bad()

        needle = content.encode("utf-8") if content else None
        results = []
        scanned = 0
        for root, dirs, files in os.walk(base, followlinks=False):
            dirs.sort()
            for name in sorted(files):
                scanned += 1
                if scanned > MAX_FILES_SCANNED or len(results) >= MAX_RESULTS:
                    break
                full = os.path.join(root, name)
                if os.path.islink(full):
                    continue
                real = os.path.realpath(full)
                if not real.startswith(DATA_DIR + os.sep):
                    continue
                if not os.path.isfile(real):
                    continue
                ok = True
                if filename and not name.startswith(filename):
                    ok = False
                if ok and needle is not None and not content_matches(real, needle):
                    ok = False
                if ok:
                    results.append(real)
            if scanned > MAX_FILES_SCANNED or len(results) >= MAX_RESULTS:
                break
        return jsonify({"files": results}), 200
    except Exception:
        return bad()


@app.errorhandler(413)
def too_large(e):
    return bad()


@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(405)
def not_allowed(e):
    return jsonify({"error": "Method not allowed"}), 405


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
