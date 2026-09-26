import os

EXPECTED_TOKEN = os.environ["API_TOKEN"]


def token_is_valid(supplied):
    """Check a caller's token against the one we expect."""
    return supplied == EXPECTED_TOKEN
