#!/usr/bin/env bash

set -eu

echo "Configuring brew autoupdate..."
if brew autoupdate --status | grep -q 'Autoupdate is installed and running.'; then
  echo "Autoupdate is enabled. Nothing to do."
else
  brew autoupdate 259200 --start --upgrade --cleanup
fi

echo "Initializing apple container..."
apiserver_plist="$HOME/Library/Application Support/com.apple.container/apiserver/apiserver.plist"
if [ -f "$apiserver_plist" ]; then
  echo "Apple container is already initialized. Nothing to do."
else
  # First run: download Kata kernel (~GB) and register Apple's own persistent
  # LaunchAgent. After this, container auto-starts at login without brew services.
  /opt/homebrew/opt/container/bin/container system start --enable-kernel-install
  # Socktainer's service may have been started before container apiserver was
  # ready (during `brew bundle`). Restart so it picks up the running apiserver.
  brew services restart socktainer
fi
