#!/bin/bash

# A shellscript that creates symlinks of dotfiles

if [ ! -e ~/dotfiles ]; then
    echo 'Error: A directory named "dotfiles" must be on your home directory.'
    exit 1
fi

RCFILES=(
    .vimrc .gvimrc .vim .bash_profile .bashrc .sshrc .sshrc.d
    .tmux.conf .eslintrc .gemrc .atom .inputrc .gitignore .gitconfig
)
for file in ${RCFILES[@]}; do
    ln -fhvs ~/dotfiles/$file ~/$file
done
ln -fhvs ~/dotfiles/.vimrc ~/.ideavimrc

# iCloud
mkdir -p ~/iCloudDrive
DIRS=(
  Keynote Numbers Pages Automator Notes
  Preview TextEdit QuickTimePlayerX ScriptEditor2
)
for dir in ${DIRS[@]}; do
    ln -fhvs ~/Library/Mobile\ Documents/com~apple~${dir}/Documents ~/iCloudDrive/${dir}
done
ln -fhvs ~/Library/Mobile\ Documents/com~apple~CloudDocs ~/iCloudDrive/CloUdDocs

if [ ! -e ~/.ssh/config ]; then
    ln -is ~/iCloudDrive/CloudDocs/ssh/config ~/.ssh/config
fi
if [ ! -e ~/.ssh/config.d ]; then
    ln -is ~/iCloudDrive/CloudDocs/ssh/config.d ~/.ssh/config.d
fi

mkdir -p ${XDG_CONFIG_HOME:=$HOME/.config}
ln -fhvs ~/.vim $XDG_CONFIG_HOME/nvim
ln -fhvs ~/Dropbox/dotconfig/karabiner $XDG_CONFIG_HOME/karabiner
