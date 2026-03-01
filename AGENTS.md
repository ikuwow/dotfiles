# AGENTS.md

Instructions for AI agents working in this repository.

## What This Repository Is

This is a personal dotfiles repository. Files here are deployed to the home directory
and other locations as symlinks by `scripts/deploy.sh`. Running `bootstrap.sh` sets up
a new Mac end-to-end.

## CRITICAL: Symlink Architecture

**Files like `~/.bashrc`, `~/.bash_profile`, `~/.gitconfig`, `~/.vimrc`, etc. in `$HOME`
are symlinks pointing to files in this repository.**

- Always edit the source files in THIS repository
- Never directly edit files under `$HOME` (e.g., `~/.bashrc`, `~/.gitconfig`)
- Never access `~/.bashrc` or similar — read from this repo instead
- When a user asks to modify a shell config, vim config, git config, etc.,
  the file to edit is in this repo, not in `$HOME`

## Symlink Map

The following shows what gets symlinked where by `scripts/deploy.sh`:

| Repository source | Deployed to |
| --- | --- |
| `.aliases` | `~/.aliases` |
| `.asdfrc` | `~/.asdfrc` |
| `.bash_profile` | `~/.bash_profile` |
| `.bashrc` | `~/.bashrc` |
| `.default-gems` | `~/.default-gems` |
| `.default-npm-packages` | `~/.default-npm-packages` |
| `.default-python-packages` | `~/.default-python-packages` |
| `.functions` | `~/.functions` |
| `.gemrc` | `~/.gemrc` |
| `.gvimrc` | `~/.gvimrc` |
| `.ideavimrc` | `~/.ideavimrc` |
| `.inputrc` | `~/.inputrc` |
| `.npmrc` | `~/.npmrc` |
| `.shellcheckrc` | `~/.shellcheckrc` |
| `.sshrc` | `~/.sshrc` |
| `.terraformrc` | `~/.terraformrc` |
| `.tmux.conf` | `~/.tmux.conf` |
| `.tool-versions` | `~/.tool-versions` |
| `.vimrc` | `~/.vimrc` |
| `.config/*` (all subdirs) | `~/.config/` |
| `.ssh/config` | `~/.ssh/config` |
| `.kube/kubie.yaml` | `~/.kube/kubie.yaml` |
| `bin/*` (executable files) | `~/bin/` |
| `claude/.mcp.json` | `~/.claude/.mcp.json` |
| `claude/settings.json` | `~/.claude/settings.json` |
| `AIRULES.md` | `~/.claude/CLAUDE.md` |
| `claude/commands/*` | `~/.claude/commands/` |

## Repository Structure

```
dotfiles/
├── bootstrap.sh          # Entry point: clones repo and runs bootstrap/main.sh
├── bootstrap/
│   └── main.sh           # OS detection, prerequisites, orchestrates full setup
├── scripts/
│   ├── deploy.sh         # Creates all symlinks (runs on Linux too)
│   ├── configure.sh      # macOS system preferences via defaults command
│   └── configure_brew.sh # Homebrew post-install configuration
├── Brewfile              # Homebrew package definitions
├── bin/                  # Custom executable scripts → ~/bin/
├── .config/              # XDG config files → ~/.config/
├── claude/               # Claude Code settings → ~/.claude/
├── AIRULES.md            # Global AI rules → ~/.claude/CLAUDE.md
├── .bash_profile         # Login shell config → ~/
├── .bashrc               # Interactive shell config → ~/
└── ... (other dotfiles)  # All symlinked to ~/
```

## Bootstrap Flow

1. `bootstrap.sh` — Clones the repo (or updates it), then calls `bootstrap/main.sh`
2. `bootstrap/main.sh` — Detects OS/architecture, checks prerequisites, orchestrates:
   - `scripts/deploy.sh` — Creates symlinks (runs on Linux and macOS)
   - `scripts/configure.sh` — macOS system defaults (macOS only)
   - Installs Homebrew (macOS only, architecture-aware)
   - `brew bundle` — Installs packages from Brewfile
   - `scripts/configure_brew.sh` — Enables Homebrew autoupdate

## How to Add a New Dotfile

1. Place the file in the repository root (e.g., `.newconfig`)
2. Add the filename to the `DOTFILES` array in `scripts/deploy.sh`
3. Run `./scripts/deploy.sh` to create the symlink

## Platform Support

- macOS (Intel and Apple Silicon): Full support
- Linux: Symlink deployment only (no Homebrew, no macOS defaults)
