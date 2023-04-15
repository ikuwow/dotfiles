#!/bin/bash

# This script must be called on each arch.
# Shebang must be !/bin/bash, not !/usr/bin/env bash.

set -eu

if [ "$(xcode-select -p 1>/dev/null; echo $?)" != 0 ]; then
  echo 'Command line tool is not installed.'
  echo 'Invoked installation.'
  echo 'Please follow prompt window.'
  xcode-select --install
  exit 1
fi

scripts/configure.sh
echo

scripts/deploy.sh
echo

archname="$(arch)"
echo "Arch: ${archname}"

# Install Rosetta 2 when ARM
if [ "${archname}" = "arm64" ]; then
  softwareupdate --install-rosetta --agree-to-license
fi

# Install homebrew for Intel
if [ "${archname}" = "i386" ]; then
  if ! command -v /usr/local/bin/brew > /dev/null 2>&1; then
    # Install homebrew: https://brew.sh/
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)"
  else
    echo "Homebrew is already installed."
  fi
  export PATH="/usr/local/bin:$PATH"
elif [ "${archname}" = "arm64" ]; then
  if ! command -v /opt/homebrew/bin/brew > /dev/null 2>&1; then
    # Install homebrew: https://brew.sh/
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)"
  else
    echo "Homebrew is already installed."
  fi
  export PATH="/opt/homebrew/bin:$PATH"
fi

brew install mackup
mackup restore
echo

export HOMEBREW_BUNDLE_NO_LOCK=1
brew bundle
echo

scripts/configure_brew.sh

echo "Bootstrapping DONE!"
