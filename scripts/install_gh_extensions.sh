#!/usr/bin/env bash

set -eu

if ! command -v gh >/dev/null 2>&1; then
  echo "gh CLI not found, skipping extension install."
  exit 0
fi

install_ext() {
  local ext="$1"
  if gh extension list | cut -f2 | grep -Fxq "$ext"; then
    echo "gh extension already installed: $ext"
  else
    echo "Installing gh extension: $ext"
    gh extension install "$ext"
  fi
}

install_ext agynio/gh-pr-review
