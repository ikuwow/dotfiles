#!/bin/bash

# Reject commits that change a *.user.js body without bumping its
# // @version line. Every userscript must carry a non-empty // @version.

set -eu

for file in "$@"; do
  case "$file" in
    userscripts/*.user.js) ;;
    *) continue ;;
  esac

  work_version=$(grep -m1 '^// @version' "$file" || true)
  if [ -z "$work_version" ]; then
    echo "$file: missing // @version line"
    exit 1
  fi

  if git cat-file -e "HEAD:$file" 2>/dev/null; then
    head_version=$(git show "HEAD:$file" | grep -m1 '^// @version' || true)
    if [ "$head_version" = "$work_version" ]; then
      echo "$file: content changed but // @version was not bumped"
      exit 1
    fi
  fi
done

exit 0
