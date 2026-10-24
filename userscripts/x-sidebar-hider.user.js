// ==UserScript==
// @name         X Sidebar Hider
// @namespace    https://github.com/ikuwow/dotfiles
// @version      0.1.1
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
// every box is matched by data-testid or link target.
// Who-to-follow is matched by its "Show more" link to /i/connect_people,
// since a post page's Relevant people box is the same aside of UserCells
// without that link.
// The trend and who-to-follow rules hide the box's wrapper, the direct child
// of the sidebar's box stack, so the box's border and the stack's gap go with
// it. The search box and the footer share that stack, so the stack stays.
// The news box's depth under the stack is unconfirmed, so the first news rule
// hides only its direct parent and skips that parent when it holds the search
// box, which is the case where the parent is the stack itself. The second
// news rule hides the news box in every case.
// Scoped to sidebarColumn, since the Explore page lists trends with the same
// data-testid in its main column.
var style = document.createElement('style');
style.textContent = [
    '[data-testid="sidebarColumn"] div:has(> [data-testid="news_sidebar"]):not(:has([data-testid="SearchBox_Search_Input"])) { display: none !important; }',
    '[data-testid="sidebarColumn"] [data-testid="news_sidebar"] { display: none !important; }',
    '[data-testid="sidebarColumn"] div:has(> section [data-testid="trend"]) { display: none !important; }',
    '[data-testid="sidebarColumn"] div:has(> div > aside > a[href^="/i/connect_people"]) { display: none !important; }'
].join('\n');
document.documentElement.append(style);
