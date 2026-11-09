from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route('/calculator', methods=['POST'])
def calculator():
    data = request.get_json(silent=True)
    if not data or 'expression' not in data or not isinstance(data['expression'], str):
        return jsonify({'error': 'Invalid input'}), 400
    expression = data['expression']
    try:
        result = eval(expression)
    except Exception:
        return jsonify({'error': 'Invalid input'}), 400
    return jsonify({'result': str(result)}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
