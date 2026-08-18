---
name: guard-context
description: Use when the user wants to stop context files from growing back after a cleanup, or asks to enforce a size limit on CLAUDE.md, AGENTS.md, or state files, or to set up the state / rationale / trail layer convention. Installs a pre-commit size cap and scaffolds the three-layer split. Use this after audit-context, or whenever the user says a convention keeps being ignored and they want a mechanical guard.
---

# Guard context

A convention decays. The rule "keep it lean" is almost always already written somewhere, and ignored. What holds is a mechanical check. This skill installs a pre-commit cap that warns near a soft limit and blocks past a hard one, and scaffolds the three-layer split so the always-loaded file stays small.

This skill is self-contained. Templates and the full method live at <https://github.com/macio-arruda/context-keep>.

## When this applies

- After auditing, the user wants the files to stay small.
- A "keep it short" rule keeps being ignored and the user wants teeth.
- The user is setting up a new context repo and wants the guard from the start.

## Install the size cap

1. Copy the `pre-commit` template into the repo's hook path:

```bash
mkdir -p .githooks
cp templates/pre-commit .githooks/pre-commit
chmod +x .githooks/pre-commit
git config core.hooksPath .githooks
```

2. Edit the `GUARDED` block at the top of the hook: one line per file as `path:soft_kb:hard_kb`. Guard the files that load on every call first (`CLAUDE.md`, `AGENTS.md`, the state file).

3. The hook warns near the soft cap and blocks past the hard cap. The emergency escape is `git commit --no-verify`, and it should be rare enough to notice.

Keep the cap in the hook, not only in a written rule. The written rule is what was already ignored.

## Scaffold the three layers

If a file mixes lifecycles, split it so each layer has one home:

- `context/STATE.md`, from `templates/STATE.md`: what is true now, read every session, capped hard.
- `DECISIONS.md`, from `templates/DECISIONS.md`: why decisions were made, read on demand.
- `CHANGELOG.md`, from `templates/CHANGELOG.md`: what changed and when, append-only, terse, rolled to an archive when it passes the cap.

The state file points to the other two. It does not repeat their content. The reasoning lives once, in DECISIONS.md, and everything else links to it.

## Hard rules

- **Guard the hot path first.** The file loaded on every call is where a cap pays off most.
- **Warn then block.** A soft cap gives a heads-up; the hard cap is the wall.
- **Keep the escape hatch.** `--no-verify` exists for emergencies; if it becomes routine, the cap is wrong, not the file.
- **Do not rewrite the user's content.** Scaffold the layers and move content only with the user's confirmation.

To measure where the bloat is before guarding, use the audit-context skill.
