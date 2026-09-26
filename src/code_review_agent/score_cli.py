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
from .llm import MissingApiKey, ModelBusy
from .reviewer import review_changes
from .scoring import Score, score_case

app = typer.Typer(add_completion=False, help="Score the reviewer against the known cases.")
console = Console()


@app.command()
def main(
    cases_dir: Path = typer.Argument(Path("cases"), help="Folder holding the test cases."),
) -> None:
    load_dotenv()

    cases = load_cases(cases_dir.resolve())
    if not cases:
        console.print(f"No cases found in {cases_dir}.", style="red")
        raise typer.Exit(code=1)

    scores: list[Score] = []
    try:
        for number, case in enumerate(cases, start=1):
            with console.status(f"[{number}/{len(cases)}] {case.name}"):
                review = review_changes(case.diff, case.files)
            scores.append(score_case(case.name, case.problems, review.findings))
    except (MissingApiKey, ModelBusy) as error:
        console.print(str(error), style="red")
        raise typer.Exit(code=1)

    scoreboard.render(scores, console)
