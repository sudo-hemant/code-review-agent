def slugify(title: str) -> str:
    """Turn a title into something safe for a URL."""
    return "-".join(title.lower().split())
