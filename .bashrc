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

ASDF_JAVA_WRAPPER="$HOME/.asdf/plugins/java/asdf-java-wrapper.bash"
# shellcheck source=/dev/null
[[ -e "$ASDF_JAVA_WRAPPER" ]] && . "$ASDF_JAVA_WRAPPER"

asdf_update_java_home() {
  command -v asdf >/dev/null || return

  local asdf_path
  if asdf_path="$(asdf where java 2>/dev/null)"; then
    JAVA_HOME="$asdf_path"
    export JAVA_HOME
  fi
}
asdf_update_java_home
