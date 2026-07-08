(function () {
  function ensureMenuStyles() {
    if (document.getElementById("static-mobile-menu-style")) {
      return;
    }
    var style = document.createElement("style");
    style.id = "static-mobile-menu-style";
    style.textContent = [
      ".header-menu-sidebar{position:fixed!important;inset:0!important;z-index:999999!important;display:block!important;visibility:hidden!important;opacity:0!important;pointer-events:none!important;transition:opacity .2s ease,visibility .2s ease!important}",
      ".header-menu-sidebar-bg{position:absolute!important;inset:0!important;background:rgba(0,0,0,.45)!important}",
      ".header-menu-sidebar-inner{position:absolute!important;top:0!important;right:0!important;bottom:0!important;width:min(86vw,360px)!important;max-width:360px!important;overflow-y:auto!important;background:#fff!important;box-shadow:-16px 0 34px rgba(0,0,0,.22)!important;transform:translateX(105%)!important;transition:transform .24s ease!important;padding:20px 22px!important}",
      "body.is-menu-sidebar .header-menu-sidebar,body.menu-sidebar-open .header-menu-sidebar{visibility:visible!important;opacity:1!important;pointer-events:auto!important}",
      "body.is-menu-sidebar .header-menu-sidebar-inner,body.menu-sidebar-open .header-menu-sidebar-inner{transform:translateX(0)!important}",
      "body.is-menu-sidebar,body.menu-sidebar-open{overflow:hidden!important}",
      ".menu-mobile-toggle.is-active .hamburger-inner,.menu-mobile-toggle.is-active .hamburger-inner:before,.menu-mobile-toggle.is-active .hamburger-inner:after{background-color:currentColor!important}",
      "#header-menu-sidebar .primary-menu-ul{display:block!important;margin:0!important;padding:0!important;list-style:none!important}",
      "#header-menu-sidebar .primary-menu-ul li{display:block!important;margin:0!important}",
      "#header-menu-sidebar .primary-menu-ul a{display:block!important;padding:12px 0!important;color:#1f2d33!important;text-decoration:none!important;border-bottom:1px solid rgba(0,0,0,.08)!important}",
      "#header-menu-sidebar .wpml-ls-current-language{margin-top:14px!important;padding-top:12px!important;border-top:2px solid #91bc06!important}",
      "#header-menu-sidebar .wpml-ls-current-language:before{content:'Taal / Language'!important;display:block!important;margin:0 0 8px!important;color:#1d81c3!important;font-size:13px!important;font-weight:700!important;text-transform:uppercase!important;letter-spacing:.04em!important}",
      "#header-menu-sidebar .wpml-ls-current-language>a{font-weight:700!important;color:#1d81c3!important}",
      "#header-menu-sidebar .wpml-ls-item img{display:inline-block!important;margin-right:8px!important;vertical-align:-1px!important}",
      "#header-menu-sidebar .sub-menu{display:block!important;position:static!important;opacity:1!important;visibility:visible!important;box-shadow:none!important;margin:0 0 0 16px!important;padding:0!important;background:transparent!important}",
      "@media (min-width:1025px){.header-menu-sidebar{display:none!important}}"
    ].join("");
    document.head.appendChild(style);
  }

  function setMenu(open) {
    ensureMenuStyles();
    document.body.classList.toggle("is-menu-sidebar", open);
    document.body.classList.toggle("menu-sidebar-open", open);
    document.querySelectorAll(".menu-mobile-toggle").forEach(function (button) {
      button.classList.toggle("is-active", open);
      button.setAttribute("aria-expanded", open ? "true" : "false");
    });
    document.querySelectorAll("#header-menu-sidebar, .header-menu-sidebar").forEach(function (panel) {
      panel.setAttribute("aria-hidden", open ? "false" : "true");
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    ensureMenuStyles();
    document.querySelectorAll(".menu-mobile-toggle").forEach(function (button) {
      button.setAttribute("aria-expanded", "false");
      button.setAttribute("aria-controls", "header-menu-sidebar");
    });
    document.querySelectorAll("#header-menu-sidebar, .header-menu-sidebar").forEach(function (panel) {
      panel.setAttribute("aria-hidden", "true");
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

    if (event.target && event.target.id === "header-menu-sidebar-bg") {
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
