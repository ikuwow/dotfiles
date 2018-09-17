#!/bin/bash

# A shellscript that creates symlinks of dotfiles

if [ ! -e ~/dotfiles ]; then
    echo 'Error: A directory named "dotfiles" must be on your home directory.'
    exit 1
fi

for file in .??*; do
    [[ "$file" = ".git" ]] && continue
    [[ "$file" = ".DS_Store" ]] && continue
    [[ "$file" = ".travis.yml" ]] && continue
    ln -fhvs "$HOME/dotfiles/$file" "$HOME/$file"
done

ln -fhvs ~/dotfiles/.vimrc ~/.ideavimrc

# iCloud
mkdir -p ~/iCloudDrive
DIRS=(
  Keynote Numbers Pages Automator Notes
  Preview TextEdit QuickTimePlayerX ScriptEditor2
)
for dir in "${DIRS[@]}"; do
    ln -fhvs "$HOME/Library/Mobile Documents/com~apple~${dir}/Documents" "$HOME/iCloudDrive/${dir}"
done
ln -fhvs "$HOME/Library/Mobile Documents/com~apple~CloudDocs" ~/iCloudDrive/CloudDocs

if [ ! -e ~/.ssh/config ]; then
    ln -is ~/iCloudDrive/CloudDocs/ssh/config ~/.ssh/config
fi
if [ ! -e ~/.ssh/config.d ]; then
    ln -is ~/iCloudDrive/CloudDocs/ssh/config.d ~/.ssh/config.d
fi

mkdir -p "${XDG_CONFIG_HOME:=$HOME/.config}"
ln -fhvs "$HOME/.vim" "$XDG_CONFIG_HOME/nvim"
ln -fhvs "$HOME/Dropbox/dotconfig/karabiner" "$XDG_CONFIG_HOME/karabiner"
