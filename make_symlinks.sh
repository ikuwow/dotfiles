#!/bin/bash

if [ ! -e ~/dotfiles ]; then
    echo 'Error: directory "dotfiles" must be your home directory.'
    exit 1
fi

ln -s ~/dotfiles/.vim ~/.vim
ln -s ~/dotfiles/.vimrc ~/.vimrc
ln -s ~/dotfiles/.gvimrc ~/.gvimrc
ln -s ~/dotfiles/.bash_profile ~/.bash_profile
ln -s ~/dotfiles/.bashrc ~/.bashrc
