# Registering a license

Read this only after the license check in `install.md` found the server unlicensed **and** the user said yes to licensing it. A license covers the whole server: on a server the user does not own, the owner decides.

## Getting a key

A free **Developer** key (for development, not production) is requested at <https://ravendb.net/download> → *Developer* and arrives by email. Its limits are carried in the key: read them off `/license/status` after activation.

**The details are the user's**: real name, email, company, country, job title, industry, intended use. Collect them in one interaction, tell the user the form has terms to accept, and say plainly that the key goes to the address they give and the details reach RavenDB's sales team. Never invent, guess or reuse details from elsewhere, whoever does the typing.

Then the user submits the form, or you drive it with a browser tool. Without one, say so and offer the choice:

> I can fill the license form for you, but I need Playwright to reach the page: `npm i playwright && npx playwright install chromium`. Otherwise, go to <https://ravendb.net/download>, pick *Developer*, fill in the form, and paste the key here when the email arrives.

## Driving the form

Derive every handle from the live page: it is a marketing page, and any selector, label or option list written here would be stale. Three things are structural: a cookie banner may swallow the first click; **the license form does not exist until a tier card is clicked**; and **the page has look-alike controls outside the license form**: a site search box, and a download section with its own terms checkbox and submit button.

1. Pick the tier by the **text of its card**, never by position. Confirm the form rendered by a field only it has (a name or email input); a terms checkbox or submit button proves nothing.
2. **Scope everything to the license form's own container.** Enumerate its visible inputs, read `name`, `id` and placeholder, map the user's answers by meaning, and read each value back: one that did not stick means you addressed something outside the form. Prefer `name` over a generated-looking `id`, which changes per render.
3. **Open each dropdown and read the options actually there**, pick the closest match to what the user said, and tell them which. Never hardcode options; stale labels silently send the wrong answer. Check whether the control is a real `<select>`: a scripted one needs the option clicked while the menu is open, because options unmount on blur.
4. Check the license form's terms checkbox, leave marketing consent alone unless the user asked for it, and submit with the button whose text offers to generate the license (a sibling button in the same form also submits). Success navigates to a confirmation page: report its response verbatim rather than declaring success yourself.

If a handle stops matching, read the page again rather than retrying it.

**An invisible reCAPTCHA ships with the form and needs no interaction**; it sits in a body-level badge outside the form, so finding one is not a failure. An interactive challenge or a rate limit ends the attempt: hand the user the manual path rather than working around either.

## Why there is no headless route

`POST /license/free/send-verification-code` and `POST /license/free/download` (`LicenseType` `Developer` or `Community`) refuse outside **setup mode**, answering `403` "RavenDB has already been setup". A server started with `Setup.Mode=None` is past setup, so the website form is the only route to a new key.

## Activating the key you were given

The email carries a JSON object: `{"Id": "…", "Name": "…", "Keys": ["…"]}`. Either the user pastes it into Studio's *About* page, or you save it to a file and post **that object, unwrapped,** as the body:

```bash
curl -s -o /dev/null -w '%{http_code}\n' -X POST http://localhost:8080/admin/license/activate \
  -H 'Content-Type: application/json' --data-binary @license.json      # 204 on success
```

- `405`: the server runs with `License.CanActivate=false`; no body gets past that.
- A key the server cannot validate returns **500** `InvalidDataException: Could not validate license!`, not a 4xx, so code that treats 5xx as a server fault misreads a bad key. A `{"License": …}` wrapper also fails, with `ArgumentNullException` from the validator. Neither changes the license state.
- Activation is a cluster-admin operation: on a secured server it needs a client certificate with that clearance.
- Setting the key in configuration instead (`License`, `License.Path`, `RAVEN_License` in Docker): `client-docs.md` (Activating a license).

Then verify, and report what you find:

```bash
curl -s http://localhost:8080/license/status      # expect Type to have changed, and the Has* flags the app needs to be true
```

An unchanged `Type` means the key did not apply: say so.
