#!/bin/bash


if [ ! `which brew` ]; then
    ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
fi

export HOMEBREW_CASK_OPTS="--appdir=/Applications --caskroom=/usr/local/Caskroom"

# echo "Updating Homebrew... "
# brew update
# echo "Done!"

# echo -n "Upgrading Homebrew... "
# brew update
# echo "Done!"

BASICS="vim brew-cask gcc pwgen tree git bash trash wget tmux"
echo "Installing Basic packages... "
brew install $BASICS
ecno "Done!"

RUBY="ruby-build rbenv gem"
echo "Installing Ruby packages... "
brew install $RUBY
echo "Done!"

CHEF="knife-solo berkshelf"
echo "Installing Chef packages... "
gem install $CHEF
echo "Done!"

CASKS="bettertouchtool menumeters vlc rescuetime firefox chrome karabiner cyberduck
    iterm2 dropbox virtualbox vagrant mysqlworkbench google-japanese-ime github"
echo "Installing Cask packages... "
brew cask install $CASKS
echo "Done!"

echo -n "Cleanup... "
brew cleanup
echo "DONE!"
