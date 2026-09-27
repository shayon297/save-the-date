// Shayon & Amanda — Save the Date
(function () {
  "use strict";

  var CONFIG = {
    // Google Apps Script web app (see google-apps-script.gs). Addresses are appended to the sheet.
    sheetEndpoint: "https://script.google.com/macros/s/AKfycbyYbDurhgmxX0IixhGSMYSQuqVLgtgFfohUF8q6cHM9bhAtRcQ9LC8ghOU7tWzb8UP9/exec",
    // Fallback if the endpoint is unreachable: open the guest's email app addressed here.
    coupleEmail: "shayon@multicoin.capital",
  };

  // ---- countdown (to the ceremony start, 5:30 PM Eastern) ----
  var target = new Date("2027-05-16T17:30:00-04:00").getTime();
  var nums = {};
  document.querySelectorAll(".count-num").forEach(function (el) {
    nums[el.dataset.unit] = el;
  });

  function tick() {
    var diff = Math.max(0, target - Date.now());
    var minutes = Math.floor(diff / 60000);
    var hours = Math.floor(minutes / 60);
    var days = Math.floor(hours / 24);
    nums.days.textContent = days;
    nums.hours.textContent = hours % 24;
    nums.minutes.textContent = minutes % 60;
  }
  tick();
  setInterval(tick, 30000);

  // ---- add-to-calendar (.ics, times given in UTC — Cincinnati is Eastern/EDT in May) ----
  var EVENTS = {
    reception: {
      title: "Shayon & Amanda — Welcome Dinner",
      location: "Via Vite, 520 Vine St, Cincinnati, OH 45202",
      start: "20270515T220000Z", // May 15, 6:00 PM EDT
      end: "20270516T010000Z",   // May 15, 9:00 PM EDT
    },
    wedding: {
      title: "Shayon & Amanda — Wedding Ceremony & Reception",
      location: "Cincinnati Art Museum, 953 Eden Park Dr, Cincinnati, OH 45202",
      start: "20270516T213000Z", // May 16, 5:30 PM EDT
      end: "20270517T030000Z",   // May 16, 11:00 PM EDT
    },
  };

  function pad(n) { return n < 10 ? "0" + n : "" + n; }

  function dtstamp() {
    var d = new Date();
    return (
      d.getUTCFullYear() + pad(d.getUTCMonth() + 1) + pad(d.getUTCDate()) + "T" +
      pad(d.getUTCHours()) + pad(d.getUTCMinutes()) + pad(d.getUTCSeconds()) + "Z"
    );
  }

  function buildIcs(ev) {
    return [
      "BEGIN:VCALENDAR",
      "VERSION:2.0",
      "PRODID:-//Shayon and Amanda//Save the Date//EN",
      "BEGIN:VEVENT",
      "UID:" + ev.start + "-shayon-amanda@savethedate",
      "DTSTAMP:" + dtstamp(),
      "DTSTART:" + ev.start,
      "DTEND:" + ev.end,
      "SUMMARY:" + ev.title,
      "LOCATION:" + ev.location,
      "DESCRIPTION:Formal invitation with full details to follow.",
      "END:VEVENT",
      "END:VCALENDAR",
    ].join("\r\n");
  }

  document.querySelectorAll("[data-cal]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var ev = EVENTS[btn.dataset.cal];
      if (!ev) return;
      var blob = new Blob([buildIcs(ev)], { type: "text/calendar;charset=utf-8" });
      var url = URL.createObjectURL(blob);
      var a = document.createElement("a");
      a.href = url;
      a.download = btn.dataset.cal + "-shayon-amanda.ics";
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      setTimeout(function () { URL.revokeObjectURL(url); }, 1000);
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
      type: "address",
      name: d.name, email: d.email,
      street: d.street, unit: d.unit, city: d.city, state: d.state, zip: d.zip, country: d.country,
      address: fullAddress(d),
      // read by the original RSVP script, so rows still land somewhere sensible before it is upgraded
      attending: "Mailing address", note: fullAddress(d).replace(/\n/g, ", "),
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
      var body = "Name: " + d.name + "\nEmail: " + d.email + "\n\n" + fullAddress(d);
      setError("We couldn't send that just now — please try again, or email it to us instead.");
      errorEl.innerHTML += ' <a href="mailto:' + CONFIG.coupleEmail + "?subject=" +
        encodeURIComponent("Mailing address — " + d.name) + "&body=" + encodeURIComponent(body) + '">Email us</a>';
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
