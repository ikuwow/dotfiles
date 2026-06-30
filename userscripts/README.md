# userscripts

Safari user scripts loaded by the [Userscripts](https://github.com/quoid/userscripts) extension.

This directory is intended to be set as the extension's Save Location so the scripts are version-controlled with the rest of the dotfiles. The path is registered in the Userscripts app as a macOS security-scoped bookmark, so point the app directly at the real path of this directory under the repo (the bookmark resolves more reliably against a real path).

## Setup

See the "Safari Userscripts" section in the top-level [README.md](../README.md) for the full installation and Save Location procedure.

## Scripts

- `ime-enter-fixer.user.js` — Stops the IME confirmation Enter from triggering a site's submit handler in Safari. Applies to all sites (`@include *://*/*`).

## Adding a new script

1. Create a file ending in `.user.js` in this directory.
1. Include a `// ==UserScript==` metadata block with at least `@name`, `@include` (or `@match`), and `@run-at`.
1. The Userscripts app picks it up automatically once the Save Location is set.
