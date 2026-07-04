#!/bin/bash

# Verify that deploy.sh created expected symlinks and directories.
# Exit with non-zero if any check fails.

set -eu

errors=0

check_symlink() {
  local path="$1"
  if [ -L "$path" ]; then
    echo "OK: $path -> $(readlink "$path")"
  else
    echo "FAIL: $path is not a symlink"
    errors=$((errors + 1))
  fi
}

check_dir() {
  local path="$1"
  if [ -d "$path" ]; then
    echo "OK: $path exists"
  else
    echo "FAIL: $path does not exist"
    errors=$((errors + 1))
  fi
}

check_no_dangling_symlinks() {
  local dir="$1"
  local dangling
  dangling=$(find "$dir" -maxdepth 1 -type l ! -exec test -e {} \; -print)
  if [ -z "$dangling" ]; then
    echo "OK: $dir has no dangling symlinks"
  else
    echo "FAIL: $dir has dangling symlinks:"
    echo "$dangling"
    errors=$((errors + 1))
  fi
}

check_no_untracked_real_files() {
  local dir="$1"
  local real_files
  real_files=$(find "$dir" -maxdepth 1 -type f -print)
  if [ -z "$real_files" ]; then
    echo "OK: $dir has no untracked real files"
  else
    echo "FAIL: $dir has real files not managed by deploy.sh (should be symlinks):"
    echo "$real_files"
    errors=$((errors + 1))
  fi
}

echo "=== Shell config ==="
check_symlink "$HOME/.bash_profile"
check_symlink "$HOME/.bashrc"
check_symlink "$HOME/.aliases"
check_symlink "$HOME/.functions"
check_symlink "$HOME/.inputrc"

echo ""
echo "=== SSH ==="
check_symlink "$HOME/.ssh/config"
check_dir "$HOME/.ssh/config.d"

echo ""
echo "=== XDG config (auto-discovered) ==="
check_symlink "${XDG_CONFIG_HOME:-$HOME/.config}/git"
check_symlink "${XDG_CONFIG_HOME:-$HOME/.config}/nvim"
check_symlink "${XDG_CONFIG_HOME:-$HOME/.config}/tmux"
check_symlink "${XDG_CONFIG_HOME:-$HOME/.config}/vim"
check_symlink "${XDG_CONFIG_HOME:-$HOME/.config}/ideavim"

echo ""
echo "=== bin (auto-discovered) ==="
check_dir "$HOME/bin"
# At least one executable should be linked
if [ -L "$HOME/bin/git-worktree-create" ]; then
  echo "OK: $HOME/bin/git-worktree-create linked"
else
  echo "FAIL: $HOME/bin/git-worktree-create not linked"
  errors=$((errors + 1))
fi

echo ""
echo "=== Claude Code ==="
check_symlink "$HOME/.claude/.mcp.json"
check_symlink "$HOME/.claude/settings.json"
check_symlink "$HOME/.claude/CLAUDE.md"
check_dir "$HOME/.claude/skills"
check_dir "$HOME/.claude/hooks"
check_dir "$HOME/.claude/agents"
check_dir "$HOME/.claude/rules"
# Auto-discovered skills, hooks, agents, and rules
check_symlink "$HOME/.claude/skills/retrospective"
check_symlink "$HOME/.claude/hooks/approve_git_gh_commands.py"
check_symlink "$HOME/.claude/hooks/hook_utils.py"
check_symlink "$HOME/.claude/agents/investigator.md"
check_symlink "$HOME/.claude/rules/git-workflow.md"
check_no_dangling_symlinks "$HOME/.claude/skills"
check_no_dangling_symlinks "$HOME/.claude/hooks"
check_no_dangling_symlinks "$HOME/.claude/agents"
check_no_dangling_symlinks "$HOME/.claude/rules"
check_no_untracked_real_files "$HOME/.claude/rules"

echo ""
if [ "$errors" -gt 0 ]; then
  echo "FAILED: $errors check(s) failed"
  exit 1
else
  echo "All checks passed"
fi
