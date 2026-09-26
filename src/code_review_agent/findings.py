"""What a single review comment looks like.

Everything the reviewer produces has to fit this shape. That is deliberate.
Free-flowing text can only be printed; a list of items with named parts can be
sorted, filtered, counted and attached to an exact line of a file.
"""

from enum import Enum

from pydantic import BaseModel, Field


class Severity(str, Enum):
    """How much this finding should worry the person reading it."""

    BLOCKER = "blocker"   # this will break. Fix before the change goes anywhere.
    MAJOR = "major"       # a real problem, but the world will not end today.
    MINOR = "minor"       # worth improving, take it or leave it.
    NIT = "nit"           # very small. Safe to ignore entirely.


class Category(str, Enum):
    """Which kind of problem this is."""

    CORRECTNESS = "correctness"          # the code does not do what it clearly means to
    SECURITY = "security"                # the code opens a door that should be shut
    PERFORMANCE = "performance"          # it will be slow in a way that matters
    MAINTAINABILITY = "maintainability"  # it works, but the next person will suffer
    TESTING = "testing"                  # something new arrived and nothing checks it
    STYLE = "style"                      # naming, layout, small tidiness


class Finding(BaseModel):
    """One thing the reviewer wants to say."""

    file: str = Field(description="Path of the file this is about, as it appears in the change.")
    line: int | None = Field(
        default=None,
        description="Line number in the new version of the file, if it can be pinned down.",
    )
    category: Category
    severity: Severity
    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description=(
            "How sure the reviewer is that this is a real problem, from 0 to 1. "
            "Low confidence means the surrounding code was not visible enough to be sure."
        ),
    )
    title: str = Field(description="One short line naming the problem.")
    explanation: str = Field(description="Why this is a problem, in plain language.")
    suggestion: str | None = Field(
        default=None, description="What to do instead. Left empty when there is no clear fix."
    )


class Verdict(str, Enum):
    """The one-line answer at the bottom of the review."""

    APPROVE = "approve"                  # nothing worth holding this up
    COMMENT = "comment"                  # some remarks, but the author can decide
    REQUEST_CHANGES = "request_changes"  # something here needs fixing first


class Review(BaseModel):
    """Everything the reviewer produced for one set of changes."""

    findings: list[Finding] = Field(
        default_factory=list,
        description=(
            "Every problem found. An empty list is a valid and welcome answer: "
            "reporting nothing is better than padding the list."
        ),
    )
    verdict: Verdict
    summary: str = Field(description="Two or three sentences on the change as a whole.")
