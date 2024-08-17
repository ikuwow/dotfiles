#!/usr/bin/env bash

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
