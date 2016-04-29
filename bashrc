## Aliases

alias ll='ls -l'
alias la='ls -A'
alias rm='rm -i'
alias less='less -iM'
alias tree='tree -F'
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

alias docker-quickstart="bash --login '/Applications/Docker/Docker Quickstart Terminal.app/Contents/Resources/Scripts/start.sh'"

case `uname` in
    "CYGWIN" )
        alias ls='ls --color';;
    "Linux" )
        alias ls='ls --color';;
    "Darwin" )
        alias ls='ls -G'
        alias postgres='postgres -D /usr/local/var/postgres';;
    * )
        # do nothing
esac

## Auto complete

complete -C aws_completer aws

if [ -f ~/dotfiles/git-completion.bash ]; then
    . ~/dotfiles/git-completion.bash
fi

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

