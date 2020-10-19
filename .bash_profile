# vim: set filetype=sh :

# shellcheck source=/dev/null

PATH="$HOME/bin:/usr/local/opt/ruby/bin:/usr/local/bin:/usr/local/sbin:$PATH"

PATH="/usr/local/opt/coreutils/libexec/gnubin:$PATH"
PATH="/usr/local/opt/binutils/bin:$PATH"
PATH="/usr/local/opt/findutils/libexec/gnubin:$PATH"
PATH="/usr/local/opt/gnu-sed/libexec/gnubin:$PATH"
PATH="/usr/local/opt/gnu-which/libexec/gnubin:$PATH"
PATH="/usr/local/opt/openssl/bin:$PATH"
export PATH

export LDFLAGS="-L/usr/local/opt/openssl/lib"
export CPPFLAGS="-I/usr/local/opt/openssl/include"

MANPATH="/usr/local/opt/coreutils/libexec/gnuman:$MANPATH"
MANPATH="/usr/local/opt/binutils/share/man:$MANPATH"
MANPATH="/usr/local/opt/findutils/libexec/gnuman:$MANPATH"
MANPATH="/usr/local/opt/gnu-sed/libexec/gnuman:$MANPATH"
MANPATH="/usr/local/opt/gnu-which/libexec/gnuman:$MANPATH"
export MANPATH

export LANG=en_US.UTF-8
export LESSCHARSET=utf-8
export EDITOR=nvim
export HISTTIMEFORMAT='%y-%m-%d %H:%M:%S '
export HISTSIZE=5000
export XDG_CONFIG_HOME=~/.config
export XDG_DATA_HOME=~/.local/share
export PROMPT_COMMAND='echo -ne "\033]0;${PWD}\007"'
export QUOTING_STYLE=literal # for GNU ls
export HOMEBREW_BUNDLE_NO_LOCK=true

asdfini=/usr/local/opt/asdf/asdf.sh
if [ -e "$asdfini" ]; then
  . "$asdfini"
fi

if [ "$(command -v gcloud)" ]; then
  gcloudpath="$(dirname "$(dirname "$(readlink "$(command -v gcloud)")")")"
  [[ -f "$gcloudpath/path.bash.inc" ]] && . "$gcloudpath/path.bash.inc"
  [[ -f "$gcloudpath/completion.bash.inc" ]] && . "$gcloudpath/completion.bash.inc"
fi

for file in ~/.{bashrc,aliases,functions,brew_api_token}; do
  [[ -r "$file" ]] && [[ -f "$file" ]] && . "$file"
done
[[ "$(command -v prompts)" ]] && prompts


shell_integration_path=~/.iterm2_shell_integration.bash
if [[ -e  "$shell_integration_path" ]]; then
  source "$shell_integration_path"
else
  echo "iTerm2 shell integration is not installed!"
  echo "Please place ${shell_integration_path}."
  echo "See: https://iterm2.com/documentation-shell-integration.html"
fi
