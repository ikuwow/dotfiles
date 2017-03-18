#!/bin/bash

# A shellscript that creates symlinks of dotfiles

if [ ! -e ~/dotfiles ]; then
    echo 'Error: A directory named "dotfiles" must be on your home directory.'
    exit 1
fi

RCFILES=(\
    vimrc gvimrc vim bash_profile bashrc sshrc sshrc.d tmux.conf jshintrc gemrc
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

if [ ! -e ~/bin/trash ]; then
    ln -is ~/dotfiles/submodules/trash/trash ~/bin/trash
fi

