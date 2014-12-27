#!/usr/local/bin/bash

# usage: $ bash Brewfile.sh
#
# To be installed by App Store in advance
# Xcode, LINE, Yorufukurou, The Unaarchiver, 1password, Degrees
# Keynote, Pages, Numbers

# homebrewが入っているか確認
if [ ! `which brew` ]; then
    echo "You don't have homebrew! Start Installing."
    ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
    brew install caskroom/cask/brew-cask
    brew tap casroom/versions
    echo "Homebrew installation Done! Please type 'brew doctor'."
    exit
fi

export HOMEBREW_CASK_OPTS="--appdir=/Applications"

## Questions
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
    printf "Done!\n\n"
fi

# brew cask update
if [ ! "${caskupdate,,}" = "n" -a ! "${caskupdate,,}" = "no" ]; then
    echo "Updating Homebrew Cask... "
    brew cask update
    printf "Done!\n\n"
fi

# brew upgrade
if [ "${upgrade,,}" = "y" -o "${upgrade,,}" = "yes" ]; then
    echo -n "Upgrading Homebrew... "
    brew update
    printf "Done!\n\n"
fi

## Basic Components
BASICS="vim brew-cask cloog gcc pwgen tree git bash trash wget tmux imagemagick ghostscript bash-completion"
echo "Installing Basic packages... "
brew install $BASICS
printf "Done!\n\n"

## PHP
PHP="php56 composer php56-mcrypt"
brew install $PHP

## Ruby
RUBY="ruby-build rbenv"
RUBY_VERSION="2.1.5"
echo "Installing Ruby packages... "
brew install $RUBY
ruby -v | grep $RUBY_VERSION > /dev/null
if [ $? -eq 1 ];then
    rbenv install $RUBY_VERSION
    rbenv global $RUBY_VERSION
    rbenv rehash
    echo 'New version of Ruby is installed! Please reboot your terminal and execute Brewfile again.'
    exit 0
else
    echo "Ruby is already installed. (${RUBY_VERSION})"
fi
printf "Done!\n\n"


## Ruby Gems
GEMS="bundler chef chef-zero knife-solo berkshelf kitchen-vagrant test-kitchen knife-solo_data_bag cocoapods tw"
echo "Installing gem packages... "
GEMLIST=`gem list`
for pkg in $GEMS; do
    echo $GEMLIST | grep $pkg > /dev/null
    ec=$?
    if [ ! $ec -eq 0 ]; then
        echo $pkg
        gem install $pkg
    else
        echo "gem package \"${pkg}\" is already installed. (Up to date)"
    fi
done
printf "Done!\n\n"

gem update

# Brew Cask
CASKS="xquartz bettertouchtool menumeters vlc rescuetime firefox google-chrome karabiner bartender \
    cyberduck iterm2 dropbox virtualbox vagrant mysqlworkbench google-japanese-ime github \
    macvim-kaoriya cocoarestclient adobe-air cacoo-ninja evernote owncloud mendeley-desktop \
    day-o onyx mactex clamxav"
echo "Installing Cask packages... "
brew cask install $CASKS
printf "Done!\n\n"

# Vagrant Plugins
echo "Updating existing vagrant plugins..."
vagrant plugin update
echo "Installing vagrant plugins..."
VAGRANT="vagrant-omnibus vagrant-vbguest vagrant-cachier sahara vagrant-vbox-snapshot"
VAGRANT_PLUGIN_LIST=`vagrant plugin list`
for pkg in $VAGRANT; do
    echo $VAGRANT_PLUGIN_LIST | grep $pkg > /dev/null
    ec=$?
    if [ ! $ec -eq 0 ]; then
        vagrant plugin install $pkg
    else
        echo "vagrant plugin \"${pkg}\" is already installed. (Up to date)"
    fi
done
printf "Done!\n\n"

echo "Cleanup... "
brew cleanup
brew cask cleanup
gem cleanup
echo "DONE!"


