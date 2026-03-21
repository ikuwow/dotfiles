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

echo "=== Shell config ==="
check_symlink "$HOME/.bash_profile"
check_symlink "$HOME/.bashrc"
check_symlink "$HOME/.aliases"
check_symlink "$HOME/.functions"
check_symlink "$HOME/.inputrc"

echo ""
echo "=== Editor ==="
check_symlink "$HOME/.vimrc"

echo ""
echo "=== Linting ==="
check_symlink "$HOME/.shellcheckrc"

echo ""
echo "=== SSH ==="
check_symlink "$HOME/.ssh/config"
check_dir "$HOME/.ssh/config.d"

echo ""
echo "=== XDG config (auto-discovered) ==="
check_symlink "$HOME/.config/git"
check_symlink "$HOME/.config/nvim"

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
check_dir "$HOME/.claude/rules"
# Auto-discovered skills and hooks
check_symlink "$HOME/.claude/skills/retrospective"
check_symlink "$HOME/.claude/hooks/approve_safe_commands.py"
check_symlink "$HOME/.claude/rules/git-workflow.md"

echo ""
if [ "$errors" -gt 0 ]; then
  echo "FAILED: $errors check(s) failed"
  exit 1
else
  echo "All checks passed"
fi
