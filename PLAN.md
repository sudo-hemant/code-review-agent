# LangGraph Code Review Agent — Phased Build Plan

## Environment note
System Python is 3.9.6. LangGraph 1.1+ dropped 3.9. Use Python 3.11+:
  brew install python@3.11 && python3.11 -m venv .venv && source .venv/bin/activate
  pip install langgraph langchain-anthropic pydantic python-dotenv typer

---

## Core architecture (target shape)

    ingest_diff -> chunk_by_file -> orchestrator(route)
                                        |
                        +---------------+---------------+--------+
                        v               v               v        v
                      bugs           security        quality    tests   (parallel fan-out)
                        +---------------+---------------+--------+
                                        v
                                  verifier (grounding / false-positive filter)
                                        v
                                    summarizer -> report / post to PR

State (single TypedDict threaded through every node):
    diff: str
    files: list[FileChunk]
    route: list[str]                 # which specialists to run
    findings: Annotated[list[Finding], operator.add]   # reducer = parallel-safe append
    verified: list[Finding]
    report: str
    verdict: Literal["APPROVE","COMMENT","REQUEST_CHANGES"]

Finding schema (pydantic, structured output — not free text):
    file, line, severity(critical|major|minor|nit), category, title,
    rationale, suggested_fix, confidence

---

## Phase 1 — Day 1 MVP (4–6h): single-agent CLI reviewer
Goal: `review .` prints a structured review of `git diff`.
- `git diff` / `git diff main...HEAD` ingestion
- chunker: split on `diff --git`, cap total chars, keep hunk headers + line numbers
- linear graph: ingest -> review -> format  (3 nodes, no fan-out yet)
- LLM node with `with_structured_output(ReviewOutput)` -> list[Finding]
- markdown report grouped by severity + verdict
Deliverable: working CLI, README with a demo diff. CV-worthy already.

## Phase 2 (2–3h): multi-agent fan-out
- Split the one reviewer into 4 specialists (bugs / security / quality / tests)
- `Send` API or conditional edges for parallel fan-out; `operator.add` reducer on findings
- Orchestrator node picks specialists by file type (CSS-only diff -> skip security)
- Summarizer node dedupes + resolves severity conflicts (escalate to higher)
Talking point: fan-out/fan-in, map-reduce over chunks, cost control via routing.

## Phase 3 (2–3h): quality — the part that actually matters
- Verifier node: re-checks each finding against the real file content; drops anything
  unfalsifiable. (58% of agentic review comments are rejected as false positives —
  this node is the differentiator.)
- Confidence threshold + "no comment is a valid answer" path
- Repo conventions file (`REVIEW.md` / CLAUDE.md) injected into prompts
- Deterministic pre-pass: ruff / bandit / mypy output fed in as evidence, so the LLM
  reasons instead of re-detecting lint

## Phase 4 (3–4h): context retrieval
- Tool node: read_file, grep, find_definition (tree-sitter or ctags)
- ReAct sub-loop so an agent can pull the surrounding function/callers before judging
- Optional: embed repo -> retrieve top-k related chunks. Selective > dumping everything
  (context dilution hurts accuracy)

## Phase 5 (3–4h): GitHub integration
- `gh` CLI or PyGithub: fetch PR diff, post inline review comments at file:line
- FastAPI webhook endpoint on `pull_request` events + GitHub App auth
- Or simpler: GitHub Action that runs the CLI on PRs and comments

## Phase 6 (2–3h): production polish
- Checkpointer (SqliteSaver) -> resumable runs, time-travel debugging
- `interrupt()` human-in-the-loop before posting REQUEST_CHANGES
- Streaming progress, token/cost tracking, LangSmith tracing
- Eval harness: 15–20 diffs with known bugs -> precision/recall per phase.
  A before/after precision number is the single strongest CV line.

## Phase 7 (optional stretch)
- Auto-fix patch generation + `git apply` validation / run tests on the patch
- Learning loop: store which findings humans accepted, feed back as few-shot examples
- Multi-language via tree-sitter grammars
- Web UI (Streamlit) showing the graph executing live

---

## Features menu (pick per phase)
Reviewer dimensions: logic bugs, security (injection/secrets/authz), performance
(N+1, unbounded loops), style/conventions, test coverage gaps, docs/API-contract
breaks, dependency & license checks, migration/DB-safety.
Behaviours: severity tiering, dedupe, inline vs summary comments, diff-size guards,
skip-list globs, cost budget per PR, incremental review of new commits only.

## CV framing
"Built a multi-agent code review system (LangGraph, Claude) using fan-out/fan-in
orchestration over per-file diff chunks with a grounding-verification stage that cut
false positives from X% to Y%, deployed as a GitHub App with human-in-the-loop gating."
