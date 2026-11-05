"""Real HTTP + SQLite acceptance tests. No network mail or browser required.

Run: python3 -m unittest discover -s scripts -p 'test_serve_site.py' -v
"""
import contextlib
import http.client
import io
import json
import os
from pathlib import Path
import sqlite3
import tempfile
import threading
import unittest
from unittest.mock import patch
import uuid
from concurrent.futures import ThreadPoolExecutor

from serve_site import Store, SiteServer, RateLimiter, MAX_BODY, main


class IntakeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.site = self.root / 'site'
        self.site.mkdir()
        (self.site / 'site-manifest.json').write_text(json.dumps({'products': [{'id': 'chicken'}], 'novelties': [{'id': 'concept'}]}))
        (self.site / 'index.html').write_text('<h1>Public site</h1>')
        self.db = self.root / 'private' / 'requests.sqlite3'
        self.store = Store(self.db, self.site)
        self.start()

    def start(self, rate_limit=100, origins=()):
        self.server = SiteServer(('127.0.0.1', 0), self.site, self.store, origins=origins, rate_limit=rate_limit)
        self.port = self.server.server_port
        self.origin = f'http://127.0.0.1:{self.port}'
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def stop(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=3)

    def tearDown(self):
        self.stop()
        self.temp.cleanup()

    def payload(self, **changes):
        value = {'company': 'Test Company', 'city': 'Test City', 'contact': 'test@example.com',
                 'message': 'Please send a specification', 'format': 'retail', 'product': 'chicken',
                 'intent': 'specification', 'consent': True, 'idempotencyKey': str(uuid.uuid4())}
        value.update(changes)
        return value

    def request(self, payload=None, method='POST', path='/api/partner-requests', headers=None, raw=None):
        defaults = {'Origin': self.origin, 'Content-Type': 'application/json'}
        defaults.update(headers or {})
        defaults = {key: value for key, value in defaults.items() if value is not None}
        data = raw if raw is not None else json.dumps(payload).encode() if payload is not None else None
        connection = http.client.HTTPConnection('127.0.0.1', self.port, timeout=5)
        try:
            connection.request(method, path, body=data, headers=defaults)
            response = connection.getresponse()
            body = response.read()
            return response.status, dict(response.getheaders()), body
        finally:
            connection.close()

    def accept(self, payload=None):
        status, headers, body = self.request(payload or self.payload())
        self.assertEqual(status, 201, body)
        return json.loads(body)

    def count(self):
        with contextlib.closing(sqlite3.connect(self.db)) as connection:
            return connection.execute('SELECT count(*) FROM requests').fetchone()[0]

    def test_receipt_follows_commit_and_survives_restart(self):
        payload = self.payload()
        receipt = self.accept(payload)
        self.assertTrue(receipt['ok'] and receipt['committed'])
        uuid.UUID(receipt['requestId'])
        self.assertEqual(self.count(), 1)  # Different SQLite connection can see commit immediately.
        self.stop()
        self.store = Store(self.db, self.site, create=False)
        self.start()
        status, _, body = self.request(payload)
        replay = json.loads(body)
        self.assertEqual(status, 200)
        self.assertEqual(replay['requestId'], receipt['requestId'])
        self.assertTrue(replay['duplicate'])
        self.assertEqual(self.count(), 1)
        self.assertEqual(self.store.show(receipt['requestId'])['data']['contact'], 'test@example.com')

    def test_concurrent_duplicate_and_conflicting_payload(self):
        payload = self.payload()
        with ThreadPoolExecutor(max_workers=2) as executor:
            responses = list(executor.map(lambda _: self.request(payload), range(2)))
        self.assertEqual(sorted(response[0] for response in responses), [200, 201])
        ids = {json.loads(response[2])['requestId'] for response in responses}
        self.assertEqual(len(ids), 1)
        status, _, body = self.request(dict(payload, company='Changed Company'))
        self.assertEqual(status, 409)
        self.assertEqual(json.loads(body)['error']['code'], 'idempotency_conflict')
        self.assertNotIn(b'Test Company', body)
        self.assertEqual(self.count(), 1)

    def test_normalized_exact_retry_has_same_receipt(self):
        payload = self.payload(company=' Test Company ')
        first = self.accept(payload)
        status, _, body = self.request(dict(payload, company='Test Company', source='partners', website=''))
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(body)['requestId'], first['requestId'])

    def test_invalid_fields_never_commit(self):
        invalid = [dict(consent=False), dict(consent=1), dict(company='  '), dict(company='x' * 121),
                   dict(city='x' * 101), dict(message='x' * 1201), dict(contact='not-a-contact'),
                   dict(contact='x' * 161), dict(format='unknown'), dict(intent='unknown'),
                   dict(product='made-up-product'), dict(source='untrusted-campaign'),
                   dict(idempotencyKey='bad-key'), dict(website='spam'), dict(company='a\nInjected'),
                   dict(company=[]), dict(message='\ud800'), dict(unknown='extra')]
        for changes in invalid:
            with self.subTest(changes=changes):
                status, _, body = self.request(self.payload(**changes))
                self.assertEqual(status, 422, body)
                self.assertIn('fields', json.loads(body)['error'])
        self.assertEqual(self.count(), 0)

    def test_valid_contact_and_concept_empty_product(self):
        for contact, product in [('+7 (931) 213-55-50', ''), ('buyer+stm@example.com', 'concept')]:
            self.accept(self.payload(contact=contact, product=product, format='stm', intent='stm'))
        self.assertEqual(self.count(), 2)

    def test_origin_host_media_and_body_guards(self):
        cases = [({'Origin': None}, 403), ({'Origin': 'https://evil.example'}, 403),
                 ({'Host': 'evil.example'}, 403), ({'Content-Type': 'text/plain'}, 415),
                 ({'Content-Type': 'application/json;charset=latin1'}, 415),
                 ({'Transfer-Encoding': 'chunked'}, 400)]
        for headers, expected in cases:
            with self.subTest(headers=headers):
                status, returned, body = self.request(self.payload(), headers=headers)
                self.assertEqual(status, expected, body)
                self.assertNotIn('Access-Control-Allow-Origin', returned)
        self.assertEqual(self.request(raw=b'x' * (MAX_BODY + 1))[0], 413)
        self.assertEqual(self.request(method='OPTIONS')[0], 405)
        self.assertEqual(self.count(), 0)

    def test_malformed_json_duplicate_keys_and_utf8(self):
        for raw in [b'{', b'\xff', b'{"company":"a","company":"b"}', b'{"x":NaN}']:
            self.assertEqual(self.request(raw=raw)[0], 400)
        self.assertEqual(self.request(raw=b'[]')[0], 422)
        self.assertEqual(self.count(), 0)

    def test_configured_proxy_origin_and_host_must_both_match(self):
        self.stop()
        self.start(origins=['https://supply.example', 'https://second.example'])
        status, _, _ = self.request(self.payload(), headers={'Host': 'supply.example', 'Origin': 'https://supply.example'})
        self.assertEqual(status, 201)
        status, _, _ = self.request(self.payload(), headers={'Host': 'supply.example', 'Origin': 'https://second.example'})
        self.assertEqual(status, 403)
        self.assertEqual(self.request(self.payload())[0], 403)
        with self.assertRaises(ValueError):
            SiteServer(('0.0.0.0', 0), self.site, self.store)

    def test_database_failure_returns_no_receipt_and_retry_can_succeed(self):
        payload = self.payload()
        with patch.object(self.store, 'accept', side_effect=sqlite3.OperationalError('sensitive private path and test@example.com')):
            status, _, body = self.request(payload)
        self.assertEqual(status, 503)
        response = json.loads(body)
        self.assertNotIn('requestId', response)
        self.assertNotIn('committed', response)
        self.assertNotIn(b'test@example.com', body)
        self.assertEqual(self.count(), 0)
        self.accept(payload)

    def test_real_sqlite_write_failure_rolls_back(self):
        with contextlib.closing(sqlite3.connect(self.db)) as connection:
            connection.execute("CREATE TRIGGER reject_event BEFORE INSERT ON stage_events BEGIN SELECT RAISE(ABORT, 'failure'); END")
            connection.commit()
        status, _, body = self.request(self.payload())
        self.assertEqual(status, 503, body)
        self.assertEqual(self.count(), 0)  # Request INSERT must be rolled back with failed event write.

    def test_private_paths_symlinks_hardlinks_api_reads_and_logs(self):
        receipt = self.accept()
        (self.site / 'leak.json').symlink_to(self.db)
        os.link(self.db, self.site / 'hardlink.json')
        (self.site / '.env').write_text('secret')
        (self.site / 'dump.sqlite').write_text('secret')
        stdout, stderr = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            for path in ['/api/partner-requests', '/api/partner-requests/' + receipt['requestId'],
                         '/api/stats', '/leak.json', '/hardlink.json', '/.env', '/dump.sqlite',
                         '/../private/requests.sqlite3', '/%2e%2e/private/requests.sqlite3',
                         '/assets/', '/?contact=test@example.com']:
                status, _, body = self.request(method='GET', path=path)
                if path.startswith('/?'):
                    self.assertEqual(status, 200)
                else:
                    self.assertEqual(status, 404, path)
                self.assertNotIn(b'test@example.com', body)
                self.assertNotIn(b'Test Company', body)
        self.assertEqual(stdout.getvalue() + stderr.getvalue(), '')
        self.assertEqual(self.request(method='GET', path='/')[0], 200)
        self.assertEqual(self.request(method='HEAD', path='/')[2], b'')

    def test_configuration_rejects_public_db_or_directory(self):
        with self.assertRaises(ValueError):
            Store(self.site / 'requests.sqlite3', self.site)
        with self.assertRaises(ValueError):
            Store(Path('relative.sqlite3'), self.site)
        unsafe = self.root / 'unsafe'
        unsafe.mkdir(mode=0o755)
        unsafe.chmod(0o755)
        with self.assertRaises(ValueError):
            Store(unsafe / 'requests.sqlite3', self.site)
        self.assertEqual(self.db.stat().st_mode & 0o777, 0o600)

    def test_rate_limit_is_bounded_and_http_retry_after(self):
        self.server.rate = RateLimiter(limit=2)
        self.accept()
        self.accept()
        status, headers, _ = self.request(self.payload())
        self.assertEqual(status, 429)
        self.assertGreater(int(headers['Retry-After']), 0)
        self.assertEqual(self.count(), 2)
        limiter = RateLimiter(limit=1, capacity=2)
        self.assertEqual(limiter.take('one'), 0)
        self.assertEqual(limiter.take('two'), 0)
        self.assertGreater(limiter.take('three'), 0)
        self.assertEqual(len(limiter.buckets), 2)

    def test_operator_list_show_update_and_segment_funnel(self):
        first = self.accept(self.payload(format='stm', intent='stm', product='concept'))['requestId']
        self.accept()
        self.store.update(first, 'qualified')
        self.store.update(first, 'quote')
        self.store.update(first, 'order')
        self.store.update(first, 'order')
        self.assertEqual(len(self.store.show(first)['events']), 4)
        listing = json.dumps(self.store.listing())
        self.assertNotIn('test@example.com', listing)
        self.assertNotIn('Test Company', listing)
        result = self.store.funnel()
        self.assertEqual(result['everRecordedAtStage']['received'], 2)
        self.assertEqual(result['bySegment']['format']['stm']['committed'], 1)
        self.assertEqual(result['bySegment']['product']['concept']['order'], 1)
        self.assertEqual(result['bySegment']['intent']['stm']['quote'], 1)
        with contextlib.redirect_stdout(io.StringIO()) as output:
            code = main(['--db', str(self.db), '--site', str(self.site), 'stats'])
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(output.getvalue())['currentStatus']['order'], 1)

    def test_online_backup_private_no_overwrite_and_restore(self):
        payload = self.payload()
        receipt = self.accept(payload)
        destination = self.root / 'backup-private' / 'snapshot.sqlite3'
        result = self.store.backup(destination)
        self.assertTrue(result['backupCreated'])
        self.assertEqual(destination.stat().st_mode & 0o777, 0o600)
        restored = Store(destination, self.site, create=False)
        self.assertEqual(restored.show(receipt['requestId'])['data']['contact'], 'test@example.com')
        from serve_site import validate
        key, data = validate(payload, {'chicken'})
        self.assertEqual(restored.accept(key, data), (receipt['requestId'], True))
        original_bytes = destination.read_bytes()
        with self.assertRaises(FileExistsError):
            self.store.backup(destination)
        self.assertEqual(destination.read_bytes(), original_bytes)
        with self.assertRaises(ValueError):
            self.store.backup(self.site / 'public-backup.sqlite3')
        symlink = destination.parent / 'link.sqlite3'
        symlink.symlink_to(destination)
        with self.assertRaises(ValueError):
            self.store.backup(symlink)


if __name__ == '__main__':
    unittest.main()
