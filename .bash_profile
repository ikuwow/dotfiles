# vim: set filetype=sh :

PATH="$HOME/bin:/usr/local/opt/ruby/bin:/usr/local/bin:/usr/local/sbin:$PATH"
PATH="$(brew --prefix coreutils)/libexec/gnubin:$PATH"
export PATH

export MANPATH="/usr/local/opt/coreutils/libexec/gnuman:$MANPATH"
export LANG=en_US.UTF-8
export LESSCHARSET=utf-8
export EDITOR=nvim
export HISTTIMEFORMAT='%y-%m-%d %H:%M:%S '
export HISTSIZE=5000
export XDG_CONFIG_HOME=~/.config
export PROMPT_COMMAND='echo -ne "\033]0;${PWD}\007"'
export HOMEBREW_INSTALL_CLEANUP=1 # default behaviour from homebrew 2.0.0

if [ "$(command -v gcloud)" ]; then
    gcloudpath="$(dirname "$(dirname "$(readlink "$(command -v gcloud)")")")"
    # shellcheck source=/dev/null
    [[ -f "$gcloudpath/path.bash.inc" ]] && . "$gcloudpath/path.bash.inc"
    # shellcheck source=/dev/null
    [[ -f "$gcloudpath/completion.bash.inc" ]] && . "$gcloudpath/completion.bash.inc"
fi

secretkeys="$(find ~/.ssh -name id_rsa)"
for secretkey in $secretkeys; do
    ssh-add -K "$secretkey" 2> /dev/null
done

# shellcheck source=/dev/null
[[ -f ~/.brew_api_token ]] && . ~/.brew_api_token

# shellcheck source=/dev/null
[[ -f ~/.bashrc ]] && . ~/.bashrc
