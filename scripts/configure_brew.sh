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
  # First run is slow: downloads the Kata kernel and registers a persistent
  # LaunchAgent. After this, container auto-starts at login without brew services.
  /opt/homebrew/opt/container/bin/container system start --enable-kernel-install
  # On first boot, `brew bundle` (run before this script in bootstrap/main.sh)
  # starts socktainer before container's apiserver is initialized, so socktainer
  # comes up pointing at nothing. Restart it now that apiserver is running.
  brew services restart socktainer
fi
