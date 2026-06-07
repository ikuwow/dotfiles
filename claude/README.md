# Claude Code configuration

This directory holds everything that ends up under `~/.claude/`, but the
mapping is per-file. `scripts/deploy.sh` symlinks each entry below
individually, not the directory as a whole — so dropping a new file in
here only takes effect after a corresponding line is added to
`deploy.sh`.

## Layout

| Source                        | Symlinks to                       | Purpose                                                                                                       |
| ----------------------------- | --------------------------------- | ------------------------------------------------------------------------------------------------------------- |
| `.mcp.json`                   | `~/.claude/.mcp.json`             | MCP server registry. Edit through `scripts/claude-code-setup.sh`, not by hand.                                |
| `settings.json`               | `~/.claude/settings.json`         | Permissions (`allow` / `ask` / `deny`), hooks, env. Schema: <https://json.schemastore.org/claude-code-settings.json>. |
| `statusline-command.sh`       | `~/.claude/statusline-command.sh` | Renders the status line.                                                                                      |
| `../AIRULES.md`               | `~/.claude/CLAUDE.md`             | Global instructions Claude reads on every session. Also linked to `~/.codex/AGENTS.md` and `~/.junie/AGENTS.md`. |
| `agents/*.md`                 | `~/.claude/agents/*.md`           | Subagent definitions.                                                                                         |
| `hooks/*` (`! test_*`)        | `~/.claude/hooks/*`               | Hook scripts. Test fixtures under `hooks/test_*` are intentionally excluded.                                  |
| `rules/*.md`                  | `~/.claude/rules/*.md`            | Workflow rules referenced from `AIRULES.md` (`git-workflow.md`, `pr-guidelines.md`, etc.).                    |
| `skills/<name>/`              | `~/.claude/skills/<name>/`        | Skills. Each directory symlinked as a whole.                                                                  |
| `plugins/config.json`         | (not symlinked)                   | Plugin enablement, applied via `scripts/claude-code-setup.sh`. Read by the `claude` CLI from its own state.   |
| `routines/*.md`               | (not symlinked)                   | Scheduled routines, applied via `scripts/claude-code-setup.sh`.                                               |

`scripts/deploy.sh` lines 63-74 are the authoritative version of this
table — keep them in sync when adding new entries.

## Setup script

MCP server registration and plugin installation are NOT done by symlink.
They run through:

```
scripts/claude-code-setup.sh
```

The script is idempotent. Run it after editing the MCP server list or
the plugin enablement, or after a fresh deploy on a new machine.

The script lives under `scripts/` (next to `deploy.sh`, `configure.sh`,
`verify_deploy.sh`) rather than under `claude/`. The reason: `claude/`
mirrors `~/.claude/`, and `~/.claude/` contains no setup scripts — so
a non-mirrored file under `claude/` would erode that invariant.

## MCP server environment variables

When an MCP server entry in `scripts/claude-code-setup.sh` needs an
environment variable:

- Non-secret values (host, port, region) are hardcoded inline in the
  setup script.
- Secrets use `${VAR}` expansion and are sourced from
  `~/.bash_profile.local`, which is not checked in.

## Hooks

Files under `hooks/` matching `test_*` are excluded from the symlink
sweep so the test fixtures do not pollute `~/.claude/hooks/`. Real
hooks have no such prefix.
