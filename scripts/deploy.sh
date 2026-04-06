#!/usr/bin/env bash

set -eu

DOTPATH="$HOME/dotfiles"
XDG_CONFIG_HOME="${XDG_CONFIG_HOME:-$HOME/.config}"

if [ ! -e "$DOTPATH" ]; then
  echo "Error: Directory $DOTPATH does not exist."
  exit 1
fi

link() {
  local src="$DOTPATH/$1"
  local dst="$2"
  if [ ! -e "$src" ]; then
    echo "Warning: $src not found, skipping"
    return
  fi
  mkdir -p "$(dirname "$dst")"
  ln -fvns "$src" "$dst"
}

# Shell
link .bash_profile  "$HOME/.bash_profile"
link .bashrc        "$HOME/.bashrc"
link .aliases       "$HOME/.aliases"
link .functions     "$HOME/.functions"
link .inputrc       "$HOME/.inputrc"
link .sshrc         "$HOME/.sshrc"

# Editor
link .vimrc         "$HOME/.vimrc"
link .gvimrc        "$HOME/.gvimrc"
link .ideavimrc     "$HOME/.ideavimrc"

# Terminal
link .tmux.conf     "$HOME/.tmux.conf"

# Version / package managers
link .tool-versions           "$HOME/.tool-versions"
link .gemrc                   "$HOME/.gemrc"
link .npmrc                   "$HOME/.npmrc"
link .default-gems            "$HOME/.default-gems"
link .default-npm-packages    "$HOME/.default-npm-packages"
link .default-python-packages "$HOME/.default-python-packages"

# Infrastructure
link .terraformrc   "$HOME/.terraformrc"

# Linting
link .shellcheckrc  "$HOME/.shellcheckrc"

# XDG config: all subdirs in xdg-config/ auto-discovered
mkdir -p "$XDG_CONFIG_HOME"
find "$DOTPATH/xdg-config" -maxdepth 1 -mindepth 1 ! -type f ! -name '.*' -exec ln -fvns {} "$XDG_CONFIG_HOME/" \;

# SSH
link .ssh/config    "$HOME/.ssh/config"
mkdir -p "$HOME/.ssh/config.d"

# Kubernetes
link .kube/kubie.yaml "$HOME/.kube/kubie.yaml"

# bin: all executable files auto-discovered
mkdir -p "$HOME/bin"
find "$DOTPATH/bin/" -type f -perm 0755 -exec ln -fvns {} "$HOME/bin/" \;

# iCloud (macOS only, conditional)
ICLOUD_DIR="$HOME/Library/Mobile Documents/com~apple~CloudDocs"
if [[ -d "$ICLOUD_DIR" ]]; then
  ln -fvns "$ICLOUD_DIR" "$HOME/iCloudDrive"
fi

# Claude Code: explicit files + skills auto-discovered
link claude/.mcp.json              "$HOME/.claude/.mcp.json"
link claude/settings.json          "$HOME/.claude/settings.json"
link claude/statusline-command.sh  "$HOME/.claude/statusline-command.sh"
link AIRULES.md           "$HOME/.claude/CLAUDE.md"
mkdir -p "$HOME/.claude/skills"
find "$DOTPATH/claude/skills" -maxdepth 1 -mindepth 1 -type d -exec ln -fvns {} "$HOME/.claude/skills/" \;
mkdir -p "$HOME/.claude/hooks"
find "$DOTPATH/claude/hooks" -maxdepth 1 -mindepth 1 -type f ! -name 'test_*' -exec ln -fvns {} "$HOME/.claude/hooks/" \;
mkdir -p "$HOME/.claude/rules"
find "$DOTPATH/claude/rules" -maxdepth 1 -mindepth 1 -type f -name '*.md' -exec ln -fvns {} "$HOME/.claude/rules/" \;

# Codex CLI
link AIRULES.md  "$HOME/.codex/AGENTS.md"
mkdir -p "$HOME/.codex/rules"
find "$DOTPATH/codex/rules" -maxdepth 1 -mindepth 1 -type f -name '*.rules' -exec ln -fvns {} "$HOME/.codex/rules/" \;
