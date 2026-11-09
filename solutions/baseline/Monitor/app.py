import re
import shlex
import subprocess

from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route('/monitor/commands', methods=['POST'])
def monitor_commands():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({'code': 400, 'message': 'Invalid input'}), 400
    command_regex = data.get('command_regex')
    filter_flags = data.get('filter_flags', 'aux')
    if not isinstance(command_regex, str) or not command_regex:
        return jsonify({'code': 400, 'message': 'command_regex is required'}), 400
    if filter_flags is None:
        filter_flags = 'aux'
    if not isinstance(filter_flags, str):
        return jsonify({'code': 400, 'message': 'Invalid filter_flags'}), 400
    try:
        pattern = re.compile(command_regex)
    except re.error:
        return jsonify({'code': 400, 'message': 'Invalid regular expression'}), 400

    try:
        flags = shlex.split(filter_flags)
    except ValueError:
        return jsonify({'code': 400, 'message': 'Invalid filter_flags'}), 400

    try:
        proc = subprocess.run(['ps'] + flags, capture_output=True, text=True, timeout=30)
    except Exception:
        return jsonify({'code': 500, 'message': 'Failed to run ps'}), 500
    if proc.returncode != 0:
        return jsonify({'code': 400, 'message': 'ps failed: ' + proc.stderr.strip()}), 400

    lines = proc.stdout.splitlines()
    if not lines:
        return jsonify([]), 200
    header = lines[0].split()
    pid_idx = header.index('PID') if 'PID' in header else 1

    results = []
    for line in lines[1:]:
        if not pattern.search(line):
            continue
        parts = line.split()
        try:
            pid = int(parts[pid_idx])
        except (ValueError, IndexError):
            continue
        results.append({'processId': pid, 'processString': line})

    return jsonify(results), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
