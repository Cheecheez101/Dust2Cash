// static/js/landing.js
// Robust toggle for sign up / sign in panels
(function () {
  'use strict';

  // Keep references for cleanup
  const listeners = [];

  function safeAddListener(el, event, fn, opts) {
    if (!el) return;
    el.addEventListener(event, fn, opts);
    listeners.push({ el, event, fn, opts });
  }

  function safeRemoveAllListeners() {
    listeners.forEach(({ el, event, fn, opts }) => {
      try { el.removeEventListener(event, fn, opts); } catch (err) { /* ignore */ }
    });
    listeners.length = 0;
  }

  function activatePanel(container) {
    if (!container) return;
    container.classList.add('right-panel-active');
    // Accessibility hints
    container.setAttribute('data-panel-state', 'signup');
  }

  function deactivatePanel(container) {
    if (!container) return;
    container.classList.remove('right-panel-active');
    container.setAttribute('data-panel-state', 'signin');
  }

  function onKeyActivate(e, cb) {
    // Activate on Enter or Space
    if (e.key === 'Enter' || e.key === ' ' || e.key === 'Spacebar') {
      e.preventDefault();
      cb();
    }
  }

  document.addEventListener('DOMContentLoaded', function () {
    try {
      // primary selectors by id, but allow fallbacks using data attributes or class names
      const signUpButton = document.getElementById('signUp') || document.querySelector('[data-signup]') || document.querySelector('.js-signup');
      const signInButton = document.getElementById('signIn') || document.querySelector('[data-signin]') || document.querySelector('.js-signin');

      // The container that gets the toggled class; fallback to a container with .auth-container or #container
      const container = document.getElementById('container') || document.querySelector('.auth-container') || document.querySelector('#main');

      if (!container) {
        // Nothing to do; don't throw an error
        console.warn('Landing JS: container element not found, auth toggles disabled.');
        return;
      }

      // Initialize ARIA state
      container.setAttribute('data-panel-state', container.classList.contains('right-panel-active') ? 'signup' : 'signin');

      // Click handlers
      const handleSignUp = function () { activatePanel(container); };
      const handleSignIn = function () { deactivatePanel(container); };

      // Attach handlers safely
      safeAddListener(signUpButton, 'click', handleSignUp);
      safeAddListener(signInButton, 'click', handleSignIn);

      // Keyboard support for accessibility
      safeAddListener(signUpButton, 'keydown', function (e) { onKeyActivate(e, handleSignUp); });
      safeAddListener(signInButton, 'keydown', function (e) { onKeyActivate(e, handleSignIn); });

      // Optional: close panel if user navigates away or page is hidden
      safeAddListener(window, 'pagehide', function () { safeRemoveAllListeners(); });
      safeAddListener(window, 'beforeunload', function () { safeRemoveAllListeners(); });

    } catch (err) {
      // Catch all — prevents this script from breaking other scripts on the page
      console.error('Landing JS initialization error', err);
    }
  });
})();
