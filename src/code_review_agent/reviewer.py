"""Step two of the review: ask Claude what is wrong with the change.

PLACEHOLDER. This is the one piece of phase one that is not built yet. It
currently hands back an empty review so the rest of the program can be run and
checked end to end without an API key. Filling this in is the next job.
"""

from .findings import Review, Verdict


def review_changes(diff: str, files: dict[str, str]) -> Review:
    """Look at a change and say what is wrong with it.

    What this will do once it is built:
      1. Build the instructions describing what a good reviewer looks for.
      2. Send those instructions, the change, and the full files to Claude.
      3. Require the answer to come back shaped like a Review, so every finding
         arrives with a file, a line, a category, a severity and a confidence.
      4. Hand that Review back.
    """
    return Review(
        findings=[],
        verdict=Verdict.COMMENT,
        summary=(
            f"The reviewer is not built yet. It was handed {len(diff)} characters "
            f"of changes across {len(files)} file(s) and did nothing with them."
        ),
    )
