# shellcheck disable=SC2148
# vim: filetype=sh :

if [ "${BASH_VERSINFO[0]}" -le 3 ]; then
  echo "WARNING: Your bash version is ${BASH_VERSINFO[0]}!"
  echo "Please use bash 4.0~"
fi

# shellcheck disable=SC1091
[[ -f /etc/bashrc ]] && . /etc/bashrc

# Completions
BASH_COMPLETION="$BREW_PREFIX/etc/profile.d/bash_completion.sh"
[[ -r "$BASH_COMPLETION" ]] && . "$BASH_COMPLETION"
[[ $(command -v fzf) ]] && eval "$(fzf --bash)"
[[ $(command -v akamai) ]] && eval "$(akamai --bash)"

## Language Specific configs
export GOPATH=$HOME/.go
# https://github.com/asdf-community/asdf-golang?tab=readme-ov-file#version-selection
export ASDF_GOLANG_MOD_VERSION_ENABLED="true"

set_java_home_bash="$HOME/.asdf/plugins/java/set-java-home.bash"
[[ -f "$set_java_home_bash" ]] && . "$set_java_home_bash"

