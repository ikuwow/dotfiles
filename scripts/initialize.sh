#!/usr/bin/env bash

set -e

/usr/local/bin/pip3 install --upgrade pip
/usr/local/bin/pip3 install neovim

/usr/local/bin/pip2 install --upgrade pip
/usr/local/bin/pip2 install neovim

/usr/local/opt/ruby/bin/gem install neovim

/usr/local/bin/npm i -g neovim

KYRAT_PATH=~/.local/share/kyrat
mkdir -p "$(dirname ~/.local/share)"
if [ ! -d $KYRAT_PATH ]; then
    git clone git@github.com:fsquillace/kyrat.git $KYRAT_PATH
else
    cd $KYRAT_PATH
    git stash save
    git checkout master
    git pull origin master
fi
mkdir -p ~/bin
ln -fs "$KYRAT_PATH/bin/kyrat" ~/bin/kyrat
