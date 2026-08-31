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

# Version / package managers
link .tool-versions           "$HOME/.tool-versions"
link .textlintrc.json         "$HOME/.textlintrc.json"

# XDG config: all subdirs in xdg-config/ auto-discovered
mkdir -p "$XDG_CONFIG_HOME"
find "$DOTPATH/xdg-config" -maxdepth 1 -mindepth 1 ! -type f ! -name '.*' -exec ln -fvns {} "$XDG_CONFIG_HOME/" \;

# SSH
link .ssh/config    "$HOME/.ssh/config"
mkdir -p "$HOME/.ssh/config.d"

# Kubernetes
link .kube/kubie.yaml "$HOME/.kube/kubie.yaml"

# bin: all executable files auto-discovered. Prune broken symlinks first
# so renamed/removed scripts don't leave stale entries on PATH.
mkdir -p "$HOME/bin"
find "$HOME/bin/" -maxdepth 1 -type l ! -exec test -e {} \; -print -delete
find "$DOTPATH/bin/" -type f -perm 0755 -exec ln -fvns {} "$HOME/bin/" \;

# iCloud (macOS only, conditional)
ICLOUD_DIR="$HOME/Library/Mobile Documents/com~apple~CloudDocs"
if [[ -d "$ICLOUD_DIR" ]]; then
  ln -fvns "$ICLOUD_DIR" "$HOME/iCloudDrive"
fi

# Hammerspoon: the app hardcodes ~/.hammerspoon, so this cannot ride the
# xdg-config glob. Link per entry so app-created state (Spoons/) stays out
# of the repository.
mkdir -p "$HOME/.hammerspoon"
find "$DOTPATH/hammerspoon" -maxdepth 1 -mindepth 1 -type f -exec ln -fvns {} "$HOME/.hammerspoon/" \;
find "$HOME/.hammerspoon/" -maxdepth 1 -type l ! -exec test -e {} \; -print -delete

# Agent CLIs (Claude Code, Codex, Junie). Each auto-discovered directory
# below relinks first and prunes broken symlinks second, so a missing or
# partial source tree aborts under `set -e` before anything is deleted.
# Only broken symlinks go: real files stay, and so do the entries deployed
# by link(), which warns and skips when its source is gone.

# Claude Code: explicit files + skills auto-discovered
link claude/.mcp.json              "$HOME/.claude/.mcp.json"
link claude/settings.json          "$HOME/.claude/settings.json"
link claude/statusline-command.sh  "$HOME/.claude/statusline-command.sh"
link AIRULES.md           "$HOME/.claude/CLAUDE.md"
mkdir -p "$HOME/.claude/skills"
find "$DOTPATH/claude/skills" -maxdepth 1 -mindepth 1 -type d -exec ln -fvns {} "$HOME/.claude/skills/" \;
find "$HOME/.claude/skills/" -maxdepth 1 -type l ! -exec test -e {} \; -print -delete
mkdir -p "$HOME/.claude/hooks"
find "$DOTPATH/claude/hooks" -maxdepth 1 -mindepth 1 -type f ! -name 'test_*' -exec ln -fvns {} "$HOME/.claude/hooks/" \;
find "$HOME/.claude/hooks/" -maxdepth 1 -type l ! -exec test -e {} \; -print -delete
mkdir -p "$HOME/.claude/agents"
find "$DOTPATH/claude/agents" -maxdepth 1 -mindepth 1 -type f -name '*.md' -exec ln -fvns {} "$HOME/.claude/agents/" \;
find "$HOME/.claude/agents/" -maxdepth 1 -type l ! -exec test -e {} \; -print -delete
mkdir -p "$HOME/.claude/rules"
find "$DOTPATH/claude/rules" -maxdepth 1 -mindepth 1 -type f -name '*.md' -exec ln -fvns {} "$HOME/.claude/rules/" \;
find "$HOME/.claude/rules/" -maxdepth 1 -type l ! -exec test -e {} \; -print -delete

# Codex CLI
link AIRULES.md  "$HOME/.codex/AGENTS.md"
mkdir -p "$HOME/.codex/rules"
find "$DOTPATH/codex/rules" -maxdepth 1 -mindepth 1 -type f -name '*.rules' -exec ln -fvns {} "$HOME/.codex/rules/" \;
find "$HOME/.codex/rules/" -maxdepth 1 -type l ! -exec test -e {} \; -print -delete

# Junie CLI (JetBrains)
link AIRULES.md  "$HOME/.junie/AGENTS.md"
mkdir -p "$HOME/.junie/skills"
find "$DOTPATH/claude/skills" -maxdepth 1 -mindepth 1 -type d -exec ln -fvns {} "$HOME/.junie/skills/" \;
find "$HOME/.junie/skills/" -maxdepth 1 -type l ! -exec test -e {} \; -print -delete
