#!/bin/bash

set -e

echo "Configuring..."
defaults write com.apple.AppleMultitouchTrackpad Clicking -bool true
defaults write com.apple.CrashReporter UseUNC -bool true
defaults write KeyRepeat -int 2
defaults write com.apple.desktopservices DSDontWriteNetworkStores -bool true

defaults write NSGlobalDomain NSAutomaticQuoteSubstitutionEnabled -bool false
defaults write NSGlobalDomain NSAutomaticDashSubstitutionEnabled -bool false

echo "Configuring Dock..."
defaults write com.apple.dock show-recents -bool false
defaults write com.apple.dock tilesize -int 77
defaults write com.apple.dock largesize -int 91
defaults write com.apple.dock magnification -int 1
defaults write com.apple.dock wvous-bl-corner -int 11 # Launchpad
defaults write com.apple.dock wvous-bl-modifier -int 0
defaults write com.apple.dock wvous-br-corner -int 10 # Put display to sleep
defaults write com.apple.dock wvous-br-modifier -int 0
defaults write com.apple.dock wvous-tr-corner -int 12 # Notification Center
defaults write com.apple.dock wvous-tr-modifier -int 0

echo "Configuring Mouse..."
defaults write com.apple.AppleMultitouchMouse MouseButtonDivision -int 55
defaults write com.apple.AppleMultitouchMouse MouseButtonMode -string TwoButton
defaults write com.apple.AppleMultitouchMouse MouseVerticalScroll -int 1
defaults write com.apple.AppleMultitouchMouse MouseHorizontalScroll -int 1
defaults write com.apple.AppleMultitouchMouse MouseMomentumScroll -int 1
defaults write com.apple.AppleMultitouchMouse MouseOneFingerDoubleTapGesture -int 0
defaults write com.apple.AppleMultitouchMouse MouseTwoFingerDoubleTapGesture -int 3
defaults write com.apple.AppleMultitouchMouse MouseTwoFingerHorizSwipeGesture -int 2

echo "Configuring Trackpad..."
defaults write com.apple.AppleMultitouchTrackpad TrackpadRightClick -bool true
defaults write com.apple.AppleMultitouchTrackpad Clicking -bool true

echo "Configuring Keyboard..."
defaults write NSGlobalDomain InitialKeyRepeat -int 35
defaults write NSGlobalDomain KeyRepeat -int 2

echo "Configuring Finder..."
defaults write com.apple.finder ShowHardDrivesOnDesktop -bool true

echo "Configuring Safari..."
defaults write com.apple.Safari ShowFullURLInSmartSearchField -bool true
defaults write com.apple.Safari IncludeInternalDebugMenu -bool true
defaults write com.apple.Safari ShowStatusBar -bool true
defaults write com.apple.Safari AutoFillPasswords -bool true

echo ""
echo "Configure Complete!"
echo "Please restart Mac to make sure settings are reflected."

## Deprecated
# defaults write com.apple.dock autohide -bool true
