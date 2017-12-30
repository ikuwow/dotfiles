## Aliases

alias ll='ls -l'
alias la='ls -A'
alias rm='rm -i'
alias less='less -iM'
alias tree='tree -NC'
alias grep='grep --color=auto'
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

case `uname` in
    "CYGWIN" )
        alias ls='ls --color';;
    "Linux" )
        alias ls='ls --color';;
    "Darwin" )
        bind "set completion-ignore-case on";;
    * )
        # do nothing
esac

## Auto complete

complete -C aws_completer aws

[ -f /usr/local/etc/bash_completion ] && . /usr/local/etc/bash_completion

function prompts {
    local WHITE="\[\e[0m\]"
    local YELLOW="\[\e[33m\]"

    if [ ! -n "$SSH_CLIENT" ]; then
        PS1='\h: \W\$ '
    fi
    local OLDPS1="$PS1"
    PS1=$(echo "$OLDPS1" | sed -e 's/\\\$/\\\[\\e\[33m\\\]$\\\[\\e\[0m\\\]/')

    if [ -n "$SSH_CLIENT" ]; then
        if [[ $PS1 != *"ssh"* ]]; then
            PS1="$YELLOW[ssh]$WHITE$PS1"
        fi
    fi
}

prompts

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

gclconf ()
{
    if [ -z $1 ]; then
        confname=$(gcloud config configurations list | awk 'NR>1' | peco | awk '{print $1}')
    else
        confname=$1
    fi
    gcloud config configurations activate $confname
}

alias fumpo='slack-cli -d times_ikuwow'
