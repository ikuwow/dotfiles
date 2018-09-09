#!/bin/bash

mkdir -p ~/iCloud\ Drive

DIRS=(
  Keynote Numbers Pages Automator Notes
  Preview TextEdit QuickTimePlayerX ScriptEditor2
)
for dir in ${DIRS[@]}; do
    ln -Ffhvs ~/Library/Mobile\ Documents/com~apple~${dir}/Documents ~/iCloud\ Drive/${dir}
done

ln -Ffhvs ~/Library/Mobile\ Documents/com~apple~CloudDocs ~/iCloud\ Drive/CloudDocs
