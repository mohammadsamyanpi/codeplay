"""Integration tests use a disposable database; no real accounts are modified."""
import http.client
import json
import tempfile
import threading
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import server
from catalog import LESSONS, correct


class QuietHandler(server.Handler):
    def log_message(self, *args):
        pass


class Client:
    def __init__(self, port):
        self.port, self.cookie, self.csrf = port, '', ''

    def call(self, path, data=None, extra=None):
        connection = http.client.HTTPConnection('127.0.0.1', self.port, timeout=15)
        headers = {'Cookie': self.cookie}
        if data is not None:
            headers.update({'Origin': f'http://127.0.0.1:{self.port}', 'Content-Type': 'application/json', 'X-CSRF-Token': self.csrf})
        headers.update(extra or {})
        connection.request('GET' if data is None else 'POST', path, json.dumps(data) if data is not None else None, headers)
        response = connection.getresponse()
        raw = response.read()
        if response.getheader('Set-Cookie'):
            self.cookie = response.getheader('Set-Cookie').split(';')[0]
        result = json.loads(raw) if 'application/json' in response.getheader('Content-Type', '') else raw
        if isinstance(result, dict) and result.get('csrf'):
            self.csrf = result['csrf']
        status = response.status
        connection.close()
        return status, result

    def register(self, name='learner'):
        return self.call('/api/register', {'username': name, 'password': 'test-password-123', 'display_name': 'یادگیرنده'})


class AccountTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        (server.ROOT / 'tmp').mkdir(exist_ok=True)
        cls.http = server.ThreadingHTTPServer(('127.0.0.1', 0), QuietHandler)
        cls.thread = threading.Thread(target=cls.http.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.http.shutdown()
        cls.http.server_close()
        cls.thread.join()

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=server.ROOT / 'tmp')
        server.DB_PATH = Path(self.temp.name) / 'test.sqlite3'
        server.RATE_LIMIT.clear()
        server.initialize()
        self.client = Client(self.http.server_port)

    def tearDown(self):
        self.temp.cleanup()

    def test_guest_cannot_read_or_answer_quests(self):
        for path in ('/api/profile', '/api/lessons/free-01', '/api/lessons/pro-01'):
            self.assertEqual(self.client.call(path)[0], 401)
        self.assertEqual(self.client.call('/api/answer', {'lesson_id': 'free-01', 'answer': 'print("Hello")'})[0], 401)
        self.assertIsNone(self.client.call('/api/session')[1]['profile'])

    def test_public_metadata_never_contains_solutions(self):
        items = self.client.call('/api/lessons')[1]['lessons']
        self.assertEqual(len(items), 44)
        for item in items:
            self.assertFalse({'answer', 'explanation', 'code', 'hint'} & item.keys())

    def test_register_login_logout_and_hashed_password(self):
        status, result = self.client.register()
        self.assertEqual(status, 200)
        self.assertEqual(result['profile']['xp'], 0)
        self.assertEqual(result['profile']['display_name'], 'یادگیرنده')
        self.assertEqual(self.client.register()[0], 409)
        with server.database() as db:
            row = db.execute('SELECT * FROM users').fetchone()
            self.assertNotEqual(row['password'], 'test-password-123')
            self.assertEqual(len(row['password']), 64)
        old_cookie = self.client.cookie
        self.assertEqual(self.client.call('/api/logout', {})[0], 200)
        self.assertEqual(self.client.call('/api/profile', extra={'Cookie': old_cookie})[0], 401)
        self.assertEqual(self.client.call('/api/login', {'username': 'learner', 'password': 'wrong-password'})[0], 401)
        self.assertEqual(self.client.call('/api/login', {'username': 'LEARNER', 'password': 'test-password-123'})[0], 200)

    def test_free_cannot_read_answer_or_self_upgrade_pro(self):
        self.client.register()
        self.assertEqual(self.client.call('/api/lessons/pro-01')[0], 403)
        self.assertEqual(self.client.call('/api/answer', {'lesson_id': 'pro-01', 'answer': 'for'})[0], 403)
        self.client.call('/api/profile', {'display_name': 'New', 'plan': 'pro'})
        self.assertEqual(self.client.call('/api/profile')[1]['profile']['plan'], 'free')
        with server.database() as db:
            db.execute("UPDATE users SET plan='pro' WHERE username='learner'")
        self.assertEqual(self.client.call('/api/lessons/pro-01')[0], 200)
        self.assertTrue(self.client.call('/api/answer', {'lesson_id': 'pro-01', 'answer': 'for'})[1]['correct'])

    def test_wrong_answer_and_duplicate_completion(self):
        self.client.register()
        wrong = self.client.call('/api/answer', {'lesson_id': 'free-01', 'answer': 'echo("Hello")'})[1]
        self.assertFalse(wrong['correct'])
        self.assertEqual(wrong['profile']['xp'], 0)
        for expected in (50, 0, 0):
            result = self.client.call('/api/answer', {'lesson_id': 'free-01', 'answer': 'print("Hello")'})[1]
            self.assertEqual(result['earned'], expected)
            self.assertEqual(result['profile']['xp'], 50)
            self.assertEqual(result['profile']['current_lesson'], 'free-01')
            self.assertEqual(len(result['profile']['completed']), 1)

    def test_concurrent_submissions_award_once(self):
        self.client.register()
        def submit(_):
            client = Client(self.http.server_port)
            client.cookie, client.csrf = self.client.cookie, self.client.csrf
            return client.call('/api/answer', {'lesson_id': 'free-01', 'answer': 'print("Hello")'})
        with ThreadPoolExecutor(max_workers=5) as executor:
            results = list(executor.map(submit, range(5)))
        self.assertTrue(all(status == 200 for status, _ in results))
        self.assertEqual(sum(result['earned'] for _, result in results), 50)

    def test_account_isolation_and_second_device_progress(self):
        self.client.register()
        self.client.call('/api/answer', {'lesson_id': 'free-03', 'answer': '7'})
        other = Client(self.http.server_port)
        other.register('other')
        self.assertEqual(other.call('/api/profile')[1]['profile']['xp'], 0)
        second_device = Client(self.http.server_port)
        second_device.call('/api/login', {'username': 'learner', 'password': 'test-password-123'})
        self.assertEqual(second_device.call('/api/profile')[1]['profile']['xp'], 50)
        self.client.call('/api/lessons/free-20')
        self.assertEqual(second_device.call('/api/profile')[1]['profile']['current_lesson'], 'free-20')

    def test_origin_csrf_expired_and_malformed_requests(self):
        self.client.register()
        answer = {'lesson_id': 'free-01', 'answer': 'print("Hello")'}
        self.assertEqual(self.client.call('/api/answer', answer, {'Origin': 'https://evil.example'})[0], 403)
        self.assertEqual(self.client.call('/api/answer', answer, {'X-CSRF-Token': 'bad'})[0], 403)
        self.assertEqual(self.client.call('/api/answer', answer, {'Content-Type': 'text/plain'})[0], 415)
        self.assertEqual(self.client.call('/api/answer', {'lesson_id': [], 'answer': {}})[0], 404)
        with server.database() as db:
            db.execute('UPDATE sessions SET expires=0')
        self.assertEqual(self.client.call('/api/profile')[0], 401)

    def test_private_files_and_directory_listing_blocked(self):
        for path in ('/server.py', '/catalog.py', '/data/codeplay.sqlite3', '/.git/config', '/assets/', '/assets/../catalog.py', '/%63atalog.py', '/test_server.py'):
            self.assertEqual(self.client.call(path)[0], 404, path)
        self.assertEqual(self.client.call('/learning.js')[0], 200)

    def test_every_lesson_has_valid_bilingual_content_and_answers(self):
        self.client.register()
        with server.database() as db:
            db.execute("UPDATE users SET plan='pro'")
        for item in LESSONS:
            with self.subTest(lesson=item['id']):
                for key in ('title', 'prompt', 'hint', 'explanation'):
                    self.assertEqual(set(item[key]), {'en', 'fa'})
                    self.assertTrue(all(item[key].values()))
                detail = self.client.call('/api/lessons/' + item['id'])[1]['lesson']
                self.assertNotIn('answer', detail)
                solution = item['answer']
                if item['kind'] == 'project':
                    solution = [accepted[0] for accepted in solution]
                elif item['kind'] != 'order' and isinstance(solution, list):
                    solution = solution[0]
                if item['kind'] in ('quiz', 'debug'):
                    self.assertIn(solution, [x['value'] if isinstance(x, dict) else x for x in item['options']])
                if item['kind'] in ('blank', 'project'):
                    self.assertEqual(item['code'].count('___'), 1 if item['kind'] == 'blank' else len(solution))
                self.assertFalse(correct(item, None))
                self.assertFalse(correct(item, {}))
                status, result = self.client.call('/api/answer', {'lesson_id': item['id'], 'answer': solution})
                self.assertEqual(status, 200)
                self.assertTrue(result['correct'])
        self.assertEqual(self.client.call('/api/profile')[1]['profile']['xp'], 2200)
        self.assertIsNone(self.client.call('/api/profile')[1]['profile']['next_lesson'])

    def test_auth_rate_limit(self):
        for _ in range(20):
            self.assertEqual(self.client.call('/api/login', {'username': 'absent', 'password': 'bad-password'})[0], 401)
        self.assertEqual(self.client.call('/api/login', {'username': 'absent', 'password': 'bad-password'})[0], 429)


if __name__ == '__main__':
    (server.ROOT / 'tmp').mkdir(exist_ok=True)
    unittest.main(verbosity=2)
