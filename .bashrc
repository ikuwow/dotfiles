# vim: filetype=sh :

if [ "${BASH_VERSINFO[0]}" -le 3 ]; then
    echo "WARNING: Your bash version is ${BASH_VERSINFO[0]}!"
    echo "Please use bash 4.0 ~ by these commands: (Mac)"
    echo "sudo bash -c 'echo /usr/local/bin/bash >> /etc/shells'"
    echo "chsh -s /usr/local/bin/bash"
fi

## Aliases
if [ "$(uname)" = Darwin ]; then
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
[[ "$(command -v hub)" ]] && eval "$(hub alias -s)"

command -v sshrc > /dev/null 2>&1 && alias ssh=sshrc

## Auto complete
complete -C aws_completer aws

BASH_COMPLETION_PATH=/usr/local/share/bash-completion/bash_completion
if [ "${BASH_VERSINFO[0]}" -ge 4 ] && [ -f "$BASH_COMPLETION_PATH" ]; then
    # shellcheck source=/dev/null
    . "$BASH_COMPLETION_PATH"
fi

bind "set completion-ignore-case on"

## Language Specific configs
export GOPATH=$HOME/.go

if [ "$(uname)" = Darwin ]; then
    java_version_file="$HOME/.java-version"
    java_version=1.8
    if [ -e "$java_version_file" ]; then
        java_version="$(cat "$java_version_file")"
    fi
    JAVA_HOME=$(/usr/libexec/java_home -v "$java_version")
    export JAVA_HOME
fi

## Functions
function prompts {

    local WHITE='\e[0m'
    local YELLOW='\e[33m'

    if [ ! -n "$SSH_CLIENT" ]; then
        PS1='\h: \W\$ '
    fi
    local OLDPS1="$PS1"
    PS1=${OLDPS1//\\\$/\\\[\\e\[33m\\\]$\\\[\\e\[0m\\\]}

    if [ -n "$SSH_CLIENT" ]; then
        if [ "$PS1" = "${PS1/ssh/}" ]; then
            PS1="${YELLOW}[ssh]${WHITE}${PS1}"
        fi
    fi
}

prompts

if [ "$(command -v networksetup)" ]; then
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
    if [ -z "$1" ]; then
        confname=$(gcloud config configurations list | awk 'NR>1' | peco | awk '{print $1}')
    else
        confname=$1
    fi
    gcloud config configurations activate "$confname"
}

fumpo () {
    if ! command -v slackcat > /dev/null 2>&1; then
        echo "Error: \`slackcat\` not found."
        return 1
    fi
    echo -n "$@" | slackcat -s
}
