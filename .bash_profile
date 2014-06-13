
# Environment Variables
export PATH=/usr/local/Cellar/php53/5.3.28/bin:/usr/local/bin:/usr/local/sbin:$PATH
export LANG=ja_JP.UTF-8
export LESSCHARSET=utf-8
export EDITOR=gvim

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


alias saying='while (true) do f=$(fortune); echo "$f"; echo ""; say "$f"; sleep 5; done'

# Rubyは全てrbenvで管理する（homebrewでは入れない）
# export PATH="$HOME/.rbenv/shims:$PATH"
eval "$(rbenv init -)"

# gitオートコンプリート
if [ -f ~/dotfiles/.git-completion.bash ]; then
    . ~/dotfiles/.git-completion.bash
fi

# .bashrc
if [ -e ~/.bashrc ]; then
    source ~/.bashrc
fi

alias ='echo "Stay hungly, stay foolish."'
