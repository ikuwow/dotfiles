#!/usr/bin/env bash

set -eu

DOTPATH=$HOME/dotfiles

BRANCH="$1"
if [ -n "$BRANCH" ]; then
  echo "Branch specified: $BRANCH"
else
  BRANCH="master"
fi

if [ ! -d "$DOTPATH" ]; then
  git clone -b "$BRANCH" https://github.com/ikuwow/dotfiles.git "$DOTPATH"
else
  echo "$DOTPATH already downloaded. Updating..."
  cd "$DOTPATH"
  git stash
  git checkout "$BRANCH"
  git pull origin "$BRANCH"
  echo
fi

cd "$DOTPATH"

./bootstrap/main.sh
