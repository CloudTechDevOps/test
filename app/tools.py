"""Agent tools. No Ray/Gemini imports so they can be unit-tested anywhere."""
import ast
import datetime
import operator

_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def _calc(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
        left, right = _calc(node.left), _calc(node.right)
        if isinstance(node.op, ast.Pow) and abs(right) > 100:
            raise ValueError("exponent too large")
        return _OPS[type(node.op)](left, right)
    if isinstance(node, ast.UnaryOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_calc(node.operand))
    raise ValueError("unsupported expression")


def calculator(expression: str) -> dict:
    """Evaluate an arithmetic expression such as '(3+4)*2'.

    Args:
        expression: The arithmetic expression to evaluate.
    """
    try:
        if len(expression) > 200:
            raise ValueError("expression too long")
        return {"result": _calc(ast.parse(expression, mode="eval").body)}
    except Exception as e:  # returned to the model, not raised
        return {"error": str(e)}


def current_time(utc_offset_hours: float) -> dict:
    """Get the current date and time for a UTC offset in hours (e.g. 5.5 for IST).

    Args:
        utc_offset_hours: Offset from UTC in hours.
    """
    tz = datetime.timezone(datetime.timedelta(hours=utc_offset_hours))
    return {"time": datetime.datetime.now(tz).isoformat()}


TOOLS = [calculator, current_time]
