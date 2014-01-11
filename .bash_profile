export PATH=/usr/local/bin:/usr/local/sbin:$PATH
export LANG=ja_JP.UTF-8
export LESSCHARSET=utf-8

alias ls='ls -G'
alias ll='ls -l'
alias la='ls -A'
alias rm='rm -i'
alias less='less -iM'

# alias devstart='sudo apachectl start & sudo mysql.server start'
# alias devstop='sudo apachectl stop & sudo mysql.server stop'

alias saying='while (true) do f=$(fortune); echo "$f"; echo ""; say "$f"; sleep 5; done'
# railsに必要
# eval "$(rbenv init -)"

if [ -e ~/.bashrc ]; then
    source .~/.bashrc
fi
