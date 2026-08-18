# The method

## The problem

A context file is any file the model reads on every call: `CLAUDE.md`, `AGENTS.md`, a state file, a changelog you keep in the repo. It starts small and useful. Months later it is large, and most of it is stale.

That costs you twice.

First, tokens. The whole file enters the context on every call, so you pay input tokens for old content on every read. A changelog that grew to 140 KB is roughly 35,000 tokens reread on every commit, which at a $5 / 1M input price is about 17 cents per commit to reread something nobody reads.

Second, attention. As the context grows, the model uses the middle of it worse. The study that named this ("Lost in the Middle", Liu et al., 2023) found accuracy highest at the start and end of a long context and lowest in the middle. Chroma's later measurement ("context rot") showed quality degrading as input length grows across current models. A bloated context file is long context, so it degrades the answer while it raises the bill.

## Why files rot

In systems you do not keep cold data in the hot path. RAM holds the working set; the archive lives on disk. Context files break that rule. They hold three things with opposite rhythms in one place:

| Layer | What it holds | Read rhythm | Write rhythm |
|---|---|---|---|
| **State** | what is true now, the open items | every session | often |
| **Rationale** | why decisions were made | on demand | rarely |
| **Trail** | what changed and when | almost never | every change |

The state is small and hot. The trail is append-only and grows without bound. The rationale is the reference you open when you need the "why". Put them in one file and the file you load on every call carries the weight of all three. The trail alone guarantees it grows forever.

## The fix, in two moves

**Split by lifecycle.** Give each layer its own file. `STATE.md` holds what is true now and stays small. `DECISIONS.md` holds the reasoning, read on demand. `CHANGELOG.md` holds the trail, append-only and terse, rolled to an archive when it passes a cap. The state file points to the other two; it does not repeat them. The reasoning lives once, and everything links to it.

**Guard the size with a mechanism, not a rule.** The rule "keep it lean" is almost always already written, and ignored. A convention decays because nothing enforces it. A pre-commit cap does: it warns near a soft limit and blocks past a hard one. The emergency escape (`--no-verify`) should be rare enough that using it is a signal.

## The workflow

1. **Audit.** Run `context_audit.py` to see size, estimated token cost per read, and which files mix lifecycles. Measure before you cut.
2. **Split.** For each file that mixes layers, move the reasoning to `DECISIONS.md`, the history to `CHANGELOG.md`, and leave only the current state in the hot path.
3. **Guard.** Install the pre-commit cap on the files that load on every call. Roll the trail to an archive when it grows past its cap.

## What good looks like

- The file loaded on every call is small, and stays small because a cap holds it.
- State, rationale and trail each have one home, with the right read rhythm.
- The reasoning for a decision lives once; everything else links to it.
- The trail is terse and rolls to an archive; the hot path never carries the full history.
- Token cost per session is something you have measured, not guessed.

## What this is not

- Not a summarizer or a compaction tool. It does not rewrite your content; it separates it and caps it.
- Not RAG or a vector store. This is the plain-file context you keep by hand.
- Not automatic. The audit is a report and the split is your call. The only thing that runs on its own is the size cap.
