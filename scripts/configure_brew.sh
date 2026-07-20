#!/usr/bin/env bash

set -eu

echo "Configuring brew autoupdate..."
if brew autoupdate --status | grep -q 'Autoupdate is installed and running.'; then
  echo "Autoupdate is enabled. Nothing to do."
else
  brew autoupdate 259200 --start --upgrade --cleanup
fi

echo "Initializing apple container..."
container system start --enable-kernel-install
# brew bundle started socktainer before apiserver existed; pick up the running apiserver.
brew services restart socktainer
