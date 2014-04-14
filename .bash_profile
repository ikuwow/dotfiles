export PATH=/usr/local/bin:/usr/local/sbin:$PATH
export LANG=ja_JP.UTF-8
export LESSCHARSET=utf-8

# ls color options
if [ `uname | grep 'CYGWIN'` ]; then
    alias ls='ls --color'
else
    alias ls='ls -G'
fi

alias ll='ls -l'
alias la='ls -A'
alias rm='rm -i'
alias less='less -iM'
alias bye='exit'

# alias devstart='sudo apachectl start & sudo mysql.server start'
# alias devstop='sudo apachectl stop & sudo mysql.server stop'

alias saying='while (true) do f=$(fortune); echo "$f"; echo ""; say "$f"; sleep 5; done'
# railsに必要
# eval "$(rbenv init -)"

# railsコマンドはhomeの物を使う
export PATH="$HOME/.rbenv/shims:$PATH:/usr/local/Cellar/php53/5.3.27/bin"

# gitオートコンプリート
if [ -f ~/dotfiles/.git-completion.bash ]; then
    . ~/dotfiles/.git-completion.bash
fi

if [ -e ~/.bashrc ]; then
    source ~/.bashrc
fi

alias ='echo "Stay hungly, stay foolish."'
