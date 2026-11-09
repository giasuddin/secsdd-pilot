import os
import re
import shutil
import subprocess
import tempfile

from flask import Flask, jsonify, request

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 256 * 1024

MAX_CONTENT_CHARS = 100000
TIMEOUT = 20
MAX_OUTPUT = 20000
NAME_RE = re.compile(r"^[A-Za-z0-9_][A-Za-z0-9_.-]{0,99}$")
CPP_EXT = (".cpp", ".cc", ".cxx")


def bad(msg):
    return jsonify({"error": msg}), 400


@app.route("/compile", methods=["POST"])
def compile_file():
    tmpdir = None
    try:
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return bad("Invalid input")
        file_name = data.get("fileName")
        content = data.get("fileContent")
        if not isinstance(file_name, str) or not isinstance(content, str):
            return bad("Invalid input")
        if len(content) > MAX_CONTENT_CHARS or "\x00" in content:
            return bad("Invalid input")
        if (
            "/" in file_name
            or "\\" in file_name
            or ".." in file_name
            or not NAME_RE.match(file_name)
        ):
            return bad("Invalid file name")
        lower = file_name.lower()
        if lower.endswith(".ts"):
            kind = "ts"
        elif lower.endswith(CPP_EXT):
            kind = "cpp"
        else:
            return bad("Unsupported file type")

        tmpdir = tempfile.mkdtemp(prefix="compile_")
        path = os.path.join(tmpdir, file_name)
        if os.path.dirname(os.path.realpath(path)) != os.path.realpath(tmpdir):
            return bad("Invalid file name")
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

        if kind == "ts":
            cmd = ["tsc", "--noEmit", "--pretty", "false", "--", file_name]
        else:
            cmd = ["g++", "-fsyntax-only", "--", file_name]

        try:
            proc = subprocess.run(
                cmd,
                cwd=tmpdir,
                capture_output=True,
                text=True,
                timeout=TIMEOUT,
                stdin=subprocess.DEVNULL,
                errors="replace",
            )
        except subprocess.TimeoutExpired:
            return jsonify({"hasError": True, "compilerError": "Compilation timed out"}), 200
        except (FileNotFoundError, OSError):
            return jsonify({"error": "Compiler unavailable"}), 500

        output = ((proc.stdout or "") + (proc.stderr or "")).strip()
        output = output[:MAX_OUTPUT]
        if proc.returncode == 0:
            return jsonify({"hasError": False, "compilerError": None}), 200
        return jsonify({"hasError": True, "compilerError": output}), 200
    except Exception:
        return jsonify({"error": "Internal error"}), 500
    finally:
        if tmpdir:
            shutil.rmtree(tmpdir, ignore_errors=True)


@app.errorhandler(413)
def too_large(e):
    return bad("Input too large")


@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(405)
def not_allowed(e):
    return jsonify({"error": "Method not allowed"}), 405


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
