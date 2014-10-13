#!/bin/bash

# dotfilesのシンボリックリンクを作成するスクリプト
# A shellscript that creates symlinks of dotfiles

if [ ! -e ~/dotfiles ]; then
    echo 'Error: A directory named "dotfiles" must be on your home directory.'
    exit 1
fi

ln -ins ~/dotfiles/.vim/ ~/.vim
ln -is ~/dotfiles/.vimrc ~/.vimrc
ln -is ~/dotfiles/.gvimrc ~/.gvimrc
ln -is ~/dotfiles/.bash_profile ~/.bash_profile
ln -is ~/dotfiles/.bashrc ~/.bashrc
ln -is ~/dotfiles/.gitignore ~/.gitignore
ln -is ~/dotfiles/.gitconfig ~/.gitconfig
ln -ins ~/dotfiles/bin/ ~/bin
ln -is ~/dotfiles/mexopts.sh ~/.matlab/R2013a/
