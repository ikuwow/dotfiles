// ==UserScript==
// @name         YouTube Shorts Normalizer
// @description  Treat YouTube Shorts as normal videos: hide the sidebar Shorts entry and redirect the swipeable Shorts player to the normal /watch player
// @run-at       document-start
// @include      *://*.youtube.com/*
// ==/UserScript==
// document.head may not exist yet at document-start, so the style is appended
// to documentElement, which is always available.
// The only element that is hidden is the sidebar Shorts entry (expanded and
// mini variants) — it is the direct entry point to the swipeable feed at
// /shorts. Every other appearance of Shorts (home shelf, search shelf,
// individual thumbnails, channel Shorts tabs) stays visible so Shorts can
// be watched as regular videos.
// The sidebar Shorts entry has no `href` on its <a> (YouTube handles the
// navigation via an internal SPA endpoint) and its title is localized, so
// neither an href nor a title selector matches across locales. Match by the
// Shorts icon's SVG `path d` prefix instead — locale-independent and unique
// to the Shorts button in the guide.
// YouTube is a SPA: same-tab navigations don't reload the document. In-page
// clicks on Shorts links are caught in the capture phase before YouTube's own
// router runs, so the swipeable Shorts UI never renders. URL-bar navigations
// and any clicks not caught by the interceptor are handled by
// `yt-navigate-finish`.
var style = document.createElement('style');
style.textContent = [
    'ytd-guide-entry-renderer:has(svg path[d^="m13.467 1.19"]) { display: none !important; }',
    'ytd-mini-guide-entry-renderer:has(svg path[d^="m13.467 1.19"]) { display: none !important; }'
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
    if (location.pathname === '/shorts') {
        location.replace('/');
        return;
    }
    if (!location.pathname.startsWith('/shorts/')) {
        return;
    }
    var target = shortsPathToWatch(location.pathname + location.search);
    location.replace(target || '/');
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

redirectIfShort();
window.addEventListener('yt-navigate-finish', redirectIfShort);
