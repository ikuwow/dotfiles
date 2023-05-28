# shellcheck disable=SC2148
# vim: filetype=sh :

if [ "${BASH_VERSINFO[0]}" -le 3 ]; then
  echo "WARNING: Your bash version is ${BASH_VERSINFO[0]}!"
  echo "Please use bash 4.0~"
fi

# shellcheck disable=SC1091
[[ -f /etc/bashrc ]] && . /etc/bashrc

BASH_COMPLETION="$BREW_PREFIX/etc/profile.d/bash_completion.sh"
# shellcheck disable=SC1090
[[ -r "$BASH_COMPLETION" ]] && . "$BASH_COMPLETION"

## Language Specific configs
export GOPATH=$HOME/.go
# shellcheck disable=SC1090
[[ -f ~/.asdf/plugions/java/set-java-home.bash ]] && . ~/.asdf/plugions/java/set-java-home.bash

# shellcheck disable=SC1090
fzf_bash="$HOME/.fzf.bash"
if [ -f "$fzf_bash" ]; then
  # shellcheck disable=SC1090
  . "$fzf_bash"
else
  echo "WARNING: ${fzf_bash} is not installed. See: 'brew info fzf'"
fi

# shellcheck disable=SC1090
[[ $(command -v akamai) ]] && eval "$(akamai --bash)"
