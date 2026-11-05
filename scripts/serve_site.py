#!/usr/bin/env python3
"""Local single-host site + durable partner intake. Python 3.9+, stdlib only.

No public request reads, email delivery or CRM integration. Operator access uses
the private SQLite file and OS permissions, never an unauthenticated HTTP route.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import hmac
import ipaddress
import json
import math
import mimetypes
import os
from pathlib import Path
import re
import secrets
import shutil
import sqlite3
import stat
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import unquote, urlsplit
import uuid
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SITE = ROOT / 'output/concept'
ENDPOINT = '/api/partner-requests'
MAX_BODY = 16 * 1024
CONSENT_VERSION = 'partner-intake-2026-11-05-v1'
STAGES = ('received', 'qualified', 'quote', 'order', 'closed')
FORMATS = {'retail', 'horeca', 'stm'}
INTENTS = {'quote', 'specification', 'samples', 'stm'}
SOURCES = {'partners', 'catalogue', 'product', 'home', 'direct'}
PUBLIC_SUFFIXES = {'.html', '.css', '.js', '.json', '.svg', '.webp', '.png', '.jpg',
                   '.jpeg', '.gif', '.ico', '.woff', '.woff2', '.txt', '.xml', '.webmanifest', '.pdf'}


def utcnow():
    return datetime.now(timezone.utc).isoformat(timespec='milliseconds')


class ValidationError(Exception):
    def __init__(self, fields):
        self.fields = fields


class Conflict(Exception):
    pass


class ClosingConnection(sqlite3.Connection):
    def __exit__(self, *args):
        try:
            return super().__exit__(*args)
        finally:
            self.close()


def validate(data, products):
    required = {'company', 'city', 'contact', 'message', 'format', 'product',
                'intent', 'consent', 'idempotencyKey'}
    if not isinstance(data, dict):
        raise ValidationError({'_schema': 'Ожидается JSON-объект.'})
    fields = {}
    if set(data) - required - {'source', 'website'}:
        fields['_schema'] = 'Запрос содержит неизвестные поля.'
    for name in required - set(data):
        fields[name] = 'Поле отсутствует.'
    result = {}
    for name, minimum, maximum in [('company', 1, 120), ('city', 0, 100),
                                    ('contact', 1, 160), ('message', 0, 1200)]:
        value = data.get(name)
        if not isinstance(value, str):
            fields[name] = 'Ожидается текст.'
            continue
        value = value.strip()
        controls = r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]' if name == 'message' else r'[\x00-\x1f\x7f]'
        if not minimum <= len(value) <= maximum or re.search(controls, value) or re.search(r'[\ud800-\udfff]', value):
            fields[name] = f'Допустимая длина: {minimum}–{maximum} символов.'
        result[name] = value
    contact = result.get('contact', '')
    email = re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+', contact)
    phone = re.fullmatch(r'\+?[0-9 ()\-.]+', contact) and 7 <= len(re.sub(r'\D', '', contact)) <= 15
    if contact and not (email or phone):
        fields['contact'] = 'Укажите электронную почту или телефон с кодом города/страны.'
    for name, allowed in [('format', FORMATS), ('intent', INTENTS), ('source', SOURCES)]:
        value = data.get(name, 'partners' if name == 'source' else None)
        if not isinstance(value, str) or value not in allowed:
            fields[name] = 'Выберите допустимое значение.'
        else:
            result[name] = value
    product = data.get('product')
    if not isinstance(product, str) or product not in products | {''}:
        fields['product'] = 'Выберите продукт из каталога.'
    else:
        result['product'] = product
    if data.get('consent') is not True:
        fields['consent'] = 'Подтвердите согласие на обработку запроса.'
    if data.get('website', '') != '':
        fields['_schema'] = 'Запрос не принят.'
    key = data.get('idempotencyKey', '')
    try:
        if not isinstance(key, str) or not re.fullmatch(r'[0-9a-fA-F-]{36}', key):
            raise ValueError()
        key = str(uuid.UUID(key))
    except (ValueError, AttributeError):
        fields['idempotencyKey'] = 'Неверный ключ повторной отправки.'
    if fields:
        raise ValidationError(fields)
    result['consent'] = True
    return key, result


def load_products(site):
    manifest = json.loads((site / 'site-manifest.json').read_text(encoding='utf-8'))
    products = {p.get('id') or p.get('slug') for p in manifest['products'] + manifest.get('novelties', [])}
    if not products or None in products:
        raise ValueError('Invalid product manifest')
    return products


def inside(path, root):
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


class Store:
    def __init__(self, db, site=DEFAULT_SITE, create=True):
        self.site = Path(site).resolve()
        original = Path(db).expanduser()
        if not original.is_absolute() or original.is_symlink():
            raise ValueError('Database must be an absolute, non-symlink private file path')
        self.path = original.resolve()
        if inside(self.path, self.site):
            raise ValueError('Database must be outside the static webroot')
        if not create and not self.path.is_file():
            raise ValueError('Existing private database required')
        self.path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        parent_stat = self.path.parent.stat()
        if stat.S_IMODE(parent_stat.st_mode) & 0o077:
            raise ValueError('Use a dedicated private database directory with mode 0700')
        if hasattr(os, 'getuid') and parent_stat.st_uid != os.getuid():
            raise ValueError('Private database directory must belong to the operator')
        if not self.path.exists():
            fd = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
            os.close(fd)
        if not self.path.is_file() or self.path.stat().st_nlink != 1:
            raise ValueError('Database must be a regular file without hard links')
        self.path.chmod(0o600)
        with self.connect() as connection:
            version = connection.execute('PRAGMA user_version').fetchone()[0]
            if version not in (0, 1):
                raise ValueError('Unsupported database schema')
            connection.execute('PRAGMA journal_mode=WAL')
            connection.executescript('''
                CREATE TABLE IF NOT EXISTS requests (
                    request_id TEXT PRIMARY KEY, idempotency_key TEXT NOT NULL UNIQUE,
                    payload_hash TEXT NOT NULL, payload TEXT NOT NULL,
                    created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
                    status TEXT NOT NULL, consent_version TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS stage_events (
                    id INTEGER PRIMARY KEY, request_id TEXT NOT NULL REFERENCES requests(request_id),
                    occurred_at TEXT NOT NULL, stage TEXT NOT NULL);
                CREATE INDEX IF NOT EXISTS events_request ON stage_events(request_id);
                PRAGMA user_version=1;
            ''')

    def connect(self):
        connection = sqlite3.connect(str(self.path), timeout=3, factory=ClosingConnection)
        connection.row_factory = sqlite3.Row
        connection.execute('PRAGMA foreign_keys=ON')
        connection.execute('PRAGMA synchronous=FULL')
        return connection

    def accept(self, key, payload):
        encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(',', ':'))
        digest = hashlib.sha256(encoded.encode('utf-8')).hexdigest()
        connection = self.connect()
        try:
            connection.execute('BEGIN IMMEDIATE')
            previous = connection.execute('SELECT request_id,payload_hash FROM requests WHERE idempotency_key=?', (key,)).fetchone()
            if previous:
                if not hmac.compare_digest(previous['payload_hash'], digest):
                    raise Conflict()
                connection.commit()
                return previous['request_id'], True
            request_id = str(uuid.uuid4())
            created = utcnow()
            connection.execute('INSERT INTO requests VALUES (?,?,?,?,?,?,?,?)',
                               (request_id, key, digest, encoded, created, created, 'received', CONSENT_VERSION))
            connection.execute('INSERT INTO stage_events(request_id,occurred_at,stage) VALUES (?,?,?)',
                               (request_id, created, 'received'))
            connection.commit()  # A receipt is returned only after this durable commit succeeds.
            return request_id, False
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def listing(self, limit=50):
        with self.connect() as connection:
            rows = connection.execute('SELECT * FROM requests ORDER BY created_at DESC LIMIT ?', (limit,)).fetchall()
        result = []
        for row in rows:
            payload = json.loads(row['payload'])
            result.append({key: row[key] for key in ('request_id', 'created_at', 'updated_at', 'status')} |
                          {key: payload[key] for key in ('format', 'intent', 'product', 'source')})
        return result

    def show(self, request_id):
        with self.connect() as connection:
            row = connection.execute('SELECT * FROM requests WHERE request_id=?', (request_id,)).fetchone()
            events = connection.execute('SELECT occurred_at,stage FROM stage_events WHERE request_id=? ORDER BY id', (request_id,)).fetchall()
        if not row:
            raise ValueError('Unknown request ID')
        return {'requestId': row['request_id'], 'createdAt': row['created_at'], 'status': row['status'],
                'consentVersion': row['consent_version'], 'data': json.loads(row['payload']),
                'events': [dict(event) for event in events]}

    def update(self, request_id, stage):
        if stage not in STAGES:
            raise ValueError('Invalid stage')
        with self.connect() as connection:
            connection.execute('BEGIN IMMEDIATE')
            row = connection.execute('SELECT status FROM requests WHERE request_id=?', (request_id,)).fetchone()
            if not row:
                raise ValueError('Unknown request ID')
            if row['status'] != stage:
                now = utcnow()
                connection.execute('UPDATE requests SET status=?,updated_at=? WHERE request_id=?', (stage, now, request_id))
                connection.execute('INSERT INTO stage_events(request_id,occurred_at,stage) VALUES (?,?,?)', (request_id, now, stage))
        return {'requestId': request_id, 'status': stage}

    def funnel(self):
        with self.connect() as connection:
            current = dict(connection.execute('SELECT status,count(*) FROM requests GROUP BY status').fetchall())
            reached = dict(connection.execute('SELECT stage,count(DISTINCT request_id) FROM stage_events GROUP BY stage').fetchall())
            segments = {name: {} for name in ('format', 'product', 'intent')}
            rows = connection.execute('''SELECT DISTINCT r.request_id,r.payload,e.stage
                FROM requests r JOIN stage_events e ON r.request_id=e.request_id''')
            for row in rows:
                payload = json.loads(row['payload'])
                stage = 'committed' if row['stage'] == 'received' else row['stage']
                for dimension in segments:
                    bucket = segments[dimension].setdefault(payload[dimension] or '(unspecified)',
                        {key: 0 for key in ('committed', 'qualified', 'quote', 'order', 'closed')})
                    bucket[stage] += 1
        return {'currentStatus': {stage: current.get(stage, 0) for stage in STAGES},
                'everRecordedAtStage': {stage: reached.get(stage, 0) for stage in STAGES},
                'bySegment': segments,
                'scope': 'Operator-recorded stages, not website visitors, delivered emails or verified revenue.'}

    def backup(self, destination):
        original = Path(destination).expanduser()
        if not original.is_absolute() or original.is_symlink():
            raise ValueError('Backup must be an absolute private non-symlink file path')
        target = original.resolve()
        if inside(target, self.site):
            raise ValueError('Backup must be outside the webroot')
        target.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        parent_stat = target.parent.stat()
        if stat.S_IMODE(parent_stat.st_mode) & 0o077 or (hasattr(os, 'getuid') and parent_stat.st_uid != os.getuid()):
            raise ValueError('Backup directory must be private and owned by the operator')
        # O_EXCL refuses overwrites and symlinks, including a concurrent creation.
        fd = os.open(target, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        os.close(fd)
        try:
            with self.connect() as source:
                with sqlite3.connect(str(target), factory=ClosingConnection) as copy:
                    source.backup(copy)
                    if copy.execute('PRAGMA integrity_check').fetchone()[0] != 'ok':
                        raise sqlite3.DatabaseError('Backup integrity check failed')
            return {'backupCreated': True, 'bytes': target.stat().st_size}
        except Exception:
            target.unlink(missing_ok=True)
            for suffix in ('-wal', '-shm', '-journal'):
                Path(str(target) + suffix).unlink(missing_ok=True)
            raise


class RateLimiter:
    """Bounded, process-local guard; use an edge limit for public exposure."""
    def __init__(self, limit=12, window=60, capacity=2048, global_limit=240):
        self.limit, self.window, self.capacity, self.global_limit = limit, window, capacity, global_limit
        self.buckets = {}
        self.global_requests = collections.deque()
        self.secret = secrets.token_bytes(32)
        self.lock = threading.Lock()

    def take(self, address):
        key = hmac.new(self.secret, address.encode(), hashlib.sha256).digest()
        now = time.monotonic()
        with self.lock:
            for candidate, times in list(self.buckets.items()):
                while times and times[0] <= now - self.window:
                    times.popleft()
                if not times:
                    del self.buckets[candidate]
            while self.global_requests and self.global_requests[0] <= now - self.window:
                self.global_requests.popleft()
            if len(self.global_requests) >= self.global_limit:
                return max(1, math.ceil(self.global_requests[0] + self.window - now))
            times = self.buckets.get(key)
            if times is None:
                if len(self.buckets) >= self.capacity:
                    return self.window
                times = self.buckets[key] = collections.deque()
            if len(times) >= self.limit:
                return max(1, math.ceil(times[0] + self.window - now))
            times.append(now)
            self.global_requests.append(now)
        return 0


def canonical_origin(origin):
    parsed = urlsplit(origin)
    if parsed.scheme not in ('http', 'https') or not parsed.hostname or parsed.username or parsed.password or parsed.path or parsed.query or parsed.fragment:
        raise ValueError('Origin must be scheme://host[:port], without a trailing slash')
    port = parsed.port
    host = parsed.hostname.lower()
    if ':' in host:
        host = '[' + host + ']'
    if port and port != (443 if parsed.scheme == 'https' else 80):
        host += ':' + str(port)
    return parsed.scheme + '://' + host


class SiteServer(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True

    def __init__(self, address, site, store, origins=(), rate_limit=12):
        self.site = Path(site).resolve()
        self.store = store
        self.products = load_products(self.site)
        self.rate = RateLimiter(limit=rate_limit)
        self.slots = threading.BoundedSemaphore(32)
        self.origins = {canonical_origin(origin) for origin in origins}
        super().__init__(address, Handler)
        port = self.server_address[1]
        if not self.origins:
            host = address[0]
            if host != 'localhost' and not ipaddress.ip_address(host).is_loopback:
                self.server_close()
                raise ValueError('Non-loopback binding requires explicit allowed origins')
            self.origins = {canonical_origin(f'http://127.0.0.1:{port}'), canonical_origin(f'http://localhost:{port}')}
        self.hosts = {urlsplit(origin).netloc for origin in self.origins}

    def process_request(self, request, client_address):
        if not self.slots.acquire(blocking=False):
            try:
                request.sendall(b'HTTP/1.0 503 Service Unavailable\r\nContent-Length: 0\r\nConnection: close\r\n\r\n')
            except OSError:
                pass
            self.shutdown_request(request)
            return
        try:
            super().process_request(request, client_address)
        except Exception:
            self.slots.release()
            raise

    def process_request_thread(self, request, client_address):
        try:
            super().process_request_thread(request, client_address)
        finally:
            self.slots.release()

    def handle_error(self, request, client_address):
        # Do not dump request bodies, URLs, IPs or stack traces into access logs.
        pass


class Handler(BaseHTTPRequestHandler):
    server_version = 'NovofermaIntake/1'
    sys_version = ''

    def setup(self):
        super().setup()
        self.connection.settimeout(10)

    def log_message(self, format, *args):
        pass

    def reply(self, status, data, headers=None):
        encoded = json.dumps(data, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(encoded)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Referrer-Policy', 'same-origin')
        for key, value in (headers or {}).items():
            self.send_header(key, str(value))
        self.end_headers()
        if getattr(self, 'command', '') != 'HEAD':
            self.wfile.write(encoded)

    def error(self, status, code, message, fields=None, headers=None):
        error = {'code': code, 'message': message}
        if fields:
            error['fields'] = fields
        self.reply(status, {'ok': False, 'error': error}, headers)

    def send_error(self, code, message=None, explain=None):
        self.error(code, 'request_rejected', 'Запрос не поддерживается.')

    def host_ok(self):
        hosts = self.headers.get_all('Host', [])
        return len(hosts) == 1 and hosts[0].lower() in self.server.hosts

    def do_GET(self):
        self.static()

    def do_HEAD(self):
        self.static()

    def static(self):
        if not self.host_ok():
            return self.error(400, 'invalid_host', 'Неверный адрес сайта.')
        path = unquote(urlsplit(self.path).path)
        parts = Path(path.lstrip('/')).parts
        if path.startswith('/api/') or '\x00' in path or '\\' in path or any(part.startswith('.') for part in parts):
            return self.error(404, 'not_found', 'Страница не найдена.')
        candidate = self.server.site.joinpath(*parts)
        if candidate.is_dir():
            candidate /= 'index.html'
        resolved = candidate.resolve()
        if not inside(resolved, self.server.site) or resolved.suffix.lower() not in PUBLIC_SUFFIXES or not resolved.is_file():
            return self.error(404, 'not_found', 'Страница не найдена.')
        # Reject symlink components and database hard links even under harmless suffixes.
        cursor = candidate
        while cursor != self.server.site:
            if cursor.is_symlink():
                return self.error(404, 'not_found', 'Страница не найдена.')
            cursor = cursor.parent
        for private in (self.server.store.path, Path(str(self.server.store.path) + '-wal'), Path(str(self.server.store.path) + '-shm')):
            if private.exists() and resolved.samefile(private):
                return self.error(404, 'not_found', 'Страница не найдена.')
        try:
            with resolved.open('rb') as stream:
                self.send_response(200)
                self.send_header('Content-Type', mimetypes.guess_type(resolved.name)[0] or 'application/octet-stream')
                self.send_header('Content-Length', str(os.fstat(stream.fileno()).st_size))
                self.send_header('X-Content-Type-Options', 'nosniff')
                self.send_header('Cache-Control', 'no-cache')
                self.send_header('Referrer-Policy', 'same-origin')
                self.end_headers()
                if self.command != 'HEAD':
                    shutil.copyfileobj(stream, self.wfile)
        except (BrokenPipeError, ConnectionResetError):
            pass
        except OSError:
            self.error(404, 'not_found', 'Страница не найдена.')

    def do_OPTIONS(self):
        self.error(405, 'method_not_allowed', 'Метод не поддерживается.', headers={'Allow': 'POST'})

    def do_POST(self):
        if self.path != ENDPOINT:
            return self.error(404, 'not_found', 'Адрес не найден.')
        origins = self.headers.get_all('Origin', [])
        if not self.host_ok() or len(origins) != 1 or origins[0] not in self.server.origins or urlsplit(origins[0]).netloc != self.headers.get('Host', '').lower():
            return self.error(403, 'origin_denied', 'Отправьте запрос со страницы сайта.')
        if self.headers.get('Transfer-Encoding') is not None or len(self.headers.get_all('Content-Length', [])) != 1:
            return self.error(400, 'invalid_framing', 'Неверный формат запроса.')
        content_type = self.headers.get('Content-Type', '').lower().replace(' ', '')
        if len(self.headers.get_all('Content-Type', [])) != 1 or content_type not in ('application/json', 'application/json;charset=utf-8', 'application/json;charset="utf-8"'):
            return self.error(415, 'unsupported_media_type', 'Используйте JSON UTF-8.')
        try:
            if not re.fullmatch(r'[0-9]+', self.headers['Content-Length']):
                raise ValueError()
            length = int(self.headers['Content-Length'])
        except (ValueError, TypeError):
            return self.error(400, 'invalid_length', 'Неверный размер запроса.')
        if length < 1 or length > MAX_BODY:
            return self.error(413, 'body_too_large', 'Допустимый размер запроса — до 16 КиБ.')
        retry = self.server.rate.take(self.client_address[0])
        if retry:
            return self.error(429, 'rate_limited', 'Слишком много запросов. Попробуйте позже.', headers={'Retry-After': retry})
        try:
            raw = self.rfile.read(length)
            if len(raw) != length:
                raise ValueError()
            def unique_pairs(pairs):
                result = {}
                for key, value in pairs:
                    if key in result:
                        raise ValueError()
                    result[key] = value
                return result
            def invalid_constant(value):
                raise ValueError()
            data = json.loads(raw.decode('utf-8'), object_pairs_hook=unique_pairs, parse_constant=invalid_constant)
        except (ValueError, UnicodeError, TimeoutError, RecursionError):
            return self.error(400, 'invalid_json', 'Не удалось прочитать запрос.')
        try:
            key, payload = validate(data, self.server.products)
        except ValidationError as error:
            return self.error(422, 'validation_failed', 'Проверьте поля запроса.', error.fields)
        try:
            request_id, duplicate = self.server.store.accept(key, payload)
        except Conflict:
            return self.error(409, 'idempotency_conflict', 'Данные изменились. Создайте новый запрос.')
        except (sqlite3.Error, OSError):
            return self.error(503, 'storage_unavailable', 'Не удалось сохранить запрос. Попробуйте ещё раз или свяжитесь напрямую.')
        self.reply(200 if duplicate else 201, {'ok': True, 'committed': True, 'requestId': request_id, 'duplicate': duplicate})


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--db', default=os.environ.get('NOVOFERMA_DB'), help='Absolute private SQLite path outside webroot (or NOVOFERMA_DB).')
    parser.add_argument('--site', type=Path, default=DEFAULT_SITE)
    sub = parser.add_subparsers(dest='command', required=True)
    serving = sub.add_parser('serve')
    serving.add_argument('--host', default='127.0.0.1')
    serving.add_argument('--port', type=int, default=8765)
    serving.add_argument('--origin', '--allowed-origin', action='append',
                         default=[value.strip() for value in os.environ.get('NOVOFERMA_ORIGINS', '').split(',') if value.strip()],
                         help='Allowed scheme://host[:port]; repeat or use comma-separated NOVOFERMA_ORIGINS.')
    serving.add_argument('--rate-limit', type=int, default=12, help='Per peer per 60 seconds; global cap 240/60s.')
    listing = sub.add_parser('list')
    listing.add_argument('--limit', type=int, default=50)
    showing = sub.add_parser('show')
    showing.add_argument('request_id')
    updating = sub.add_parser('update')
    updating.add_argument('request_id')
    updating.add_argument('--status', required=True, choices=STAGES)
    sub.add_parser('funnel')
    sub.add_parser('stats', help='Alias of funnel: aggregate committed/stages by format, product and intent.')
    backup = sub.add_parser('backup', help='SQLite online backup to a new private file; never overwrite.')
    backup.add_argument('--to', required=True, type=Path)
    args = parser.parse_args(argv)
    if not args.db:
        parser.error('Specify --db or NOVOFERMA_DB; no database path is guessed.')
    os.umask(0o077)
    try:
        store = Store(args.db, args.site, create=args.command == 'serve')
        if args.command == 'serve':
            if not 1 <= args.rate_limit <= 240:
                parser.error('--rate-limit must be 1..240')
            server = SiteServer((args.host, args.port), args.site, store, args.origin, args.rate_limit)
            print(f'Listening on {args.host}:{server.server_port}. Intake saves to the private operator registry; no email is sent.', flush=True)
            try:
                server.serve_forever()
            except KeyboardInterrupt:
                pass
            finally:
                server.server_close()
            return 0
        if args.command == 'list':
            if not 1 <= args.limit <= 500:
                parser.error('--limit must be 1..500')
            result = store.listing(args.limit)
        elif args.command == 'show':
            result = store.show(args.request_id)
        elif args.command == 'update':
            result = store.update(args.request_id, args.status)
        elif args.command == 'backup':
            result = store.backup(args.to)
        else:
            result = store.funnel()
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (ValueError, OSError, sqlite3.Error, KeyError):
        print('Configuration or private storage unavailable. Check the documented path, permissions, manifest and request ID.', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
