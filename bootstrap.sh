#!/usr/bin/env bash

set -eu

DOTPATH=$HOME/dotfiles

if [ ! -d "$DOTPATH" ]; then
  git clone https://github.com/ikuwow/dotfiles.git "$DOTPATH"
else
  echo "$DOTPATH already downloaded. Updating..."
  cd "$DOTPATH"
  git stash
  git checkout master
  git pull origin master
  echo
fi

cd "$DOTPATH"

# Mac basic settings
scripts/configure.sh
echo

scripts/deploy.sh
echo

# install homebrew
if ! command -v brew >/dev/null 2>&1; then
  # Install homebrew: https://brew.sh/
  /usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
  echo
fi

if [ -n "$GITHUB_ACTIONS" ]; then
  brew bundle
  echo
  mackup restore
  echo
fi

scripts/initialize.sh
echo

echo "Bootstrapping DONE!"
