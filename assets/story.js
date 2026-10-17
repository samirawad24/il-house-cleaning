/* Home page scroll story: a squeegee wipes each room from dirty to clean.
   Runs only when the visitor allows motion; otherwise CSS shows the clean house
   and the steps as a plain list. */
(function () {
  "use strict";
  var root = document.documentElement;
  if (!root.classList.contains("motion") || !window.gsap || !window.ScrollTrigger) {
    root.classList.remove("motion");
    return;
  }
  gsap.registerPlugin(ScrollTrigger);

  var ROOMS = {
    kitchen: [568, 534, 318, 252],
    bath: [530, 262, 356, 244],
    bed: [114, 262, 392, 244],
    living: [114, 534, 440, 252]
  };
  var ORDER = ["kitchen", "bath", "bed", "living"];
  var WIPE = 2;
  var steps = gsap.utils.toArray(".step");
  var tl = gsap.timeline({ paused: true, defaults: { ease: "none" } });

  gsap.set(".sun", { y: 150 });
  ORDER.forEach(function (n) {
    var r = ROOMS[n];
    gsap.set("#sq-" + n, { x: r[0], y: r[1], opacity: 0 });
  });

  function swap(from, to, at) {
    tl.to(steps[from], { autoAlpha: 0, y: -18, duration: 0.35, ease: "power1.in" }, at);
    tl.fromTo(steps[to], { autoAlpha: 0, y: 18 }, { autoAlpha: 1, y: 0, duration: 0.4, ease: "power2.out" }, at + 0.3);
  }

  var t = 1.8;
  ORDER.forEach(function (n, i) {
    var r = ROOMS[n];
    swap(i, i + 1, t - 0.5);
    tl.set("#sq-" + n, { opacity: 1 }, t);
    tl.fromTo(["#wd-" + n, "#wc-" + n], { attr: { width: 0 } }, { attr: { width: r[2] }, duration: WIPE, ease: "power1.inOut" }, t);
    tl.fromTo("#sq-" + n, { x: r[0] }, { x: r[0] + r[2], duration: WIPE, ease: "power1.inOut" }, t);
    tl.set("#sq-" + n, { opacity: 0 }, t + WIPE);
    t += WIPE + 0.6;
  });

  swap(4, 5, t - 0.3);
  tl.to("#outside-dirt", { opacity: 0, duration: 1.1, ease: "power1.inOut" }, t);
  tl.to(".sun", { y: 0, duration: 1.4, ease: "power2.out" }, t);
  tl.to("#outside-clean", { opacity: 1, duration: 0.8 }, t + 0.6);
  tl.to({}, { duration: 0.8 });

  ScrollTrigger.create({
    trigger: "#story",
    start: "top top",
    end: "bottom bottom",
    scrub: 0.6,
    animation: tl
  });
})();
