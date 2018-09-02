#!/bin/bash

# A shellscript that creates symlinks of dotfiles

if [ ! -e ~/dotfiles ]; then
    echo 'Error: A directory named "dotfiles" must be on your home directory.'
    exit 1
fi

RCFILES=(\
    vimrc gvimrc vim bash_profile bashrc sshrc sshrc.d tmux.conf eslintrc gemrc atom inputrc
)
for file in ${RCFILES[@]}; do
    if [ ! -e ~/.$file ]; then
        ln -is ~/dotfiles/$file ~/.$file
    fi
done

if [ ! -d ~/bin ]; then
    ln -is ~/dotfiles/bin ~/bin
fi

if [ ! -e ~/.gitconfig ]; then
    ln -is ~/dotfiles/.gitconfig ~/.gitconfig
fi

if [ ! -e ~/.gitignore ]; then
    ln -is ~/dotfiles/gitignore_global ~/.gitignore
fi

if [ ! -e ~/.ssh/config ]; then
    ln -is ~/iCloud\ Drive/CloudDocs/ssh/config ~/.ssh/config
fi
if [ ! -e ~/.ssh/config.d ]; then
    ln -is ~/iCloud\ Drive/CloudDocs/ssh/config.d ~/.ssh/config.d
fi
if [ ! -e ~/.ideavimrc ]; then
    ln -is ~/dotfiles/vimrc ~/.ideavimrc
fi

# NeoVim
mkdir -p ${XDG_CONFIG_HOME:=$HOME/.config}
if [ ! -d $XDG_CONFIG_HOME/nvim ]; then
    ln -is ~/.vim $XDG_CONFIG_HOME/nvim
fi
if [ ! -e $XDG_CONFIG_HOME/nvim/init.vim ]; then
    ln -is ~/.vimrc $XDG_CONFIG_HOME/nvim/init.vim
fi
