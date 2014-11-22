#!/bin/bash

# App Storeでインストールするもの
# Xcode (さきに), Evernote, LINE, Yorufukurou, The Unaarchiver, 1password, Degrees

# homebrewが入っているか確認
if [ ! `which brew` ]; then
    echo "You don't have homebrew! Start Installing."
    ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
    echo "Homebrew installation Done! Please type 'brew install'."
    exit
fi

export HOMEBREW_CASK_OPTS="--appdir=/Applications"

echo "Do you 'yum update'? This takes a few minutes. (recommended) [Y/n]"
echo -n "> "
read update
echo  "OK, next, do you 'yum upgrade'? This takes a lot of times. [y/N]"
echo -n "> "
read upgrade

if [ ! "${update,,}" = "n" -a ! "${update,,}" = "no" ]; then
    echo "Updating Homebrew... "
    brew update
    echo "Done!"
fi

if [ "${upgrade,,}" = "y" -o "${upgrade,,}" = "yes" ]; then
    echo -n "Upgrading Homebrew... "
    brew update
    echo "Done!"
fi

exit

BASICS="vim brew-cask gcc pwgen tree git bash trash wget tmux"
echo "Installing Basic packages... "
brew install $BASICS
echo "Done!"

RUBY="ruby-build rbenv"
echo "Installing Ruby packages... "
brew install $RUBY
echo "Done!"

CHEF="knife-solo berkshelf"
echo "Installing Chef packages... "
gem install $CHEF
echo "Done!"

CASKS="bettertouchtool menumeters vlc rescuetime firefox google-chrome karabiner cyberduck
    iterm2 dropbox virtualbox vagrant mysqlworkbench google-japanese-ime github macvim-kaoriya"
echo "Installing Cask packages... "
brew cask install $CASKS
echo "Done!"

echo "Cleanup... "
brew cleanup
echo "DONE!"


