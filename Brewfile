#!/bin/bash

# usage: $ bash Brewfile.sh
#
# Apps to be installed by App Store in advance: 
# Xcode, LINE, Yorufukurou, The Unaarchiver, Degrees
# Keynote, Pages, Numbers, 1password
# 
# Safari Extentions
# Adblock plus, hatena, pocket, Evernote, HideNicoVideoNews
# 


# homebrewが入っているか確認
if [ ! `which brew` ]; then
    echo "You don't have homebrew! Start Installing."
    ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
    brew tap caskroom/cask
    brew tap caskroom/versions
    brew tap homebrew/versions
    brew install caskroom/cask/brew-cask
    echo "Homebrew installation Done! Please type 'brew doctor'."
    exit 0
fi

export HOMEBREW_CASK_OPTS="--appdir=/Applications"

# Default values
update=true
gem_update=true
vagrant_plugin_update=true
caskupdate=true
upgrade=false

## Options
while [ $# -gt 0 ];do
    case ${1} in
    --upgrade)
        upgrade=true
    ;;
    --noupdate)
        update=false
        caskupdate=false
        gem_update=false
        vagrant_plugin_update=false
    ;;
    *)
        echo "[ERROR] Invalid option '${1}'"
        exit 1
        ;;
    esac
    shift
done

# brew update
if $update ; then
    echo "Updating Homebrew... "
    brew update
    printf "Done!\n\n"
fi

# brew cask update
if $caskupdate; then
    echo "Updating Homebrew Cask... "
    brew cask update
    printf "Done!\n\n"
fi

# brew upgrade
if $upgrade; then
    echo "Upgrading Homebrew... "
    brew upgrade
    printf "Done!\n\n"
fi

# Brew Cask
CASKS="dropbox owncloud iterm2 google-japanese-ime bettertouchtool menumeters karabiner evernote \
    macvim-kaoriya flash java cyberduck virtualbox vagrant mysqlworkbench bartender vlc rescuetime \
    cocoarestclient adobe-air cacoo-ninja mendeley-desktop github \
    day-o onyx mactex heroku-toolbelt xquartz firefox google-chrome goofy recordit libreoffice kobito duet kindle"
echo "Installing Cask packages... "
brew cask install $CASKS
printf "Done!\n\n"

## Basic Components
BASICS="vim cloog gcc pwgen tree git bash trash wget tmux imagemagick ghostscript bash-completion watch nkf nmap"
echo "Installing Basic packages... "
brew install $BASICS
printf "Done!\n\n"

## PHP
echo "Installing PHPs...."
brew tap homebrew/php
PHP="php56 composer php56-mcrypt"
brew install $PHP
printf "Done!\n\n"

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
GEMS="bundler chef chef-zero knife-solo berkshelf kitchen-vagrant test-kitchen knife-solo_data_bag cocoapods tw serverspec"
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

if $gem_update; then
    gem update
fi


# Vagrant Plugins
if $vagrant_plugin_update;then
    echo "Updating existing vagrant plugins..."
    vagrant plugin update
fi
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


