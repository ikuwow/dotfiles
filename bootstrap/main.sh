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

# Install homebrew for Intel
if ! command -v /usr/local/bin/brew >/dev/null 2>&1; then
  prefix=""
  if [ "$(uname -m)" = "arm64" ]; then
    # Install on Rosetta 2
    prefix="arch -arch x86_64"
  fi
  # Install homebrew: https://brew.sh/
  $prefix /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)"
fi

# Install homebrew for ARM
if [ "$(uname -m)" = "arm64" ] && (! command -v /opt/homebrew/bin/brew > /dev/null); then
  sudo mkdir /opt/homebrew
  sudo chown "$(whoami)" /opt/homebrew
  curl -L https://github.com/Homebrew/brew/tarball/master | tar xz --strip 1 -C /opt/homebrew
fi

export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"

brew bundle
echo

mackup restore
echo

scripts/initialize.sh
echo

scripts/configure_brew.sh

echo "Bootstrapping DONE!"
