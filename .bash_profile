# vim: set filetype=sh :

export PATH=~/bin:/usr/local/bin:/usr/local/sbin:$PATH
export LANG=ja_JP.UTF-8
export LESSCHARSET=utf-8
export EDITOR=nvim
export HISTTIMEFORMAT='%y-%m-%d %H:%M:%S '
export HISTSIZE=5000
export ANSIBLE_COW_SELECTION=random
export XDG_CONFIG_HOME=~/.config
export PROMPT_COMMAND='echo -ne "\033]0;${PWD}\007"'

gcloudpath="$(dirname "$(dirname "$(readlink "$(command -v gcloud)")")")"
if [ -f "$gcloudpath/path.bash.inc" ]; then
    # shellcheck source=/dev/null
    source "$gcloudpath/path.bash.inc"
fi
if [ -f "$gcloudpath/completion.bash.inc" ]; then
    # shellcheck source=/dev/null
    source "$gcloudpath/completion.bash.inc"
fi

# shellcheck source=/dev/null
[[ -e ~/.bashrc ]] && . ~/.bashrc

ssh-add -K > /dev/null 2>&1 && status=$?
if [ $status != 0 ]; then
    echo "ERROR: 'ssh-add -K' failed!"
    exit 1
fi

