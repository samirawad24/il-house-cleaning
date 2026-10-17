/* Home page scroll story: a squeegee wipes each room from dirty to clean while the
   room list beside it ticks off. Scroll drives it, so it runs for every visitor;
   reduced-motion visitors only lose the buzzing flies. If GSAP fails to load,
   CSS shows the clean house instead. */
(function () {
  "use strict";
  var root = document.documentElement;
  if (!window.gsap || !window.ScrollTrigger) { root.classList.remove("motion"); return; }
  gsap.registerPlugin(ScrollTrigger);

  var ROOMS = {
    kitchen: [568, 534, 318, 252],
    bath: [530, 262, 356, 244],
    bed: [114, 262, 392, 244],
    living: [114, 534, 440, 252]
  };
  var ORDER = ["kitchen", "bath", "bed", "living"];
  var WIPE = 2;
  var todo = document.getElementById("todo");
  var now = document.getElementById("todo-now");
  var rows = ORDER.map(function (n) { return todo.querySelector('[data-room="' + n + '"]'); });
  var spans = [];
  var tl = gsap.timeline({ paused: true, defaults: { ease: "none" } });

  gsap.set(".sun", { y: 150 });
  ORDER.forEach(function (n) {
    var r = ROOMS[n];
    gsap.set("#sq-" + n, { x: r[0], y: r[1], opacity: 0 });
  });

  var t = 1.2;
  ORDER.forEach(function (n) {
    var r = ROOMS[n];
    tl.set("#sq-" + n, { opacity: 1 }, t);
    tl.fromTo(["#wd-" + n, "#wc-" + n], { attr: { width: 0 } }, { attr: { width: r[2] }, duration: WIPE, ease: "power1.inOut" }, t);
    tl.fromTo("#sq-" + n, { x: r[0] }, { x: r[0] + r[2], duration: WIPE, ease: "power1.inOut" }, t);
    tl.set("#sq-" + n, { opacity: 0 }, t + WIPE);
    spans.push([t - 0.4, t + WIPE]);
    t += WIPE + 0.5;
  });
  var finish = t - 0.2;
  tl.to("#outside-dirt", { opacity: 0, duration: 1.1, ease: "power1.inOut" }, finish);
  tl.to(".sun", { y: 0, duration: 1.4, ease: "power2.out" }, finish);
  tl.to("#outside-clean", { opacity: 1, duration: 0.8 }, finish + 0.6);
  tl.to({}, { duration: 0.9 });

  var last = "";
  function sync() {
    var time = tl.time();
    var key = "";
    var active = -1;
    rows.forEach(function (li, i) {
      var on = time >= spans[i][0] && time < spans[i][1];
      var done = time >= spans[i][1];
      li.classList.toggle("on", on);
      li.classList.toggle("done", done);
      if (on) active = i;
      key += on ? "o" : done ? "d" : "-";
    });
    var all = time >= finish;
    key += all ? "A" : "";
    if (key === last) return;
    last = key;
    todo.classList.toggle("all", all);
    var shown = active > -1 ? active : rows.findIndex(function (li) { return !li.classList.contains("done"); });
    if (shown > -1) now.textContent = rows[shown].querySelector(".todo-d").textContent;
  }
  tl.eventCallback("onUpdate", sync);
  sync();

  ScrollTrigger.create({
    trigger: "#story",
    start: "top top",
    end: "bottom bottom",
    scrub: 0.6,
    animation: tl
  });
})();
