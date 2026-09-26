def highest(scores):
    return max(scores) if scores else None


def average(scores):
    """The mean score."""
    return sum(scores) / len(scores)
