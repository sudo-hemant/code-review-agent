"""Which model the reviewer talks to.

Kept in its own file on purpose. Swapping between Gemini, a model running on
your own machine, or a paid one later should be a change to the .env file and
nothing else.
"""

import os

from langchain.chat_models import init_chat_model

# Used when .env says nothing. Gemini's free tier covers this one.
DEFAULT_MODEL = "google_genai:gemini-3.8-flash"


class MissingApiKey(Exception):
    """Raised when the chosen model needs a key and none was found."""


def get_model(temperature: float = 0.0):
    """Build the model named in REVIEW_MODEL, or the default.

    The name is "provider:model", for example:
        google_genai:gemini-2.0-flash   a free Gemini model
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
