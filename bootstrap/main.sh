#!/bin/bash

# Shebang must be !/bin/bash, not !/usr/bin/env bash.

set -eu

os="$(uname)"
# If os is neither Linux or Darwin, exit 1
if [ "$os" != 'Darwin' ] && [ "$os" != 'Linux' ]; then
  echo "Error: Unsupported OS: $os"
  exit 1
fi
echo "OS detected: $os"

scripts/deploy.sh

if [ "$os" = "Linux" ]; then
  echo "Linux: symlink deployment complete. Skipping macOS-specific setup."
  exit 0
fi

if ! xcode-select -p >/dev/null 2>&1; then
  echo 'Command line tool is not installed.'
  echo 'Invoked installation.'
  echo 'Please follow prompt window.'
  xcode-select --install
  exit 1
fi

scripts/configure.sh
echo

softwareupdate --install-rosetta --agree-to-license

if ! command -v /opt/homebrew/bin/brew > /dev/null 2>&1; then
  # Install homebrew: https://brew.sh/
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)"
else
  echo "Homebrew is already installed."
fi
export PATH="/opt/homebrew/bin:$PATH"

if [ -n "${CI+x}" ]; then
  echo "Warning: You are on CI. Skip some setup like 'brew bundle'."
  exit 0
fi

brew bundle
echo

pre-commit install
echo

gh extension install agynio/gh-pr-review
gh extension install dlvhdr/gh-dash
(cd gh-extensions/gh-sub-issue && gh extension install .)
echo

scripts/configure_brew.sh

echo "Bootstrapping DONE!"
