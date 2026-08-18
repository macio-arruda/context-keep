#!/usr/bin/env python3
"""context_audit: report bloat, token cost, and lifecycle mixing in context files.

Context files (CLAUDE.md, AGENTS.md, state files, changelogs) enter the model's
context on every call. When they grow you pay twice: tokens for stale content on
every read, and worse attention to the middle of a long context (the effect the
literature calls "lost in the middle"). This tool measures both and flags files
that pack more than one lifecycle into a single file.

Token counts are ESTIMATES (bytes divided by chars-per-token). For exact counts,
use your model's tokenizer or count_tokens endpoint. Cost is estimated at the
input price you pass in.

Usage:
    python3 context_audit.py [PATH ...] [options]

Examples:
    python3 context_audit.py .                 # audit CLAUDE.md / AGENTS.md under .
    python3 context_audit.py CLAUDE.md docs/STATE.md
    python3 context_audit.py . --cap-kb 25 --hard-kb 40 --price-in 5 --reads 100
    python3 context_audit.py . --strict        # exit 1 if any file passes the hard cap
"""
from __future__ import annotations

import argparse
import os
import re
import sys

DISCOVER = ("CLAUDE.md", "AGENTS.md", "GEMINI.md")

# Lifecycle markers. A context file should hold one of these, not several.
# Keyword hits are heuristic (EN + PT); they flag mixing, they do not prove it.
LAYERS = {
    "state (hot, read every session)": [
        r"\bstatus\b", r"\bcurrent\b", r"\bto ?do\b", r"\bbacklog\b",
        r"\bin progress\b", r"\bnow\b", r"\bpend[êe]ncias?\b", r"\baberto\b",
    ],
    "rationale (cold, read on demand)": [
        r"\bdecision\b", r"\brationale\b", r"\badr\b", r"\bwhy\b",
        r"\btrade-?off\b", r"\bdecis[ãa]o\b", r"\bracional\b",
    ],
    "trail (append-only, rarely read)": [
        r"\bchangelog\b", r"\bhistory\b", r"\bchange ?log\b", r"\brelease notes\b",
        r"\bhist[óo]rico\b", r"\baudit\b",
    ],
}


def find_targets(paths):
    targets = []
    for p in paths:
        if os.path.isdir(p):
            for root, _dirs, files in os.walk(p):
                if ".git" in root.split(os.sep):
                    continue
                for name in files:
                    if name in DISCOVER:
                        targets.append(os.path.join(root, name))
        elif os.path.isfile(p):
            targets.append(p)
        else:
            print("skip (not found): {}".format(p), file=sys.stderr)
    # de-dup, stable order
    seen = set()
    out = []
    for t in targets:
        rp = os.path.relpath(t)
        if rp not in seen:
            seen.add(rp)
            out.append(rp)
    return out


def detect_layers(text):
    low = text.lower()
    present = []
    for layer, patterns in LAYERS.items():
        hits = sum(1 for pat in patterns if re.search(pat, low))
        if hits >= 2:
            present.append(layer)
    return present


def audit_file(path, chars_per_token, price_in, reads):
    with open(path, "rb") as fh:
        raw = fh.read()
    size = len(raw)
    text = raw.decode("utf-8", errors="replace")
    tokens = int(round(len(text) / chars_per_token))
    cost_read = tokens * price_in / 1_000_000
    return {
        "path": path,
        "kb": size / 1024,
        "tokens": tokens,
        "cost_read": cost_read,
        "cost_reads": cost_read * reads,
        "layers": detect_layers(text),
    }


def main(argv):
    ap = argparse.ArgumentParser(description="Audit context files for bloat, cost, and lifecycle mixing.")
    ap.add_argument("paths", nargs="*", default=["."], help="files or directories (default: .)")
    ap.add_argument("--cap-kb", type=float, default=25.0, help="soft cap in KB (warn), default 25")
    ap.add_argument("--hard-kb", type=float, default=40.0, help="hard cap in KB (fail with --strict), default 40")
    ap.add_argument("--chars-per-token", type=float, default=4.0, help="estimate divisor, default 4.0")
    ap.add_argument("--price-in", type=float, default=5.0, help="input price USD per 1M tokens, default 5.0")
    ap.add_argument("--reads", type=int, default=1, help="project cumulative cost over N reads, default 1")
    ap.add_argument("--strict", action="store_true", help="exit 1 if any file passes the hard cap")
    args = ap.parse_args(argv)

    paths = args.paths or ["."]
    targets = find_targets(paths)
    if not targets:
        print("No context files found. Pass files explicitly, or check the path.", file=sys.stderr)
        return 0

    rows = [audit_file(t, args.chars_per_token, args.price_in, args.reads) for t in targets]

    print("context_audit  (token counts are estimates; cost at ${:.2f}/1M input)".format(args.price_in))
    print("cap: warn > {:.0f} KB, fail > {:.0f} KB\n".format(args.cap_kb, args.hard_kb))

    over_hard = 0
    for r in sorted(rows, key=lambda x: x["kb"], reverse=True):
        flags = []
        if r["kb"] > args.hard_kb:
            flags.append("OVER HARD CAP")
            over_hard += 1
        elif r["kb"] > args.cap_kb:
            flags.append("over soft cap")
        if len(r["layers"]) >= 2:
            flags.append("mixes {} lifecycles".format(len(r["layers"])))
        flag_str = "  <- " + "; ".join(flags) if flags else ""
        print("{:>7.1f} KB  ~{:>6} tok  ${:>7.4f}/read  {}{}".format(
            r["kb"], r["tokens"], r["cost_read"], r["path"], flag_str))
        if len(r["layers"]) >= 2:
            print("            layers: {}".format(" | ".join(r["layers"])))

    total_kb = sum(r["kb"] for r in rows)
    total_tokens = sum(r["tokens"] for r in rows)
    total_reads_cost = sum(r["cost_reads"] for r in rows)
    print("\ntotal: {:.1f} KB  ~{} tok".format(total_kb, total_tokens))
    if args.reads != 1:
        print("projected over {} reads: ${:.2f}".format(args.reads, total_reads_cost))

    if args.strict and over_hard:
        print("\n{} file(s) over the hard cap. Split by lifecycle or archive the cold parts.".format(over_hard), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
