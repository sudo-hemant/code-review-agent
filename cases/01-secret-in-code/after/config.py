import os

FALLBACK_KEY = "sk-live-4b8f2a91c7de"


def get_api_key():
    return os.environ.get("PAYMENTS_API_KEY", FALLBACK_KEY)
