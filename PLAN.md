# Code review agent: the plan

A program that reads the code you have changed and tells you what is wrong with it.
Built in phases, where every phase ends with something that actually runs.

## The decisions this is built on

- **One reviewer to begin with, not several.** Splitting it up comes later, once
  there are numbers showing it is needed.
- **It sees the change plus the full contents of every file the change touched.**
  A handful of changed lines almost never make sense on their own.
- **Findings come back in a fixed shape, never as free writing.** Each one carries a
  file, a line, a category, a seriousness level, a confidence level, an explanation
  and a suggested fix. This is what makes everything later possible.
- **Finding nothing is a correct answer.** The reviewer is told this explicitly,
  because otherwise it invents problems to seem useful.
- **It judges on general programming knowledge for now**, with a slot ready for the
  project's own written rules later.
- **It runs as a terminal command**, and only a terminal command, until phase six.
- **Python only** at first.

## Phase one: a reviewer that works, start to finish  (a day)

A command you type inside any project that prints a review of what you changed.
Four pieces, in this order:

1. Get hold of the changes, by running git from inside the program.
2. Read the full contents of every file that changed.
3. Send the change, the files and the instructions to Claude, and require the
   answer back in the fixed shape.
4. Print it so a person wants to read it, serious things first, verdict at the end.

Status: pieces 1, 2 and 4 are built. Piece 3 is a placeholder in `reviewer.py`.

## Phase two: a way to tell whether it is any good  (half a day)

Fifteen to twenty small example changes where you already know what is wrong with
each one, including a few that are completely fine. A command that runs the reviewer
over all of them and reports two numbers: how many real problems it caught, and how
many things it reported that were not real.

This comes second, not last, because from here on every change is a guess without it.

## Phase three: teaching it your standards  (2-3 hours)

A rules file the reviewer reads if the project has one, so it judges against real
team standards instead of generic ones. Plus running the ordinary Python checking
tools first and handing their results over as evidence, so the model spends its
attention on logic rather than re-finding things a plain tool finds more reliably.

## Phases four and five: whichever the scoreboard says  (2-3 hours each)

- **Missing real problems?** Split the one reviewer into four narrower ones running
  at the same time, then merge and de-duplicate their findings.
- **Inventing problems that are not real?** Add a checking step that looks at each
  finding on its own and throws away anything the evidence does not support.

Let the numbers from phase two choose the order.

## Phase six: running on GitHub  (3-4 hours)

Runs by itself when someone proposes a change, and posts what it found. One whole
comment first; comments attached to exact lines once that works.

## Phase seven: the plug for other assistants  (an afternoon)

Wrap it so Claude Code, Cursor and others can call it directly. Not a rebuild, just
describing what the existing program can do in a standard form.

## Phase eight: optional

Letting it look up extra context on demand, proposing fixes as patches and checking
they apply, learning from which findings people accepted, other languages, a web page.
Pick by interest. The project is complete without any of it.
