// ==UserScript==
// @name         YouTube Shorts Blocker
// @description  Hide Shorts entry points and redirect /shorts/<id> to the normal /watch?v=<id> player
// @run-at       document-start
// @include      *://*.youtube.com/*
// ==/UserScript==
// document.head may not exist yet at document-start, so the style is appended
// to documentElement, which is always available.
// The sidebar Shorts entry has no `href` on its <a> (YouTube handles the
// navigation via an internal SPA endpoint) and its title is localized, so
// neither an href nor a title match works. Match by the Shorts icon's SVG
// `path d` prefix instead — it is stable across locales and is unique to
// the Shorts button in the guide.
// YouTube is a SPA: same-tab navigations don't reload the document. In-page
// clicks on Shorts links are caught in the capture phase before YouTube's own
// router runs, so the Shorts UI never renders. URL-bar navigations and any
// clicks not caught by the interceptor are handled by `yt-navigate-finish`.
// Shorts shelves and Shorts thumbnails are kept visible on /feed/subscriptions
// so Shorts from subscribed channels remain reachable; the shelf-hiding rules
// are gated behind a class on <html> that is removed on that page.
var HIDE_SHELVES_CLASS = 'shorts-blocker-hide-shelves';

var style = document.createElement('style');
style.textContent = [
    'ytd-guide-entry-renderer:has(svg path[d^="m13.467 1.19"]) { display: none !important; }',
    'ytd-mini-guide-entry-renderer:has(svg path[d^="m13.467 1.19"]) { display: none !important; }',
    'ytd-rich-shelf-renderer[is-shorts] { display: none !important; }',
    'html.' + HIDE_SHELVES_CLASS + ' ytd-reel-shelf-renderer { display: none !important; }',
    'html.' + HIDE_SHELVES_CLASS + ' ytd-video-renderer:has(a[href^="/shorts/"]) { display: none !important; }',
    'html.' + HIDE_SHELVES_CLASS + ' ytd-rich-item-renderer:has(a[href^="/shorts/"]) { display: none !important; }'
].join('\n');
document.documentElement.append(style);

function shortsPathToWatch(path) {
    var queryIndex = path.indexOf('?');
    var pathname = queryIndex === -1 ? path : path.slice(0, queryIndex);
    var search = queryIndex === -1 ? '' : path.slice(queryIndex + 1);
    var id = pathname.slice('/shorts/'.length).split('/')[0];
    if (!id) {
        return null;
    }
    return '/watch?v=' + id + (search ? '&' + search : '');
}

function redirectIfShort() {
    if (!location.pathname.startsWith('/shorts/')) {
        return;
    }
    var target = shortsPathToWatch(location.pathname + location.search);
    location.replace(target || '/');
}

function updateShelfHiding() {
    var onSubscriptions = location.pathname === '/feed/subscriptions';
    document.documentElement.classList.toggle(HIDE_SHELVES_CLASS, !onSubscriptions);
}

function onNavigate() {
    redirectIfShort();
    updateShelfHiding();
}

document.addEventListener('click', function(event) {
    if (event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) {
        return;
    }
    var anchor = event.target.closest && event.target.closest('a[href^="/shorts/"]');
    if (!anchor) {
        return;
    }
    var target = shortsPathToWatch(anchor.getAttribute('href'));
    if (!target) {
        return;
    }
    event.preventDefault();
    event.stopPropagation();
    location.assign(target);
}, {capture: true});

onNavigate();
window.addEventListener('yt-navigate-finish', onNavigate);
