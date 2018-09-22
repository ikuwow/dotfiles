# vim: set filetype=sh :

export PATH=~/bin:/usr/local/bin:/usr/local/sbin:$PATH
export LANG=en_US.UTF-8
export LESSCHARSET=utf-8
export EDITOR=nvim
export HISTTIMEFORMAT='%y-%m-%d %H:%M:%S '
export HISTSIZE=5000
export XDG_CONFIG_HOME=~/.config
export PROMPT_COMMAND='echo -ne "\033]0;${PWD}\007"'

if [ "$(command -v gcloud)" ]; then
    gcloudpath="$(dirname "$(dirname "$(readlink "$(command -v gcloud)")")")"
    # shellcheck source=/dev/null
    [[ -f "$gcloudpath/path.bash.inc" ]] && . "$gcloudpath/path.bash.inc"
    # shellcheck source=/dev/null
    [[ -f "$gcloudpath/completion.bash.inc" ]] && . "$gcloudpath/completion.bash.inc"
fi

[[ -f ~/.ssh/id_rsa ]] && ssh-add -K 2> /dev/null

# shellcheck source=/dev/null
[[ -f ~/.brew_api_token ]] && . ~/.brew_api_token

# shellcheck source=/dev/null
[[ -f ~/.bashrc ]] && . ~/.bashrc
