
# ls color options
if [ `uname | grep 'CYGWIN'` ]; then
    alias ls='ls --color'
else
    alias ls='ls -G'
fi

alias ll='ls -l'
alias la='ls -A'
alias rm='rm -i'
alias less='less -iM'
alias bye='exit'
alias hosts='sudo vim /etc/hosts'

alias ='echo "Stay hungly, stay foolish."'
alias saying='while (true) do f=$(fortune); echo "$f"; echo ""; say "$f"; sleep 5; done'
