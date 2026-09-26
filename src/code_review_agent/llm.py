"""Which model the reviewer talks to.

Kept in its own file on purpose. Swapping between Gemini, a model running on
your own machine, or a paid one later should be a change to the .env file and
nothing else.
"""

import os

from google.genai.errors import ServerError
from langchain.chat_models import init_chat_model

# Used when .env says nothing. Gemini's free tier covers this one.
DEFAULT_MODEL = "google_genai:gemini-3.8-flash"

# Free tiers get busy and answer "try again later". That is worth waiting out
# rather than failing the whole review, so we retry a few times with a pause
# that grows each go.
MAX_ATTEMPTS = 5


class MissingApiKey(Exception):
    """Raised when the chosen model needs a key and none was found."""


class ModelBusy(Exception):
    """Raised when the model was too busy to answer, even after waiting."""


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


def with_retries(runnable):
    """Wrap a model so a busy server is waited out instead of failing the run.

    Only retries the "server is overloaded" kind of failure. A wrong key or a
    model name that does not exist will never succeed on a second try, so those
    come straight back to you.
    """
    return runnable.with_retry(
        retry_if_exception_type=(ServerError,),
        stop_after_attempt=MAX_ATTEMPTS,
        wait_exponential_jitter=True,
    )
