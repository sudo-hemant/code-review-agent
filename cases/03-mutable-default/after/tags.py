def normalise(tag):
    return tag.strip().lower()


def collect(tag, seen=[]):
    """Add a tag to the running list and hand the list back."""
    seen.append(normalise(tag))
    return seen
