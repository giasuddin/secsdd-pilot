import multiprocessing
import os
import re

from flask import Flask, request, jsonify

app = Flask(__name__)

ROOT = os.path.realpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "files"))
MAX_REGEX_LEN = 500
MAX_FILE_BYTES = 2 * 1024 * 1024
MAX_FILES_SCANNED = 5000
MAX_RESULTS = 5000
SEARCH_TIMEOUT = 10


def error(message, status):
    return jsonify({"error": message}), status


def is_inside(root, path):
    try:
        return os.path.commonpath([root, path]) == root
    except ValueError:
        return False


def _worker(pattern, base, recursive, queue):
    try:
        rx = re.compile(pattern)
        found = []
        scanned = 0
        if recursive:
            walker = os.walk(base, followlinks=False)
        else:
            try:
                names = sorted(os.listdir(base))
            except OSError:
                names = []
            walker = [(base, [], names)]
        for dirpath, dirnames, filenames in walker:
            dirnames.sort()
            for fn in sorted(filenames):
                full = os.path.join(dirpath, fn)
                real = os.path.realpath(full)
                if not is_inside(ROOT, real) or not os.path.isfile(real):
                    continue
                scanned += 1
                if scanned > MAX_FILES_SCANNED:
                    queue.put(("ok", found))
                    return
                try:
                    with open(real, "rb") as fh:
                        data = fh.read(MAX_FILE_BYTES)
                    text = data.decode("utf-8", errors="ignore")
                except OSError:
                    continue
                if rx.search(text):
                    found.append(os.path.relpath(full, base).replace(os.sep, "/"))
                    if len(found) >= MAX_RESULTS:
                        queue.put(("ok", found))
                        return
        queue.put(("ok", found))
    except Exception:
        queue.put(("err", "search failed"))


def run_search(pattern, base, recursive):
    try:
        ctx = multiprocessing.get_context("fork")
    except ValueError:
        ctx = multiprocessing.get_context()
    queue = ctx.Queue()
    proc = ctx.Process(target=_worker, args=(pattern, base, recursive, queue))
    proc.start()
    try:
        result = queue.get(timeout=SEARCH_TIMEOUT)
    except Exception:
        result = ("timeout", None)
    finally:
        if proc.is_alive():
            proc.terminate()
        proc.join(timeout=2)
        if proc.is_alive():
            proc.kill()
            proc.join(timeout=2)
    return result


@app.errorhandler(404)
def not_found(e):
    return error("Not found", 404)


@app.errorhandler(405)
def not_allowed(e):
    return error("Method not allowed", 405)


@app.errorhandler(Exception)
def unexpected(e):
    return error("Internal server error", 500)


@app.route("/search", methods=["GET"])
def search():
    pattern = request.args.get("regex")
    if not pattern:
        return error("Missing regex", 400)
    if len(pattern) > MAX_REGEX_LEN:
        return error("Regex too long", 400)
    try:
        re.compile(pattern)
    except (re.error, RecursionError, OverflowError):
        return error("Malformed regex", 400)

    rec = request.args.get("recursive", "false").strip().lower()
    if rec in ("true", "1", "yes"):
        recursive = True
    elif rec in ("false", "0", "no", ""):
        recursive = False
    else:
        return error("Invalid recursive value", 400)

    directory = request.args.get("directory", "") or ""
    if "\x00" in directory or os.path.isabs(directory):
        return error("Invalid directory", 400)
    base = os.path.realpath(os.path.join(ROOT, directory))
    if not is_inside(ROOT, base) or not os.path.isdir(base):
        return error("Invalid or inaccessible directory", 400)

    status, payload = run_search(pattern, base, recursive)
    if status == "ok":
        return jsonify({"files": payload}), 200
    if status == "timeout":
        return error("Search timed out; regex too complex", 400)
    return error("Internal server error", 500)


if __name__ == "__main__":
    os.makedirs(ROOT, exist_ok=True)
    app.run(host="0.0.0.0", port=5000, debug=False)
