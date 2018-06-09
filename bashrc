# vim: filetype=sh :

## Aliases
alias ls='ls --color'
alias ll='ls -l'
alias la='ls -A'
alias rm='rm -i'
alias less='less -iM'
alias tree='tree -NC'
alias grep='grep --color=auto'
alias man='LANG=C man'
alias bye='exit'

alias be='bundle exec'
alias de='docker exec'
alias ke='kubectl exec'
alias vag='vagrant'
alias gccg='gcloud container clusters get-credentials'
alias wkc='watch -n 5 kubectl get po -o wide'
alias dr='docker run -it --rm'
alias drv='docker run -it --rm -w /tmp -v $(pwd):/tmp'
alias mysql='mysql --pager="less -S -n -i -F -X"'

alias ='echo "Stay hungly, stay foolish."'

if [ -f ~/bin/ssh-host-color ]; then
    alias ssh=~/bin/ssh-host-color
fi

## Auto complete

complete -C aws_completer aws

if [ "${BASH_VERSINFO}" -ge 4 ] && [ -f /usr/local/share/bash-completion/bash_completion ]; then
  . /usr/local/share/bash-completion/bash_completion
fi

function prompts {
    local WHITE="\[\e[0m\]"
    local YELLOW="\[\e[33m\]"

    if [ ! -n "$SSH_CLIENT" ]; then
        PS1='\h: \W\$ '
    fi
    local OLDPS1="$PS1"
    PS1=$(echo "$OLDPS1" | sed -e 's/\\\$/\\\[\\e\[33m\\\]$\\\[\\e\[0m\\\]/')

    if [ -n "$SSH_CLIENT" ]; then
        if [ "$PS1" = "${PS1/ssh/}" ]; then
            PS1="$YELLOW[ssh]$WHITE$PS1"
        fi
    fi
}

prompts

gclconf ()
{
    if [ -z $1 ]; then
        confname=$(gcloud config configurations list | awk 'NR>1' | peco | awk '{print $1}')
    else
        confname=$1
    fi
    gcloud config configurations activate $confname
}

fumpo ()
{
    eval "slack chat send '$@' '#times_ikuwow'" 1> /dev/null
    if [ $? != 0 ]; then
        echo 'Error: exiting'
        return 1
    fi
}
