# shellcheck disable=SC2148
# vim: filetype=sh :

if [ "${BASH_VERSINFO[0]}" -le 3 ]; then
  echo "WARNING: Your bash version is ${BASH_VERSINFO[0]}!"
  echo "Please use bash 4.0~"
fi

# shellcheck disable=SC1091
[[ -f /etc/bashrc ]] && . /etc/bashrc

# Completions
if [ -n "${BREW_PREFIX:-}" ]; then
  BASH_COMPLETION="$BREW_PREFIX/etc/profile.d/bash_completion.sh"
  [[ -r "$BASH_COMPLETION" ]] && . "$BASH_COMPLETION"
elif [ -f /usr/share/bash-completion/bash_completion ]; then
  . /usr/share/bash-completion/bash_completion
fi
[[ $(command -v fzf) ]] && eval "$(fzf --bash)"
[[ $(command -v akamai) ]] && eval "$(akamai --bash)"

## Language Specific configs

[[ $(command -v direnv) ]] && eval "$(direnv hook bash)"
