"""The `review-score` command.

Runs the reviewer over every case in cases/ and prints how it did. This is the
thing you run before and after changing anything, so you find out whether the
change helped instead of guessing.
"""

from pathlib import Path

import typer
from dotenv import load_dotenv
from rich.console import Console

from . import scoreboard
from .cases import load_cases
from .llm import MissingApiKey, ModelUnavailable
from .reviewer import review_changes
from .scoring import Score, score_case

app = typer.Typer(add_completion=False, help="Score the reviewer against the known cases.")
console = Console()


@app.command()
def main(
    cases_dir: Path = typer.Argument(Path("cases"), help="Folder holding the test cases."),
    limit: int = typer.Option(
        0, "--limit", "-n", help="Only run this many cases. Useful on a small free quota."
    ),
    only: str = typer.Option(
        "", "--only", help="Only run cases whose name contains this text."
    ),
) -> None:
    load_dotenv()

    cases = load_cases(cases_dir.resolve())
    if only:
        cases = [case for case in cases if only in case.name]
    if limit:
        cases = cases[:limit]

    if not cases:
        console.print(f"No cases found in {cases_dir}.", style="red")
        raise typer.Exit(code=1)

    scores: list[Score] = []
    stopped_early: str | None = None

    for number, case in enumerate(cases, start=1):
        try:
            with console.status(f"[{number}/{len(cases)}] {case.name}"):
                review = review_changes(case.diff, case.files)
        except (MissingApiKey, ModelUnavailable) as error:
            # Running out of free quota part way through should not throw away
            # the cases that did run. Report what we have and say so.
            stopped_early = str(error)
            break
        scores.append(score_case(case.name, case.problems, review.findings))

    if not scores:
        console.print(stopped_early or "No cases could be run.", style="red")
        raise typer.Exit(code=1)

    scoreboard.render(scores, console)

    if stopped_early:
        console.print(
            f"Stopped after {len(scores)} of {len(cases)} cases. {stopped_early}",
            style="yellow",
        )
        console.print()
        raise typer.Exit(code=1)
