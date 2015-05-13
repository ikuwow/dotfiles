
# ls color options
if [ `uname | grep 'CYGWIN'` ]; then
    alias ls='ls --color'
else
    alias ls='ls -G'
fi

if [ `uname | grep 'Linux'` ]; then
    alias ls='ls --color'
fi

# bash-completion
if [ `uname | grep Darwin` ]; then
    if [ -f `brew --prefix`/etc/bash_completion ]; then
        . `brew --prefix`/etc/bash_completion
    fi
fi

complete -C aws_completer aws

alias ll='ls -l'
alias la='ls -A'
alias rm='rm -i'
alias less='less -iM'
alias grep='grep --color=auto'
alias bye='exit'
alias hosts='sudo vim /etc/hosts'

alias be='bundle exec'
alias vag='vagrant'

alias ='echo "Stay hungly, stay foolish."'
alias saying='while (true) do f=$(fortune); echo "$f"; echo ""; say "$f"; sleep 5; done'


