(function () {
  function setMenu(open) {
    document.body.classList.toggle("is-menu-sidebar", open);
    document.querySelectorAll(".menu-mobile-toggle").forEach(function (button) {
      button.classList.toggle("is-active", open);
      button.setAttribute("aria-expanded", open ? "true" : "false");
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".menu-mobile-toggle").forEach(function (button) {
      button.setAttribute("aria-expanded", "false");
      button.setAttribute("aria-controls", "header-menu-sidebar");
    });
  });

  document.addEventListener("click", function (event) {
    if (event.target.closest(".menu-mobile-toggle")) {
      event.preventDefault();
      setMenu(!document.body.classList.contains("is-menu-sidebar"));
      return;
    }

    if (event.target.closest(".close-sidebar-panel")) {
      event.preventDefault();
      setMenu(false);
      return;
    }

    if (
      document.body.classList.contains("is-menu-sidebar") &&
      !event.target.closest("#header-menu-sidebar") &&
      !event.target.closest(".menu-mobile-toggle")
    ) {
      setMenu(false);
    }
  });

  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape") {
      setMenu(false);
    }
  });
})();
