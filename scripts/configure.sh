#!/usr/bin/env bash

set -e

function condkillall() {
  local -r process="$1"
  if pgrep "^${process}$" >/dev/null 2>&1; then
    killall "${process}"
  fi
}

if ! command -v defaults >/dev/null 2>&1; then
  echo "Command \"defaults\" not found. Nothing to do."
  exit 0
fi

echo "Configuring..."
defaults write -g AppleLanguages '( "en-JP", "ja-JP")'
defaults write -g AppleShowScrollBars -string "WhenScrolling"
defaults write -g NSAutomaticQuoteSubstitutionEnabled -bool false
defaults write -g NSAutomaticDashSubstitutionEnabled -bool false
defaults write -g NSAutomaticCapitalizationEnabled -bool false
defaults write -g AppleShowAllExtensions -bool true
defaults write -g NSQuitAlwaysKeepsWindows -bool true
defaults write com.apple.menuextra.clock IsAnalog -bool true
defaults write com.apple.AppleMultitouchTrackpad Clicking -bool true
defaults write com.apple.CrashReporter UseUNC -bool true
defaults write KeyRepeat -int 2
defaults write com.apple.desktopservices DSDontWriteNetworkStores -bool true
defaults write com.apple.menuextra.battery ShowPercent -string "YES"
defaults write com.apple.Siri HotkeyTag -int 3 # Hold Option Space

echo "Configuring with sudo..."
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --setglobalstate on

# Disable shortcut (this conflicts spotlight shortcut)
defaults write com.apple.symbolichotkeys AppleSymbolicHotKeys -dict-add 60 "<dict><key>enabled</key><false/></dict>"
defaults write com.apple.symbolichotkeys AppleSymbolicHotKeys -dict-add 61 "<dict><key>enabled</key><false/></dict>"
# spotlight shortcut command + space
defaults write com.apple.symbolichotkeys AppleSymbolicHotKeys -dict-add 64 "<dict><key>enabled</key><true/><key>value</key><dict><key>parameters</key><array><integer>65535</integer><integer>49</integer><integer>262144</integer></array><key>type</key><string>standard</string></dict></dict>"
defaults -currentHost write com.apple.screensaver idleTime -int 0

defaults write com.apple.messageshelper.MessageController SOInputLineSettings -dict-add "automaticEmojiSubstitutionEnablediMessage" -bool false
defaults write com.apple.messageshelper.MessageController SOInputLineSettings -dict-add "automaticQuoteSubstitutionEnabled" -bool false


# activity monitor:
defaults write com.apple.ActivityMonitor UpdatePeriod -int 2
defaults write com.apple.ActivityMonitor ShowCategory -int 100

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
defaults write com.apple.AppleMultitouchTrackpad TrackpadThreeFingerDrag -bool true

echo "Configuring Keyboard..."
defaults write -g InitialKeyRepeat -int 35
defaults write -g KeyRepeat -int 2

echo "Configuring SystemUIServer..."
defaults write com.apple.systemuiserver menuExtras -array \
  "/System/Library/CoreServices/Menu Extras/TimeMachine.menu" \
  "/System/Library/CoreServices/Menu Extras/Bluetooth.menu" \
  "/System/Library/CoreServices/Menu Extras/TextInput.menu" \
  "/System/Library/CoreServices/Menu Extras/Clock.menu" \
  "/System/Library/CoreServices/Menu Extras/AirPort.menu"
defaults write com.apple.menuextra.clock isAnalog -bool true
condkillall SystemUIServer

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
defaults write com.apple.dock mru-spaces -bool false # Disable automatically rearrange spacet
defaults write com.apple.dock expose-group-apps -int 0 # Disable Mission Control's "Group windows by application"
condkillall Dock

echo "Configuring Finder..."
defaults write com.apple.finder ShowHardDrivesOnDesktop -bool true
defaults write com.apple.finder ShowExternalHardDrivesOnDesktop -bool true
defaults write com.apple.finder ShowRemovableMediaOnDesktop -bool true
defaults write com.apple.finder ShowMountedServersOnDesktop -bool true
defaults write com.apple.finder ShowStatusBar -bool true
/usr/libexec/PlistBuddy -c "Set :DesktopViewSettings:IconViewSettings:showItemInfo true" ~/Library/Preferences/com.apple.finder.plist
/usr/libexec/PlistBuddy -c "Set :DesktopViewSettings:IconViewSettings:arrangeBy grid" ~/Library/Preferences/com.apple.finder.plist
defaults write com.apple.finder FXRemoveOldTrashItems -bool true
condkillall Finder

echo "Configuring Safari..."
defaults write com.apple.Safari ShowFullURLInSmartSearchField -bool true
defaults write com.apple.Safari IncludeInternalDebugMenu -bool true
defaults write com.apple.Safari ShowStatusBar -bool true
defaults write com.apple.Safari AutoFillPasswords -bool true
condkillall Safari

echo "Configuring Notes..."
defaults write com.apple.Notes ShouldContinuouslyCheckSpelling -bool false
defaults write com.apple.Notes ShouldCorrectSpellingAutomatically -bool false
condkillall Notes

echo "Configuring Pastebot..."
defaults write com.tapbots.Pastebot2Mac UIVisibilityState 10
condkillall Pastebot

echo ""
echo "Configuration Complete!"
echo "Please restart Mac to make sure settings are reflected."

## Deprecated
# defaults write com.apple.dock autohide -bool true
