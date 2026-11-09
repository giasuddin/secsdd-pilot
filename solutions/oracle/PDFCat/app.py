import os
import subprocess
import tempfile
import uuid

from flask import Flask, request, jsonify, Response

app = Flask(__name__)

MAX_FILES = 50
MAX_FILE_SIZE = 20 * 1024 * 1024
app.config["MAX_CONTENT_LENGTH"] = MAX_FILES * MAX_FILE_SIZE // 5
SUBPROCESS_TIMEOUT = 60


def error(message, status):
    return jsonify({"error": message}), status


def is_pdf(data):
    return data[:5] == b"%PDF-"


@app.errorhandler(413)
def too_large(e):
    return error("Request too large.", 400)


@app.errorhandler(404)
def not_found(e):
    return error("Not found.", 404)


@app.errorhandler(405)
def not_allowed(e):
    return error("Method not allowed.", 405)


@app.errorhandler(Exception)
def unexpected(e):
    return error("An error occurred while processing the files.", 500)


@app.route("/concatenate", methods=["POST"])
def concatenate():
    try:
        files = request.files.getlist("files")
    except Exception:
        return error("Invalid input or missing files.", 400)
    files = [f for f in files if f and f.filename]
    if not files:
        return error("Invalid input or missing files.", 400)
    if len(files) > MAX_FILES:
        return error("Too many files.", 400)

    contents = []
    for f in files:
        data = f.read(MAX_FILE_SIZE + 1)
        if len(data) > MAX_FILE_SIZE:
            return error("File too large.", 400)
        if not is_pdf(data):
            return error("Invalid input or missing files.", 400)
        contents.append(data)

    try:
        with tempfile.TemporaryDirectory() as tmp:
            paths = []
            for data in contents:
                # server-generated names only; user filenames are never used
                path = os.path.join(tmp, uuid.uuid4().hex + ".pdf")
                with open(path, "wb") as out:
                    out.write(data)
                paths.append(path)
            output = os.path.join(tmp, "concatenated-" + uuid.uuid4().hex + ".pdf")
            if len(paths) == 1:
                result = contents[0]
            else:
                try:
                    proc = subprocess.run(
                        ["pdfunite"] + paths + [output],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        timeout=SUBPROCESS_TIMEOUT,
                        shell=False,
                        check=False,
                    )
                except subprocess.TimeoutExpired:
                    return error("An error occurred while processing the files.", 500)
                if proc.returncode != 0 or not os.path.isfile(output):
                    return error("Invalid input or missing files.", 400)
                with open(output, "rb") as fh:
                    result = fh.read()
        return Response(result, mimetype="application/pdf")
    except Exception:
        return error("An error occurred while processing the files.", 500)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
