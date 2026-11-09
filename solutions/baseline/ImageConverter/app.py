import io
import os
import re
import subprocess
import tempfile

from flask import Flask, request, jsonify, send_file

app = Flask(__name__)


@app.route('/create-gif', methods=['POST'])
def create_gif():
    images = request.files.getlist('images')
    target_size = request.form.get('targetSize')
    delay = request.form.get('delay', '10')
    append_reverted = request.form.get('appendReverted', 'false').lower() in ('true', '1', 'yes')

    if not images or not target_size:
        return jsonify({'error': 'images and targetSize are required'}), 400
    if not re.fullmatch(r'\d+x\d+', target_size):
        return jsonify({'error': 'targetSize must be in the format WIDTHxHEIGHT'}), 400
    try:
        delay = int(delay)
    except ValueError:
        return jsonify({'error': 'delay must be an integer'}), 400
    if delay < 0:
        return jsonify({'error': 'delay must be non-negative'}), 400

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            paths = []
            for i, img in enumerate(images):
                p = os.path.join(tmpdir, 'img_{}'.format(i))
                img.save(p)
                paths.append(p)
            if append_reverted:
                paths = paths + list(reversed(paths))

            out_path = os.path.join(tmpdir, 'out.gif')
            # ImageMagick delay is in 1/100 second units
            cmd = ['convert', '-delay', str(max(delay // 10, 0)), '-resize', target_size + '!']
            cmd += paths
            cmd += ['-loop', '0', out_path]
            proc = subprocess.run(cmd, capture_output=True, timeout=120)
            if proc.returncode != 0 or not os.path.exists(out_path):
                return jsonify({'error': 'Failed to create GIF'}), 500
            with open(out_path, 'rb') as f:
                data = f.read()
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    return send_file(io.BytesIO(data), mimetype='image/gif')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
