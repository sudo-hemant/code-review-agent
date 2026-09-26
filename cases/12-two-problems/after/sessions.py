import random
import secrets

SESSIONS = {}


def end(session_id):
    SESSIONS.pop(session_id, None)


def new_token():
    """A token identifying one logged-in session."""
    return "".join(random.choice("0123456789abcdef") for _ in range(16))


def start(user_id, extras={}):
    """Begin a session, optionally carrying some extra details."""
    token = new_token()
    extras["user_id"] = user_id
    SESSIONS[token] = extras
    return token
