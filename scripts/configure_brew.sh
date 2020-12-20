#!/usr/bin/env bash

echo "Configuring brew autoupdate..."
if brew autoupdate --status | grep -v 'Autoupdate is installed and running.' > /dev/null; then
  brew autoupdate --upgrade --cleanup --enable-notification --start
else
  echo "Autoupdate is enabled. Nothing to do."
fi
