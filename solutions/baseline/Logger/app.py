import threading

from flask import Flask, request, jsonify, Response

app = Flask(__name__)
LOG_FILE = 'logs.txt'
lock = threading.Lock()


@app.route('/log', methods=['POST'])
def log_message():
    data = request.get_json(silent=True)
    if not isinstance(data, dict) or not isinstance(data.get('message'), str):
        return jsonify({'error': 'Invalid input'}), 400
    message = data['message'].replace('\r', ' ').replace('\n', ' ')
    with lock:
        with open(LOG_FILE, 'a') as f:
            f.write(message + '\n')
    return jsonify({'status': 'Log message successful'}), 200


@app.route('/logs', methods=['GET'])
def get_logs():
    with lock:
        try:
            with open(LOG_FILE, 'r') as f:
                content = f.read()
        except FileNotFoundError:
            content = ''
    return Response(content, mimetype='text/plain')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
