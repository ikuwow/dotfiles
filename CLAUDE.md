# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a personal dotfiles repository for macOS setup and configuration. It contains:
- Shell configuration files (bash, vim, git, etc.)
- macOS system preferences automation
- Homebrew package management via Brewfile
- Automated deployment scripts for symlinking dotfiles

## Key Commands

### Initial Setup
```bash
# Bootstrap a new Mac (from remote)
curl -L https://raw.githubusercontent.com/ikuwow/dotfiles/master/bootstrap.sh | bash -s

# Bootstrap specific branch
curl -L https://raw.githubusercontent.com/ikuwow/dotfiles/master/bootstrap.sh | bash -s -- branchname
```

### Deployment
```bash
# Deploy/update dotfiles (creates symlinks)
./scripts/deploy.sh

# Configure macOS system preferences
./scripts/configure.sh

# Configure Homebrew packages
./scripts/configure_brew.sh
```

### Homebrew Management
```bash
# Install all packages from Brewfile
brew bundle

# Check if all dependencies are installed
brew bundle check
```

### Shell Script Quality
When modifying shell scripts:
```bash
# Validate shell scripts with shellcheck
shellcheck scripts/*.sh bootstrap/*.sh
```

## Architecture & Structure

### Bootstrap Flow
1. `bootstrap.sh` - Entry point that clones repo and calls main.sh
2. `bootstrap/main.sh` - OS detection, prerequisites check, orchestrates setup
3. `scripts/deploy.sh` - Creates symlinks from dotfiles to home directory
4. `scripts/configure.sh` - Sets macOS defaults using `defaults` command
5. `scripts/configure_brew.sh` - Post-Homebrew installation configuration

### Symlink Strategy
- Regular dotfiles (`.bashrc`, `.gitconfig`, etc.) are symlinked directly to `$HOME`
- Config files in `.config/` are symlinked to `$XDG_CONFIG_HOME` (defaults to `~/.config`)
- Neovim configuration: `.vimrc` → `~/.config/nvim/init.vim`, `.gvimrc` → `~/.config/nvim/ginit.vim`
- Special handling for `.ssh/config`, `.kube/kubie.yaml`, and bin scripts

### Key Directories
- `bin/` - Custom executable scripts, symlinked to `~/bin/`
- `.config/` - XDG config files, symlinked to `~/.config/`
- `scripts/` - Setup and configuration scripts
- `bootstrap/` - Initial setup orchestration

## Development Notes

### Adding New Dotfiles
1. Place the dotfile in the repository root (e.g., `.newconfig`)
2. Run `./scripts/deploy.sh` to create the symlink
3. Files matching `.git*`, `.DS_Store`, `.travis.yml`, `.config`, `.github`, `.kube` are automatically excluded

### Script Requirements
- Bootstrap scripts use `/bin/bash` (not `/usr/bin/env bash`) for compatibility
- All scripts should pass shellcheck validation
- Use `set -eu` for error handling in critical scripts

### Platform Support
- Primary support for macOS (both Intel and Apple Silicon)
- Limited Linux support (deployment only, no package management)
- Architecture detection for Homebrew path differences (`/usr/local` vs `/opt/homebrew`)
