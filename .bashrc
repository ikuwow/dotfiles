# shellcheck disable=SC2148
# vim: filetype=sh :

# shellcheck disable=SC1091
[[ -f /etc/bashrc ]] && . /etc/bashrc

# Completions
if [ -n "${BREW_PREFIX:-}" ]; then
  BASH_COMPLETION="$BREW_PREFIX/etc/profile.d/bash_completion.sh"
  [[ -r "$BASH_COMPLETION" ]] && . "$BASH_COMPLETION"
elif [ -f /usr/share/bash-completion/bash_completion ]; then
  . /usr/share/bash-completion/bash_completion
fi
[[ $(command -v fzf) ]] && eval "$(fzf --bash 2>/dev/null)"
[[ $(command -v akamai) ]] && eval "$(akamai --bash)"

## Language Specific configs

[[ $(command -v direnv) ]] && eval "$(direnv hook bash)"
