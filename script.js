// Shayon & Amanda — Save the Date
(function () {
  "use strict";

  var CONFIG = {
    // Web app URL (ends in /exec) of the Apps Script in google-apps-script.gs,
    // bound to the mailing-address spreadsheet. Each submission becomes a row.
    sheetEndpoint: "https://script.google.com/macros/s/AKfycbwte4JkUkFrMbIr9vCFheFrXyUqlp8kNnHFpgsEffheSdWF8FL3PkFY5gzFQzuQ5XNK/exec",
  };

  // ---- countdown: whole days to the ceremony start, 5:30 PM Eastern ----
  var target = new Date("2027-05-16T17:30:00-04:00").getTime();
  var daysEl = document.querySelector('.count-num[data-unit="days"]');
  var daysLabel = document.querySelector(".count-label");

  function tick() {
    var days = Math.ceil(Math.max(0, target - Date.now()) / 86400000);
    daysEl.textContent = days;
    daysLabel.textContent = days === 1 ? "day to go" : "days to go";
  }
  tick();
  setInterval(tick, 60000);

  // ---- add-to-calendar ----
  // Each button reveals two links: a static .ics file (assets/*.ics; iPhone and Mac open it
  // straight into Calendar, Outlook imports it) and a Google Calendar link (Android, Gmail).
  // A real file works in phone browsers and in-app browsers, where blob downloads often fail.
  // Times are UTC — Cincinnati is on EDT (UTC−4) in May. Keep in sync with assets/*.ics.
  var EVENTS = {
    reception: {
      title: "Shayon & Amanda — Welcome Party",
      location: "Via Vite, 520 Vine St, Cincinnati, OH 45202",
      start: "20270515T223000Z", // May 15, 6:30 PM EDT
      end: "20270516T013000Z",   // May 15, 9:30 PM EDT
    },
    wedding: {
      title: "Shayon & Amanda — Wedding Ceremony & Reception",
      location: "Cincinnati Art Museum, 953 Eden Park Dr, Cincinnati, OH 45202",
      start: "20270516T213000Z", // May 16, 5:30 PM EDT
      end: "20270517T030000Z",   // May 16, 11:00 PM EDT
    },
  };

  function googleUrl(ev) {
    return "https://calendar.google.com/calendar/render?action=TEMPLATE" +
      "&text=" + encodeURIComponent(ev.title) +
      "&dates=" + ev.start + "/" + ev.end +
      "&location=" + encodeURIComponent(ev.location) +
      "&details=" + encodeURIComponent("Formal invitation with full details to follow. https://shayon297.github.io/save-the-date/");
  }

  document.querySelectorAll("[data-cal]").forEach(function (btn) {
    var ev = EVENTS[btn.dataset.cal];
    var opts = btn.parentNode.querySelector(".cal-options");
    if (!ev || !opts) return;
    opts.querySelector("[data-gcal]").href = googleUrl(ev);
    btn.addEventListener("click", function () {
      var open = opts.hidden;
      opts.hidden = !open;
      btn.setAttribute("aria-expanded", open ? "true" : "false");
    });
  });

  // ---- mailing address form ----
  var form = document.getElementById("addr-form");
  if (!form) return;

  var search = document.getElementById("addr-search");
  var list = document.getElementById("addr-suggest");
  var manualBtn = document.getElementById("addr-manual");
  var fields = document.getElementById("addr-fields");
  var errorEl = document.getElementById("addr-error");
  var submitBtn = document.getElementById("addr-submit");
  var thanks = document.getElementById("addr-thanks");
  var f = form.elements;

  var timer = null, seq = 0, activeIdx = -1, items = [];

  function showFields() {
    fields.hidden = false;
    manualBtn.hidden = true;
    search.removeAttribute("required");
  }

  manualBtn.addEventListener("click", function () {
    showFields();
    closeList();
    if (search.value && !f.street.value) f.street.value = search.value;
    f.street.focus();
  });

  function closeList() {
    list.hidden = true;
    list.innerHTML = "";
    items = [];
    activeIdx = -1;
    search.setAttribute("aria-expanded", "false");
  }

  function label(p) {
    var line1 = [p.housenumber, p.street].filter(Boolean).join(" ") || p.name || "";
    var line2 = [p.city || p.town || p.village || p.county, p.state, p.postcode, p.country].filter(Boolean).join(", ");
    return { line1: line1, line2: line2 };
  }

  function render(features) {
    list.innerHTML = "";
    items = features;
    activeIdx = -1;
    features.forEach(function (ft, i) {
      var p = ft.properties, l = label(p);
      var li = document.createElement("li");
      li.setAttribute("role", "option");
      li.id = "addr-opt-" + i;
      li.innerHTML = "<span></span><small></small>";
      li.firstChild.textContent = l.line1;
      li.lastChild.textContent = l.line2;
      li.addEventListener("mousedown", function (e) { e.preventDefault(); choose(i); });
      list.appendChild(li);
    });
    if (!features.length) {
      var li = document.createElement("li");
      li.className = "suggest-note";
      li.textContent = "No matches — add your address manually below.";
      list.appendChild(li);
    }
    list.hidden = false;
    search.setAttribute("aria-expanded", "true");
  }

  function choose(i) {
    var p = items[i].properties, l = label(p);
    f.street.value = l.line1;
    f.city.value = p.city || p.town || p.village || "";
    f.state.value = p.state || "";
    f.zip.value = p.postcode || "";
    f.country.value = p.country || f.country.value;
    search.value = [l.line1, l.line2].filter(Boolean).join(", ");
    closeList();
    showFields();
    f.unit.focus();
  }

  function lookup(q) {
    var mySeq = ++seq;
    // Cincinnati as a soft location bias; results are still global.
    var url = "https://photon.komoot.io/api/?limit=5&lang=en&lat=39.10&lon=-84.51&q=" + encodeURIComponent(q);
    fetch(url).then(function (r) { return r.json(); }).then(function (json) {
      if (mySeq !== seq) return;
      var seen = {};
      var feats = (json.features || []).filter(function (ft) {
        var p = ft.properties;
        if (!p || !(p.housenumber || p.street || p.name)) return false;
        var l = label(p), key = l.line1 + "|" + l.line2;
        if (seen[key]) return false;
        seen[key] = true;
        return true;
      });
      render(feats);
    }).catch(function () {
      if (mySeq !== seq) return;
      closeList();
      showFields();
    });
  }

  search.addEventListener("input", function () {
    clearTimeout(timer);
    var q = search.value.trim();
    if (q.length < 4) { closeList(); return; }
    timer = setTimeout(function () { lookup(q); }, 260);
  });

  search.addEventListener("keydown", function (e) {
    if (list.hidden || !items.length) return;
    if (e.key === "ArrowDown" || e.key === "ArrowUp") {
      e.preventDefault();
      activeIdx = (activeIdx + (e.key === "ArrowDown" ? 1 : -1) + items.length) % items.length;
      Array.prototype.forEach.call(list.children, function (li, i) {
        li.setAttribute("aria-selected", i === activeIdx ? "true" : "false");
      });
    } else if (e.key === "Enter" && activeIdx >= 0) {
      e.preventDefault();
      choose(activeIdx);
    } else if (e.key === "Escape") {
      closeList();
    }
  });

  search.addEventListener("blur", function () { setTimeout(closeList, 150); });

  function setError(msg, el) {
    errorEl.textContent = msg;
    errorEl.hidden = !msg;
    form.querySelectorAll("[aria-invalid]").forEach(function (i) { i.removeAttribute("aria-invalid"); });
    if (el) { el.setAttribute("aria-invalid", "true"); el.focus(); }
  }

  function fullAddress(d) {
    return [
      [d.street, d.unit].filter(Boolean).join(", "),
      [d.city, d.state].filter(Boolean).join(", ") + (d.zip ? " " + d.zip : ""),
      d.country,
    ].filter(Boolean).join("\n");
  }

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    // A bot filled the hidden honeypot: show the usual thank-you, send nothing.
    if (f.website.value) {
      form.hidden = true;
      thanks.hidden = false;
      return;
    }
    var d = {
      name: f.name.value.trim(),
      email: f.email.value.trim(),
      street: f.street.value.trim(),
      unit: f.unit.value.trim(),
      city: f.city.value.trim(),
      state: f.state.value.trim(),
      zip: f.zip.value.trim(),
      country: f.country.value.trim(),
    };
    if (!d.name) return setError("Please add your name.", f.name);
    if (!d.email) return setError("Please add your email.", f.email);
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(d.email)) return setError("Please check your email address.", f.email);
    if (fields.hidden) {
      if (!search.value.trim()) return setError("Please add your mailing address.", search);
      // typed but never picked a suggestion: keep what they wrote as the street line
      showFields();
      d.street = search.value.trim();
      f.street.value = d.street;
    }
    if (!d.street) return setError("Please add your street address.", f.street);
    if (!d.city) return setError("Please add your city.", f.city);
    setError("");

    var payload = {
      name: d.name, email: d.email,
      street: d.street, unit: d.unit, city: d.city, state: d.state, zip: d.zip, country: d.country,
      address: fullAddress(d),
    };

    submitBtn.disabled = true;
    submitBtn.textContent = "Sending…";

    var done = function () {
      form.hidden = true;
      thanks.hidden = false;
    };
    var fail = function () {
      submitBtn.disabled = false;
      submitBtn.textContent = "Send";
      setError("Something went wrong sending that — please try again in a moment.");
    };

    if (!CONFIG.sheetEndpoint) return fail();
    // text/plain avoids a CORS preflight, which Apps Script web apps do not answer.
    fetch(CONFIG.sheetEndpoint, {
      method: "POST",
      headers: { "Content-Type": "text/plain;charset=utf-8" },
      body: JSON.stringify(payload),
    }).then(function (r) { return r.json(); }).then(function (res) {
      if (res && res.ok) done(); else fail();
    }).catch(fail);
  });
})();
