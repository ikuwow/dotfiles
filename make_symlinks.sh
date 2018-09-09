#!/bin/bash

# A shellscript that creates symlinks of dotfiles

if [ ! -e ~/dotfiles ]; then
    echo 'Error: A directory named "dotfiles" must be on your home directory.'
    exit 1
fi

RCFILES=(\
    .vimrc .gvimrc .vim .bash_profile .bashrc .macrc .sshrc .sshrc.d .tmux.conf .eslintrc .gemrc .atom .inputrc .gitignore
)
for file in ${RCFILES[@]}; do
    if [ ! -e ~/$file ]; then
        ln -is ~/dotfiles/$file ~/$file
    fi
done

if [ ! -e ~/.gitconfig ]; then
    ln -is ~/dotfiles/.gitconfig ~/.gitconfig
fi

# iCloud
mkdir -p ~/iCloud\ Drive

DIRS=(
  Keynote Numbers Pages Automator Notes
  Preview TextEdit QuickTimePlayerX ScriptEditor2
)
for dir in ${DIRS[@]}; do
    ln -Ffhvs ~/Library/Mobile\ Documents/com~apple~${dir}/Documents ~/iCloud\ Drive/${dir}
done

ln -Ffhvs ~/Library/Mobile\ Documents/com~apple~CloudDocs ~/iCloud\ Drive/CloudDocs

if [ ! -e ~/.ssh/config ]; then
    ln -is ~/iCloud\ Drive/CloudDocs/ssh/config ~/.ssh/config
fi
if [ ! -e ~/.ssh/config.d ]; then
    ln -is ~/iCloud\ Drive/CloudDocs/ssh/config.d ~/.ssh/config.d
fi
if [ ! -e ~/.ideavimrc ]; then
    ln -is ~/dotfiles/.vimrc ~/.ideavimrc
fi

mkdir -p ${XDG_CONFIG_HOME:=$HOME/.config}

# NeoVim
if [ ! -d $XDG_CONFIG_HOME/nvim ]; then
    ln -is ~/.vim $XDG_CONFIG_HOME/nvim
fi
if [ ! -e $XDG_CONFIG_HOME/nvim/init.vim ]; then
    ln -is ~/.vimrc $XDG_CONFIG_HOME/nvim/init.vim
fi

# Karabiner Elements
if [ ! -e $XDG_CONFIG_HOME/karabiner ]; then
    ln -ihs ~/Dropbox/dotconfig/karabiner $XDG_CONFIG_HOME/karabiner
fi

