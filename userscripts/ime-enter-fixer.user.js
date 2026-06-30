// ==UserScript==
// @name         IME Enter Fixer
// @description  Prevent Safari from sending the IME confirmation Enter as a submit keystroke
// @run-at       document-start
// @include      *://*/*
// ==/UserScript==
document.addEventListener('keydown', function(event) {
    if ((event.key === 'Enter' && event.isComposing) || event.keyCode === 229) {
        event.stopPropagation();
    }
}, {capture: true});
