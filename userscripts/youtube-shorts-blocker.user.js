// ==UserScript==
// @name         YouTube Shorts Blocker
// @description  Hide Shorts entry points and redirect /shorts/<id> to the normal /watch?v=<id> player
// @run-at       document-start
// @include      *://*.youtube.com/*
// ==/UserScript==
// document.head may not exist yet at document-start, so the style is appended
// to documentElement, which is always available.
// YouTube is a SPA: same-tab navigations don't reload the document, so the
// redirect check also runs on `yt-navigate-finish` to catch clicks into
// /shorts/<id> after the initial page load.
var style = document.createElement('style');
style.textContent = [
    'ytd-guide-entry-renderer:has(a[title="Shorts"]) { display: none !important; }',
    'ytd-mini-guide-entry-renderer:has(a[title="Shorts"]) { display: none !important; }',
    'ytd-rich-shelf-renderer[is-shorts] { display: none !important; }',
    'ytd-reel-shelf-renderer { display: none !important; }',
    'ytd-video-renderer:has(a[href^="/shorts/"]) { display: none !important; }',
    'ytd-rich-item-renderer:has(a[href^="/shorts/"]) { display: none !important; }'
].join('\n');
document.documentElement.append(style);

function redirectIfShort() {
    if (!location.pathname.startsWith('/shorts/')) {
        return;
    }
    var id = location.pathname.slice('/shorts/'.length).split('/')[0];
    if (!id) {
        location.replace('/');
        return;
    }
    location.replace('/watch?v=' + id + location.search);
}

redirectIfShort();
window.addEventListener('yt-navigate-finish', redirectIfShort);
