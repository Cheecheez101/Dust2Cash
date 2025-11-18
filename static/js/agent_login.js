// static/js/agent_login.js
// Robust, accessible client-side behaviour for the Agent Login form

(function () {
  'use strict';

  function qs(selector, root = document) {
    return root.querySelector(selector);
  }

  function createToggleIcon() {
    const icon = document.createElement('button');
    icon.type = 'button';
    icon.className = 'pw-toggle';
    icon.setAttribute('aria-label', 'Show password');
    icon.innerHTML = '<i class="fas fa-eye-slash" aria-hidden="true"></i>';
    return icon;
  }

  document.addEventListener('DOMContentLoaded', () => {
    const form = qs('#agent-form');
    if (!form) return;

    const usernameInput = qs("input[name='username']", form);
    const passwordInput = qs("input[name='password']", form);
    const forgotLink = qs('.forgot-link', form);
    const feedback = qs('#form-feedback', form);

    // Client-side validation with accessible feedback
    form.addEventListener('submit', (e) => {
      if (!usernameInput || !passwordInput) return; // nothing to validate
      const user = usernameInput.value.trim();
      const pass = passwordInput.value.trim();

      if (!user || !pass) {
        e.preventDefault();
        const msg = 'Please enter both username and password.';
        if (feedback) {
          feedback.hidden = false;
          feedback.textContent = msg;
        } else {
          alert(msg);
        }
        usernameInput.focus();
      }
    });

    // Toggle password visibility with accessible button
    if (passwordInput) {
      const wrap = passwordInput.closest('.password-wrap') || passwordInput.parentNode;
      const toggle = createToggleIcon();

      // Place toggle button after the password input
      wrap.appendChild(toggle);

      function updateToggleLabel() {
        const isHidden = passwordInput.type === 'password';
        toggle.setAttribute('aria-label', isHidden ? 'Show password' : 'Hide password');
        toggle.querySelector('i').className = isHidden ? 'fas fa-eye-slash' : 'fas fa-eye';
      }

      toggle.addEventListener('click', () => {
        if (passwordInput.type === 'password') {
          passwordInput.type = 'text';
        } else {
          passwordInput.type = 'password';
        }
        updateToggleLabel();
        passwordInput.focus();
      });

      // Keyboard support
      toggle.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          toggle.click();
        }
      });

      updateToggleLabel();
    }

    // Forgot password placeholder behaviour (non-destructive)
    if (forgotLink) {
      forgotLink.addEventListener('click', (e) => {
        e.preventDefault();
        // Friendly guidance; replace with real flow as needed
        if (feedback) {
          feedback.hidden = false;
          feedback.textContent = 'Please contact the system administrator to reset your agent password.';
        } else {
          alert('Please contact the system administrator to reset your agent password.');
        }
      });
    }

    // Gentle overlay fade-in (non-blocking)
    const overlay = qs('.overlay');
    if (overlay) {
      overlay.style.opacity = 0;
      // Use requestAnimationFrame to avoid layout thrash
      requestAnimationFrame(() => {
        overlay.style.transition = 'opacity 900ms ease';
        overlay.style.opacity = 1;
      });
    }
  });
})();