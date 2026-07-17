// ==UserScript==
// @name         YouTube Shorts Blocker
// @description  Hide Shorts entry points and redirect /shorts/<id> to the normal /watch?v=<id> player
// @run-at       document-start
// @include      *://*.youtube.com/*
// ==/UserScript==
// document.head may not exist yet at document-start, so the style is appended
// to documentElement, which is always available.
// YouTube is a SPA: same-tab navigations don't reload the document, so the
// redirect check and the shelf-hiding toggle also run on `yt-navigate-finish`.
// Shorts shelves and Shorts thumbnails are kept visible on /feed/subscriptions
// so Shorts from subscribed channels remain reachable; the shelf-hiding rules
// are gated behind a class on <html> that is removed on that page.
var HIDE_SHELVES_CLASS = 'shorts-blocker-hide-shelves';

var style = document.createElement('style');
style.textContent = [
    'ytd-guide-entry-renderer:has(a[title="Shorts"]) { display: none !important; }',
    'ytd-mini-guide-entry-renderer:has(a[title="Shorts"]) { display: none !important; }',
    'ytd-rich-shelf-renderer[is-shorts] { display: none !important; }',
    'html.' + HIDE_SHELVES_CLASS + ' ytd-reel-shelf-renderer { display: none !important; }',
    'html.' + HIDE_SHELVES_CLASS + ' ytd-video-renderer:has(a[href^="/shorts/"]) { display: none !important; }',
    'html.' + HIDE_SHELVES_CLASS + ' ytd-rich-item-renderer:has(a[href^="/shorts/"]) { display: none !important; }'
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
    var extra = location.search ? '&' + location.search.slice(1) : '';
    location.replace('/watch?v=' + id + extra);
}

function updateShelfHiding() {
    var onSubscriptions = location.pathname === '/feed/subscriptions';
    document.documentElement.classList.toggle(HIDE_SHELVES_CLASS, !onSubscriptions);
}

function onNavigate() {
    redirectIfShort();
    updateShelfHiding();
}

onNavigate();
window.addEventListener('yt-navigate-finish', onNavigate);
