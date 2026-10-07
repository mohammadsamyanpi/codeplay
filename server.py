"""CodePlay account API and static site. Python 3.11+, no dependencies."""
import argparse
from contextlib import contextmanager
import hashlib
import hmac
import json
import os
import re
import secrets
import sqlite3
import time
from datetime import date, timedelta
from http.cookies import SimpleCookie
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Lock
from urllib.parse import urlsplit

from catalog import BY_ID, LESSONS, correct, public

ROOT = Path(__file__).resolve().parent
DB_PATH = Path(os.environ.get('CODEPLAY_DB', str(ROOT / 'data' / 'codeplay.sqlite3')))
PUBLIC_ORIGIN = os.environ.get('CODEPLAY_ORIGIN', '').rstrip('/')
SECURE = PUBLIC_ORIGIN.startswith('https://')
ROUNDS = 600_000
MAX_BODY = 16_384
RATE_LIMIT = {}
RATE_LOCK = Lock()


@contextmanager
def database():
    db = sqlite3.connect(DB_PATH, timeout=15)
    db.row_factory = sqlite3.Row
    db.execute('PRAGMA foreign_keys=ON')
    try:
        with db:
            yield db
    finally:
        db.close()


def initialize():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with database() as db:
        db.executescript('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY, username TEXT UNIQUE NOT NULL,
                display_name TEXT NOT NULL, salt TEXT NOT NULL, password TEXT NOT NULL,
                plan TEXT NOT NULL DEFAULT 'free' CHECK(plan IN ('free','pro')),
                current_lesson TEXT, created_at INTEGER NOT NULL);
            CREATE TABLE IF NOT EXISTS sessions (
                token TEXT PRIMARY KEY, user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                csrf TEXT NOT NULL, expires INTEGER NOT NULL);
            CREATE TABLE IF NOT EXISTS completions (
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                lesson_id TEXT NOT NULL, day TEXT NOT NULL,
                PRIMARY KEY(user_id, lesson_id));
        ''')


def password_hash(password, salt):
    return hashlib.pbkdf2_hmac('sha256', password.encode(), bytes.fromhex(salt), ROUNDS).hex()


def session_key(token):
    return hashlib.sha256(token.encode()).hexdigest()


class APIError(Exception):
    def __init__(self, status, code):
        self.status, self.code = status, code


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def end_headers(self):
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Referrer-Policy', 'same-origin')
        self.send_header('X-Frame-Options', 'DENY')
        self.send_header('Cache-Control', 'no-store' if self.path.startswith('/api/') else 'no-cache')
        super().end_headers()

    def json_response(self, status, payload, cookie=None):
        if getattr(self, 'buffer_api', False):
            self.pending_response = (status, payload, cookie)
            return
        body = json.dumps(payload, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        if cookie:
            self.send_header('Set-Cookie', cookie)
        self.end_headers()
        self.wfile.write(body)

    def cookie(self, token='', max_age=0):
        return f'codeplay_session={token}; Path=/; HttpOnly; SameSite=Lax; Max-Age={max_age}' + ('; Secure' if SECURE else '')

    def session(self, db, required=True):
        try:
            cookies = SimpleCookie(self.headers.get('Cookie', ''))
            token = cookies['codeplay_session'].value if 'codeplay_session' in cookies else ''
        except Exception:
            token = ''
        row = db.execute('''SELECT u.*, s.csrf, s.token FROM sessions s JOIN users u ON s.user_id=u.id
                            WHERE s.token=? AND s.expires>?''', (session_key(token), int(time.time()))).fetchone()
        if not row and required:
            raise APIError(401, 'login_required')
        return row

    def profile(self, db, user):
        completed = [dict(row) for row in db.execute('SELECT lesson_id,day FROM completions WHERE user_id=? ORDER BY day,lesson_id', (user['id'],))]
        ids = {row['lesson_id'] for row in completed}
        available = [item for item in LESSONS if item['track'] == 'free' or user['plan'] == 'pro']
        next_lesson = next((item['id'] for item in available if item['id'] not in ids), None)
        days = {row['day'] for row in completed}
        cursor = date.today()
        if cursor.isoformat() not in days:
            cursor -= timedelta(days=1)
        streak = 0
        while cursor.isoformat() in days:
            streak += 1
            cursor -= timedelta(days=1)
        return dict(username=user['username'], display_name=user['display_name'], plan=user['plan'],
                    completed=completed, xp=sum(BY_ID[row['lesson_id']]['xp'] for row in completed if row['lesson_id'] in BY_ID),
                    current_lesson=user['current_lesson'], next_lesson=next_lesson, streak=streak,
                    tracks={track: dict(completed=sum(item['id'] in ids for item in LESSONS if item['track'] == track),
                                        total=sum(item['track'] == track for item in LESSONS)) for track in ('free', 'pro')})

    def allowed_lesson(self, user, lesson_id):
        item = BY_ID.get(lesson_id)
        if not item:
            raise APIError(404, 'lesson_missing')
        if item['track'] == 'pro' and user['plan'] != 'pro':
            raise APIError(403, 'pro_required')
        return item

    def origin_check(self):
        expected = PUBLIC_ORIGIN or f'http://{self.headers.get("Host", "")}'
        if self.headers.get('Origin') != expected:
            raise APIError(403, 'invalid_origin')
        if self.headers.get('Content-Type', '').split(';')[0].strip() != 'application/json':
            raise APIError(415, 'json_required')

    def body(self):
        try:
            size = int(self.headers.get('Content-Length', '0'))
            if size <= 0 or size > MAX_BODY:
                raise APIError(413, 'invalid_body')
            payload = json.loads(self.rfile.read(size))
            if not isinstance(payload, dict):
                raise ValueError()
            return payload
        except (ValueError, UnicodeError):
            raise APIError(400, 'invalid_body')

    def throttle(self):
        now = time.monotonic()
        key = self.client_address[0]
        with RATE_LOCK:
            expired = [ip for ip, visits in RATE_LIMIT.items() if not visits or now - visits[-1] >= 300]
            for ip in expired:
                del RATE_LIMIT[ip]
            visits = [t for t in RATE_LIMIT.get(key, []) if now - t < 300]
            if len(visits) >= 20:
                raise APIError(429, 'too_many_attempts')
            visits.append(now)
            RATE_LIMIT[key] = visits

    def api(self, method):
        path = urlsplit(self.path).path
        self.buffer_api = True
        self.pending_response = None
        try:
            with database() as db:
                if method == 'GET':
                    if path == '/api/session':
                        user = self.session(db, False)
                        return self.json_response(200, dict(profile=self.profile(db, user) if user else None, csrf=user['csrf'] if user else None))
                    if path == '/api/lessons':
                        user = self.session(db, False)
                        return self.json_response(200, dict(lessons=[dict(public(item), locked=item['track'] == 'pro' and (not user or user['plan'] != 'pro')) for item in LESSONS]))
                    user = self.session(db)
                    if path == '/api/profile':
                        return self.json_response(200, dict(profile=self.profile(db, user)))
                    if path.startswith('/api/lessons/'):
                        item = self.allowed_lesson(user, path.rsplit('/', 1)[1])
                        db.execute('UPDATE users SET current_lesson=? WHERE id=?', (item['id'], user['id']))
                        return self.json_response(200, dict(lesson=public(item, True)))
                elif method == 'POST':
                    self.origin_check()
                    payload = self.body()
                    if path in ('/api/register', '/api/login'):
                        self.throttle()
                        username, password = payload.get('username'), payload.get('password')
                        if not isinstance(username, str) or not re.fullmatch(r'[A-Za-z0-9_]{3,32}', username) or not isinstance(password, str) or not 10 <= len(password) <= 128:
                            raise APIError(400, 'invalid_credentials')
                        username = username.lower()
                        if path == '/api/register':
                            name = payload.get('display_name', username)
                            if not isinstance(name, str) or not 1 <= len(name.strip()) <= 60:
                                raise APIError(400, 'invalid_name')
                            if db.execute('SELECT 1 FROM users WHERE username=?', (username,)).fetchone():
                                raise APIError(409, 'username_taken')
                            salt = secrets.token_hex(16)
                            db.execute('INSERT INTO users(username,display_name,salt,password,created_at) VALUES(?,?,?,?,?)',
                                       (username, name.strip(), salt, password_hash(password, salt), int(time.time())))
                        user = db.execute('SELECT * FROM users WHERE username=?', (username,)).fetchone()
                        salt = user['salt'] if user else '0' * 32
                        hashed = password_hash(password, salt)
                        if not user or not hmac.compare_digest(user['password'], hashed):
                            raise APIError(401, 'wrong_credentials')
                        token, csrf = secrets.token_urlsafe(32), secrets.token_urlsafe(32)
                        db.execute('DELETE FROM sessions WHERE expires<=?', (int(time.time()),))
                        db.execute('INSERT INTO sessions VALUES(?,?,?,?)', (session_key(token), user['id'], csrf, int(time.time()) + 604800))
                        db.commit()
                        return self.json_response(200, dict(profile=self.profile(db, user), csrf=csrf), self.cookie(token, 604800))
                    user = self.session(db)
                    if not hmac.compare_digest(self.headers.get('X-CSRF-Token', ''), user['csrf']):
                        raise APIError(403, 'invalid_csrf')
                    if path == '/api/logout':
                        db.execute('DELETE FROM sessions WHERE token=?', (user['token'],))
                        db.commit()
                        return self.json_response(200, dict(ok=True), self.cookie())
                    if path == '/api/profile':
                        name = payload.get('display_name')
                        if not isinstance(name, str) or not 1 <= len(name.strip()) <= 60:
                            raise APIError(400, 'invalid_name')
                        db.execute('UPDATE users SET display_name=? WHERE id=?', (name.strip(), user['id']))
                        user = db.execute('SELECT * FROM users WHERE id=?', (user['id'],)).fetchone()
                        db.commit()
                        return self.json_response(200, dict(profile=self.profile(db, user)))
                    if path == '/api/answer':
                        item = self.allowed_lesson(user, payload.get('lesson_id') if isinstance(payload.get('lesson_id'), str) else '')
                        passed = correct(item, payload.get('answer'))
                        earned = 0
                        if passed:
                            inserted = db.execute('INSERT OR IGNORE INTO completions VALUES(?,?,?)', (user['id'], item['id'], date.today().isoformat())).rowcount
                            earned = item['xp'] if inserted else 0
                            db.execute('UPDATE users SET current_lesson=? WHERE id=?', (item['id'], user['id']))
                        db.commit()
                        user = db.execute('SELECT * FROM users WHERE id=?', (user['id'],)).fetchone()
                        return self.json_response(200, dict(correct=passed, earned=earned, explanation=item['explanation'], profile=self.profile(db, user)))
                raise APIError(404, 'not_found')
        except APIError as error:
            self.json_response(error.status, dict(error=error.code))
        except sqlite3.IntegrityError:
            self.json_response(409, dict(error='username_taken'))
        except Exception:
            self.log_error('API request failed')
            self.json_response(500, dict(error='server_error'))
        finally:
            self.buffer_api = False
            if self.pending_response:
                self.json_response(*self.pending_response)

    def public_file(self):
        # Allowlist prevents exposing SQLite, solutions, Python, .git or deployment config.
        path = urlsplit(self.path).path
        if path in ('/', '/index.html', '/app.js', '/learning.js', '/styles.css', '/python-worker.js'):
            return True
        return path in {f'/assets/{file.name}' for file in (ROOT / 'assets').iterdir() if file.is_file()}

    def do_GET(self):
        if urlsplit(self.path).path.startswith('/api/'):
            self.api('GET')
        elif self.public_file():
            super().do_GET()
        else:
            self.send_error(404)

    def do_HEAD(self):
        if self.public_file():
            super().do_HEAD()
        else:
            self.send_error(404)

    def do_POST(self):
        if urlsplit(self.path).path.startswith('/api/'):
            self.api('POST')
        else:
            self.send_error(404)


def run():
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', type=int, default=int(os.environ.get('PORT', '8000')))
    parser.add_argument('--grant-pro', metavar='USERNAME')
    parser.add_argument('--revoke-pro', metavar='USERNAME')
    args = parser.parse_args()
    initialize()
    if args.grant_pro or args.revoke_pro:
        with database() as db:
            count = db.execute('UPDATE users SET plan=? WHERE username=?', ('pro' if args.grant_pro else 'free', (args.grant_pro or args.revoke_pro).lower())).rowcount
        if not count:
            parser.error('Account not found')
        print('Account plan updated.')
        return
    if args.host not in ('127.0.0.1', 'localhost') and not PUBLIC_ORIGIN.startswith('https://'):
        parser.error('Set CODEPLAY_ORIGIN to your HTTPS origin before binding publicly.')
    print(f'CodePlay running at http://{args.host}:{args.port}', flush=True)
    ThreadingHTTPServer((args.host, args.port), Handler).serve_forever()


if __name__ == '__main__':
    run()
