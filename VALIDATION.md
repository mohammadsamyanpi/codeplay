# Validation — account and quest extension

Validated locally on October 7, 2026. These checks cover the account extension to the existing CodePlay project; no hosted account-server deployment has been performed.

## Automated checks

`python test_server.py`: 11 integration tests passing. Disposable SQLite databases are used; real accounts are unaffected. Coverage includes authentication, login/logout, hashed passwords, expired sessions, CSRF/origin enforcement, Free/Pro restrictions, account isolation, cross-device progress, all 44 bilingual exercises, duplicate and concurrent completion awards, and private-file protection.

Python source compiles and JavaScript source parses. Git whitespace checks pass. Docker configuration is supplied but no container build was available locally.

## Browser inspection

Inspected DOM and rendered page structure in Chrome: anonymous quest visits show login; the Free map contains 24 quests; all six exercise types render; the profile displays current stage and independent path totals. Authenticated UI was inspected through an isolated read-only preview fixture; real authentication and submission were tested through the API integration suite. Horizontal scroll width matched viewport width in the inspected mobile map/profile pages.

Browser screenshot capture timed out, so pixel-level visual verification is incomplete. Browser form submission and Python WebAssembly execution were not re-tested in this extension. The existing worker was preserved.

## Release conditions

Deploy the Python account server behind HTTPS with persistent storage, then verify registration, login, logout, progress on a second device and Pro denial/activation on that host. GitHub Pages alone cannot run the API. Pro currently uses administrator-managed access; payments, password recovery, account deletion/export and production operating controls remain future work.
