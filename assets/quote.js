/* Price calculator, booking handoff and request forms.
   The price math matches estimate() in _src/build.py. Change both together. */
(function () {
  "use strict";
  var dataEl = document.getElementById("site-data");
  if (!dataEl) return;
  var D = JSON.parse(dataEl.textContent);
  var P = D.pricing;
  var $ = function (s, el) { return (el || document).querySelector(s); };
  var $$ = function (s, el) { return Array.prototype.slice.call((el || document).querySelectorAll(s)); };
  var money = function (n) { return "$" + Math.round(n).toLocaleString("en-US"); };
  var rnd = function (x, step) { return Math.floor(x / step + 0.5) * step; };
  var lastSummary = "";

  function estimate(o) {
    var core = P.base + o.beds * P.per_bedroom + o.full * P.per_full_bath + o.half * P.per_half_bath;
    core += Math.max(0, o.sqft - P.sqft_included) * P.per_extra_sqft;
    var typed = core * P.types[o.type].mult;
    var sub = typed * P.conditions[o.cond].mult;
    var lines = [[P.types[o.type].label + " clean", null]];
    if (o.cond !== "kept") lines.push([P.conditions[o.cond].label, sub - typed]);
    if (o.pets) { sub += P.pets; lines.push(["Pets", P.pets]); }
    var add = 0;
    P.addons.forEach(function (a) {
      if (o.addons.indexOf(a.id) > -1 && a.included.indexOf(o.type) === -1) {
        add += a.price;
        lines.push([a.label, a.price]);
      }
    });
    var total = sub + add;
    var disc = o.type === "standard" ? P.frequencies[o.freq].discount : 0;
    if (disc) lines.push([P.frequencies[o.freq].label + " discount", -total * disc]);
    var est = Math.max(P.min_price, total * (1 - disc));
    if (est > total * (1 - disc)) lines.push(["Minimum booking", est - total * (1 - disc)]);
    var hours = est / P.rate_per_cleaner_hour;
    return {
      lo: rnd(est * P.range_low, P.round_to),
      hi: rnd(est * P.range_high, P.round_to),
      hours: Math.max(1.5, Math.floor(hours * 2 + 0.5) / 2),
      team: Math.max(1, Math.floor(hours / P.team_size * 2 + 0.5) / 2),
      recurring: disc > 0,
      lines: lines
    };
  }

  /* ---------------------------------------------------------------- calculator */
  var form = $("#calc");
  if (form) {
    var params = new URLSearchParams(location.search);
    var setVal = function (name, v) {
      var els = $$('[name="' + name + '"]', form);
      els.forEach(function (el) {
        if (el.type === "radio") el.checked = el.value === v;
        else if (el.type === "checkbox") el.checked = v === "1";
        else el.value = v;
      });
    };
    ["type", "beds", "full", "half", "sqft", "cond", "freq", "pets", "zip"].forEach(function (k) {
      var v = params.get(k);
      if (v === null) return;
      if (k === "type" && !P.types[v]) return;
      if (k === "cond" && !P.conditions[v]) return;
      if (k === "freq" && !P.frequencies[v]) return;
      setVal(k, v);
    });
    var addParam = (params.get("add") || "").split(",");
    $$('input[name="addon"]', form).forEach(function (el) {
      if (addParam.indexOf(el.value) > -1) el.checked = true;
      el.dataset.user = el.checked ? "1" : "0";
      el.addEventListener("change", function () { el.dataset.user = el.checked ? "1" : "0"; });
    });

    var num = function (name, min, max, dflt) {
      var v = parseInt(form.elements[name].value, 10);
      if (isNaN(v)) return dflt;
      return Math.min(max, Math.max(min, v));
    };
    var radio = function (name) {
      var el = $('[name="' + name + '"]:checked', form);
      return el ? el.value : null;
    };

    var read = function () {
      var type = radio("type") || "standard";
      return {
        type: type,
        beds: num("beds", 0, 6, 3),
        full: num("full", 1, 5, 2),
        half: num("half", 0, 3, 0),
        sqft: num("sqft", 300, 8000, 1800),
        cond: radio("cond") || "kept",
        freq: type === "standard" ? (radio("freq") || "once") : "once",
        pets: form.elements.pets.checked,
        zip: (form.elements.zip.value || "").replace(/\D/g, "").slice(0, 5),
        addons: $$('input[name="addon"]:checked', form).map(function (el) { return el.value; })
      };
    };

    var syncIncluded = function (type) {
      $$(".check[data-included]", form).forEach(function (lab) {
        var input = $("input", lab);
        var inc = (lab.dataset.included || "").split(" ").indexOf(type) > -1;
        lab.classList.toggle("is-inc", inc);
        input.disabled = inc;
        input.checked = inc ? true : input.dataset.user === "1";
      });
      var std = type === "standard";
      $$('[name="freq"]', form).forEach(function (el) { el.disabled = !std; });
      $("#freq-msg").textContent = std ? "Discounts apply to standard cleans." : "Recurring discounts apply to standard cleans only. This clean is priced as a one-time visit.";
    };

    var zipMsg = function (zip) {
      var el = $("#zip-msg");
      if (zip.length < 5) { el.textContent = ""; return; }
      el.textContent = D.zips[zip]
        ? "We clean in " + D.zips[zip] + "."
        : "We don't list " + zip + " yet. Call " + D.phone_show + " and we'll check.";
    };

    var describe = function (o, e) {
      var home = (o.beds ? o.beds + " bed" : "Studio") + ", " + o.full + " full bath" + (o.full > 1 ? "s" : "") +
        (o.half ? ", " + o.half + " half bath" + (o.half > 1 ? "s" : "") : "") + ", " + o.sqft.toLocaleString("en-US") + " sq ft";
      var adds = P.addons.filter(function (a) { return o.addons.indexOf(a.id) > -1; }).map(function (a) {
        return a.label + (a.included.indexOf(o.type) > -1 ? " (included)" : "");
      });
      return {
        title: P.types[o.type].label + " clean" + (e.recurring ? ", " + P.frequencies[o.freq].label.toLowerCase() : ""),
        home: home,
        text: P.types[o.type].label + " clean. " + home + ". Condition: " + P.conditions[o.cond].label + ". " +
          P.frequencies[o.freq].label + ". Pets: " + (o.pets ? "yes" : "no") + ". Add-ons: " + (adds.length ? adds.join(", ") : "none") +
          ". ZIP: " + (o.zip || "not given") + ". Estimate: " + money(e.lo) + " to " + money(e.hi) + (e.recurring ? " per visit" : "") + "."
      };
    };

    var update = function () {
      var o = read();
      syncIncluded(o.type);
      o = read();
      var e = estimate(o);
      $("#r-price").textContent = money(e.lo) + " to " + money(e.hi);
      $("#r-per").textContent = e.recurring ? "per visit, " + P.frequencies[o.freq].label.toLowerCase() : "one-time cleaning";
      $("#r-time").textContent = "About " + e.hours + " cleaner hours. A team of " + P.team_size + " spends about " + e.team + " hours at your home.";
      $("#r-lines").innerHTML = e.lines.map(function (l) {
        if (l[1] === null) return "<li><span>" + l[0] + "</span><span>Base price</span></li>";
        return "<li><span>" + l[0] + "</span><span>" + (l[1] < 0 ? "&minus;" : "+") + money(Math.abs(l[1])) + "</span></li>";
      }).join("");
      zipMsg(o.zip);
      var d = describe(o, e);
      lastSummary = d.text;
      var sum = $("#book-sum");
      if (sum) sum.innerHTML = "<h3>" + d.title + ": " + money(e.lo) + " to " + money(e.hi) + "</h3><p>" + d.home + ". <a href=\"#calc\">Change details</a></p>";
      $$('input[name="quote"]').forEach(function (h) { h.value = d.text; });
      var zipField = $("#book-zip");
      if (zipField && o.zip) zipField.value = o.zip;

      var q = new URLSearchParams();
      q.set("type", o.type); q.set("beds", o.beds); q.set("full", o.full); q.set("half", o.half);
      q.set("sqft", o.sqft); q.set("cond", o.cond); q.set("freq", o.freq);
      if (o.pets) q.set("pets", "1");
      var userAdds = $$('input[name="addon"]', form).filter(function (el) { return el.dataset.user === "1"; }).map(function (el) { return el.value; });
      if (userAdds.length) q.set("add", userAdds.join(","));
      if (o.zip) q.set("zip", o.zip);
      history.replaceState(null, "", location.pathname + "?" + q.toString() + location.hash);
    };

    form.addEventListener("input", update);
    form.addEventListener("change", update);
    form.addEventListener("submit", function (e) { e.preventDefault(); });
    update();

    var toBook = $("#to-book");
    toBook.addEventListener("click", function () { update(); if (D.cal_link) loadCal(true); });
    if (D.cal_link && "IntersectionObserver" in window) {
      var io = new IntersectionObserver(function (en) {
        if (en[0].isIntersecting) { loadCal(false); io.disconnect(); }
      }, { rootMargin: "200px" });
      io.observe($("#book"));
    }
  }

  /* ---------------------------------------------------------------- Cal.com */
  var calNotes = null;
  function loadCal(force) {
    var box = $("#cal-inline");
    if (!box || (!force && calNotes !== null) || calNotes === lastSummary) return;
    calNotes = lastSummary;
    (function (C, A, L) {
      var p = function (a, ar) { a.q.push(ar); };
      var d = C.document;
      C.Cal = C.Cal || function () {
        var cal = C.Cal, ar = arguments;
        if (!cal.loaded) { cal.ns = {}; cal.q = cal.q || []; d.head.appendChild(d.createElement("script")).src = A; cal.loaded = true; }
        if (ar[0] === L) {
          var api = function () { p(api, arguments); };
          var ns = ar[1];
          api.q = api.q || [];
          if (typeof ns === "string") { cal.ns[ns] = cal.ns[ns] || api; p(cal.ns[ns], ar); p(cal, ["initNamespace", ns]); } else p(cal, ar);
          return;
        }
        p(cal, ar);
      };
    })(window, "https://app.cal.com/embed/embed.js", "init");
    if (!window.Cal.ns || !window.Cal.ns.book) window.Cal("init", "book", { origin: "https://app.cal.com" });
    box.innerHTML = "";
    window.Cal.ns.book("inline", { elementOrSelector: "#cal-inline", calLink: D.cal_link, config: { layout: "month_view", notes: calNotes } });
    var dark = matchMedia("(prefers-color-scheme: dark)").matches;
    window.Cal.ns.book("ui", { theme: dark ? "dark" : "light", hideEventTypeDetails: false, layout: "month_view",
      cssVarsPerTheme: { light: { "cal-brand": "#15262b" }, dark: { "cal-brand": "#f2c230" } } });
  }

  /* ---------------------------------------------------------------- request forms */
  var tomorrow = new Date();
  tomorrow.setDate(tomorrow.getDate() + 1);
  var iso = function (d) { return d.getFullYear() + "-" + String(d.getMonth() + 1).padStart(2, "0") + "-" + String(d.getDate()).padStart(2, "0"); };
  $$('input[type="date"]').forEach(function (el) { el.min = iso(tomorrow); });

  $$("form.req").forEach(function (f) {
    var kind = f.dataset.kind;
    var note = $(".form-note", f);
    var err = function (name, msg) {
      var el = f.elements[name];
      var out = $("#" + el.id + "-err");
      el.setAttribute("aria-invalid", msg ? "true" : "false");
      if (msg) el.setAttribute("aria-describedby", el.id + "-err"); else el.removeAttribute("aria-describedby");
      if (out) out.textContent = msg || "";
      return !msg;
    };
    var check = function () {
      var ok = true, first = null;
      var mark = function (name, msg) { if (!err(name, msg)) { ok = false; first = first || f.elements[name]; } };
      mark("name", f.elements.name.value.trim() ? "" : "Please enter your name.");
      mark("phone", f.elements.phone.value.replace(/\D/g, "").length >= 10 ? "" : "Please enter a 10-digit phone number.");
      mark("email", /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(f.elements.email.value.trim()) ? "" : "Please enter a valid email address.");
      if (kind === "book") {
        var dv = f.elements.date.value;
        mark("date", !dv ? "Please pick a day." : (dv < iso(tomorrow) ? "Please pick a day from tomorrow on." : ""));
        mark("address", f.elements.address.value.trim() ? "" : "Please enter the address we'll clean.");
      } else {
        mark("message", f.elements.message.value.trim() ? "" : "Please tell us how we can help.");
      }
      if (first) first.focus();
      return ok;
    };
    f.addEventListener("submit", function (e) {
      e.preventDefault();
      note.textContent = "";
      if (!check()) return;
      var fd = {};
      $$("input, select, textarea", f).forEach(function (el) { if (el.name) fd[el.name] = el.value.trim(); });
      fd.form = kind === "book" ? "Booking request" : "Contact message";
      var subject = kind === "book" ? "Cleaning request for " + fd.date + " (" + fd.window + ")" : "Message from " + fd.name;
      var body = kind === "book"
        ? ["Name: " + fd.name, "Phone: " + fd.phone, "Email: " + fd.email, "Address: " + fd.address, "Preferred day: " + fd.date + ", arrival " + fd.window,
           "Second choice: " + (fd.alt_date || "none"), "", "Quote: " + fd.quote, "", "Notes: " + (fd.message || "none")].join("\n")
        : ["Name: " + fd.name, "Phone: " + fd.phone, "Email: " + fd.email, "", fd.message].join("\n");

      if (D.form_endpoint) {
        var btn = $('button[type="submit"]', f);
        btn.disabled = true;
        fd._subject = subject;
        fetch(D.form_endpoint, { method: "POST", headers: { "Content-Type": "application/json", "Accept": "application/json" }, body: JSON.stringify(fd) })
          .then(function (r) { if (!r.ok) throw new Error(r.status); })
          .then(function () {
            f.reset();
            note.textContent = kind === "book" ? "Thanks, we got your request. We'll text you to confirm the time." : "Thanks, we got your message and will reply soon.";
          })
          .catch(function () { note.textContent = "That didn't send. Please call or text " + D.phone_show + "."; })
          .then(function () { btn.disabled = false; });
      } else {
        location.href = "mailto:" + D.email + "?subject=" + encodeURIComponent(subject) + "&body=" + encodeURIComponent(body);
        note.textContent = "Your email app should open with everything filled in. Press send and we'll confirm by text. Nothing opened? Call or text " + D.phone_show + ".";
      }
    });
  });
})();
