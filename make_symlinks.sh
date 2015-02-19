#!/bin/bash

# dotfilesのシンボリックリンクを作成するスクリプト
# A shellscript that creates symlinks of dotfiles

if [ ! -e ~/dotfiles ]; then
    echo 'Error: A directory named "dotfiles" must be on your home directory.'
    exit 1
fi

if [ ! -L ~/Library/Application\ Support/Karabiner/private.xml ]; then
    ln -is ~/dotfiles/karabiner_private.xml ~/Library/Application\ Support/Karabiner/private.xml
fi

if [ -d ~/.matlab/ -a ! -L ~/.matlab/R2014b/mexopts.sh ]; then
    ln -is ~/dotfiles/mexopts.sh ~/.matlab/R2014b/mexopts.sh
fi


