"""Step two of the review: ask the model what is wrong with the change."""

from langchain_core.messages import HumanMessage, SystemMessage

from .findings import Review, Verdict
from .llm import ask, get_model
from .prompt import SYSTEM, USER, build_files_section


def review_changes(diff: str, files: dict[str, str]) -> Review:
    """Look at a change and say what is wrong with it.

    The model is required to answer in the shape of a Review, so every finding
    comes back with a file, a line, a category, a seriousness level and a
    confidence. It cannot reply with loose prose even if it wants to.
    """
    model = get_model().with_structured_output(Review)

    result = ask(
        model,
        [
            SystemMessage(SYSTEM),
            HumanMessage(USER.format(diff=diff, files=build_files_section(files))),
        ],
    )

    # Belt and braces: if the model returns nothing usable, say so plainly
    # rather than pretending the change was fine.
    if not isinstance(result, Review):
        return Review(
            findings=[],
            verdict=Verdict.COMMENT,
            summary="The model did not answer in the expected shape, so there is no review.",
        )

    return result
