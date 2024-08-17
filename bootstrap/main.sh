#!/bin/bash

# This script must be called on each arch.
# Shebang must be !/bin/bash, not !/usr/bin/env bash.

set -eu

os="$(uname)"
if [ "${os}" != "Darwin" ] &&  [ "${os}" != "Linux" ]; then
  echo "Unsupported OS: ${os}"
  exit 1
fi

echo "OS detected: $os"

if [ "${os}" = "Darwin" ]; then
  if [ -z "$(xcode-select -p)" ]; then
    echo 'Command line tool is not installed.'
    echo 'Invoked installation.'
    echo 'Please follow prompt window.'
    xcode-select --install
    exit 1
  fi

scripts/configure.sh
echo

fi

scripts/deploy.sh
echo

if [ "${os}" = "Darwin" ]; then
  scripts/icloud_dirs.sh

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
fi

echo "Bootstrapping DONE!"
