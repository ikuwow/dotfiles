
# ls color options
if [ `uname | grep 'CYGWIN'` ]; then
    alias ls='ls --color'
else
    alias ls='ls -G'
fi

if [ `uname | grep 'Linux'` ]; then
    alias ls='ls --color'
fi

## It's slow, so removed temporary
# bash-completion
# if [ `uname | grep Darwin` ]; then
#     BREW_PREFIX=`brew --prefix`
#     if [ -f ${BREW_PREFIX}/etc/bash_completion ]; then
#         . ${BREW_PREFIX}/etc/bash_completion
#         # TODO: it's slow.
#     fi
# fi

complete -C aws_completer aws

alias ll='ls -l'
alias la='ls -A'
alias rm='rm -i'
alias less='less -iM'
alias grep='grep --color=auto'
alias bye='exit'
alias hosts='sudo vim /etc/hosts'
alias teratail='open https://teratail.com'

alias be='bundle exec'
alias vag='vagrant'

alias ='echo "Stay hungly, stay foolish."'
alias saying='while (true) do f=$(fortune); echo "$f"; echo ""; say "$f"; sleep 5; done'

alias ssh=~/bin/ssh-host-color

alias docker-quickstart="bash --login '/Applications/Docker/Docker Quickstart Terminal.app/Contents/Resources/Scripts/start.sh'"
