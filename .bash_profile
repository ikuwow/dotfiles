# vim: set filetype=sh :

PATH="$HOME/bin:/usr/local/opt/ruby/bin:/usr/local/bin:/usr/local/sbin:$PATH"

PATH="/usr/local/opt/coreutils/libexec/gnubin:$PATH"
PATH="/usr/local/opt/binutils/bin:$PATH"
PATH="/usr/local/opt/findutils/libexec/gnubin:$PATH"
PATH="/usr/local/opt/gnu-sed/libexec/gnubin:$PATH"
export PATH

MANPATH="/usr/local/opt/coreutils/libexec/gnuman:$MANPATH"
MANPATH="/usr/local/opt/binutils/share/man:$MANPATH"
MANPATH="/usr/local/opt/findutils/libexec/gnubin:$MANPATH"
MANPATH="/usr/local/opt/gnu-sed/libexec/gnuman:$MANPATH"
export MANPATH

export LANG=en_US.UTF-8
export LESSCHARSET=utf-8
export EDITOR=nvim
export HISTTIMEFORMAT='%y-%m-%d %H:%M:%S '
export HISTSIZE=5000
export XDG_CONFIG_HOME=~/.config
export PROMPT_COMMAND='echo -ne "\033]0;${PWD}\007"'
export QUOTING_STYLE=literal # for GNU ls

asdfini=/usr/local/opt/asdf/asdf.sh
if [ -e "$asdfini" ]; then
    # shellcheck source=/dev/null
    . "$asdfini"
fi

if [ "$(command -v gcloud)" ]; then
    gcloudpath="$(dirname "$(dirname "$(readlink "$(command -v gcloud)")")")"
    # shellcheck source=/dev/null
    [[ -f "$gcloudpath/path.bash.inc" ]] && . "$gcloudpath/path.bash.inc"
    # shellcheck source=/dev/null
    [[ -f "$gcloudpath/completion.bash.inc" ]] && . "$gcloudpath/completion.bash.inc"
fi

if [ -z "$SSH_CLIENT" ]; then
    secretkeys="$(find ~/.ssh -name id_rsa)"
    for secretkey in $secretkeys; do
        ssh-add -K "$secretkey" 2> /dev/null
    done
fi

# shellcheck source=/dev/null
[[ -f ~/.brew_api_token ]] && . ~/.brew_api_token

# shellcheck source=/dev/null
[[ -f ~/.bashrc ]] && . ~/.bashrc
