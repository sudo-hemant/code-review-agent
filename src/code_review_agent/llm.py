"""Which model the reviewer talks to, and how to cope when it says no.

Kept in its own file on purpose. Swapping between Gemini, a model running on
your own machine, or a paid one later should be a change to the .env file and
nothing else.
"""

import os
import re
import time

from google.genai.errors import ClientError, ServerError
from langchain.chat_models import init_chat_model

# Used when .env says nothing.
DEFAULT_MODEL = "google_genai:gemini-3.8-flash"

# How many times to try before giving up on a busy or rate limited model.
MAX_ATTEMPTS = 5

# Free tiers often say exactly how long to wait, like "Please retry in 9.4s".
_RETRY_HINT = re.compile(r"retry in ([0-9.]+)s")


class MissingApiKey(Exception):
    """Raised when the chosen model needs a key and none was found."""


class ModelUnavailable(Exception):
    """Raised when the model was busy or out of quota, even after waiting."""


def get_model(temperature: float = 0.0):
    """Build the model named in REVIEW_MODEL, or the default.

    The name is "provider:model", for example:
        google_genai:gemini-3.8-flash   a free Gemini model
        ollama:qwen2.5-coder:3b         a model running on your own Mac
        anthropic:claude-opus-5         paid, for when quality matters

    Temperature is zero because a reviewer should give the same answer twice
    when handed the same code.
    """
    name = os.getenv("REVIEW_MODEL", DEFAULT_MODEL)

    if name.startswith("google_genai:") and not os.getenv("GOOGLE_API_KEY"):
        raise MissingApiKey(
            "GOOGLE_API_KEY is not set. Copy .env.example to .env and put your "
            "Gemini key in it."
        )

    return init_chat_model(name, temperature=temperature)


def _is_rate_limited(error: Exception) -> bool:
    """Is this the "you have asked too often" refusal, rather than a real fault?"""
    return isinstance(error, ClientError) and getattr(error, "code", None) == 429


def _wait_for(error: Exception, attempt: int) -> float:
    """How long to wait before trying again.

    If the service told us how long to wait, believe it. Otherwise wait a
    little longer after each failure.
    """
    hint = _RETRY_HINT.search(str(error))
    if hint:
        return float(hint.group(1)) + 1.0
    return min(2**attempt, 30)


def ask(runnable, messages):
    """Send something to the model, waiting out a busy or rate limited service.

    Only retries the two failures that go away on their own: the server being
    overloaded, and being told to slow down. A wrong key or a model name that
    does not exist will never succeed on a second try, so those come straight
    back to you.
    """
    last: Exception | None = None

    for attempt in range(MAX_ATTEMPTS):
        try:
            return runnable.invoke(messages)
        except (ServerError, ClientError) as error:
            if isinstance(error, ClientError) and not _is_rate_limited(error):
                raise
            last = error
            if attempt < MAX_ATTEMPTS - 1:
                time.sleep(_wait_for(error, attempt))

    raise ModelUnavailable(
        f"The model would not answer after {MAX_ATTEMPTS} tries. "
        "This is usually the free tier running out of quota. "
        "Wait, or set REVIEW_MODEL in your .env to a different model."
    ) from last
