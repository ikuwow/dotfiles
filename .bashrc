# shellcheck disable=SC2148
# vim: filetype=sh :

if [ "${BASH_VERSINFO[0]}" -le 3 ]; then
  echo "WARNING: Your bash version is ${BASH_VERSINFO[0]}!"
  echo "Please use bash 4.0 ~ by these commands: (Mac)"
  echo "sudo bash -c 'echo /usr/local/bin/bash >> /etc/shells'"
  echo "chsh -s /usr/local/bin/bash"
fi

# shellcheck disable=SC1091
[[ -f /etc/bashrc ]] && . /etc/bashrc

## Auto complete
complete -C aws_completer aws

BASH_COMPLETION="/usr/local/etc/profile.d/bash_completion.sh"
# shellcheck disable=SC1090
[[ -r "$BASH_COMPLETION" ]] && . "$BASH_COMPLETION"

## Language Specific configs
export GOPATH=$HOME/.go
[[ -f ~/.asdf/plugions/java/set-java-home.bash ]] && . ~/.asdf/plugions/java/set-java-home.bash
