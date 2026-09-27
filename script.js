// Shayon & Amanda — Save the Date
(function () {
  "use strict";

  // ---- countdown (midnight Eastern on the wedding day; exact time TBD) ----
  var target = new Date("2027-05-16T00:00:00-04:00").getTime();
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

  // ---- add-to-calendar (all-day .ics, no time assumed yet) ----
  var EVENTS = {
    reception: {
      title: "Shayon & Amanda — Reception Dinner",
      location: "Via Vite, 520 Vine St, Cincinnati, OH 45202",
      start: "20270515",
      end: "20270516",
    },
    wedding: {
      title: "Shayon & Amanda — Wedding Ceremony",
      location: "Cincinnati Art Museum, 953 Eden Park Dr, Cincinnati, OH 45202",
      start: "20270516",
      end: "20270517",
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
      "DTSTART;VALUE=DATE:" + ev.start,
      "DTEND;VALUE=DATE:" + ev.end,
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
})();
