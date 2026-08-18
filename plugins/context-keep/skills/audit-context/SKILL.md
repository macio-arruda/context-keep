---
name: audit-context
description: Use when the user asks to check, clean up, shrink, or review their context files (CLAUDE.md, AGENTS.md, state files, changelogs), or worries that a context file got too big or costly. Reports size, estimated token cost per read, and whether a file mixes lifecycles (state, rationale, trail), then recommends what to split or archive. Also use when a repo feels slow or expensive per session and the cause may be a bloated context file.
---

# Audit context

Context files enter the model's context on every call. When they grow, you pay twice: tokens for stale content on every read, and worse attention to the middle of a long context, the effect the literature calls "lost in the middle". This skill measures both and finds files that pack more than one lifecycle into one place.

This skill is self-contained. The standalone script, templates and full method live at <https://github.com/macio-arruda/context-keep>.

## When this applies

- The user asks to shrink, clean up, or review a `CLAUDE.md`, `AGENTS.md`, or a state/changelog file.
- A session feels expensive or slow and a bloated context file may be the cause.
- The user wants to know the token cost of the files loaded on every call.

Not for auditing arbitrary source code. This is about the files that feed the model on every call.

## How to run it

If the repo has the script, run it and read the report to the user:

```bash
python3 scripts/context_audit.py . --reads 100
```

Pass `--price-in` with the input price of the model actually in use (for example `--price-in 5` for a $5 / 1M input model), and `--reads` with a realistic number of sessions or commits so the projected cost is concrete. Use `--strict` in CI to fail when a file passes the hard cap.

If the script is not present, do the same by hand: for each context file report its size in KB, an estimated token count (bytes divided by about 4, and say it is an estimate), the cost per read at the model's input price, and which lifecycles it contains.

## The three lifecycles

A context file should hold one of these, not several. Their read and write rhythms are opposite, so mixing them forces the always-loaded file to carry weight it does not need.

| Layer | What it holds | Read rhythm |
|---|---|---|
| **State** | what is true now, the open items | every session |
| **Rationale** | why decisions were made | on demand |
| **Trail** | what changed and when | almost never |

When one file holds two or more of these, flag it. The fix is to split by lifecycle and keep only the state in the hot path.

## What to tell the user

1. The heaviest files, with size and estimated cost per read and over N reads.
2. Which files mix lifecycles, and which layers were detected.
3. A concrete recommendation: split file X into state, rationale and trail; archive the cold part of file Y; set a cap so it does not grow back.

## Hard rules

- **Token counts are estimates.** Say so. For exact numbers, point to the model's tokenizer or count_tokens endpoint.
- **Do not delete anything on your own.** Recommend the split or archive; let the user run it, or confirm first.
- **Cost is illustrative.** It depends on the model price passed in and on how often the file is actually read.

To stop the bloat from coming back after cleaning, hand off to the guard-context skill.
