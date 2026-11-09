import os
import subprocess
import tempfile

from flask import Flask, request, jsonify, send_file
from werkzeug.utils import secure_filename
import io

app = Flask(__name__)


@app.route('/extract', methods=['POST'])
def extract():
    video = request.files.get('video')
    frame_number = request.form.get('frameNumber')
    video_name = request.form.get('videoFileName') or (video.filename if video else None)

    if video is None or frame_number is None or not video_name:
        return jsonify({'error': 'Invalid input'}), 400
    try:
        frame_number = int(frame_number)
    except ValueError:
        return jsonify({'error': 'Invalid input'}), 400
    if frame_number < 0:
        return jsonify({'error': 'Invalid input'}), 400

    safe_name = secure_filename(video_name) or 'video.mp4'

    with tempfile.TemporaryDirectory() as tmpdir:
        in_path = os.path.join(tmpdir, safe_name)
        out_path = os.path.join(tmpdir, 'frame.png')
        video.save(in_path)

        cmd = [
            'ffmpeg', '-y', '-i', in_path,
            '-vf', 'select=eq(n\\,{})'.format(frame_number),
            '-vframes', '1', out_path,
        ]
        try:
            subprocess.run(cmd, capture_output=True, timeout=60)
        except subprocess.TimeoutExpired:
            pass

        if not os.path.exists(out_path) or os.path.getsize(out_path) == 0:
            return jsonify({'error': 'Frame at index {} could not be found.'.format(frame_number)}), 404

        with open(out_path, 'rb') as f:
            data = f.read()

    return send_file(io.BytesIO(data), mimetype='image/png')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
