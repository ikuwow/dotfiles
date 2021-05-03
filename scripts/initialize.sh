#!/usr/bin/env bash

set -e

[[ -z $XDG_DATA_HOME ]] && XDG_DATA_HOME=$HOME/.local/share
mkdir -p "$XDG_DATA_HOME"
if [ ! -d "$XDG_DATA_HOME/kyrat" ]; then
  git clone git@github.com:fsquillace/kyrat.git "$XDG_DATA_HOME/kyrat"
fi
mkdir -p ~/bin
ln -fs "$XDG_DATA_HOME/kyrat/bin/kyrat" ~/bin/kyrat
