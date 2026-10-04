/**
 * Save the Date — mailing addresses → Google Sheet
 * ------------------------------------------------------------
 * Bound to the "Save the Date — Mailing Addresses" spreadsheet only.
 * Unrelated to the main wedding site's RSVP sheet.
 *
 * SETUP:
 *  1. Open the spreadsheet → Extensions → Apps Script.
 *  2. Replace the sample code with this whole file. Save.
 *  3. Deploy → New deployment → gear icon → "Web app".
 *       Execute as: Me    ·    Who has access: Anyone
 *     Deploy, then authorize when asked.
 *  4. Copy the Web app URL (ends in /exec) and put it in
 *     CONFIG.sheetEndpoint in script.js.
 */

var HEADERS = ['Received', 'Name', 'Email', 'Street', 'Apt / unit', 'City', 'State', 'ZIP', 'Country', 'Full address'];

// Guest-typed text that starts with = + - @ would run as a formula; store it as text.
function clean(v) {
  v = String(v == null ? '' : v).slice(0, 500);
  return /^[=+\-@]/.test(v) ? "'" + v : v;
}

function doPost(e) {
  try {
    var d = JSON.parse(e.postData.contents);
    var sh = SpreadsheetApp.getActiveSpreadsheet().getSheets()[0];
    if (sh.getLastRow() === 0) sh.appendRow(HEADERS);
    var row = sh.getLastRow() + 1;
    sh.getRange(row, 8).setNumberFormat('@');  // ZIP as text, so 02134 keeps its leading zero
    sh.getRange(row, 1, 1, HEADERS.length).setValues([[
      new Date(),
      clean(d.name), clean(d.email), clean(d.street), clean(d.unit),
      clean(d.city), clean(d.state), clean(d.zip), clean(d.country), clean(d.address)
    ]]);
    return ContentService.createTextOutput(JSON.stringify({ ok: true }))
      .setMimeType(ContentService.MimeType.JSON);
  } catch (err) {
    return ContentService.createTextOutput(JSON.stringify({ ok: false, error: String(err) }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}

// Opening the /exec URL in a browser confirms it's live.
function doGet() {
  return ContentService.createTextOutput('Save the Date address endpoint is live.');
}
