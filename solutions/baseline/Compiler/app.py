import os
import subprocess
import tempfile

from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route('/compile', methods=['POST'])
def compile_code():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'Invalid input'}), 400
    file_name = data.get('fileName')
    file_content = data.get('fileContent')
    if not isinstance(file_name, str) or not isinstance(file_content, str):
        return jsonify({'error': 'Invalid input'}), 400

    ext = os.path.splitext(file_name)[1].lower()
    if ext not in ('.ts', '.cpp'):
        return jsonify({'error': 'Unsupported file type'}), 400

    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, file_name)
        with open(path, 'w') as f:
            f.write(file_content)

        if ext == '.ts':
            cmd = ['tsc', '--noEmit', file_name]
        else:
            cmd = ['g++', '-fsyntax-only', file_name]

        try:
            proc = subprocess.run(cmd, cwd=tmpdir, capture_output=True, text=True, timeout=30)
        except subprocess.TimeoutExpired:
            return jsonify({'hasError': True, 'compilerError': 'Compilation timed out'}), 200

        output = (proc.stdout + proc.stderr).strip()
        if proc.returncode != 0:
            return jsonify({'hasError': True, 'compilerError': output}), 200
        return jsonify({'hasError': False, 'compilerError': None}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
