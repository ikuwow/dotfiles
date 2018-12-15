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

KYRAT_PATH=~/.local/share/kyrat
mkdir -p "$(dirname ~/.local/share)"
if [ ! -d $KYRAT_PATH ]; then
    git clone git@github.com:fsquillace/kyrat.git $KYRAT_PATH
else
    cd $KYRAT_PATH
    git stash save
    git checkout master
    git pull origin master
fi
mkdir -p ~/bin
ln -s "$KYRAT_PATH/bin/kyrat" ~/bin/kyrat
