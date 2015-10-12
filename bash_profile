
# Environment Variables
export PATH=~/bin:/usr/local/heroku/bin:/usr/local/bin:/usr/local/sbin:$PATH
export LANG=ja_JP.UTF-8
export LESSCHARSET=utf-8
export EDITOR=vim
export HOMEBREW_CASK_OPTS="--appdir=/Applications"
export HISTTIMEFORMAT='%y-%m-%d %H:%M:%S '
export HISTSIZE=3000

if [ `hostname` = 'teratail.com' ];then
    export PS1="\e[1;31m${PS1}\e[m"
fi

if [ -f ~/.brew_api_token ];then
    source ~/.brew_api_token
fi

if [ `uname | grep Darwin` ]; then
    eval "$(rbenv init - --no-rehash)"
    # adding --no-rehash makes this faster
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
