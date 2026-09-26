import os

HTTP_TIMEOUT_SECONDS = int(os.environ.get("HTTP_TIMEOUT_SECONDS", "30"))


def request_kwargs():
    return {"timeout": HTTP_TIMEOUT_SECONDS}


def describe():
    return f"requests time out after {HTTP_TIMEOUT_SECONDS}s"
