#!/usr/bin/env bash

# vim: set filetype=sh :

# shellcheck source=/dev/null

ARCH="$(arch)"
if [ "$ARCH" = "arm64" ]; then
  BREW_PREFIX="/opt/homebrew"
elif [ "$ARCH" = "i386" ]; then
  BREW_PREFIX="/usr/local"
fi
export BREW_PREFIX

# It sets envvars below
# - HOMEBREW_PREFIX
# - HOMEBREW_CELLAR
# - HOMEBREW_REPOSITORY
# - PATH
# - MANPAHT
# - INFOPATH
# ref: https://github.com/Homebrew/brew/blob/master/Library/Homebrew/cmd/shellenv.sh
eval "$("$BREW_PREFIX/bin/brew" shellenv)"

PATH="$BREW_PREFIX/opt/ruby/bin:$PATH"
PATH="$BREW_PREFIX/opt/coreutils/libexec/gnubin:$PATH"
PATH="$BREW_PREFIX/opt/binutils/bin:$PATH"
PATH="$BREW_PREFIX/opt/findutils/libexec/gnubin:$PATH"
PATH="$BREW_PREFIX/opt/gnu-sed/libexec/gnubin:$PATH"
PATH="$BREW_PREFIX/opt/gnu-which/libexec/gnubin:$PATH"
PATH="$BREW_PREFIX/opt/grep/libexec/gnubin:$PATH"
PATH="$BREW_PREFIX/opt/openssl/bin:$PATH"
PATH="$HOME/bin:$PATH"
export PATH

export LDFLAGS="-L$BREW_PREFIX/opt/openssl/lib"
export CPPFLAGS="-I$BREW_PREFIX/opt/openssl/include"

MANPATH="$BREW_PREFIX/opt/coreutils/libexec/gnuman:$MANPATH"
MANPATH="$BREW_PREFIX/opt/binutils/share/man:$MANPATH"
MANPATH="$BREW_PREFIX/opt/findutils/libexec/gnuman:$MANPATH"
MANPATH="$BREW_PREFIX/opt/gnu-sed/libexec/gnuman:$MANPATH"
MANPATH="$BREW_PREFIX/opt/gnu-which/libexec/gnuman:$MANPATH"
MANPATH="$BREW_PREFIX/opt/grep/libexec/gnuman:$MANPATH"
export MANPATH

export LANG=en_US.UTF-8
export LESSCHARSET=utf-8
export EDITOR=nvim
export HISTTIMEFORMAT='%y-%m-%d %H:%M:%S '
export HISTSIZE=5000
export XDG_CONFIG_HOME=~/.config
export XDG_DATA_HOME=~/.local/share
export QUOTING_STYLE=literal # for GNU ls
export HOMEBREW_NO_ENV_HINTS=true

# AWS Profile Switcher
if [ -f ~/.aws/current_profile ]; then
  AWS_PROFILE="$(cat ~/.aws/current_profile)"
  export AWS_PROFILE
fi

if [ -f ~/.config/gcloud/active_config ]; then
  GC_ACTIVE_CONFIG="$(cat ~/.config/gcloud/active_config)"
  export GC_ACTIVE_CONFIG
fi

# Version managers (asdf, aqua)
[[ -f "$BREW_PREFIX/opt/asdf/libexec/asdf.sh" ]] && . "$BREW_PREFIX/opt/asdf/libexec/asdf.sh"
export PATH=${AQUA_ROOT_DIR:-${XDG_DATA_HOME:-$HOME/.local/share}/aquaproj-aqua}/bin:$PATH

[[ -f "$BREW_PREFIX/share/google-cloud-sdk/path.bash.inc" ]] && . "$BREW_PREFIX/share/google-cloud-sdk/path.bash.inc"
[[ -f "$HOME/.asdf/plugins/golang/set-env.bash" ]] && . "$HOME/.asdf/plugins/golang/set-env.bash"
export PATH="${GOBIN}:${PATH}"
export ASDF_GOLANG_MOD_VERSION_ENABLED="true"
export CLOUDSDK_PYTHON="$BREW_PREFIX/bin/python3" # for gcloud

for file in ~/.{bashrc,aliases,functions,brew_api_token}; do
  [[ -r "$file" ]] && [[ -f "$file" ]] && . "$file"
done
[[ "$(command -v prompts)" ]] && prompts

# iTerm2 shell integration
# See: https://iterm2.com/documentation-shell-integration.html
shell_integration_path=~/.iterm2_shell_integration.bash
if [[ -e  "$shell_integration_path" ]]; then
  source "$shell_integration_path"
else
  echo "iTerm2 shell integration is not installed!"
  echo "Please place ${shell_integration_path}."
  echo "See: https://iterm2.com/documentation-shell-integration.html"
fi
