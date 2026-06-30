// ==UserScript==
// @name         IME Enter Fixer
// @description  Prevent Safari from sending the IME confirmation Enter as a submit keystroke
// @run-at       document-start
// @include      *://*/*
// ==/UserScript==
// Safari clears `isComposing` before keydown for the IME confirmation Enter,
// so cover both signals: the modern `isComposing` flag and the legacy
// `keyCode === 229` that some WebKit input paths still emit.
document.addEventListener('keydown', function(event) {
    if ((event.key === 'Enter' && event.isComposing) || event.keyCode === 229) {
        event.stopPropagation();
    }
}, {capture: true});
