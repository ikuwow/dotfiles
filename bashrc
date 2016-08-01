## Aliases

alias ll='ls -l'
alias la='ls -A'
alias rm='rm -i'
alias less='less -iM'
alias tree='tree -NC'
alias grep='grep --color=auto'
alias bye='exit'
alias hosts='sudo vim /etc/hosts'
alias teratail='open https://teratail.com'

alias be='bundle exec'
alias vag='vagrant'

alias ='echo "Stay hungly, stay foolish."'
alias saying='while (true) do f=$(fortune); echo "$f"; echo ""; say "$f"; sleep 5; done'

if [ -f ~/bin/ssh-host-color ]; then
    alias ssh=~/bin/ssh-host-color
fi

function altgit {
    cmd=$1
    shift
    extra=""
    if [ "$cmd" == "clone" ]; then
        extra="--recursive"
    fi
    git $cmd $extra $@
}
alias git='altgit'

alias docker-quickstart="bash --login docker-quickstart.sh"

case `uname` in
    "CYGWIN" )
        alias ls='ls --color';;
    "Linux" )
        alias ls='ls --color';;
    "Darwin" )
        alias ls='ls -G'
        alias postgres='postgres -D /usr/local/var/postgres'

        commands=(awk sed)
        for c in ${commands[@]}; do
            if [ `type g$c > /dev/null 2>&1` ]; then
                alias $c=g$c
            fi
        done

        vimexec=(mvim mview)
        macvim=/Applications/MacVim.app/Contents/MacOS/
        for vimexec in ${vimexec[@]}; do
            if [ -e ${macvim}${vimexec} ]; then
                alias $vimexec=${macvim}${vimexec}
            fi
        done

        ;;
    * )
        # do nothing
esac

## Auto complete

complete -C aws_completer aws

if [ -f /usr/local/etc/bash_completion ]; then
    . /usr/local/etc/bash_completion
fi

if [ -n "$SSH_CLIENT" ]; then
    PS1="\[\e[36m\e[33m\][ssh]\[\e[0m\]${PS1}"
    # PS1="\[\e[36m\e[33m\]${PS1}\[\e[0m\]"
fi

if [ -n "$DOCKER_MACHINE_NAME" ]; then
    PS1="\[\e[36m\e[33m\][docker]\[\e[0m\]${PS1}"
fi

# ssh-agent start
# if [ ! -n "$SSH_AUTH_SOCK" ]; then
#     eval `ssh-agent -s`
#     ssh-add
# fi

if [ -f ~/.ssh-agent ]; then
    . ~/.ssh-agent > /dev/null
fi
if [ -z "$SSH_AGENT_PID" ] || ! kill -0 $SSH_AGENT_PID; then
    ssh-agent > ~/.ssh-agent
    . ~/.ssh-agent > /dev/null
fi
ssh-add -l >& /dev/null || ssh-add


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

