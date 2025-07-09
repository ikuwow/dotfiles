#!/usr/bin/env bash

echo "Configuring brew autoupdate..."
brew autoupdate --status | grep 'Autoupdate is installed and running.' > /dev/null
status="$?"
if [ "$status" != 0 ]; then
  brew autoupdate 259200 --start --upgrade --cleanup
else
  echo "Autoupdate is enabled. Nothing to do."
fi
