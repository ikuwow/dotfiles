# AGENTS.md

Instructions for AI agents working in this repository.

Read @README.md for the project overview, repository structure, and how it works.

## CRITICAL: Symlink Architecture

Files like `~/.bashrc`, `~/.bash_profile`, `~/.inputrc`, etc. in `$HOME`
are symlinks pointing to files in this repository.

- Files under `claude/` are symlinked into `~/.claude/` — always look at `claude/` in this repo first for Claude Code configuration (settings, hooks, MCP, skills, etc.)
- `AIRULES.md` is also symlinked to `~/.codex/AGENTS.md` (Codex CLI) and `~/.junie/AGENTS.md` (Junie CLI) for their global instructions
- When investigating, reading, or editing files managed by this repository,
  always start from the path within this repo. Examples: `bin/foo` not
  `~/bin/foo`, `claude/settings.json` not `~/.claude/settings.json`,
  `ls claude/hooks/` not `ls ~/.claude/hooks/`, `cat AIRULES.md` not
  `cat ~/.claude/CLAUDE.md`. Deploy targets under `$HOME` (`~/.claude/`,
  `~/.codex/`, etc.) generally require a permission prompt
- Check `scripts/deploy.sh` for the full list of symlink mappings

## Key Commands

```bash
# Deploy/update dotfiles (creates symlinks)
./scripts/deploy.sh

# Validate shell scripts
shellcheck scripts/*.sh bootstrap/*.sh

# Run pre-commit hooks
pre-commit run --all-files
```

## How to Add a New Dotfile

1. Place the file in the repository root (e.g., `.newconfig`)
1. Add a `link` call in `scripts/deploy.sh` under the appropriate category:
   `link .newconfig "$HOME/.newconfig"`
1. Run `./scripts/deploy.sh` to create the symlink

## Git Workflow

- Always create a branch before making changes. When the user explicitly requests direct work on main, proceed after the default-branch guard hook's first deny — its retry is sanctioned for the rest of the session
- Do NOT create git worktrees — branch only, no worktree
- The working tree may be shared by multiple concurrent Claude Code
  sessions: claude/settings.json's model field commonly shows as a
  spurious uncommitted diff from another session's /model command.
  This is expected drift, not real work — stash-and-restore it
  around branch switches instead of investigating or reconciling it

## Language

- Write all text in English: commit messages, PR descriptions, issue comments, code comments, etc
- Exception: `AIRULES.md` is written in Japanese; references to its content may also be in Japanese

## Script Requirements

- Bootstrap scripts use `/bin/bash` (not `/usr/bin/env bash`) for compatibility
- All scripts must pass shellcheck validation
- Use `set -eu` for error handling in critical scripts

## Machine-local Git Config

Machine-specific git settings (host-only URL rewrites, per-repo
credentials, work-account overrides) go in `~/.gitconfig.local`,
which `xdg-config/git/config` includes. Do not add these to the
tracked config.

## Personal Tool Defaults

This repository is a personal dotfiles repo. Scripts here may assume:

- The host environment (PATH, brew packages like coreutils, shell,
  editor) is set up by this repository's own bootstrap. Probing for
  `gtimeout` vs `timeout` vs no-timeout fallback is over-engineering —
  assume `timeout` is on PATH.
- "Best-effort" failure is acceptable for discretionary helpers. Let
  bash propagate errors under `set -eu` so the user sees the real
  failure, instead of wrapping every step in `|| { stderr; exit 0; }`
  defensive handlers. Reserve always-exit-0 contracts for scripts
  that would block a user-critical operation on failure.
- An automated test harness (bats, shunit2, etc.) is NOT required for
  short shell utilities even when reviewers recommend one. The user
  exercises these scripts on every commit; regressions surface
  immediately and can be fixed inline.

Reviewer agents (silent-failure-hunter, pr-test-analyzer, etc.) are
calibrated for production code and will recommend defensive handlers
and test coverage that are over-engineering for personal-dotfiles
scope. This governs how you weigh their findings (decline
recommendations you judge over-engineered), never whether to run the
review phases themselves — the git-workflow skill's phase pre-
authorization is not overridable by this section.
