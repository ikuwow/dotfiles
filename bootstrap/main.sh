#!/usr/bin/env bash

set -eu

# Mac basic settings
scripts/configure.sh
echo

scripts/deploy.sh
echo

# install homebrew
if ! command -v brew >/dev/null 2>&1; then
  # Install homebrew: https://brew.sh/
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)"
  echo
fi
brew bundle
echo

mackup restore
echo

scripts/initialize.sh
echo

scripts/configure_brew.sh

echo "Bootstrapping DONE!"
