from collections import defaultdict

_sessions: dict[str, list] = defaultdict(list)
MAX_HISTORY = 6

def get_history(session_id: str) -> list[dict]:
    return _sessions[session_id]

def add_turn(session_id: str, question: str, sql: str) -> None:
    _sessions[session_id].append({"role": "user", "content": question})
    _sessions[session_id].append({"role": "assistant", "content": sql})
    _sessions[session_id] = _sessions[session_id][-MAX_HISTORY:]

def clear_history(session_id: str) -> None:
    _sessions[session_id] = []