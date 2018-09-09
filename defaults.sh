#!/bin/bash

defaults write com.apple.AppleMultitouchTrackpad Clicking -bool true
defaults write com.apple.CrashReporter UseUNC -bool true
defaults write KeyRepeat -int 2
defaults write com.apple.desktopservices DSDontWriteNetworkStores -bool true
defaults write com.apple.dock autohide -bool true

## Finder
echo "Configuring Finder..."
defaults write com.apple.finder ShowHardDrivesOnDesktop -bool true

## Safari
echo "Configuring Safari..."
defaults write com.apple.Safari ShowFullURLInSmartSearchField -bool true
defaults write com.apple.Safari IncludeInternalDebugMenu -bool true

