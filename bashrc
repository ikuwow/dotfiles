
# ls color options
if [ `uname | grep 'CYGWIN'` ]; then
    alias ls='ls --color'
else
    alias ls='ls -G'
fi

# bash-completion
if [ -f `brew --prefix`/etc/bash_completion ]; then
    . `brew --prefix`/etc/bash_completion
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

alias ='echo "Stay hungly, stay foolish."'
alias saying='while (true) do f=$(fortune); echo "$f"; echo ""; say "$f"; sleep 5; done'


