// Amanda & Shayon — Save the Date
(function () {
  "use strict";

  var CONFIG = {
    // Web app URL (ends in /exec) of the Apps Script in google-apps-script.gs,
    // bound to the mailing-address spreadsheet. Each submission becomes a row.
    sheetEndpoint: "https://script.google.com/macros/s/AKfycbwte4JkUkFrMbIr9vCFheFrXyUqlp8kNnHFpgsEffheSdWF8FL3PkFY5gzFQzuQ5XNK/exec",
    // Google Maps Platform API key with "Places API (New)" enabled, restricted to
    // HTTP referrers shayon297.github.io/* (and localhost for testing). Empty = use Photon.
    placesKey: "AIzaSyBnqjve2DVUoVrRj5Jfyils5QPLZowL0yg",
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
      title: "Amanda & Shayon — Welcome Party",
      location: "Via Vite, 520 Vine St, Cincinnati, OH 45202",
      start: "20270515T223000Z", // May 15, 6:30 PM EDT
      end: "20270516T013000Z",   // May 15, 9:30 PM EDT
    },
    wedding: {
      title: "Amanda & Shayon — Wedding Ceremony & Reception",
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
    btn.addEventListener("click", function (e) {
      e.stopPropagation();
      var open = opts.hidden;
      closeCalendars();
      opts.hidden = !open;
      btn.setAttribute("aria-expanded", open ? "true" : "false");
    });
  });

  // close an open calendar pop-over on an outside click or Escape
  function closeCalendars() {
    document.querySelectorAll(".cal-options").forEach(function (o) { o.hidden = true; });
    document.querySelectorAll("[data-cal]").forEach(function (b) { b.setAttribute("aria-expanded", "false"); });
  }
  document.addEventListener("click", function (e) {
    if (!e.target.closest(".event-actions")) closeCalendars();
  });
  document.addEventListener("keydown", function (e) { if (e.key === "Escape") closeCalendars(); });

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

  // ---- address lookup ----
  // Google Places (New) when CONFIG.placesKey is set: accurate US house-level addresses.
  // Otherwise Photon (OpenStreetMap, no key), which often lacks US house numbers, so it
  // only offers exact matches. Each suggestion is
  // { line1, line2, resolve() -> Promise<{street, city, state, zip, country}> }.
  var sessionToken = null;   // groups one guest's keystrokes + pick into one Google billing session

  function newToken() {
    return (window.crypto && crypto.randomUUID) ? crypto.randomUUID() : String(Date.now()) + Math.random();
  }

  function googleSuggest(q) {
    if (!sessionToken) sessionToken = newToken();
    return fetch("https://places.googleapis.com/v1/places:autocomplete", {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-Goog-Api-Key": CONFIG.placesKey },
      body: JSON.stringify({
        input: q,
        sessionToken: sessionToken,
        includedPrimaryTypes: ["street_address", "premise", "subpremise"],
        regionCode: "us",
        locationBias: { circle: { center: { latitude: 39.10, longitude: -84.51 }, radius: 50000 } },
      }),
    }).then(function (r) {
      if (!r.ok) throw new Error("places " + r.status);
      return r.json();
    }).then(function (json) {
      return (json.suggestions || []).filter(function (s) { return s.placePrediction; }).slice(0, 5).map(function (s) {
        var p = s.placePrediction, sf = p.structuredFormat || {};
        return {
          line1: (sf.mainText && sf.mainText.text) || (p.text && p.text.text) || "",
          line2: (sf.secondaryText && sf.secondaryText.text) || "",
          resolve: function () { return googleDetails(p.placeId); },
        };
      });
    });
  }

  function googleDetails(placeId) {
    var url = "https://places.googleapis.com/v1/places/" + encodeURIComponent(placeId) +
      "?sessionToken=" + encodeURIComponent(sessionToken);
    sessionToken = null;   // a pick ends the session
    return fetch(url, {
      headers: { "X-Goog-Api-Key": CONFIG.placesKey, "X-Goog-FieldMask": "addressComponents" },
    }).then(function (r) {
      if (!r.ok) throw new Error("place " + r.status);
      return r.json();
    }).then(function (place) {
      var c = {};
      (place.addressComponents || []).forEach(function (a) {
        (a.types || []).forEach(function (t) { if (!c[t]) c[t] = a; });
      });
      function long(t) { return c[t] ? c[t].longText : ""; }
      function short(t) { return c[t] ? c[t].shortText : ""; }
      return {
        street: [long("street_number"), long("route")].filter(Boolean).join(" "),
        unit: long("subpremise"),
        city: long("locality") || long("postal_town") || long("sublocality") || long("administrative_area_level_2"),
        state: short("administrative_area_level_1"),
        zip: long("postal_code"),
        country: long("country"),
      };
    });
  }

  function photonSuggest(q) {
    // Cincinnati as a soft location bias; results are still global.
    var url = "https://photon.komoot.io/api/?limit=6&lang=en&lat=39.10&lon=-84.51&q=" + encodeURIComponent(q);
    var typedNumber = (q.match(/^\s*(\d+[a-z]?)\b/i) || [])[1] || "";
    return fetch(url).then(function (r) { return r.json(); }).then(function (json) {
      var seen = {}, out = [];
      (json.features || []).forEach(function (ft) {
        var p = ft.properties;
        if (!p || !(p.housenumber || p.street || (p.type === "street" && p.name))) return;
        var street = p.street || p.name;
        // Photon readily returns similar streets elsewhere, and often lacks US house
        // numbers. Only offer real addresses: the street the guest typed, and, if they
        // typed a number, that exact house number. Otherwise nothing is suggested and
        // what they typed is kept as the street line.
        var word = (street.toLowerCase().match(/[a-z0-9]{3,}/) || [""])[0];
        if (!word || q.toLowerCase().indexOf(word) === -1) return;
        if (typedNumber && String(p.housenumber || "").toLowerCase() !== typedNumber.toLowerCase()) return;
        var number = p.housenumber || "";
        var fields = {
          street: [number, street].filter(Boolean).join(" "),
          unit: "",
          city: p.city || p.town || p.village || p.county || "",
          state: p.state || "",
          zip: p.postcode || "",
          country: p.country || "",
        };
        var line2 = [fields.city, fields.state, fields.zip, fields.country].filter(Boolean).join(", ");
        var key = fields.street + "|" + line2;
        if (seen[key] || out.length >= 5) return;
        seen[key] = true;
        out.push({ line1: fields.street, line2: line2, resolve: function () { return Promise.resolve(fields); } });
      });
      return out;
    });
  }

  function render(suggestions) {
    list.innerHTML = "";
    items = suggestions;
    activeIdx = -1;
    suggestions.forEach(function (sug, i) {
      var li = document.createElement("li");
      li.setAttribute("role", "option");
      li.id = "addr-opt-" + i;
      li.innerHTML = "<span></span><small></small>";
      li.firstChild.textContent = sug.line1;
      li.lastChild.textContent = sug.line2;
      li.addEventListener("mousedown", function (e) { e.preventDefault(); choose(i); });
      list.appendChild(li);
    });
    if (!suggestions.length) {
      var li = document.createElement("li");
      li.className = "suggest-note";
      li.textContent = "No matches — add your address manually below.";
      list.appendChild(li);
    }
    list.hidden = false;
    search.setAttribute("aria-expanded", "true");
  }

  function choose(i) {
    var sug = items[i];
    search.value = [sug.line1, sug.line2].filter(Boolean).join(", ");
    closeList();
    showFields();
    sug.resolve().then(function (a) {
      f.street.value = a.street || sug.line1;
      if (a.unit) f.unit.value = a.unit;
      f.city.value = a.city;
      f.state.value = a.state;
      f.zip.value = a.zip;
      f.country.value = a.country || f.country.value;
    }).catch(function () {
      f.street.value = sug.line1;   // details failed: keep what we have, the fields are editable
    }).then(function () { f.unit.focus(); });
  }

  function lookup(q) {
    var mySeq = ++seq;
    var suggest = CONFIG.placesKey ? googleSuggest : photonSuggest;
    suggest(q).catch(function () {
      return CONFIG.placesKey ? photonSuggest(q) : Promise.reject();   // Google down or key refused: fall back
    }).then(function (suggestions) {
      if (mySeq !== seq) return;
      render(suggestions);
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
    // email is optional, but if given it should look like one
    if (d.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(d.email)) return setError("Please check your email address.", f.email);
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
      submitBtn.textContent = "Submit mailing address";
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
