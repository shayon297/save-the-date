# Save the Date — Amanda & Shayon

A static save-the-date site (plain HTML/CSS/JS, no build step) for the wedding on
Sunday, May 16, 2027 at the Cincinnati Art Museum.

- Live: https://shayon297.github.io/save-the-date/
- Deploy: push to `main`. GitHub Pages serves the repo root and updates in about a minute.

## Files

| File | What it is |
|---|---|
| `index.html` | The card: header, engagement photo, countdown, The Weekend, address form, closing |
| `styles.css` | All styling. Palette and fonts are CSS variables at the top |
| `script.js` | Countdown, "Add to calendar" links, address form |
| `assets/welcome-party.ics`, `assets/wedding.ics` | Calendar files for Apple / Outlook. Keep in sync with `EVENTS` in `script.js` |
| `tools-flora.py` | Draws the drapes, flowers and the top swag. Run `python3 tools-flora.py assets` to regenerate them |
| `assets/drape-wide.svg`, `assets/drape-narrow.svg` | Generated drapes (desktop / phone and tablet). Don't hand-edit; change `tools-flora.py` |
| `assets/swag.svg` | Generated shallow swag across the top joining the drapes at the centre (stretches to the card width) |
| `assets/engagement.jpg` | Engagement photo in the arched frame under the header (the figure hides itself if the file is missing) |
| `assets/og.jpg` | Link preview (1200×630), rendered from the page with `?preview=og` |
| `assets/card-email.jpg` | Image used in `email.html`, rendered with `?preview=email` |
| `email.html` | Email version (replace `GUEST_NAME` per send) |
| `sms.txt` | Text-message version |
| `google-apps-script.gs` | The Apps Script that runs inside the address spreadsheet |

## Run it locally

```bash
python3 -m http.server 8792
```

Open http://localhost:8792 and check both a desktop width (about 760px or wider)
and a phone width (375px) before calling a change done.

## Conventions

- **Cache-busting:** after editing `styles.css`, `script.js`, or an asset, bump its
  `?v=` number in `index.html`, or browsers keep showing the old file.
- **Share images:** after visual changes to the top of the card, re-render the
  previews with headless Chrome, then save them as JPGs in `assets/`:

  ```bash
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --hide-scrollbars \
    --window-size=1200,630 --force-device-scale-factor=2 --virtual-time-budget=10000 \
    --screenshot=og.png "http://localhost:8792/?preview=og"
  ```
  (For the email image use `?preview=email` with `--window-size=760,<card height>` so the card fills the image edge to edge. Headless
  Chrome sometimes doesn't exit on its own; stop it once the PNG is written.)
- **Event times** (Eastern): Welcome Party Sat May 15, 6:30–9:30 PM at Via Vite;
  Wedding Ceremony & Reception Sun May 16, 5:30–11:00 PM. Times in `script.js`
  and `assets/*.ics` are stored in UTC (EDT is UTC−4).

## Address form

- Posts JSON to the Apps Script web app in `CONFIG.sheetEndpoint` (`script.js`).
  Each submission becomes a row in a Google Sheet that Shayon owns; ask him for
  access. If the script in `google-apps-script.gs` changes, it has to be pasted
  into the sheet and redeployed (Deploy → Manage deployments → New version).
- Email is optional (Amanda's call), but checked if given. A hidden `website` field is a honeypot: if it's filled,
  the form shows the thank-you and sends nothing.
- By design there is no email/mailto fallback. Submissions go to the sheet only.
- Address suggestions: Google Places (New) when `CONFIG.placesKey` is set in
  `script.js` (key restricted to this site's referrers, Places API (New) enabled);
  otherwise Photon (OpenStreetMap), which only offers exact matches (the typed
  street and house number), because OSM often lacks US house numbers and would
  otherwise suggest wrong addresses. Google failures fall back to Photon.

## Design decisions so far (keep unless asked to change)

- Styled after Minted's "museo" save the date: "Save the Date" in copperplate
  script, names in spaced capitals, a lowercase italic date line, an olive
  double-rule frame, one olive ink throughout. Fonts are Pinyon Script and
  Baskervville, free stand-ins for museo's licensed Monalisa Script and Mrs Eaves.
- Direction: classical Greek / Roman in spirit (restraint, symmetry, proportion),
  not literal. Script is used only for "Save the Date", the closing line and the
  monogram; section titles are Baskervville spaced capitals.
- Hebrew: only the verse אֲנִי לְדוֹדִי וְדוֹדִי לִי at the top, no translation.
  No Hebrew date (that belongs on the formal invitation).
- The engagement photo sits in an arch-topped frame under the header.
- No ornamental dividers, as on museo: sections are separated by space and
  the change of type (script, spaced capitals, lowercase italics).
- Countdown is a quiet line in the closing ("224 days to go"); "formal invitation
  to follow" sits under the date line in lowercase italics.
- Calendar buttons are outlined (ghost); only Send is solid.
- Drapes (Amanda's pick, "B" + "C"'s swag): full-height drapes hanging from the
  frame's top corners with a pale fabric fill; the outer edge stays flush with the
  frame and the tie-back (about a third of the way down) gathers the folds against
  it, widening gradually to the hem, and a garland along each inner edge (fullest at the top corner,
  open roses spaced to the hem). A shallow scalloped swag runs across the top from
  each drape and the two halves meet at the centre (no knot, tail or centre tie);
  it sits behind the drapes.
- The monogram is museo's own: A over S in Baskervville capitals inside a double-ruled
  oval (as on museo's enclosure cards and belly band). Script monograms were tried and
  rejected (Pinyon's S reads as an L).
- Names are bride first everywhere (card, titles, monogram A & S, calendar events,
  email, text message), the usual order on wedding stationery.
- Phones should look like a scaled-down desktop, not a different design, and
  text must not touch the drapes.
- Tried and rejected: a deep swag with a long hanging tail; a curtain-top arch; curtains drawn from a rod meeting at the centre (round or pointed opening); literal classical motifs (Cinzel inscription capitals,
  Greek-key dividers, a laurel wreath around the monogram, Roman-numeral date),
  pinstripe borders, all-over flower patterns, extra frames
  competing with the drapes. (An earlier note rejected flowers bunched at the ties;
  the curtain references Amanda chose have a cluster there, so the tie cluster stays.)
- The page has `noindex` so it stays out of search results.

## Working on this site

- Say explicitly when you remove any content; don't let removals pass silently.
- Verify changes visually at desktop and phone widths before reporting them done.
