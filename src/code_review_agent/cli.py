"""The terminal command.

    review            reviews whatever you have changed but not yet committed
    review --base main   reviews everything on your branch that is not on main
"""

from pathlib import Path
from typing import Optional

import typer
from dotenv import load_dotenv
from rich.console import Console

from . import report
from .changes import NotAGitRepository
from .graph import build_graph
from .llm import MissingApiKey, ModelBusy

app = typer.Typer(add_completion=False, help="Review your code changes.")
console = Console()


@app.command()
def main(
    path: Path = typer.Argument(
        Path("."), help="The project to review. Defaults to the folder you are in."
    ),
    base: Optional[str] = typer.Option(
        None,
        "--base",
        "-b",
        help="Compare against this branch instead of reviewing uncommitted work.",
    ),
) -> None:
    load_dotenv()

    repo = path.resolve()
    graph = build_graph()

    try:
        with console.status("Reviewing your changes..."):
            state = graph.invoke({"repo": repo, "base": base})
    except NotAGitRepository:
        console.print(f"{repo} is not a git repository.", style="red")
        raise typer.Exit(code=1)
    except (MissingApiKey, ModelBusy) as error:
        console.print(str(error), style="red")
        raise typer.Exit(code=1)
    except RuntimeError as error:
        console.print(str(error), style="red")
        raise typer.Exit(code=1)

    if not state.get("diff", "").strip():
        console.print("No changes to review.", style="dim")
        raise typer.Exit(code=0)

    report.render(state["review"], console)
