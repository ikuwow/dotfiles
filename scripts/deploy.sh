#!/usr/bin/env bash

DOTPATH="$HOME/dotfiles"

if [ ! -e "$DOTPATH" ]; then
  echo "Error: Directory $DOTPATH does not exist."
  exit 1
fi

cd "$DOTPATH" || exit 1

if [[ -z $XDG_CONFIG_HOME ]]; then
  XDG_CONFIG_HOME=$HOME/.config
fi

# Whitelist of dotfiles to symlink
DOTFILES=(
  ".aliases"
  ".asdfrc"
  ".bash_profile"
  ".bashrc"
  ".default-gems"
  ".default-npm-packages"
  ".default-python-packages"
  ".functions"
  ".gemrc"
  ".gvimrc"
  ".ideavimrc"
  ".inputrc"
  ".npmrc"
  ".shellcheckrc"
  ".sshrc"
  ".terraformrc"
  ".tmux.conf"
  ".tool-versions"
  ".vimrc"
)

for file in "${DOTFILES[@]}"; do
  if [[ -e "$DOTPATH/$file" ]]; then
    ln -fvns "$DOTPATH/$file" "$HOME/$file"
  else
    echo "Warning: $file not found in $DOTPATH"
  fi
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

# iCloud
ICLOUD_DIR="$HOME/Library/Mobile Documents/com~apple~CloudDocs"
if [[ -d "$ICLOUD_DIR" ]]; then
  ln -fvns "$ICLOUD_DIR" "$HOME/iCloudDrive"
fi
echo

# Claude Code user settings
if [[ ! -d "$HOME/.claude" ]]; then
  ln -fvns "$DOTPATH/claude-user-config" "$HOME/.claude"
else
  echo "Note: ~/.claude already exists, skipping claude-user-config symlink"
fi
