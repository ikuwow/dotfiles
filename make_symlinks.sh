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
ICLOUD_DIR="$HOME/iCloudDrive"
mkdir -p "$ICLOUD_DIR"
DIRS=(
  Keynote Numbers Pages Automator Notes
  Preview TextEdit QuickTimePlayerX ScriptEditor2
)
for dir in "${DIRS[@]}"; do
    ln -fhvs "$HOME/Library/Mobile Documents/com~apple~${dir}/Documents" "${ICLOUD_DIR}/${dir}"
done
ln -fhvs "$HOME/Library/Mobile Documents/com~apple~CloudDocs" "${ICLOUD_DIR}/CloudDocs"

# ssh config
sshs=(config config.d)
for s in "${sshs[@]}"; do
    if [ ! -e "$HOME/.ssh/$s" ]; then
        ln -hvs "${ICLOUD_DIR}/CloudDocs/ssh/$s" "$HOME/.ssh/$s"
    fi
done

mkdir -p "${XDG_CONFIG_HOME:=$HOME/.config}"
ln -fhvs "$HOME/.vim" "$XDG_CONFIG_HOME/nvim"
ln -fhvs "${ICLOUD_DIR}/CloudDocs/dotconfig/karabiner" "$XDG_CONFIG_HOME/karabiner"
