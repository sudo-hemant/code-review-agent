"""Step one of the review: find out what changed, and read the files it touched.

Nothing here talks to a model. This is the plain, boring, entirely predictable
part, which is exactly why it is worth keeping separate from the part that guesses.
"""

import re
import subprocess
from pathlib import Path

# Lines in a git change that announce a file, for example:
#   diff --git a/src/thing.py b/src/thing.py
_FILE_HEADER = re.compile(r"^diff --git a/(?P<old>.+?) b/(?P<new>.+?)$", re.MULTILINE)


class NotAGitRepository(Exception):
    """Raised when we are asked to review a folder that git does not know about."""


def _git(repo: Path, *args: str) -> str:
    """Run a git command inside a repository and hand back whatever it printed."""
    result = subprocess.run(
        ["git", *args],
        cwd=repo,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {result.stderr.strip()}")
    return result.stdout


def get_diff(repo: Path, base: str | None = None) -> str:
    """Collect the changes to review.

    With no base given, this is everything you have changed but not yet committed.
    With a base given, such as "main", it is everything on your branch that is not
    on that base yet.
    """
    if not (repo / ".git").exists():
        raise NotAGitRepository(f"{repo} is not a git repository")

    if base:
        return _git(repo, "diff", f"{base}...HEAD")

    # Uncommitted work, staged and unstaged together.
    return _git(repo, "diff", "HEAD")


def changed_files(diff: str) -> list[str]:
    """Pull the list of touched file paths out of a change."""
    seen: list[str] = []
    for match in _FILE_HEADER.finditer(diff):
        path = match.group("new")
        if path != "/dev/null" and path not in seen:
            seen.append(path)
    return seen


def read_files(repo: Path, paths: list[str], max_bytes: int = 200_000) -> dict[str, str]:
    """Read the full current contents of each changed file.

    The reviewer needs these because a handful of changed lines almost never
    make sense on their own. Files that are gone, unreadable, or far too large
    are simply left out rather than allowed to break the run.
    """
    contents: dict[str, str] = {}
    for path in paths:
        full = repo / path
        try:
            if not full.is_file() or full.stat().st_size > max_bytes:
                continue
            contents[path] = full.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
    return contents
