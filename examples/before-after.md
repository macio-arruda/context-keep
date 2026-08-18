# Example: one file, split by lifecycle

## Before: one file carrying three lifecycles

A single `CLAUDE.md` that mixes what is true now, why it was decided, and what changed. Every call reads all of it.

```markdown
# Project

## Status
- Migration to the new API is in progress. Auth is done, billing is next.
- Blocked on the vendor sandbox key.

## Why we moved off the old API
We hit rate limits we could not raise, and the old client dropped webhooks
under load. We evaluated three options and chose the new API because it
supports server-side retries. Ruled out building our own proxy: too much to
maintain. (long paragraph continues...)

## Changelog
- 2026-05-02 migrated auth to the new API
- 2026-04-28 added the feature flag
- 2026-04-19 spike on the new client
- ... (fifty more lines, growing every commit)
```

The status is five lines and the file is hundreds, because the reasoning and the history live in the hot path.

## After: three files, one lifecycle each

**`context/STATE.md`** (hot, read every session, capped):

```markdown
# State

## Now
- [ ] Migration to the new API -> billing next (auth done)

## Blocked
- [ ] Migration -> waiting on the vendor sandbox key
```

**`DECISIONS.md`** (cold, read on demand):

```markdown
## 2026-04-19 Move off the old API

- **Decision:** adopt the new API.
- **Why:** unraisable rate limits and dropped webhooks under load. The new API
  does server-side retries. Ruled out a self-built proxy (maintenance cost).
- **Refs:** spike notes, vendor docs.
```

**`CHANGELOG.md`** (trail, append-only, terse, rolls to an archive at the cap):

```markdown
## 2026-05
- Changed: auth migrated to the new API -> `context/STATE.md`
- Added: feature flag for the migration
```

The state file is what loads every session, and it is tiny. The reasoning is one link away when you need it. The history stops weighing down every call and rolls to an archive when it grows.
