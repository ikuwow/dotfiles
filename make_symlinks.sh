#!/bin/bash

# A shellscript that creates symlinks of dotfiles

if [ ! -e ~/dotfiles ]; then
    echo 'Error: A directory named "dotfiles" must be on your home directory.'
    exit 1
fi


if [ ! -e ~/.vimrc ]; then
    ln -is ~/dotfiles/vimrc ~/.vimrc
fi

if [ ! -e ~/.bash_profile ]; then
    ln -is ~/dotfiles/bash_profile ~/.bash_profile
fi

if [ ! -e ~/.bashrc ]; then
    ln -is ~/dotfiles/bashrc ~/.bashrc
fi

if [ ! -e ~/.vim ]; then
    ln -is ~/dotfiles/vim ~/.vim
fi

if [ ! -e ~/.gvimrc ]; then
    ln -is ~/dotfiles/gvimrc ~/.gvimrc
fi

if [ ! -e ~/.sshrc ]; then
    ln -is ~/dotfiles/sshrc ~/.sshrc
fi

if [ ! -e ~/.sshrc.d ]; then
    ln -is ~/dotfiles/sshrc.d ~/.sshrc.d
fi

if [ ! -e ~/.tmux.conf ]; then
    ln -is ~/dotfiles/tmux.conf ~/.tmux.conf
fi

if [ ! -d ~/bin ]; then
    ln -is ~/dotfiles/bin ~/bin
fi

if [ ! -e ~/.gitconfig ]; then
    ln -is ~/dotfiles/.gitconfig ~/.gitconfig
fi

if [ ! -e ~/.gitignore ]; then
    ln -is ~/dotfiles/gitignore_global ~/.gitignore
fi

if [ ! -e ~/bin/trash ]; then
    ln -is ~/dotfiles/submodules/trash/trash ~/bin/trash
fi

if [ ! -e ~/.jshintrc ]; then
    ln -is ~/dotfiles/jshintrc ~/.jshintrc
fi

