"""The scoreboard: run the reviewer over every case and report how it did.

Two numbers matter. How many of the planted problems it caught, and how many
things it reported that were not planted at all. Everything else on the screen
is there to help you work out why.
"""

from rich.console import Console
from rich.table import Table

from .scoring import Score


def summarise(scores: list[Score]) -> dict[str, float]:
    """Boil the whole run down to the numbers you compare between runs."""
    planted = sum(score.total_problems for score in scores)
    caught = sum(len(score.caught) for score in scores)
    invented = sum(len(score.invented) for score in scores)

    return {
        "cases": len(scores),
        "planted": planted,
        "caught": caught,
        "missed": planted - caught,
        "invented": invented,
        # Of the problems we planted, what share did it find?
        "catch_rate": (caught / planted) if planted else 0.0,
        # Of everything it said, what share was real?
        "precision": (caught / (caught + invented)) if (caught + invented) else 0.0,
    }


def render(scores: list[Score], console: Console | None = None) -> None:
    """Print the per-case table and the two headline numbers."""
    console = console or Console()

    table = Table(title="Per case")
    table.add_column("Case")
    table.add_column("Caught", justify="right")
    table.add_column("Missed", justify="right", style="yellow")
    table.add_column("Invented", justify="right", style="red")

    for score in scores:
        table.add_row(
            score.case,
            f"{len(score.caught)}/{score.total_problems}",
            str(len(score.missed)) if score.missed else "-",
            str(len(score.invented)) if score.invented else "-",
        )

    console.print()
    console.print(table)

    totals = summarise(scores)
    console.print()
    console.print(
        f"Caught [green]{totals['caught']}[/green] of {totals['planted']} planted problems "
        f"([green]{totals['catch_rate']:.0%}[/green])."
    )
    console.print(
        f"Of everything it reported, [green]{totals['precision']:.0%}[/green] was real "
        f"([red]{totals['invented']}[/red] invented)."
    )
    console.print()
