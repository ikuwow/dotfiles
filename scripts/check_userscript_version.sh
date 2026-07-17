#!/bin/bash

# Reject commits that change a *.user.js body without bumping its
# // @version line. New userscripts must include // @version from the start.

set -eu

for file in "$@"; do
  case "$file" in
    userscripts/*.user.js) ;;
    *) continue ;;
  esac

  if git cat-file -e "HEAD:$file" 2>/dev/null; then
    head_version=$(git show "HEAD:$file" | grep -m1 '^// @version' || true)
    work_version=$(grep -m1 '^// @version' "$file" || true)
    if [ -n "$head_version" ] && [ "$head_version" = "$work_version" ]; then
      echo "$file: content changed but // @version was not bumped"
      exit 1
    fi
    continue
  fi

  if ! grep -q '^// @version' "$file"; then
    echo "$file: new userscript must include a // @version line"
    exit 1
  fi
  continue
done

exit 0
