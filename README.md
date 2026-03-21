# dotfiles

![CI](https://github.com/ikuwow/dotfiles/actions/workflows/ci.yml/badge.svg)

Personal configuration files for macOS and Linux, managed as symlinks for portability across machines.

## Set up your new Mac

### Initial Setup (usually done in setup wizard)

Complete these during initial Mac setup or from System Preferences (reboot required if changed later):

* ☑️ Update macOS to the latest version
* ☑️ Set language
* ☑️ Connect to internet
* ☑️ Sign in with Apple ID
* ☑️ Set password for login user

### Required Manual Steps

* ☑️ Install Developer Tools: `xcode-select --install`
* ☑️ Grant Full Disk Access to Terminal (System Preferences => Privacy & Security => Privacy => Full Disk Access => Add Terminal.app)
* ☑️ Generate SSH key pair and register it to GitHub:

```bash
ssh-keygen -t ed25519 -C "your-email@example.com"
```

Be sure to set a passphrase.

## Bootstrapping

```
curl -L https://raw.githubusercontent.com/ikuwow/dotfiles/main/bootstrap.sh | bash -s
```

When you want to bootstrap a specific branch:

```
curl -L https://raw.githubusercontent.com/ikuwow/dotfiles/main/bootstrap.sh | bash -s -- branchname
```

### Set login shell after bootstrapping

```bash
# Intel
LOGIN_SHELL="/usr/local/bin/bash"
sudo sh -c "echo $LOGIN_SHELL >> /etc/shells"
chsh -s "$LOGIN_SHELL"
```

```bash
# Apple Silicon
LOGIN_SHELL="/opt/homebrew/bin/bash"
sudo sh -c "echo $LOGIN_SHELL >> /etc/shells"
chsh -s "$LOGIN_SHELL"
```

## How It Works

All dotfiles in this repository are deployed as symlinks to your home directory by `scripts/deploy.sh`.
For example, `~/.bashrc` is a symlink pointing to `~/dotfiles/.bashrc`.
Editing any dotfile means editing the source file in this repository.

### Symlink Map

| Repository source | Deployed to |
| --- | --- |
| `.aliases`, `.bash_profile`, `.bashrc`, `.vimrc`, etc. (19 dotfiles) | `~/` |
| `.config/*` (all subdirectories) | `~/.config/` |
| `.ssh/config` | `~/.ssh/config` |
| `.kube/kubie.yaml` | `~/.kube/kubie.yaml` |
| `bin/*` (executable files) | `~/bin/` |
| `claude/` (settings, hooks, skills, MCP config) | `~/.claude/` |
| `AIRULES.md` | `~/.claude/CLAUDE.md` |

### Repository Structure

```
dotfiles/
├── bootstrap.sh          # Entry point (run via curl on a new Mac)
├── bootstrap/
│   ├── main.sh           # OS detection, prerequisites, orchestrates full setup
│   └── remote.sh         # Minimal bootstrap for remote environments
├── scripts/
│   ├── deploy.sh         # Creates all symlinks (runs on Linux too)
│   ├── configure.sh      # macOS system preferences via defaults command
│   └── configure_brew.sh # Homebrew post-install configuration
├── Brewfile              # Homebrew package definitions
├── bin/                  # Custom executable scripts → ~/bin/
├── .config/              # XDG config files → ~/.config/
├── claude/               # Claude Code settings → ~/.claude/
├── .bash_profile         # Login shell config → ~/
├── .bashrc               # Interactive shell config → ~/
└── ... (other dotfiles)
```

### Bootstrap Flow

1. `bootstrap.sh` — Clones the repo (or updates it). If `DOTFILES_MINIMAL=1`, runs `bootstrap/claude-code-web.sh` (symlinks only) and exits. Otherwise calls `bootstrap/main.sh`.
2. `bootstrap/main.sh` — Detects OS/architecture, checks prerequisites, orchestrates:
   - `scripts/deploy.sh` — Creates symlinks (runs on Linux and macOS)
   - `scripts/configure.sh` — macOS system defaults (macOS only)
   - Installs Homebrew (macOS only, architecture-aware)
   - `brew bundle` — Installs packages from Brewfile
   - `scripts/configure_brew.sh` — Enables Homebrew autoupdate

### Platform Support

- macOS (Intel and Apple Silicon): Full support (Homebrew, system defaults, GUI apps)
- Linux: Symlink deployment only

On Linux, the bootstrap process deploys symlinks and exits. Homebrew is not used on Linux in this project; shell configuration (`.bash_profile`, `.bashrc`) detects whether Homebrew is installed and skips all Homebrew-dependent setup when it is absent.

### Claude Code Web

When `CLAUDE_CODE_REMOTE=true` is detected (set automatically by Claude Code web), `bootstrap.sh` runs `bootstrap/claude-code-web.sh` instead of the full macOS setup. This script:

1. Installs packages not in the default image (`gh`, `jq`, `fzf`)
2. Deploys all dotfile symlinks via `deploy.sh`
3. Registers MCP servers (`deepwiki`, `Context7`) via `claude mcp add`

Use this as the Claude Code web setup script:

```
curl -L https://raw.githubusercontent.com/ikuwow/dotfiles/main/bootstrap.sh | bash -s
```

`CLAUDE_CODE_REMOTE` is set automatically by the platform; no environment variables need to be configured. For PR creation, use the Claude Code web UI (diff view) instead of `gh` CLI, as the environment variables field does not support secrets.
