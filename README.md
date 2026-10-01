# Code review agent

Reads the code you have changed and tells you what is wrong with it.

Built on LangGraph, with the model behind a single setting so it runs against
Gemini, a model on your own machine, or a paid one, without touching the code.

```
$ review
╭───────────────────────────── Summary ──────────────────────────────╮
│ Adds a spend total. One hardcoded secret and an SQL injection need │
│ fixing first.                                                      │
╰────────────────────────────────────────────────────────────────────╯

Must fix before this goes anywhere  (2)

Hardcoded live API secret key
  account.py:3  ·  security  ·  confidence 100%
  A live API key is committed to the repository.
  Suggested: load it from an environment variable.
```

## Why it is built this way

Finding problems in code is the easy half. The hard half is not saying things
that are wrong. A study of an agentic reviewer on real projects found **58% of
its comments were rejected as invalid**, mostly false positives. So this project
is organised around measuring that rather than around adding reviewers.

Three decisions follow from it:

- **Findings have a fixed shape, never free prose.** Each one carries a file, a
  line, a category, a severity and a confidence. That is what makes them
  sortable, filterable, de-duplicable, and attachable to an exact line.
- **Saying nothing is a correct answer.** The instructions say so explicitly,
  because a model asked to review will otherwise invent something to seem useful.
- **There is a scoreboard before there are features.** A set of changes with
  known problems, including some with nothing wrong, and two numbers that move
  when you change something.

## Using it

Needs Python 3.12 and [uv](https://docs.astral.sh/uv/).

```bash
uv sync
cp .env.example .env     # then put a Gemini API key in it
```

Review what you have changed but not committed:

```bash
uv run review
uv run review ../some-other-project
uv run review --base main      # everything on this branch that is not on main
```

Score the reviewer against the known cases:

```bash
uv run review-score
uv run review-score --limit 6          # a free tier has a small daily budget
uv run review-score --only security
```

### Choosing a model

Set `REVIEW_MODEL` in `.env`:

| Value | |
|---|---|
| `google_genai:gemini-3.8-flash` | free tier, the default |
| `google_genai:gemini-3.1-flash-lite` | free tier, more generous daily budget |
| `ollama:qwen2.5-coder:3b` | runs on your own machine, nothing leaves it |
| `anthropic:claude-opus-5` | paid, for when quality matters |

Rate limits and overloaded servers are waited out, honouring the delay the
service asks for. A wrong key or a model name that does not exist fails straight
away rather than retrying pointlessly.

## How it fits together

```
changes.py    run git, read the files the change touched
prompt.py     the instructions the reviewer is given
reviewer.py   send them, require the answer in the fixed shape
report.py     print it, serious things first
graph.py      the steps, in order
llm.py        which model, and coping when it says no
```

And the scoreboard:

```
cases/        each case is before/, after/, and what is deliberately wrong
cases.py      turn a case folder into a diff plus file contents
scoring.py    decide whether a finding matches a planted problem
scoreboard.py the table and the two numbers
```

A finding counts as a catch when it names the same file, an accepted category,
and a line within three of the planted one. Anything matching nothing counts as
invented.

## Where it is up to

Phases one and two are done: a working reviewer, and a scoreboard to judge it by.

Baseline on 10 of the 17 cases: **6 of 6 planted problems caught, 1 invention
across 4 clean changes.** The invention is instructive. It claimed with 100%
confidence that a correct truncation function could exceed its limit, and its
reasoning contradicted itself. Confidence is therefore not yet a usable signal,
which is an argument for building the verification step before splitting the
reviewer into several.

Next: a project rules file and deterministic tools feeding in as evidence, then
whichever of those two the numbers say is hurting more.

See [PLAN.md](PLAN.md) for the full phasing.
