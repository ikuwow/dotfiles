#!/bin/bash

# dotfilesのシンボリックリンクを作成するスクリプト
# A shellscript that creates symlinks of dotfiles

if [ ! -e ~/dotfiles ]; then
    echo 'Error: A directory named "dotfiles" must be on your home directory.'
    exit 1
fi

# TODO: リンク先もチェックする

if [ ! -L ~/.vim ]; then
    ln -ins ~/dotfiles/vim/ ~/.vim
fi

if [ ! -L ~/.vimrc ]; then
    ln -is ~/dotfiles/vimrc ~/.vimrc
fi

if [ ! -L ~/.gvimrc ]; then
    ln -is ~/dotfiles/gvimrc ~/.gvimrc
fi

if [ ! -L ~/.bash_profile ]; then
    ln -is ~/dotfiles/bash_profile ~/.bash_profile
fi

if [ ! -L ~/.bashrc ]; then
    ln -is ~/dotfiles/bashrc ~/.bashrc
fi

if [ ! -L ~/.gitignore ]; then
    ln -is ~/dotfiles/gitignore_global ~/.gitignore
fi

if [ ! -L ~/.gitconfig ]; then
    ln -is ~/dotfiles/.gitconfig ~/.gitconfig
fi

if [ ! -L ~/bin ]; then
    ln -ins ~/dotfiles/bin/ ~/bin
fi

if [ ! -L ~/Library/Application\ Support/Karabiner/private.xml ]; then
    ln -is ~/dotfiles/karabiner_private.xml ~/Library/Application\ Support/Karabiner/private.xml
fi

if [ -d ~/.matlab/ -a ! -L ~/.matlab/R2014b/mexopts.sh ]; then
    ln -is ~/dotfiles/mexopts.sh ~/.matlab/R2014b/mexopts.sh
fi


