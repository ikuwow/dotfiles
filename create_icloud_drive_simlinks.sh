#!/bin/bash

# if [ ! -e ~/iCloud\ Drive ]; then
    mkdir ~/iCloud\ Drive
# else
    # echo "\"~/iCloud Drive\" directory already exists."
# fi

iWorks="Keynote Numbers Pages"
other="Automator Notes Preview TextEdit QuickTimePlayerX ScriptEditor2"

for dir in $iWorks $other; do
    ln -ns ~/Library/Mobile\ Documents/com~apple~${dir}/Documents \
        ~/iCloud\ Drive/${dir}
done

ln -ns ~/Library/Mobile\ Documents/com~apple~CloudDocs ~/iCloud\ Drive/CloudDocs
