"""Conversation helpers. No Ray/Gemini imports so they can be unit-tested anywhere."""

MAX_HISTORY = 20          # most recent turns sent to the model
MAX_TEXT_LEN = 4000       # per message

# UI role -> Gemini role
_ROLES = {"user": "user", "assistant": "model"}


def build_contents(history: list[dict], message: str) -> list[dict]:
    """Convert UI chat history plus the new message into Gemini `contents`.

    history items look like {"role": "user"|"assistant", "content": "..."}.
    Invalid roles and empty messages are dropped; only the last MAX_HISTORY are kept.
    """
    contents = []
    for item in history[-MAX_HISTORY:]:
        role = _ROLES.get(item.get("role"))
        text = (item.get("content") or "").strip()[:MAX_TEXT_LEN]
        if role and text:
            contents.append({"role": role, "parts": [{"text": text}]})
    contents.append({"role": "user", "parts": [{"text": message[:MAX_TEXT_LEN]}]})
    return contents
