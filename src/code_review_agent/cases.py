"""Reading the test cases in the cases/ folder.

Each case is a folder holding the code before the change, the code after it,
and a note of what is deliberately wrong. This file turns one of those folders
into the same two things the reviewer normally gets from git: a diff, and the
full contents of the changed files.
"""

import difflib
from dataclasses import dataclass, field
from pathlib import Path

import yaml


@dataclass
class Problem:
    """One thing we know is wrong with a case, written by hand."""

    file: str
    line: int
    category: str
    note: str = ""


@dataclass
class Case:
    """One test case, ready to hand to the reviewer."""

    name: str
    description: str
    diff: str
    files: dict[str, str]
    problems: list[Problem] = field(default_factory=list)


def _relative_files(folder: Path) -> dict[str, str]:
    """Read every file under a folder, keyed by its path relative to that folder."""
    if not folder.is_dir():
        return {}
    return {
        str(path.relative_to(folder)): path.read_text(encoding="utf-8")
        for path in sorted(folder.rglob("*"))
        if path.is_file()
    }


def build_diff(before: dict[str, str], after: dict[str, str]) -> str:
    """Work out the change between two sets of files.

    The output is shaped like the diff git produces, because that is what the
    reviewer already knows how to read.
    """
    chunks: list[str] = []

    for path in sorted(set(before) | set(after)):
        old = before.get(path, "").splitlines(keepends=True)
        new = after.get(path, "").splitlines(keepends=True)
        if old == new:
            continue

        body = list(
            difflib.unified_diff(
                old,
                new,
                fromfile=f"a/{path}",
                tofile=f"b/{path}",
                n=3,
            )
        )
        if not body:
            continue

        chunks.append(f"diff --git a/{path} b/{path}\n" + "".join(body))

    return "\n".join(chunks)


def load_case(folder: Path) -> Case:
    """Read one case folder."""
    before = _relative_files(folder / "before")
    after = _relative_files(folder / "after")

    expected = yaml.safe_load((folder / "expected.yaml").read_text(encoding="utf-8")) or {}

    return Case(
        name=folder.name,
        description=expected.get("description", ""),
        diff=build_diff(before, after),
        files=after,
        problems=[Problem(**problem) for problem in expected.get("problems") or []],
    )


def load_cases(root: Path) -> list[Case]:
    """Read every case folder under cases/, in name order."""
    return [
        load_case(folder)
        for folder in sorted(root.iterdir())
        if folder.is_dir() and (folder / "expected.yaml").is_file()
    ]
