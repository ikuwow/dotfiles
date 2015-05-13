
# Environment Variables
export PATH=~/bin:/usr/local/heroku/bin:/usr/local/bin:/usr/local/sbin:$PATH
export LANG=ja_JP.UTF-8
export LESSCHARSET=utf-8
export EDITOR=vim
export HOMEBREW_CASK_OPTS="--appdir=/Applications"

if [ -f ~/.brew_api_token ];then
    source ~/.brew_api_token
fi

# Rubyは全てrbenvで管理する（homebrewでは入れない）
# export PATH="$HOME/.rbenv/shims:$PATH"
if [ `uname | grep Darwin` ]; then
    eval "$(rbenv init -)"
fi

# git autocomplete
if [ -f ~/dotfiles/git-completion.bash ]; then
    . ~/dotfiles/git-completion.bash
fi

# load .bashrc
if [ -e ~/.bashrc ]; then
    source ~/.bashrc
fi

alias ='echo "Stay hungry, stay foolish."'
