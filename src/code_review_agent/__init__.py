from .cli import app
from .score_cli import app as score_app


def main() -> None:
    app()


def score() -> None:
    score_app()
