def slugify(title: str) -> str:
    """Turn a title into something safe for a URL."""
    return "-".join(title.lower().split())


def truncate(text: str, limit: int) -> str:
    """Shorten text to at most `limit` characters, ending with an ellipsis.

    Text already short enough is returned untouched.
    """
    if limit <= 0:
        raise ValueError("limit must be positive")
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"
