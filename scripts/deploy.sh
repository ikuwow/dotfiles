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

# bin
mkdir -p ~/bin
find "$DOTPATH/bin/" -type f -perm 0755 -exec ln -fvns {} ~/bin/ \;

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
