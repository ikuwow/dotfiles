
# Environment Variables
export PATH=~/bin:/usr/local/Cellar/php53/5.3.28/bin:/usr/local/bin:/usr/local/sbin:$PATH
export LANG=ja_JP.UTF-8
export LESSCHARSET=utf-8
export EDITOR=vim

# Rubyは全てrbenvで管理する（homebrewでは入れない）
# export PATH="$HOME/.rbenv/shims:$PATH"
eval "$(rbenv init -)"

# git autocomplete
if [ -f ~/dotfiles/.git-completion.bash ]; then
    . ~/dotfiles/.git-completion.bash
fi

# load .bashrc
if [ -e ~/.bashrc ]; then
    source ~/.bashrc
fi

