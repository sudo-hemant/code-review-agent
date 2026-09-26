import os

TIMEOUT = int(os.environ.get("TIMEOUT", "30"))


def request_kwargs():
    return {"timeout": TIMEOUT}


def describe():
    return f"requests time out after {TIMEOUT}s"
