"""Step three of the review: turn the findings into something a human wants to read.

A review that is hard to scan does not get read, so the serious things go at the
top, the small things go at the bottom, and the verdict is impossible to miss.
"""

from rich.console import Console, Group
from rich.panel import Panel
from rich.text import Text

from .findings import Finding, Review, Severity, Verdict

# Most serious first. This is the order findings are printed in.
_SEVERITY_ORDER = [Severity.BLOCKER, Severity.MAJOR, Severity.MINOR, Severity.NIT]

_SEVERITY_STYLE = {
    Severity.BLOCKER: "bold red",
    Severity.MAJOR: "bold yellow",
    Severity.MINOR: "cyan",
    Severity.NIT: "dim",
}

_SEVERITY_HEADING = {
    Severity.BLOCKER: "Must fix before this goes anywhere",
    Severity.MAJOR: "Real problems",
    Severity.MINOR: "Worth improving",
    Severity.NIT: "Very small things",
}

_VERDICT_STYLE = {
    Verdict.APPROVE: "bold green",
    Verdict.COMMENT: "bold yellow",
    Verdict.REQUEST_CHANGES: "bold red",
}

_VERDICT_WORDS = {
    Verdict.APPROVE: "Looks good",
    Verdict.COMMENT: "Some remarks, your call",
    Verdict.REQUEST_CHANGES: "Needs changes first",
}


def _format_finding(finding: Finding) -> Text:
    """Lay out a single finding as a few lines of text."""
    where = finding.file if finding.line is None else f"{finding.file}:{finding.line}"
    style = _SEVERITY_STYLE[finding.severity]

    text = Text()
    text.append(f"{finding.title}\n", style=style)
    text.append(f"  {where}", style="dim")
    text.append(f"  ·  {finding.category.value}", style="dim")
    text.append(f"  ·  confidence {finding.confidence:.0%}\n", style="dim")
    text.append(f"  {finding.explanation}\n")
    if finding.suggestion:
        text.append("  Suggested: ", style="green")
        text.append(f"{finding.suggestion}\n")
    return text


def render(review: Review, console: Console | None = None) -> None:
    """Print a whole review to the terminal."""
    console = console or Console()

    console.print()
    console.print(Panel(review.summary, title="Summary", border_style="dim"))

    if not review.findings:
        console.print()
        console.print("Nothing worth reporting.", style="green")
    else:
        for severity in _SEVERITY_ORDER:
            group = [f for f in review.findings if f.severity == severity]
            if not group:
                continue
            console.print()
            console.print(
                f"{_SEVERITY_HEADING[severity]}  ({len(group)})",
                style=_SEVERITY_STYLE[severity],
            )
            console.print()
            console.print(Group(*[_format_finding(f) for f in group]))

    console.print()
    console.print(
        Panel(
            _VERDICT_WORDS[review.verdict],
            title="Verdict",
            border_style=_VERDICT_STYLE[review.verdict],
        )
    )
    console.print()
