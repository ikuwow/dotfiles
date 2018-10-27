#!/usr/bin/env bash

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")"; pwd)"

pip3 install --upgrade pip
pip3 install neovim

pip2 install --upgrade pip
pip2 install neovim

gem update
gem install neovim

npm i -g neovim

cp "$SCRIPT_DIR/brew_cleanup.plist" ~/Library/LaunchAgents/

launchctl load "$SCRIPT_DIR/brew_cleanup.plist"
