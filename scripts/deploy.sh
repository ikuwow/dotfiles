#!/usr/bin/env bash

DOTPATH="$HOME/dotfiles"

if [ ! -e "$DOTPATH" ]; then
    echo "Error: Directory $DOTPATH does not exist."
    exit 1
fi

cd "$DOTPATH" || exit 1

for file in .??*; do
    [[ "$file" = ".git" ]] && continue
    [[ "$file" = ".DS_Store" ]] && continue
    [[ "$file" = ".travis.yml" ]] && continue
    ln -fvns "$DOTPATH/$file" "$HOME/$file"
done

[[ -z $XDG_CONFIG_HOME ]] && XDG_CONFIG_HOME=$HOME/.config
mkdir -p "$XDG_CONFIG_HOME"

ln -fvns "$DOTPATH/.config/git" "$XDG_CONFIG_HOME/git"
ln -fvns "$HOME/.vim" "$XDG_CONFIG_HOME/nvim"

# kyrat
mkdir -p "$XDG_CONFIG_HOME/kyrat"
ln -fvns "$HOME/.bashrc" "$XDG_CONFIG_HOME/kyrat/bashrc"
ln -fvns "$HOME/.inputrc" "$XDG_CONFIG_HOME/kyrat/inputrc"
ln -fvns "$HOME/.vimrc" "$XDG_CONFIG_HOME/kyrat/vimrc"
ln -fvns "$HOME/.tmux.conf" "$XDG_CONFIG_HOME/kyrat/tmux.conf"

# bin
mkdir -p ~/bin
find "$DOTPATH/bin/" -type f -executable -exec ln -fvns {} ~/bin/ \;

# iCloud
ICLOUD_DIR="$HOME/iCloudDrive"
mkdir -p "$ICLOUD_DIR"
DIRS=(
  Keynote Numbers Pages Automator Notes
  Preview TextEdit QuickTimePlayerX ScriptEditor2
)
for dir in "${DIRS[@]}"; do
    ln -fvns "$HOME/Library/Mobile Documents/com~apple~${dir}/Documents" "${ICLOUD_DIR}/${dir}"
done
ln -fvns "$HOME/Library/Mobile Documents/com~apple~CloudDocs" "${ICLOUD_DIR}/CloudDocs"
