# userscripts

Safari user scripts loaded by the [Userscripts](https://github.com/quoid/userscripts) extension. This directory is set as the extension's Save Location so the scripts are version-controlled with the rest of the dotfiles.

## Setup

See the "Safari Userscripts" section in the top-level [README.md](../README.md) for the full installation and Save Location procedure, including why the extension is pointed at the real repo path.

## Scripts

- `ime-enter-fixer.user.js` — stops the IME confirmation Enter from triggering a site's submit handler in Safari, applied to all sites (`@include *://*/*`)

## Adding a new script

1. Create a file ending in `.user.js` in this directory
1. Include a `// ==UserScript==` metadata block with at least `@name` and one of `@include` / `@match`
1. Add `@run-at document-start` when the script needs to hook events before the page's own listeners attach (defaults to `document-end` if omitted)
1. The Userscripts extension picks it up automatically once the Save Location is set
