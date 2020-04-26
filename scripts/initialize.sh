#!/usr/bin/env bash

set -e

brew install python

/usr/local/bin/pip3 install --upgrade pip
/usr/local/bin/pip3 uninstall neovim
/usr/local/bin/pip3 install --upgrade pynvim

/usr/local/bin/pip2 install --upgrade pip
/usr/local/bin/pip2 uninstall neovim
/usr/local/bin/pip2 install --upgrade pynvim

[[ -z $XDG_DATA_HOME ]] && XDG_DATA_HOME=$HOME/.local/share
mkdir -p "$XDG_DATA_HOME"
if [ ! -d "$XDG_DATA_HOME/kyrat" ]; then
  git clone https://github.com/fsquillace/kyrat.git "$XDG_DATA_HOME/kyrat"
fi
mkdir -p ~/bin
ln -fs "$XDG_DATA_HOME/kyrat/bin/kyrat" ~/bin/kyrat
