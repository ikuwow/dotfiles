#!/usr/bin/env bash

# vim: set filetype=sh :

# shellcheck source=/dev/null

ARCH="$(arch)"
if [ "$ARCH" = "arm64" ]; then
  BREW_PREFIX="/opt/homebrew"
elif [ "$ARCH" = "i386" ]; then
  BREW_PREFIX="/usr/local"
fi

# Homebrew setup (only when installed)
if [ -n "${BREW_PREFIX:-}" ] && [ -x "$BREW_PREFIX/bin/brew" ]; then
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
  PATH="$BREW_PREFIX/opt/mysql-client/bin:$PATH"

  export LDFLAGS="-L$BREW_PREFIX/opt/openssl/lib"
  export CPPFLAGS="-I$BREW_PREFIX/opt/openssl/include"

  MANPATH="$BREW_PREFIX/opt/coreutils/libexec/gnuman:$MANPATH"
  MANPATH="$BREW_PREFIX/opt/binutils/share/man:$MANPATH"
  MANPATH="$BREW_PREFIX/opt/findutils/libexec/gnuman:$MANPATH"
  MANPATH="$BREW_PREFIX/opt/gnu-sed/libexec/gnuman:$MANPATH"
  MANPATH="$BREW_PREFIX/opt/gnu-which/libexec/gnuman:$MANPATH"
  MANPATH="$BREW_PREFIX/opt/grep/libexec/gnuman:$MANPATH"
  export MANPATH

  export HOMEBREW_NO_ENV_HINTS=true
  export CLOUDSDK_PYTHON="$BREW_PREFIX/bin/python3" # for gcloud
  [[ -f "$BREW_PREFIX/share/google-cloud-sdk/path.bash.inc" ]] && . "$BREW_PREFIX/share/google-cloud-sdk/path.bash.inc"
fi

# Universal PATH
PATH="$HOME/bin:$PATH"
PATH="$HOME/.local/bin:$PATH"
export PATH

# Universal environment
export LANG=en_US.UTF-8
export LESSCHARSET=utf-8
if command -v nvim &>/dev/null; then
  export EDITOR=nvim
else
  export EDITOR=vim
fi
export HISTTIMEFORMAT='%y-%m-%d %H:%M:%S '
export HISTSIZE=5000
export XDG_CONFIG_HOME=~/.config # Some tools hardcode this path; do not change without auditing
export XDG_DATA_HOME=~/.local/share
export QUOTING_STYLE=literal # for GNU ls

# npm
export NPM_CONFIG_FUND=false
export NPM_CONFIG_MIN_RELEASE_AGE=7
export NPM_CONFIG_IGNORE_SCRIPTS=true

# ShellCheck
export SHELLCHECK_OPTS='--exclude=SC1090,SC1091,SC2039,SC3010,SC3060,SC3028'

# terraform
export TF_PLUGIN_CACHE_DIR="$HOME/.terraform.d/plugin-cache"
export CHECKPOINT_DISABLE=1

# AWS Profile Switcher
if [ -f ~/.aws/current_profile ]; then
  AWS_PROFILE="$(cat ~/.aws/current_profile)"
  export AWS_PROFILE
fi

export CLOUDSDK_CONFIG="$XDG_CONFIG_HOME/gcloud"

export COLIMA_HOME="$XDG_CONFIG_HOME/colima"

# Version managers (mise, aqua)
export PATH="${AQUA_ROOT_DIR:-${XDG_DATA_HOME:-$HOME/.local/share}/aquaproj-aqua}/bin:$PATH"
[[ $(command -v mise) ]] && eval "$(mise activate bash)"

[[ -n "$GOBIN" ]] && export PATH="${GOBIN}:${PATH}"

for file in ~/.{bashrc,aliases,functions,brew_api_token}; do
  [[ -r "$file" ]] && [[ -f "$file" ]] && . "$file"
done

[[ "$(command -v prompts)" ]] && prompts

# Machine-local overrides (not managed by dotfiles repo)
if [[ -r ~/.bash_profile.local ]] && [[ -f ~/.bash_profile.local ]]; then
  . ~/.bash_profile.local
fi
