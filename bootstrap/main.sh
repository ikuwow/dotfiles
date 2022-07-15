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

command_prefix=""
if [ "$(uname -m)" = "arm64" ]; then
  # Install on Rosetta 2
  command_prefix="arch -arch x86_64"
fi

# Install Rosetta 2 when ARM
if [ "$(uname -m)" = "arm64" ]; then
  softwareupdate --install-rosetta --agree-to-license
fi

# Install homebrew for Intel
if ! command -v /usr/local/bin/brew >/dev/null 2>&1; then
  # Install homebrew: https://brew.sh/
  $command_prefix /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)"
fi

# Install homebrew for ARM
if [ "$(uname -m)" = "arm64" ] && (! command -v /opt/homebrew/bin/brew > /dev/null); then
  sudo mkdir /opt/homebrew
  sudo chown "$(whoami)" /opt/homebrew
  curl -L https://github.com/Homebrew/brew/tarball/master | tar xz --strip 1 -C /opt/homebrew
fi

# TODO: prioritize ARM homebrew
# export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"

export HOMEBREW_BUNDLE_NO_LOCK=1
$command_prefix brew bundle
echo

mackup restore
echo

scripts/configure_brew.sh

echo "Bootstrapping DONE!"
