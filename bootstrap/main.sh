#!/bin/bash

# This script must be called on each arch.
# Shebang must be !/bin/bash, not !/usr/bin/env bash.

set -eu

if ! command -v xcodebuild 1>/dev/null; then
  echo 'Xcode is not installed.'
  echo 'mas requires Xcode. Please install the latest version of Xcode from App Store.'
  echo 'For more info, see https://github.com/mas-cli/mas.'
  exit 1
fi

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

archname="$(uname -m)"

# Install Rosetta 2 when ARM
if [ "${archname}" = "arm64" ]; then
  softwareupdate --install-rosetta --agree-to-license
fi

# Install homebrew for Intel
if ! command -v brew > /dev/null 2>&1; then
  # Install homebrew: https://brew.sh/
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)"
else
  echo "Homebrew is already installed."
fi

export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"

export HOMEBREW_BUNDLE_NO_LOCK=1
brew bundle
echo

mackup restore
echo

scripts/configure_brew.sh

echo "Bootstrapping DONE!"
