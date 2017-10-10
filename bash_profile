## TODO: it must be in .macrc (specific to homebrew)
export PATH=~/.jenv/bin:~/.nodebrew/current/bin:~/bin:/usr/local/heroku/bin:/usr/local/bin:/usr/local/sbin:$PATH
if [ -f ~/.phpbrew/bashrc ]; then
    . ~/.phpbrew/bashrc
fi

# Environment Variables
export LANG=ja_JP.UTF-8
export LESSCHARSET=utf-8
export EDITOR=nvim
export HISTTIMEFORMAT='%y-%m-%d %H:%M:%S '
export HISTSIZE=5000
export ANSIBLE_COW_SELECTION=random
export XDG_CONFIG_HOME=~/.config

if `type rbenv > /dev/null 2>&1`; then
  eval "$(rbenv init - --no-rehash)"
fi

if `type pyenv > /dev/null 2>&1`; then
    eval "$(pyenv init - --no-rehash)" # adding --no-rehash makes this faster
fi

if $(type jenv > /dev/null 2>&1); then
    eval "$(jenv init - --no-rehash)"
fi

OTHER=(.bashrc .macrc)
for rcfile in ${OTHER[@]}; do
    if [ -e ~/$rcfile ]; then
        source ~/$rcfile
    fi
done
