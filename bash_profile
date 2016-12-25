# STARTTIME=$(gdate +%s%N)

## TODO: it must be in .macrc (specific to homebrew)
export PATH=~/bin:~/.phpbrew/bin:/usr/local/heroku/bin:/usr/local/bin:/usr/local/sbin:$PATH
if [ -f ~/.phpbrew/bashrc ]; then
    source ~/.phpbrew/bashrc
fi
export PATH=~/.phpbrew/bin:$PATH

# Environment Variables
export LANG=ja_JP.UTF-8
export LESSCHARSET=utf-8
export EDITOR=vim
export HISTTIMEFORMAT='%y-%m-%d %H:%M:%S '
export HISTSIZE=5000
export ANSIBLE_COW_SELECTION=random

if `type rbenv > /dev/null 2>&1`; then
  eval "$(rbenv init - --no-rehash)" # adding --no-rehash makes this faster
fi

if `type pyenv > /dev/null 2>&1`; then
    eval "$(pyenv init - --no-rehash)" # adding --no-rehash makes this faster
fi

OTHER=(.bashrc .macrc)
for rcfile in ${OTHER[@]}; do
    if [ -e ~/$rcfile ]; then
        source ~/$rcfile
    fi
done

# ENDTIME=$(gdate +%s%N)
# ELAPSED=`echo "scale=3; (${ENDTIME} - ${STARTTIME})/1000000000" | bc`
# echo "It took ${ELAPSED} sec"
