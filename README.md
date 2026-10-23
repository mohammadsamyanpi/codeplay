# CodePlay

A bilingual English/Persian learning app with account-based Python and Django quests. The existing landing page, assets, themes and browser Python editor are preserved. No Node installation or build step is required.

## Run locally

Requires Python 3.11 or newer, with no additional packages.

```powershell
python server.py
```

Open `http://127.0.0.1:8000/`. Register an account before playing. Accounts and progress are stored in `data/codeplay.sqlite3`; that directory is excluded from Git. Use the account server rather than a generic static file server.

## Learning paths

- Free: 24 quests — 20 Python fundamentals and four broad Django introductions.
- Pro: 20 separate missions — six advanced Python and 14 detailed Django exercises.
- Six exercise types: multiple choice, missing code, output prediction, debugging, line ordering, and guided projects with multiple code gaps.
- Any quest in an account's available path can be opened without sequential locks.
- Correct answers award 50 XP once per quest. Hints and bilingual explanations accompany each quest.
- Profiles show the current stage, next unfinished stage, completion history, XP, streak and separate Free/Pro totals. Progress is shared across devices signing into the same server account.

All registrations create Free accounts. The administrator grants Pro with `python server.py --grant-pro USERNAME` and removes it with `--revoke-pro USERNAME`. No checkout or automatic paid subscription is connected.

## Accounts and execution

The backend validates authentication and plan access for quest content and answers. Passwords use salted PBKDF2 hashes; session cookies are HttpOnly. Authenticated writes require CSRF tokens and matching origins. Server-side completion records prevent duplicate XP, including concurrent submissions. Private source and database files are excluded from HTTP serving.

The practice editor runs real Python via Pyodide 0.29.2 in a Web Worker, with a 60-second limit. Its first run needs internet access to jsDelivr. Editor drafts, language and theme remain local; completed quests are stored in the account. The server checks structured exercise answers and never executes submitted Python. Django exercises teach code through questions and guided scaffolds; this app does not execute learner-created Django websites.

## Verification

```powershell
python test_server.py
```

The 11 integration tests cover guest restrictions, Pro authorization, sessions, CSRF/origin checks, account isolation, progress across devices, all 44 lessons, duplicate/concurrent XP and private-file protection. See [VALIDATION.md](VALIDATION.md) for current evidence and limits.

## Hosting

The existing public site uses GitHub Pages. Pages cannot run this account API. This version must be hosted with a Python process, HTTPS and persistent storage; see [DEPLOYMENT.md](DEPLOYMENT.md). Do not replace the public static preview until that deployment is verified. A Dockerfile is included. The dependency-free HTTP server is suitable for local development and a small pilot behind an HTTPS proxy; a larger public launch needs production hosting, durable rate limiting, monitoring, password recovery, account export/deletion and backups.

## GitHub Pages + Supabase

The hosted GitHub Pages build now uses the public Supabase URL and publishable key in `site-config.js`. It loads the Supabase browser SDK from esm.sh only on the GitHub Pages origin; local development continues to use `server.py`.

To activate accounts on the published site, open the Supabase **SQL Editor**, paste the complete contents of `supabase/setup.sql`, and run it once. Then set the Supabase Auth URL configuration: add `https://mohammadsamyanpi.github.io/codeplay/` to **Site URL** and to the allowed redirect URLs. Email confirmation is enabled in the current project, so learners must confirm their email before their first sign-in. The SQL script seeds all 44 lessons, creates protected profile/completion tables, and exposes only the required authenticated RPCs.

Never put `SUPABASE_SECRET_KEY` in this repository or in a browser. Rotate the secret key if it has been exposed. `SUPABASE_JWKS_URL` is for a separate token-verifying backend and is not needed by the GitHub Pages client.

## Sources and assets

Learning format research and primary references are recorded in [RESEARCH.md](RESEARCH.md). Lessons are original bilingual content. Existing hero and robot images were extracted from the original supplied design. Vazirmatn uses the SIL Open Font License in `assets/OFL.txt`. Persona stories remain explicitly illustrative, rather than customer reviews.
