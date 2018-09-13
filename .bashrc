# vim: filetype=sh :

if [ $BASH_VERSINFO -le 3 ]; then
    echo "WARNING: Your bash version is ${BASH_VERSINFO}!"
    echo "Please use bash 4.0 ~ by these commands: (Mac)"
    echo "sudo bash -c 'echo /usr/local/bin/bash >> /etc/shells'"
    echo "chsh -s /usr/local/bin/bash"
fi

## Aliases
if [ $(uname) = Darwin ]; then
    alias ls='ls -G'
else
    alias ls='ls --color'
fi
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

if [ $(uname) = Darwin ]; then
    commands=(awk sed)
    for c in ${commands[@]}; do
        if $(type g$c > /dev/null 2>&1); then
            alias $c=g$c
        fi
    done
fi

command -v sshrc > /dev/null 2>&1 && alias ssh=sshrc

## Auto complete
complete -C aws_completer aws

if [ "${BASH_VERSINFO}" -ge 4 ] && [ -f /usr/local/share/bash-completion/bash_completion ]; then
  . /usr/local/share/bash-completion/bash_completion
fi

## Homebrew
if [ -f ~/.brew_api_token ];then
    source ~/.brew_api_token
fi

bind "set completion-ignore-case on"

## Language Specific configs
export GOPATH=$HOME/.go

if [ -e $HOME/.java_version ]; then
    java_version=$(cat $HOME/.java_version)
else
    java_version=1.8
fi
export JAVA_HOME=$(/usr/libexec/java_home -v $java_version)

## Functions
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

if [ $(command -v networksetup) ]; then
    function wifireset {
        interface='en0'
        networksetup -setairportpower "$interface" off
        echo 'Re-enabling Wi-Fi...'
        networksetup -setairportpower "$interface" on
        echo 'Done.'
    }
fi

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
