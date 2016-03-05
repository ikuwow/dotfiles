
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

if [ `uname | grep Darwin` ]; then
    eval "$(rbenv init - --no-rehash)" # adding --no-rehash makes this faster
fi

# git autocomplete
if [ -f ~/dotfiles/git-completion.bash ]; then
    . ~/dotfiles/git-completion.bash
fi

# ssh completion
_complete_ssh_hosts ()
{
        COMPREPLY=()
        cur="${COMP_WORDS[COMP_CWORD]}"
        comp_ssh_hosts=`cat ~/.ssh/known_hosts | \
                        cut -f 1 -d ' ' | \
                        sed -e s/,.*//g | \
                        grep -v ^# | \
                        uniq | \
                        grep -v "\[" ;
                cat ~/.ssh/config | \
                        grep "^Host " | \
                        awk '{print $2}'
                `
        COMPREPLY=( $(compgen -W "${comp_ssh_hosts}" -- $cur))
        return 0
}
complete -F _complete_ssh_hosts ssh

# load .bashrc
if [ -e ~/.bashrc ]; then
    source ~/.bashrc
fi

