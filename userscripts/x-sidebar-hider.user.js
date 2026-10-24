// ==UserScript==
// @name         X Sidebar Hider
// @namespace    https://github.com/ikuwow/dotfiles
// @version      0.1.0
// @downloadURL  https://raw.githubusercontent.com/ikuwow/dotfiles/main/userscripts/x-sidebar-hider.user.js
// @updateURL    https://raw.githubusercontent.com/ikuwow/dotfiles/main/userscripts/x-sidebar-hider.user.js
// @description  Hide the news, trends, and who-to-follow boxes in X's right sidebar
// @run-at       document-start
// @include      *://x.com/*
// ==/UserScript==
// Pure CSS with no observer or timer, so the script holds nothing that grows
// over a long-lived SPA session. :has() keeps applying as X re-renders.
// document.head may not exist yet at document-start, so the style is appended
// to documentElement, which is always available.
// X's class names are generated, and aria-labels follow the UI language, so
// every box is matched by the data-testid inside it. Each selector hides the
// box's wrapper, the direct child of the sidebar's box stack, so no border
// or gap is left behind. The search box and the footer share that stack.
// The news box's wrapper depth is unconfirmed, so its wrapper rule skips any
// element that holds the search box, which keeps a match on the whole stack
// from hiding the search box, and a second rule hides the news box itself.
// Scoped to sidebarColumn, since the Explore page lists trends with the same
// data-testid in its main column.
var style = document.createElement('style');
style.textContent = [
    '[data-testid="sidebarColumn"] div:has(> [data-testid="news_sidebar"]):not(:has([data-testid="SearchBox_Search_Input"])) { display: none !important; }',
    '[data-testid="sidebarColumn"] [data-testid="news_sidebar"] { display: none !important; }',
    '[data-testid="sidebarColumn"] div:has(> section [data-testid="trend"]) { display: none !important; }',
    '[data-testid="sidebarColumn"] div:has(> div > aside [data-testid="UserCell"]) { display: none !important; }'
].join('\n');
document.documentElement.append(style);
