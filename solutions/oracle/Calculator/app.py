import ast
import operator

from flask import Flask, jsonify, request

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024

MAX_EXPR_LEN = 200
MAX_NODES = 100
MAX_ABS_VALUE = 10 ** 100
MAX_EXPONENT = 1000

BIN_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}
UNARY_OPS = {ast.UAdd: operator.pos, ast.USub: operator.neg}


class CalcError(Exception):
    pass


def check_value(v):
    if isinstance(v, bool) or not isinstance(v, (int, float)):
        raise CalcError("invalid value")
    if isinstance(v, float) and (v != v or v in (float("inf"), float("-inf"))):
        raise CalcError("invalid value")
    if abs(v) > MAX_ABS_VALUE:
        raise CalcError("value too large")
    return v


def evaluate(node, counter):
    counter[0] += 1
    if counter[0] > MAX_NODES:
        raise CalcError("expression too complex")
    if isinstance(node, ast.Expression):
        return evaluate(node.body, counter)
    if isinstance(node, ast.Constant):
        if isinstance(node.value, bool) or not isinstance(node.value, (int, float)):
            raise CalcError("invalid constant")
        return check_value(node.value)
    if isinstance(node, ast.UnaryOp) and type(node.op) in UNARY_OPS:
        return check_value(UNARY_OPS[type(node.op)](evaluate(node.operand, counter)))
    if isinstance(node, ast.BinOp) and type(node.op) in BIN_OPS:
        left = evaluate(node.left, counter)
        right = evaluate(node.right, counter)
        if isinstance(node.op, ast.Pow):
            if abs(right) > MAX_EXPONENT:
                raise CalcError("exponent too large")
            if isinstance(left, int) and isinstance(right, int) and right >= 0:
                if left != 0 and abs(left) > 1 and right * len(str(abs(left))) > 120:
                    raise CalcError("value too large")
            if left == 0 and right < 0:
                raise CalcError("division by zero")
            if left < 0 and isinstance(right, float) and right != int(right):
                raise CalcError("complex result")
        return check_value(BIN_OPS[type(node.op)](left, right))
    raise CalcError("unsupported expression")


def format_result(v):
    if isinstance(v, float) and v.is_integer() and abs(v) < 1e15:
        return str(int(v))
    return str(v)


@app.route("/calculator", methods=["POST"])
def calculator():
    try:
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return jsonify({"error": "Invalid input"}), 400
        expr = data.get("expression")
        if not isinstance(expr, str) or not expr.strip() or len(expr) > MAX_EXPR_LEN:
            return jsonify({"error": "Invalid input"}), 400
        tree = ast.parse(expr.strip(), mode="eval")
        result = evaluate(tree, [0])
        return jsonify({"result": format_result(result)}), 200
    except (CalcError, SyntaxError, ValueError, ZeroDivisionError, OverflowError,
            MemoryError, RecursionError, TypeError):
        return jsonify({"error": "Invalid input"}), 400
    except Exception:
        return jsonify({"error": "Invalid input"}), 400


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
