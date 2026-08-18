# Example: an audit report

A fictional repo whose `CLAUDE.md` grew for months. Run the auditor from the repo root:

```bash
python3 scripts/context_audit.py . --price-in 5 --reads 100
```

Output:

```
context_audit  (token counts are estimates; cost at $5.00/1M input)
cap: warn > 25 KB, fail > 40 KB

   58.0 KB  ~ 14848 tok  $ 0.0742/read  CLAUDE.md  <- OVER HARD CAP; mixes 3 lifecycles
            layers: state (hot, read every session) | rationale (cold, read on demand) | trail (append-only, rarely read)
    9.1 KB  ~  2330 tok  $ 0.0116/read  AGENTS.md  <- mixes 2 lifecycles
            layers: state (hot, read every session) | trail (append-only, rarely read)
    2.4 KB  ~   610 tok  $ 0.0030/read  docs/STATE.md

total: 69.5 KB  ~17788 tok
projected over 100 reads: $8.88
```

## How to read it

`CLAUDE.md` is the problem. It loads on every call, it is over the hard cap, and it holds all three lifecycles. The 58 KB is reread every session, so at 100 sessions it is close to seven dollars just for that one file, most of it stale.

`AGENTS.md` mixes state and trail. Smaller, but the trail part will grow forever if nothing stops it.

## The fix

1. Split `CLAUDE.md`. The "why we decided" sections move to `DECISIONS.md`, the changelog section moves to `CHANGELOG.md`, and only the current state stays. The hot file drops from 58 KB to a few KB.
2. Move the trail out of `AGENTS.md` into the changelog.
3. Install the pre-commit cap on `CLAUDE.md`, `AGENTS.md` and `docs/STATE.md` so they cannot grow back.

Re-run the auditor after the split and the hot path should be a fraction of the total, with the cold parts out of every call.

> Numbers here are illustrative. Token counts are estimates and cost depends on the model price you pass in.
