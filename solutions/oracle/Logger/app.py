import os
import threading

from flask import Flask, Response, jsonify, request

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024

LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs.txt")
MAX_MESSAGE_LEN = 4096
MAX_LOG_READ = 5 * 1024 * 1024
lock = threading.Lock()


def sanitize(message):
    out = []
    for ch in message:
        if ch == "\n":
            out.append("\\n")
        elif ch == "\r":
            out.append("\\r")
        elif ch == "\\":
            out.append("\\\\")
        elif ord(ch) < 32 or ord(ch) == 127 or ch in "  \u0085":
            out.append("\\x%02x" % (ord(ch) & 0xFF) if ord(ch) < 256 else "\\u%04x" % ord(ch))
        else:
            out.append(ch)
    return "".join(out)


@app.route("/log", methods=["POST"])
def log_message():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Invalid input"}), 400
    message = data.get("message")
    if not isinstance(message, str) or len(message) > MAX_MESSAGE_LEN:
        return jsonify({"error": "Invalid input"}), 400
    line = sanitize(message) + "\n"
    try:
        with lock:
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(line)
    except OSError:
        return jsonify({"error": "Internal error"}), 500
    return jsonify({"status": "ok"}), 200


@app.route("/logs", methods=["GET"])
def get_logs():
    try:
        with lock:
            if not os.path.exists(LOG_FILE):
                content = ""
            else:
                size = os.path.getsize(LOG_FILE)
                with open(LOG_FILE, "rb") as f:
                    if size > MAX_LOG_READ:
                        f.seek(size - MAX_LOG_READ)
                    raw = f.read()
                content = raw.decode("utf-8", errors="replace")
    except OSError:
        return Response("Internal error", status=500, mimetype="text/plain")
    resp = Response(content, status=200, mimetype="text/plain")
    resp.headers["X-Content-Type-Options"] = "nosniff"
    return resp


@app.errorhandler(413)
def too_large(e):
    return jsonify({"error": "Invalid input"}), 400


@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(405)
def not_allowed(e):
    return jsonify({"error": "Method not allowed"}), 405


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
