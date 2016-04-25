
# Environment Variables
export PATH=~/bin:/usr/local/heroku/bin:/usr/local/bin:/usr/local/sbin:$PATH
export LANG=ja_JP.UTF-8
export LESSCHARSET=utf-8
export EDITOR=vim
export HOMEBREW_CASK_OPTS="--appdir=/Applications"
export HISTTIMEFORMAT='%y-%m-%d %H:%M:%S '
export HISTSIZE=3000
export ANSIBLE_COW_SELECTION=random
export PGDATA=/usr/local/var/postgres

if [ `hostname` = 'teratail.com' ];then
    export PS1="\e[1;31m${PS1}\e[m"
fi

if [ -f ~/.brew_api_token ];then
    source ~/.brew_api_token
fi

if [ `which rbenv` ]; then
    eval "$(rbenv init - --no-rehash)" # adding --no-rehash makes this faster
fi

if [ `which pyenv` ]; then
    eval "$(pyenv init - --no-rehash)" # adding --no-rehash makes this faster
fi

## load .bashrc
if [ -e ~/.bashrc ]; then
    source ~/.bashrc
fi
