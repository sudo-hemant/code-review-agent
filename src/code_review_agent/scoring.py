"""Deciding whether the reviewer found the problem you planted.

The reviewer will never word a finding the way you did, so we cannot compare
the text. Instead a finding counts as a match when it points at the same place
and calls it the same kind of problem.

This rule is deliberately simple and it will occasionally judge wrongly. That
is acceptable, because what you care about is whether the numbers move in the
right direction over time, not whether any single case was graded perfectly.
"""

from dataclasses import dataclass

from .cases import Problem
from .findings import Finding

# How far from the stated line a finding may point and still count. The model
# often names the function's line rather than the exact one, so a little room
# is fair.
LINE_TOLERANCE = 3


def matches(finding: Finding, problem: Problem) -> bool:
    """Is this finding talking about this problem?"""
    if finding.file != problem.file:
        return False
    if finding.category.value not in problem.categories:
        return False
    if finding.line is None:
        # No line given. Same file and same kind of problem is enough.
        return True
    return abs(finding.line - problem.line) <= LINE_TOLERANCE


@dataclass
class Score:
    """How one case went."""

    case: str
    caught: list[Problem]    # planted problems the reviewer found
    missed: list[Problem]    # planted problems it walked past
    invented: list[Finding]  # things it reported that were not planted

    @property
    def total_problems(self) -> int:
        return len(self.caught) + len(self.missed)


def score_case(case_name: str, problems: list[Problem], findings: list[Finding]) -> Score:
    """Compare what the reviewer said against what we planted.

    Each finding can only account for one problem, so reporting the same issue
    five times does not earn five points.
    """
    unclaimed = list(problems)
    caught: list[Problem] = []
    invented: list[Finding] = []

    for finding in findings:
        hit = next((p for p in unclaimed if matches(finding, p)), None)
        if hit is None:
            invented.append(finding)
        else:
            unclaimed.remove(hit)
            caught.append(hit)

    return Score(case=case_name, caught=caught, missed=unclaimed, invented=invented)
