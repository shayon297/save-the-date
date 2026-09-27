/**
 * Shayon & Amanda — RSVPs + mailing addresses → Google Sheet
 * ------------------------------------------------------------
 * Drop-in upgrade for the script already deployed for the main wedding site.
 * It keeps the RSVP behaviour exactly as before and adds an "Addresses" tab
 * for submissions from the save-the-date site.
 *
 * TO UPGRADE THE EXISTING DEPLOYMENT (keeps the same /exec URL):
 *  1. Open the RSVP Google Sheet → Extensions → Apps Script.
 *  2. Replace the code with THIS file. Save.
 *  3. Deploy → Manage deployments → pencil icon → Version: "New version" → Deploy.
 *
 * Until you do this, address submissions still arrive: the old script writes
 * them into the RSVPs tab with Response = "Mailing address" and the full
 * address in the Note column.
 */

var RSVP_SHEET = 'RSVPs';
var RSVP_HEADERS = ['Received', 'Name', 'Email', 'Phone', 'Response', 'Guests', 'Events', 'Dietary', 'Song', 'Note'];

var ADDRESS_SHEET = 'Addresses';
var ADDRESS_HEADERS = ['Received', 'Name', 'Email', 'Street', 'Apt / unit', 'City', 'State', 'ZIP', 'Country', 'Full address'];

function doPost(e) {
  try {
    var data = JSON.parse(e.postData.contents);
    var ss = SpreadsheetApp.getActiveSpreadsheet();

    if (data.type === 'address') {
      var ash = ss.getSheetByName(ADDRESS_SHEET) || ss.insertSheet(ADDRESS_SHEET);
      if (ash.getLastRow() === 0) ash.appendRow(ADDRESS_HEADERS);
      ash.appendRow([
        new Date(),
        data.name || '', data.email || '',
        data.street || '', data.unit || '', data.city || '', data.state || '', data.zip || '', data.country || '',
        data.address || ''
      ]);
    } else {
      var sh = ss.getSheetByName(RSVP_SHEET) || ss.insertSheet(RSVP_SHEET);
      if (sh.getLastRow() === 0) sh.appendRow(RSVP_HEADERS);
      sh.appendRow([
        new Date(),
        data.name || '', data.email || '', data.phone || '',
        data.attending || '', data.guests || '', data.events || '',
        data.diet || '', data.song || '', data.note || ''
      ]);
    }

    return ContentService
      .createTextOutput(JSON.stringify({ ok: true }))
      .setMimeType(ContentService.MimeType.JSON);
  } catch (err) {
    return ContentService
      .createTextOutput(JSON.stringify({ ok: false, error: String(err) }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}

function doGet() {
  return ContentService.createTextOutput('Endpoint is live.');
}
