#!/usr/bin/env bash

DOTPATH="$HOME/dotfiles"

if [ ! -e "$DOTPATH" ]; then
  echo "Error: Directory $DOTPATH does not exist."
  exit 1
fi

cd "$DOTPATH" || exit 1

[[ -z $XDG_CONFIG_HOME ]] && XDG_CONFIG_HOME=$HOME/.config

for file in .??*; do
  [[ "$file" == ".git" ]] && continue
  [[ "$file" == ".gitignore" ]] && continue
  [[ "$file" == ".DS_Store" ]] && continue
  [[ "$file" == ".travis.yml" ]] && continue
  [[ "$file" == ".config" ]] && continue
  [[ "$file" == ".github" ]] && continue
  ln -fvns "$DOTPATH/$file" "$HOME/$file"
done

mkdir -p "$XDG_CONFIG_HOME"
find "$DOTPATH/.config" -maxdepth 1 -mindepth 1 -exec ln -fvns {} "$XDG_CONFIG_HOME/" \;

# ssh
mkdir -p "$HOME/.ssh"
ln -fvns "$DOTPATH/.ssh/config" "$HOME/.ssh/config"
mkdir -p "$HOME/.ssh/config.d"

# ~/.kube
mkdir -p "$HOME/.kube"
ln -fvns "$DOTPATH/.kube/kubie.yaml" "$HOME/.kube/kubie.yaml"

# bin
mkdir -p ~/bin
find "$DOTPATH/bin/" -type f -perm 0755 -exec ln -fvns {} ~/bin/ \;
