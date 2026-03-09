# AGENTS.md

Instructions for AI agents working in this repository.

Read README.md for the project overview, repository structure, and how it works.

## CRITICAL: Symlink Architecture

**Files like `~/.bashrc`, `~/.bash_profile`, `~/.vimrc`, etc. in `$HOME`
are symlinks pointing to files in this repository.**

- `claude/` directory is symlinked to `~/.claude/` — always look at `claude/` in this repo first for Claude Code configuration (settings, hooks, MCP, skills, etc.)
- Before searching for a file's location, check `scripts/deploy.sh` for symlink mappings first
- Always edit the source files in THIS repository
- Never directly edit files under `$HOME` (e.g., `~/.bashrc`, `~/.gitconfig`)
- Never access `~/.bashrc` or similar — read from this repo instead

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
2. Add a `link` call in `scripts/deploy.sh` under the appropriate category:
   `link .newconfig "$HOME/.newconfig"`
3. Run `./scripts/deploy.sh` to create the symlink

## Git Workflow

- Always create a branch before making changes (direct commits to main are prohibited)
- Do NOT create git worktrees — branch only, no worktree

## Language

- Write all text in English: commit messages, PR descriptions, issue comments, code comments, etc.
- Exception: `AIRULES.md` is written in Japanese; references to its content may also be in Japanese

## Script Requirements

- Bootstrap scripts use `/bin/bash` (not `/usr/bin/env bash`) for compatibility
- All scripts must pass shellcheck validation (see `.shellcheckrc` for disabled rules)
- Use `set -eu` for error handling in critical scripts
