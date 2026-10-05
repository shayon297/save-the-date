// Shayon & Amanda — Save the Date
(function () {
  "use strict";

  var CONFIG = {
    // Web app URL (ends in /exec) of the Apps Script in google-apps-script.gs,
    // bound to the mailing-address spreadsheet. Each submission becomes a row.
    sheetEndpoint: "https://script.google.com/macros/s/AKfycbwte4JkUkFrMbIr9vCFheFrXyUqlp8kNnHFpgsEffheSdWF8FL3PkFY5gzFQzuQ5XNK/exec",
    // Google Maps Platform API key with "Places API (New)" enabled, restricted to
    // HTTP referrers shayon297.github.io/* (and localhost for testing). Empty = use Photon.
    placesKey: "",
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

  // ---- curtains ----
  // Two curtains hang from a gathered rod across the top, meet at the centre, and are
  // tied back low at each side, where the fabric pools on the floor (after the satin
  // drapery references). Drawn here as SVG at the card's exact size, so the shape is
  // never stretched. The inner (leading) edge is fitted to clear every line of text:
  // straight down past the content, and up through the header as a pointed arch.
  // Flowers and leaves come from assets/flora.svg (made by tools-flora.py) and are
  // placed along the leading edge, thickest at the tie.
  var SVGNS = "http://www.w3.org/2000/svg";
  var FLORA = "assets/flora.svg?v=1#";
  var SYM = {   // symbol -> its viewBox [x, y, w, h], drawn around the origin
    rose1: [-26, -26, 52, 52], rose2: [-26, -26, 52, 52], rose3: [-26, -26, 52, 52],
    peony: [-26, -26, 52, 52], roseside: [-26, -26, 52, 52],
    bud: [-4, -14, 30, 28], leaves: [-4, -16, 40, 32], sprig: [-4, -14, 44, 28],
  };
  var INK = "#7f8a4e", FABRIC = "#eeeede";
  var card = document.querySelector(".card");
  var curtains = null;

  function rng(seed) {   // small deterministic PRNG, so the drawing is the same on every visit
    return function () {
      seed = (seed + 0x6D2B79F5) | 0;
      var t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }

  function sampleSegs(segs) {   // cubic segments -> dense points, y increasing
    var pts = [];
    segs.forEach(function (sg) {
      for (var i = 0; i <= 60; i++) {
        var t = i / 60, u = 1 - t;
        pts.push([
          u * u * u * sg[0][0] + 3 * u * u * t * sg[1][0] + 3 * u * t * t * sg[2][0] + t * t * t * sg[3][0],
          u * u * u * sg[0][1] + 3 * u * u * t * sg[1][1] + 3 * u * t * t * sg[2][1] + t * t * t * sg[3][1],
        ]);
      }
    });
    return pts;
  }

  function xAt(pts, y) {   // x on a sampled edge at height y
    if (y <= pts[0][1]) return pts[0][0];
    for (var i = 1; i < pts.length; i++) {
      if (pts[i][1] >= y) {
        var a = pts[i - 1], b = pts[i], f = (b[1] - a[1]) ? (y - a[1]) / (b[1] - a[1]) : 0;
        return a[0] + (b[0] - a[0]) * f;
      }
    }
    return pts[pts.length - 1][0];
  }

  function contentRects(origin, W) {
    // tight boxes of every line of text and every control, in curtain coordinates;
    // each also mirrored, so one (left) curtain shape clears both sides
    var out = [];
    var sel = ".hero > *, .portrait, .section-title, .address-sub, .event > *, .field-label, " +
              ".addr-form input, .link-btn, .btn, .cal-options, .closing > *, .card-footer > *, .addr-thanks > *";
    document.querySelectorAll(sel).forEach(function (el) {
      var list;
      if (/^(INPUT|BUTTON|FIGURE)$/.test(el.tagName) || el.classList.contains("btn")) {
        list = [el.getBoundingClientRect()];
      } else {   // the text itself, line by line (block children span the full width)
        list = [];
        var walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT), node;
        while ((node = walker.nextNode())) {
          if (!node.nodeValue.trim()) continue;
          var range = document.createRange();
          range.selectNodeContents(node);
          list = list.concat(Array.prototype.slice.call(range.getClientRects()));
        }
      }
      list.forEach(function (r) {
        // skip empty boxes and anything outside the card (the form's off-screen honeypot)
        if (!r.width || !r.height || r.right < origin.left || r.left > origin.right) return;
        var l = r.left - origin.left, rt = r.right - origin.left, t = r.top - origin.top, b = r.bottom - origin.top;
        out.push({ l: l, t: t, b: b });
        out.push({ l: W - rt, t: t, b: b });
      });
    });
    return out;
  }

  function el(name, attrs, parent) {
    var e = document.createElementNS(SVGNS, name);
    for (var k in attrs) e.setAttribute(k, attrs[k]);
    if (parent) parent.appendChild(e);
    return e;
  }

  function pathFrom(pts) {
    return "M" + pts.map(function (p) { return p[0].toFixed(1) + " " + p[1].toFixed(1); }).join("L");
  }

  function place(g, sym, x, y, size, rot) {   // size: px per symbol unit * 52 (a bloom's box)
    var vb = SYM[sym], s = size / 52;
    var u = el("use", {
      href: FLORA + sym,
      x: (x + vb[0] * s).toFixed(1), y: (y + vb[1] * s).toFixed(1),
      width: (vb[2] * s).toFixed(1), height: (vb[3] * s).toFixed(1),
    }, g);
    u.setAttributeNS("http://www.w3.org/1999/xlink", "xlink:href", FLORA + sym);   // older Safari
    if (rot) u.setAttribute("transform", "rotate(" + rot.toFixed(1) + " " + x.toFixed(1) + " " + y.toFixed(1) + ")");
  }

  function drawCurtains() {
    if (!card) return;
    if (!curtains) {
      curtains = el("svg", { class: "curtains", "aria-hidden": "true" });
      card.insertBefore(curtains, card.firstChild);
    }
    var box = curtains.getBoundingClientRect();
    var W = box.width, H = box.height;
    if (W < 50 || H < 50) return;
    while (curtains.firstChild) curtains.removeChild(curtains.firstChild);
    curtains.setAttribute("viewBox", "0 0 " + W + " " + H);

    var k = Math.max(0.5, Math.min(1, W / 600));        // scale for flowers and details
    var pad = 8 + 6 * k;                                 // breathing room around text
    var rects = contentRects(box, W);
    function minLeft(y0, y1) {
      var m = Infinity;
      rects.forEach(function (r) { if (r.b >= y0 && r.t <= y1) m = Math.min(m, r.l); });
      return m;
    }

    var tieY = H * 0.78;
    var bundle = Math.max(10, W * 0.07), tieX = bundle / 2 + 3;
    var g = Math.max(W * 0.05, Math.min(W * 0.22, minLeft(0, tieY) - pad));          // edge beside the content
    var hemIn = Math.max(tieX + bundle / 2 + 6, Math.min(g + W * 0.12, minLeft(tieY, H) - pad));   // where the pool reaches
    var apex = [W / 2 + 1, 0];
    var tieIn = [tieX + bundle / 2, tieY];

    function leading(Ha) {
      return sampleSegs([
        [apex, [apex[0] - (apex[0] - g) * 0.45, Ha * 0.06], [g, Ha * 0.42], [g, Ha]],          // pointed arch
        [[g, Ha], [g, Ha + (tieY - Ha) * 0.6], [tieIn[0] + (g - tieIn[0]) * 0.45, tieY - (tieY - Ha) * 0.08], tieIn],
        [tieIn, [tieIn[0] + 4 * k, tieY + (H - tieY) * 0.45], [hemIn, H - (H - tieY) * 0.3], [hemIn, H]],
      ]);
    }
    function clears(pts) {
      for (var i = 0; i < rects.length; i++) {
        var r = rects[i];
        for (var j = 0; j < pts.length; j++) {
          var p = pts[j];
          if (p[1] >= r.t - pad && p[1] <= r.b + pad && p[0] > r.l - pad) return false;
        }
      }
      return true;
    }
    var inner = null;
    for (var Ha = Math.min(H * 0.32, W * 0.75); Ha >= 16; Ha -= 4) {   // tallest arch that still clears the header
      inner = leading(Ha);
      if (clears(inner)) break;
    }
    var outer = sampleSegs([
      [[0, 0], [0, tieY * 0.6], [tieX - bundle / 2, tieY * 0.9], [tieX - bundle / 2, tieY]],
      [[tieX - bundle / 2, tieY], [tieX - bundle / 2, tieY + (H - tieY) * 0.4], [0, H - (H - tieY) * 0.3], [0, H]],
    ]);

    var R = rng(20270516);
    var left = el("g", {}, curtains);
    // folds: lines fanning from the rod into the tie, then spreading into the pool
    var ys = [];
    for (var y = 0; y < H; y += 5) ys.push(y);
    ys.push(H);
    var n = 11, ts = [0];
    for (var i = 1; i < n; i++) ts.push((i + (R() - 0.5) * 0.6) / n);
    ts.push(1);
    function fold(t) {
      var wob = (R() - 0.5) * 2;
      return ys.map(function (y) {
        var xo = xAt(outer, y), xi = xAt(inner, y);
        return [xo + (xi - xo) * t + wob * Math.sin(y / 70) * k, y];
      });
    }
    var lines = ts.map(fold);
    el("path", { d: pathFrom(lines[0]) + "L" + lines[n].slice().reverse().map(function (p) { return p[0].toFixed(1) + " " + p[1].toFixed(1); }).join("L") + "Z", fill: FABRIC }, left);
    for (i = 0; i < n; i += 2) {   // shadowed folds of uneven depth, like satin
      var band = lines[i].concat(lines[i + 1].slice().reverse());
      el("path", { d: pathFrom(band) + "Z", fill: INK, opacity: (0.05 + R() * 0.11).toFixed(2) }, left);
    }
    for (i = 1; i < n; i++) el("path", { d: pathFrom(lines[i]), fill: "none", stroke: INK, "stroke-width": 0.75, opacity: 0.5 }, left);
    el("path", { d: pathFrom(lines[n]), fill: "none", stroke: INK, "stroke-width": 1.1 }, left);   // leading edge

    // gathered heading along the rod
    var head = "";
    for (var x = 2; x < W / 2 + 1; x += 9 * k + 3) head += "M" + x.toFixed(1) + " 0q" + (2.5 * k + 1).toFixed(1) + " " + (6 * k + 2).toFixed(1) + " " + (5 * k + 2).toFixed(1) + " 0";
    el("path", { d: head, fill: "none", stroke: INK, "stroke-width": 0.7, opacity: 0.7 }, left);

    // pool: soft scallops along the hem, and folds lying on the floor
    var hem = "M" + lines[0][lines[0].length - 1][0].toFixed(1) + " " + (H - 1);
    for (i = 1; i <= n; i++) {
      var ax = lines[i - 1][lines[i - 1].length - 1][0], bx = lines[i][lines[i].length - 1][0];
      hem += "Q" + ((ax + bx) / 2).toFixed(1) + " " + (H + 2).toFixed(1) + " " + bx.toFixed(1) + " " + (H - 2).toFixed(1);
    }
    el("path", { d: hem, fill: "none", stroke: INK, "stroke-width": 1 }, left);
    for (i = 0; i < 4; i++) {
      var x0 = R() * hemIn * 0.6, x1 = x0 + hemIn * (0.3 + R() * 0.3), yy = H - 6 - R() * 14 * k;
      el("path", { d: "M" + x0.toFixed(1) + " " + (yy + 3) + "Q" + ((x0 + x1) / 2).toFixed(1) + " " + (yy - 5) + " " + x1.toFixed(1) + " " + (yy + 2), fill: "none", stroke: INK, "stroke-width": 0.7, opacity: 0.5 }, left);
    }

    // tie-back band
    var t0 = tieX - bundle / 2 - 5, t1 = tieX + bundle / 2 + 5;
    el("path", { d: "M" + t0 + " " + (tieY - 6) + "Q" + tieX + " " + (tieY - 2) + " " + t1 + " " + (tieY - 6) + "L" + t1 + " " + (tieY + 6) + "Q" + tieX + " " + (tieY + 10) + " " + t0 + " " + (tieY + 6) + "Z", fill: "#fbf8f0", stroke: INK, "stroke-width": 1 }, left);

    // greenery and roses climbing the leading edge, thickest at the tie
    var lead = lines[n];
    var cum = [0];
    for (i = 1; i < lead.length; i++) cum.push(cum[i - 1] + Math.hypot(lead[i][0] - lead[i - 1][0], lead[i][1] - lead[i - 1][1]));
    var tieIdx = 0;
    while (tieIdx < lead.length - 1 && lead[tieIdx][1] < tieY) tieIdx++;
    function at(s) {   // point, outward normal (onto the fabric) and angle at arc length s
      var j = 1;
      while (j < cum.length - 1 && cum[j] < s) j++;
      var a = lead[j - 1], b = lead[j], dx = b[0] - a[0], dy = b[1] - a[1], len = Math.hypot(dx, dy) || 1;
      var f = (cum[j] - cum[j - 1]) ? (s - cum[j - 1]) / (cum[j] - cum[j - 1]) : 0;
      return { x: a[0] + dx * f, y: a[1] + dy * f, nx: -dy / len, ny: dx / len, ang: Math.atan2(dy, dx) * 180 / Math.PI };
    }
    var flowers = el("g", {}, left);
    var sTie = cum[tieIdx];
    function bloom(s, sym, size, off) {
      var p = at(s);
      var x = Math.max(p.x + p.nx * size * off, size * 0.42);   // never over the frame
      place(flowers, sym, x, p.y + p.ny * size * off, size, R() * 360);
    }
    function leaf(s, side, len) {
      // pointing up the edge: alternately along it, or angled out onto the fabric
      // (never into the opening, where the text is)
      var p = at(s);
      if (p.y < len * 0.9) return;   // too near the rod: it would poke above the frame
      var rot = p.ang + 180 - (side > 0 ? 38 + R() * 22 : 6 + R() * 10);
      place(flowers, R() < 0.5 ? "leaves" : "sprig", p.x + p.nx * 5, p.y + p.ny * 5, len, rot);
    }
    // climbing from the tie toward the apex
    var step = 46 * k + 16, idx = 0;
    for (var s = sTie - step; s > sTie * 0.22; s -= step * (0.85 + R() * 0.5)) {
      idx++;
      leaf(s, idx % 2 ? 1 : -1, 44 * k + 10);
      if (idx % 3 === 0) bloom(s - step * 0.4, ["rose1", "rose2", "rose3", "roseside"][idx % 4], (22 + R() * 8) * k + 6, 0.35);
    }
    // below the tie, into the pool
    leaf(sTie + step * 1.2, -1, 40 * k + 8);
    bloom(sTie + step * 2.6, "roseside", 20 * k + 6, 0.3);
    // the tie cluster
    leaf(sTie - 6, -1, 52 * k + 10);
    leaf(sTie + 8, 1, 52 * k + 10);
    bloom(sTie - 14 * k, "peony", 34 * k + 8, 0.45);
    bloom(sTie + 12 * k, "rose1", 38 * k + 8, 0.25);
    bloom(sTie + 30 * k, "rose3", 26 * k + 6, 0.55);

    // the right curtain is the left one mirrored
    var right = left.cloneNode(true);
    right.setAttribute("transform", "translate(" + W + " 0) scale(-1 1)");
    curtains.appendChild(right);
  }

  var redraw = null;
  function scheduleDraw() { clearTimeout(redraw); redraw = setTimeout(drawCurtains, 60); }
  if (window.ResizeObserver && card) new ResizeObserver(scheduleDraw).observe(card);
  window.addEventListener("resize", scheduleDraw);
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(drawCurtains);
  drawCurtains();

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

  // ---- address lookup ----
  // Google Places (New) when CONFIG.placesKey is set: accurate US house-level addresses.
  // Otherwise Photon (OpenStreetMap, no key), which often lacks US house numbers; for
  // that case we keep the number the guest typed. Each suggestion is
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
        // Photon readily returns nearby but different streets: keep only streets whose
        // name the guest actually typed
        var word = (street.toLowerCase().match(/[a-z0-9]{3,}/) || [""])[0];
        if (!word || q.toLowerCase().indexOf(word) === -1) return;
        var number = p.housenumber || typedNumber;   // OSM often lacks the house number; keep the guest's
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
