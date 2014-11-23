#!/bin/bash
#
# usage: $ bash Brewfile.sh
#
# To be installed by App Store in advance
# Xcode, Evernote, LINE, Yorufukurou, The Unaarchiver, 1password, Degrees

# homebrewが入っているか確認
if [ ! `which brew` ]; then
    echo "You don't have homebrew! Start Installing."
    ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
    brew install brew-cask
    echo "Homebrew installation Done! Please type 'brew install'."
    exit
fi

export HOMEBREW_CASK_OPTS="--appdir=/Applications"

echo "Do you 'brew update'? This takes a few minutes. (recommended) [Y/n]"
echo -n "> "
read update
echo "OK, next, do you 'brew cask update'? This takes a few minutes. (recommended) [Y/n]"
echo -n "> "
read caskupdate
echo  "OK, at last, do you 'brew upgrade'? This takes a lot of times. [y/N]"
echo -n "> "
read upgrade

# brew update
if [ ! "${update,,}" = "n" -a ! "${update,,}" = "no" ]; then
    echo "Updating Homebrew... "
    brew update
    echo "Done!"
fi

# brew cask update
if [ ! "${caskupdate,,}" = "n" -a ! "${caskupdate,,}" = "no" ]; then
    echo "Updating Homebrew Cask... "
    brew cask update
    echo "Done!"
fi

# brew upgrade
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

GEMS="chef knife-solo berkshelf berkshelf kitchen-vagrant test-kitchen knife-solo_data_bag"
echo "Installing Chef packages... "
gem install $GEMS
echo "Done!"

CASKS="bettertouchtool menumeters vlc rescuetime firefox google-chrome karabiner cyberduck
    iterm2 dropbox virtualbox vagrant mysqlworkbench google-japanese-ime github macvim-kaoriya"
echo "Installing Cask packages... "
brew cask install $CASKS
echo "Done!"

echo "Cleanup... "
brew cleanup
brew cask cleanup
echo "DONE!"


