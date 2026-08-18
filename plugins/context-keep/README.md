# Context Keep (plugin)

Keep your context files lean, and stop them from growing back.

This plugin ships two model-invoked skills:

- **audit-context** triggers when you ask to check, clean up, or shrink your context files. It runs `context_audit.py`, reports size, estimated tokens and cost per read, and flags files that pack more than one lifecycle (state, rationale, trail) into one file.
- **guard-context** triggers when you ask to stop the bloat from coming back. It installs the pre-commit size cap and scaffolds the three-layer convention.

Full method, templates and the standalone script live at <https://github.com/macio-arruda/context-keep>.

Install on Claude Code:

```
/plugin marketplace add macio-arruda/context-keep
/plugin install context-keep@context-engineering
```

The scripts and templates work anywhere, with or without the plugin.
