"""The three steps of a review, wired together in order.

Right now the order is a plain straight line: collect the change, review it,
present it. LangGraph is more machinery than a straight line needs, and that is
on purpose. In a later phase the middle step splits into several reviewers
running at the same time, and when that happens the shape changes rather than
the whole program being rewritten.

The state below is the shared notebook. Every step reads from it and writes
back into it, and whatever is in it at the end is the result.
"""

from pathlib import Path
from typing import TypedDict

from langgraph.graph import END, START, StateGraph

from . import changes, reviewer
from .findings import Review


class ReviewState(TypedDict, total=False):
    """Everything the steps pass between each other."""

    repo: Path            # the project being reviewed
    base: str | None      # what to compare against, or None for uncommitted work
    diff: str             # the raw changes
    files: dict[str, str] # full contents of every file the change touched
    review: Review        # what the reviewer concluded


def collect(state: ReviewState) -> ReviewState:
    """Find out what changed and read the files it touched."""
    repo = state["repo"]
    diff = changes.get_diff(repo, state.get("base"))
    paths = changes.changed_files(diff)
    return {"diff": diff, "files": changes.read_files(repo, paths)}


def review(state: ReviewState) -> ReviewState:
    """Ask the model what is wrong with the change."""
    return {"review": reviewer.review_changes(state["diff"], state.get("files", {}))}


def build_graph():
    """Put the steps in order and hand back something that can be run."""
    graph = StateGraph(ReviewState)

    graph.add_node("collect", collect)
    graph.add_node("review", review)

    graph.add_edge(START, "collect")
    graph.add_edge("collect", "review")
    graph.add_edge("review", END)

    return graph.compile()
