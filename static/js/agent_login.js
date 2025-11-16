// main.js for Dust2Cash Agent Login

document.addEventListener("DOMContentLoaded", () => {
  const form = document.querySelector("form");
  const usernameInput = form.querySelector("input[name='username']");
  const passwordInput = form.querySelector("input[name='password']");
  const forgotLink = form.querySelector("a[href='#']");

  // Simple client-side validation before submitting
  form.addEventListener("submit", (e) => {
    if (!usernameInput.value.trim() || !passwordInput.value.trim()) {
      e.preventDefault();
      alert("Please enter both username and password.");
    }
  });

  // Toggle password visibility
  const toggleIcon = document.createElement("i");
  toggleIcon.className = "fas fa-eye-slash";
  toggleIcon.style.cursor = "pointer";
  toggleIcon.style.marginLeft = "8px";

  passwordInput.parentNode.appendChild(toggleIcon);

  toggleIcon.addEventListener("click", () => {
    if (passwordInput.type === "password") {
      passwordInput.type = "text";
      toggleIcon.className = "fas fa-eye";
    } else {
      passwordInput.type = "password";
      toggleIcon.className = "fas fa-eye-slash";
    }
  });

  // Forgot password link (placeholder)
  forgotLink.addEventListener("click", (e) => {
    e.preventDefault();
    alert("Please contact the system administrator to reset your agent password.");
  });

  // Overlay animation (optional polish)
  const overlay = document.querySelector(".overlay");
  overlay.style.opacity = 0;
  setTimeout(() => {
    overlay.style.transition = "opacity 1s ease";
    overlay.style.opacity = 1;
  }, 200);
});
