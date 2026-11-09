import re
import subprocess

from flask import Flask, jsonify, request

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024

MAX_REGEX_LEN = 200
MAX_LINE_LEN = 4000
MAX_PROCESSES = 5000
MAX_RESULTS = 2000
TIMEOUT = 10

# Only these flag tokens are passed through to ps. Anything else is rejected.
ALLOWED_FLAGS = {
    "aux", "ax", "au", "axu", "-e", "-A", "-a", "-x", "-f", "-F", "-T", "-H",
    "-l", "-w", "-ww", "-ef", "-eF", "-ax", "-aux", "-eT", "-eLf", "-L", "-ely",
    "-u", "-j", "-y", "w", "ww", "f", "e", "l", "u", "a", "x", "T", "H", "L",
}
NESTED_QUANTIFIER = re.compile(r"(\([^)]*[+*][^)]*\))\s*[+*{]|(\\\d)\s*[+*{]")


def err(msg, code=400):
    return jsonify({"code": code, "message": msg}), code


def build_ps_args(flags):
    if flags is None or flags == "":
        return ["-e"]
    tokens = flags.split()
    if len(tokens) > 6:
        raise ValueError("too many flags")
    for t in tokens:
        if t not in ALLOWED_FLAGS:
            raise ValueError("flag not allowed")
    # Command-only output options are not supported on this OS; we never pass them.
    return tokens


@app.route("/monitor/commands", methods=["POST"])
def monitor_commands():
    try:
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return err("Invalid input")
        regex = data.get("command_regex")
        flags = data.get("filter_flags")
        if not isinstance(regex, str) or not regex or len(regex) > MAX_REGEX_LEN:
            return err("Invalid command_regex")
        if flags is not None and not isinstance(flags, str):
            return err("Invalid filter_flags")
        if NESTED_QUANTIFIER.search(regex):
            return err("Regular expression too complex")
        try:
            pattern = re.compile(regex)
        except re.error:
            return err("Invalid command_regex")
        try:
            args = build_ps_args(flags)
        except ValueError as e:
            return err(str(e))

        try:
            proc = subprocess.run(
                ["ps"] + args,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                timeout=TIMEOUT,
                text=True,
                errors="replace",
            )
        except subprocess.TimeoutExpired:
            return err("ps timed out", 500)
        except OSError:
            return err("ps unavailable", 500)
        if proc.returncode != 0:
            return err("ps failed with the given flags")

        lines = proc.stdout.splitlines()
        if not lines:
            return jsonify([]), 200
        header = lines[0].split()
        if "PID" not in header:
            return err("Unsupported output format")
        pid_idx = header.index("PID")
        ncols = len(header)
        results = []
        for line in lines[1: MAX_PROCESSES + 1]:
            line = line[:MAX_LINE_LEN]
            parts = line.split(None, ncols - 1)
            if len(parts) <= pid_idx:
                continue
            try:
                pid = int(parts[pid_idx])
            except ValueError:
                continue
            if pattern.search(line):
                results.append({"processId": pid, "processString": line.strip()})
                if len(results) >= MAX_RESULTS:
                    break
        return jsonify(results), 200
    except Exception:
        return err("Internal error", 500)


@app.errorhandler(413)
def too_large(e):
    return err("Input too large")


@app.errorhandler(404)
def not_found(e):
    return err("Not found", 404)


@app.errorhandler(405)
def not_allowed(e):
    return err("Method not allowed", 405)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
