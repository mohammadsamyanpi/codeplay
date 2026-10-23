# Deploying the account version

## GitHub Pages without a separate server

The account version can stay on the existing GitHub Pages URL by using Supabase as the hosted auth/database service. The repository contains `site-config.js`, `supabase-api.js`, and the generated `supabase/setup.sql`. Run that SQL once in the Supabase SQL Editor, configure the GitHub Pages URL under Auth URL Configuration, and publish the branch that contains these files. Keep only the publishable key in the browser; never add the secret key.

This version needs a Python process and persistent SQLite storage. GitHub Pages only serves static files; committing this code does not deploy the account API. Keep the existing public Pages site until the Python deployment is verified.

## Local preview

Run `python server.py` and open `http://127.0.0.1:8000/`. No packages are required. Database files are created in `data/`, which is ignored by Git. Do not use `python -m http.server` for accounts: it cannot run the API and would expose source files.

## Hosted pilot

Use a host that runs Python 3.11+ or the supplied Docker image, with an HTTPS reverse proxy and a persistent data volume. Configure:

- `CODEPLAY_ORIGIN`: exact public HTTPS origin, for example `https://learn.example.com`, without a trailing slash or path.
- `CODEPLAY_DB`: persistent path to `codeplay.sqlite3`; its parent must be writable by the app user.
- `PORT`: port expected by the host, default 8000. The Docker command explicitly uses 8000.

Start with `python server.py --host 0.0.0.0`. The process refuses public binding without an HTTPS origin. HTTPS must be provided by the hosting service or reverse proxy; the Python process itself serves HTTP behind it. Serve the frontend and `/api/` on the same origin at the site root. No API keys or browser-stored authentication tokens are needed.

For Docker, build `docker build -t codeplay .`, then run with your exact `CODEPLAY_ORIGIN` and a named volume mounted at `/app/data`. Use the platform's HTTPS proxy. A permanent volume is necessary: replacing a container without it loses accounts and progress. Back up the database using SQLite's backup API rather than copying it during writes.

The dependency-free HTTP server is intended for development and a small hosted pilot behind a maintained reverse proxy. Before a larger public launch, migrate request handling to a production application server, add durable rate limiting, monitoring, backups, password recovery, and account deletion/export. The existing application already hashes passwords, validates requests, checks CSRF/origin, and authorizes lessons server-side, but these are not substitutes for operating the hosting environment.

## Pro accounts

All registrations create Free accounts. From the server's trusted terminal, run:

```text
python server.py --grant-pro USERNAME
python server.py --revoke-pro USERNAME
```

Set the same `CODEPLAY_DB` when running administration commands. The API never accepts plan changes from a learner. An existing session sees updated access on its next API request. Pro is managed access, not a payment subscription. No billing has been connected.

## Release verification

Run `python test_server.py` before release. On the hosted site, verify registration, login, logout, quest completion, progress after signing in on another device, and a denied Pro quest for a Free user. Verify HTTPS and persistent storage before directing learners away from the Pages preview. Never publish `data/`, `.env`, test databases or account credentials.
