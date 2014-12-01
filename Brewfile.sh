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
    echo "Homebrew installation Done! Please type 'brew doctor'."
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

BASICS="vim brew-cask gcc pwgen tree git bash trash wget tmux"
echo "Installing Basic packages... "
brew install $BASICS
printf "Done!\n\n"

RUBY="ruby-build rbenv"
echo "Installing Ruby packages... "
brew install $RUBY
printf "Done!\n\n"

GEMS="bundler chef knife-solo berkshelf kitchen-vagrant test-kitchen knife-solo_data_bag"
echo "Installing gem packages... "
for pkg in $GEMS; do
    gem list | grep $pkg > /dev/null
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

echo "Installing vagrant plugins..."
VAGRANT="vagrant-omnibus vagrant-vbguest vagrant-cachier sahara vagrant-vbox-snapshot"
# vagrant-global-status is available on vagrant core without plugin!
for pkg in $VAGRANT; do
    vagrant plugin list | grep $pkg > /dev/null
    ec=$?
    if [ ! $ec -eq 0 ]; then
        vagrant plugin install $pkg
    else
        echo "vagrant plugin \"${pkg}\" is already installed. (Up to date)"
    fi
done
printf "Done!\n\n"

CASKS="bettertouchtool menumeters vlc rescuetime firefox google-chrome karabiner \
    cyberduck iterm2 dropbox virtualbox vagrant mysqlworkbench google-japanese-ime github \
    macvim-kaoriya cocoarestclient adobe-air cacoo-ninja"
echo "Installing Cask packages... "
brew cask install $CASKS
printf "Done!\n\n"

echo "Cleanup... "
brew cleanup
brew cask cleanup
gem cleanup
echo "DONE!"


