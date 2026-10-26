// ==UserScript==
// @name         X Declutter
// @namespace    https://github.com/ikuwow/dotfiles
// @version      0.3.2
// @downloadURL  https://raw.githubusercontent.com/ikuwow/dotfiles/main/userscripts/x-declutter.user.js
// @updateURL    https://raw.githubusercontent.com/ikuwow/dotfiles/main/userscripts/x-declutter.user.js
// @description  Hide distracting parts of X: the right sidebar's news, trends, and who-to-follow boxes, the Grok and Calls entries in the left navigation, and the Discover more posts under a post's replies
// @run-at       document-start
// @include      *://x.com/*
// ==/UserScript==
// The sidebar and navigation rules are CSS, and :has() keeps applying as X
// re-renders. Discover more needs a measured offset, so it uses one observer,
// which holds nothing that grows over a long-lived SPA session.
// document.head may not exist yet at document-start, so the style is appended
// to documentElement, which is always available.
// X's class names are generated, and aria-labels follow the UI language, so
// every element is matched by data-testid, link target, or tag.
//
// Right sidebar:
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
//
// Left navigation:
// The Grok entry has no data-testid, so it is matched by its link target.
var style = document.createElement('style');
style.textContent = [
    '[data-testid="sidebarColumn"] div:has(> [data-testid="news_sidebar"]):not(:has([data-testid="SearchBox_Search_Input"])) { display: none !important; }',
    '[data-testid="sidebarColumn"] [data-testid="news_sidebar"] { display: none !important; }',
    '[data-testid="sidebarColumn"] div:has(> section [data-testid="trend"]) { display: none !important; }',
    '[data-testid="sidebarColumn"] div:has(> div > aside > a[href^="/i/connect_people"]) { display: none !important; }',
    'nav[role="navigation"] > a[href="/i/grok"] { display: none !important; }',
    'nav[role="navigation"] > a[data-testid="AppTabBar_Calls_Link"] { display: none !important; }'
].join('\n');
document.documentElement.append(style);

// Discover more:
// A post page's conversation timeline appends recommended posts under a
// heading cell, the only cell in that timeline holding an h2. The timeline is
// virtualized: cells are absolutely positioned and unmount once scrolled far
// enough away. The timeline is clipped at the heading's offset, which removes
// the blank space the hidden cells would leave and keeps the page from
// scrolling into them, so the heading stays mounted.
// The clip applies only on /status/ paths, which also cover the photo viewer,
// so a heading cell in another timeline, such as a who-to-follow module on
// home, cannot clip that timeline.
// The observer keeps no state of its own: clipped timelines are found again
// by their data attribute, and at most one measurement is pending per frame.
var CLIP_ATTR = 'data-x-declutter-clip';
var pending = false;

function clipDiscoverMore() {
    pending = false;
    var headings = /\/status\/\d+/.test(location.pathname)
        ? document.querySelectorAll('[data-testid="cellInnerDiv"]:has(h2)')
        : [];
    var clipped = new Set();
    headings.forEach(function (cell) {
        var list = cell.parentElement;
        var timeline = list.parentElement;
        var offset = cell.getBoundingClientRect().top - list.getBoundingClientRect().top;
        // A cell not yet measured sits at offset 0; clipping there would hide the whole timeline.
        if (offset <= 0) {
            return;
        }
        var maxHeight = offset + 'px';
        if (timeline.style.maxHeight !== maxHeight) {
            timeline.style.maxHeight = maxHeight;
            timeline.style.overflow = 'hidden';
            timeline.setAttribute(CLIP_ATTR, '');
        }
        clipped.add(timeline);
    });
    document.querySelectorAll('[' + CLIP_ATTR + ']').forEach(function (timeline) {
        if (!clipped.has(timeline)) {
            timeline.style.maxHeight = '';
            timeline.style.overflow = '';
            timeline.removeAttribute(CLIP_ATTR);
        }
    });
}

new MutationObserver(function () {
    if (!pending) {
        pending = true;
        requestAnimationFrame(clipDiscoverMore);
    }
}).observe(document.documentElement, { childList: true, subtree: true, attributes: true, attributeFilter: ['style'] });
