# userscripts

These userscripts are consumed by two different runtimes: Safari's [Userscripts](https://github.com/quoid/userscripts) extension reads this directory directly as its Save Location, and Chrome's [Violentmonkey](https://violentmonkey.github.io/) installs each script from its GitHub raw URL. Both are version-controlled with the rest of the dotfiles.

The Userscripts extension keeps its Save Location as a macOS security-scoped bookmark, so point it at the real path of this directory under the repo rather than a `$HOME` symlink — the bookmark resolves more reliably against the real path, and it must be set once per Mac via the app's UI (no way to bootstrap it from the dotfiles deploy).

## Setup (Safari, one time per Mac, after `brew bundle`)

1. Enable the Userscripts extension in Safari → Settings → Extensions
1. Open the Userscripts popover from the Safari toolbar and click the gear icon to open the Settings modal
1. Click the cogs icon next to "Save Location" — this launches the Userscripts host app
1. In the host app, pick this repo's `userscripts/` directory as the Save Location
1. Back in the popover, every `.user.js` in this directory appears in the script list and is active automatically; reload any open Safari tabs to pick them up

## Setup (Chrome, one time per browser)

1. Install Violentmonkey from the Chrome Web Store
1. Open `chrome://extensions/`, click Violentmonkey's Details, and enable "Allow User Scripts" (Chrome 138 removed the global developer-mode requirement in favor of this per-extension toggle)
1. Open each raw URL in Chrome; Violentmonkey detects the userscript metadata block and shows an install prompt: `https://raw.githubusercontent.com/ikuwow/dotfiles/main/userscripts/ime-enter-fixer.user.js` and `https://raw.githubusercontent.com/ikuwow/dotfiles/main/userscripts/youtube-shorts-normalizer.user.js`
1. Reload any open tabs on the target sites (`claude.ai`, `youtube.com`) to pick the scripts up

## Scripts

- `ime-enter-fixer.user.js` — stops the IME confirmation Enter from triggering a site's submit handler in Safari, scoped to `*://claude.ai/*`
- `youtube-shorts-normalizer.user.js` — treats YouTube Shorts as normal videos: Shorts thumbnails stay visible everywhere, but clicking one or navigating to `/shorts/<id>` opens the standard `/watch?v=<id>` player instead of the swipeable feed. Also hides the sidebar Shorts entry, which has no equivalent non-swipe landing. Scoped to `*://*.youtube.com/*`

## Adding a new script

1. Create a file ending in `.user.js` in this directory
1. Include a `// ==UserScript==` metadata block with `@name`, `@namespace`, `@version`, `@downloadURL`, `@updateURL`, and one of `@include` / `@match`
1. `@downloadURL` and `@updateURL` both point at the file's raw URL: `https://raw.githubusercontent.com/ikuwow/dotfiles/main/userscripts/<basename>.user.js`
1. Add `@run-at document-start` when the script needs to hook events before the page's own listeners attach (defaults to `document-end` if omitted)
1. The Userscripts extension picks it up automatically once the Save Location is set; for Chrome, open the raw URL in a tab and let Violentmonkey prompt for install

## Updating a script

1. Edit the file
1. Bump `// @version` (semver patch increment is enough); the `check-userscript-version` pre-commit hook rejects commits that modify a userscript without bumping this field
1. Commit and push; Safari picks changes up from the Save Location automatically, and Chrome refreshes via Violentmonkey's periodic update check (or the "Check all for updates" button in the dashboard for immediate pickup)
