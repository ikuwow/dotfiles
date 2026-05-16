#!/usr/bin/env bash
# install-aimsg-hook: symlink the AI-draft prepare-commit-msg hook into the
# current repository's .git/hooks/. Idempotent. Disable later with
# `rm "$(git rev-parse --git-path hooks)/prepare-commit-msg"`.

set -eu

SRC="$HOME/.config/git/hooks/prepare-commit-msg"
if [ ! -x "$SRC" ]; then
  echo "install-aimsg-hook: source hook not found or not executable: $SRC" >&2
  exit 1
fi

HOOKS_DIR=$(git rev-parse --git-path hooks) || {
  echo "install-aimsg-hook: not inside a git repository" >&2
  exit 1
}

mkdir -p "$HOOKS_DIR"
ln -snf "$SRC" "$HOOKS_DIR/prepare-commit-msg"
echo "install-aimsg-hook: installed $HOOKS_DIR/prepare-commit-msg -> $SRC"
