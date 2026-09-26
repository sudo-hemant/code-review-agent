import secrets

SESSIONS = {}


def end(session_id):
    SESSIONS.pop(session_id, None)
