def average(scores):
    """The mean score, or None when there are no scores."""
    if not scores:
        return None
    return sum(scores) / len(scores)
