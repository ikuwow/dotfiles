# vim: set filetype=sh :

## TODO: it must be in .macrc (specific to homebrew)
PATH=~/bin:/usr/local/bin:/usr/local/sbin:$PATH
if [ -f ~/.phpbrew/bashrc ]; then
    . ~/.phpbrew/bashrc
fi

PATH="$HOME/.anyenv/bin:$PATH"
if $(type anyenv > /dev/null 2>&1); then
    eval "$(anyenv init - --no-rehash)"
fi
export PATH
# java home setting
export JAVA_HOME=$(/usr/libexec/java_home -v $(cat ~/.anyenv/envs/jenv/version))

# Environment Variables
export LANG=ja_JP.UTF-8
export LESSCHARSET=utf-8
export EDITOR=nvim
export HISTTIMEFORMAT='%y-%m-%d %H:%M:%S '
export HISTSIZE=5000
export ANSIBLE_COW_SELECTION=random
export XDG_CONFIG_HOME=~/.config

OTHER=(.bashrc .macrc)
for rcfile in ${OTHER[@]}; do
    if [ -e ~/$rcfile ]; then
        source ~/$rcfile
    fi
done

ssh-add -K > /dev/null 2>&1
if [ $? != 0 ]; then
    echo "ERROR: 'ssh-add -K' failed!"
    exit 1
fi

