#!/usr/bin/env bash

set -eu

scripts/configure.sh
echo

scripts/deploy.sh
echo

# Install Rosetta 2 when ARM
if [ "$(uname -m)" = "arm64" ]; then
  softwareupdate --install-rosetta --agree-to-license
fi

# install homebrew
if ! command -v brew >/dev/null 2>&1; then
  prefix=""
  if [ "$(uname -m)" = "arm64" ]; then
    # Install on Rosetta 2
    prefix="arch -arch x86_64"
  fi
  # Install homebrew: https://brew.sh/
  "${prefix}" /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)"
fi
brew bundle
echo

mackup restore
echo

scripts/initialize.sh
echo

scripts/configure_brew.sh

echo "Bootstrapping DONE!"
