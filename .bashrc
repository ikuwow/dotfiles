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

if [ "${BASH_VERSINFO[0]}" -ge 4 ]; then
  export BASH_COMPLETION_COMPAT_DIR="/usr/local/etc/bash_completion.d"
  BASH_COMPLETION_PATH=/usr/local/etc/profile.d/bash_completion.sh
  # shellcheck source=/dev/null
  [[ -f "$BASH_COMPLETION_PATH" ]] && . "$BASH_COMPLETION_PATH"
fi

## Language Specific configs
export GOPATH=$HOME/.go

# shellcheck disable=SC2155
[[ "$(command -v /usr/libexec/java_home)" ]] && export JAVA_HOME=$(/usr/libexec/java_home -v 1.8)
# DO NOT USE asdf FOR Java
