// ==UserScript==
// @name         RaenonX Popup Dismisser
// @namespace    https://github.com/ikuwow/dotfiles
// @version      0.1.2
// @downloadURL  https://raw.githubusercontent.com/ikuwow/dotfiles/main/userscripts/raenonx-popup-dismisser.user.js
// @updateURL    https://raw.githubusercontent.com/ikuwow/dotfiles/main/userscripts/raenonx-popup-dismisser.user.js
// @description  Dismiss the subscription popup that RaenonX shows every 30 minutes (7 with an ad blocker)
// @run-at       document-start
// @include      *://pks.raenonx.cc/*
// ==/UserScript==
// The popup is a Base UI dialog whose open state lives only in React, so it
// is closed through its own close button, the dialog's first button. Hiding
// it alone would leave the page scroll-locked and its other elements inert.
// Only a dialog with data-open is matched, so one playing its close
// transition is not clicked again.
// The popup's text follows the UI language and it carries no stable id or
// class of its own, so it is matched by the utm_source of its plan link.
// The close button stays disabled for the first moments after the popup
// opens, and a click or Escape in that window is ignored, so the button is
// clicked once its disabled attribute is removed. Until then the popup's
// portal is hidden so it does not flash.
// document.head may not exist yet at document-start, so the style is appended
// to documentElement, which is always available.
var POPUP_LINK = 'a[href*="utm_source=subscription_popup"]';

var style = document.createElement('style');
style.textContent = '[data-base-ui-portal]:has(' + POPUP_LINK + ') { visibility: hidden !important; }';
document.documentElement.append(style);

var pending = false;

function dismissPopup() {
    pending = false;
    var link = document.querySelector('[role="dialog"][data-open] ' + POPUP_LINK);
    if (!link) {
        return;
    }
    var closeButton = link.closest('[role="dialog"]').querySelector('button');
    if (closeButton && !closeButton.disabled) {
        closeButton.click();
    }
}

new MutationObserver(function () {
    if (!pending) {
        pending = true;
        requestAnimationFrame(dismissPopup);
    }
}).observe(document.documentElement, { childList: true, subtree: true, attributes: true, attributeFilter: ['disabled'] });
