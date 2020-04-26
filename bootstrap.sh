#!/usr/bin/env bash

set -eu

if [ -z "$DOTPATH" ]; then
  export DOTPATH=$HOME/dotfiles
fi

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
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)"
  echo
fi
brew bundle
echo

mackup restore
echo

scripts/initialize.sh
echo

echo "Bootstrapping DONE!"
