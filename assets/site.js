(function () {
  "use strict";
  var $ = function (s, el) { return (el || document).querySelector(s); };
  var $$ = function (s, el) { return Array.prototype.slice.call((el || document).querySelectorAll(s)); };

  // full-screen mobile menu
  var burger = $(".burger");
  var menu = $("#menu");
  if (burger && menu) {
    var setMenu = function (open) {
      burger.setAttribute("aria-expanded", String(open));
      document.body.classList.toggle("menu-on", open);
      if (open) {
        menu.hidden = false;
        requestAnimationFrame(function () { requestAnimationFrame(function () { menu.classList.add("open"); }); });
      } else {
        menu.classList.remove("open");
        setTimeout(function () { if (burger.getAttribute("aria-expanded") === "false") menu.hidden = true; }, 450);
      }
    };
    burger.addEventListener("click", function () { setMenu(burger.getAttribute("aria-expanded") !== "true"); });
    $$("a", menu).forEach(function (a) { a.addEventListener("click", function () { setMenu(false); }); });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && burger.getAttribute("aria-expanded") === "true") { setMenu(false); burger.focus(); }
    });
    matchMedia("(min-width: 981px)").addEventListener("change", function (m) { if (m.matches) setMenu(false); });
  }

  // fade sections up as they come into view
  document.documentElement.classList.add("ready");
  var rev = $$("[data-r]");
  if ("IntersectionObserver" in window && !document.documentElement.classList.contains("rm")) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { en.target.classList.add("in"); io.unobserve(en.target); }
      });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.08 });
    rev.forEach(function (el) { io.observe(el); });
  } else {
    rev.forEach(function (el) { el.classList.add("in"); });
  }

  // tabs (room checklist)
  $$("[data-tabs]").forEach(function (box) {
    var tabs = $$('[role="tab"]', box);
    function select(tab, focus) {
      tabs.forEach(function (t) {
        var on = t === tab;
        t.setAttribute("aria-selected", String(on));
        t.tabIndex = on ? 0 : -1;
        document.getElementById(t.getAttribute("aria-controls")).hidden = !on;
      });
      if (focus) tab.focus();
      tab.scrollIntoView({ block: "nearest", inline: "nearest" });
    }
    tabs.forEach(function (t, i) {
      t.addEventListener("click", function () { select(t); });
      t.addEventListener("keydown", function (e) {
        var n = null;
        if (e.key === "ArrowRight") n = tabs[(i + 1) % tabs.length];
        if (e.key === "ArrowLeft") n = tabs[(i - 1 + tabs.length) % tabs.length];
        if (e.key === "Home") n = tabs[0];
        if (e.key === "End") n = tabs[tabs.length - 1];
        if (n) { e.preventDefault(); select(n, true); }
      });
    });
  });

  // home page price picker: looks up prices the build already worked out
  var pt = $("#pt");
  if (pt) {
    var D = JSON.parse(pt.getAttribute("data-prices"));
    var m = function (n) { return "$" + n.toLocaleString("en-US"); };
    var upd = function () {
      var type = $('input[name="pt-type"]:checked', pt).value;
      var i = parseInt($('input[name="pt-size"]:checked', pt).value, 10);
      var e = D.t[type][i], h = D.h[i];
      $("#pt-price").textContent = m(e[0]) + " to " + m(e[1]);
      $("#pt-home").textContent = h.label;
      var note = "About " + e[2] + " hours for a team of two.";
      if (type === "standard") { var b = D.t.biweekly[i]; note = "Every 2 weeks: " + m(b[0]) + " to " + m(b[1]) + " per visit. " + note; }
      $("#pt-note").textContent = note;
      $("#pt-go").href = "quote/?type=" + type + "&beds=" + h.beds + "&full=" + h.full + "&half=" + h.half + "&sqft=" + h.sqft;
    };
    pt.addEventListener("change", upd);
  }
})();
