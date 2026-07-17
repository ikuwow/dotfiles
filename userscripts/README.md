# userscripts

Safari user scripts loaded by the [Userscripts](https://github.com/quoid/userscripts) extension. This directory is set as the extension's Save Location so the scripts are version-controlled with the rest of the dotfiles.

The Userscripts extension keeps its Save Location as a macOS security-scoped bookmark, so point it at the real path of this directory under the repo rather than a `$HOME` symlink — the bookmark resolves more reliably against the real path, and it must be set once per Mac via the app's UI (no way to bootstrap it from the dotfiles deploy).

## Setup (one time per Mac, after `brew bundle`)

1. Enable the Userscripts extension in Safari → Settings → Extensions
1. Open the Userscripts popover from the Safari toolbar and click the gear icon to open the Settings modal
1. Click the cogs icon next to "Save Location" — this launches the Userscripts host app
1. In the host app, pick this repo's `userscripts/` directory as the Save Location
1. Back in the popover, every `.user.js` in this directory appears in the script list and is active automatically; reload any open Safari tabs to pick them up

## Scripts

- `ime-enter-fixer.user.js` — stops the IME confirmation Enter from triggering a site's submit handler in Safari, applied to all sites (`@include *://*/*`)
- `youtube-shorts-blocker.user.js` — hides the Shorts tab/shelf/thumbnails on YouTube and redirects `/shorts/<id>` URLs to the normal `/watch?v=<id>` player, scoped to `*://*.youtube.com/*`

## Adding a new script

1. Create a file ending in `.user.js` in this directory
1. Include a `// ==UserScript==` metadata block with at least `@name` and one of `@include` / `@match`
1. Add `@run-at document-start` when the script needs to hook events before the page's own listeners attach (defaults to `document-end` if omitted)
1. The Userscripts extension picks it up automatically once the Save Location is set
