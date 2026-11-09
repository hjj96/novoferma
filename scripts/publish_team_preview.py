#!/usr/bin/env python3
"""Prepare/push the checked team snapshot; Codex then calls the returned native tool.

No builder is run: the existing output/concept files are the source of truth.
Use --prepare-only to check without pushing. After native deployment reaches READY,
use --finalize ID --deployment-url URL to verify the permanent URL and record it.
"""
import argparse
from contextlib import contextmanager
from datetime import datetime
import fcntl
import hashlib
import json
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys
import tempfile
import time
from urllib.parse import urlsplit
from urllib.request import Request, urlopen
import zipfile
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / 'output/concept'
HOSTING = ROOT / 'output/hosting'
META = HOSTING / 'deployment.json'
PENDING = HOSTING / 'pending-publish.json'
REPORT = ROOT / 'output/research/site-package-validation.json'
TMP = ROOT / 'tmp/hosting'


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def atomic_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile('w', encoding='utf-8', dir=path.parent,
                                     prefix='.' + path.name, delete=False) as handle:
        temporary = Path(handle.name)
        json.dump(value, handle, ensure_ascii=False, indent=2)
        handle.write('\n')
        handle.flush()
        import os
        os.fsync(handle.fileno())
    temporary.replace(path)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def tree_hash(files):
    return sha(''.join(name + '\0' + sha(data) + '\n'
                       for name, data in sorted(files.items())).encode())


def run(args, cwd=ROOT, visible=False):
    result = subprocess.run([str(x) for x in args], cwd=cwd, text=True,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if visible or result.returncode:
        sys.stderr.write(result.stdout + result.stderr)
    if result.returncode:
        raise RuntimeError('Command failed: ' + str(args[0]))
    return result.stdout.strip()


def git(*args, cwd=ROOT):
    return run(['git', *args], cwd)


@contextmanager
def locked():
    TMP.mkdir(parents=True, exist_ok=True)
    with (TMP / 'publish.lock').open('a') as handle:
        try:
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise RuntimeError('Another team publication is running.')
        yield


def source_hashes():
    return {p.relative_to(SITE).as_posix(): sha(p.read_bytes())
            for p in SITE.rglob('*') if p.is_file()}


def check_consistency(report, before):
    for name, expected in report['sourceHashes'].items():
        file = SITE / name
        if (not file.is_file() or sha(file.read_bytes()) != expected
                or before.get(name) != expected):
            raise RuntimeError('Source changed during publication: ' + name)


def safe_member(name, prefix):
    if not name.startswith(prefix):
        raise RuntimeError('Unexpected package root: ' + name)
    relative = name[len(prefix):]
    if not relative or PurePosixPath(relative).is_absolute() or '..' in PurePosixPath(relative).parts:
        raise RuntimeError('Unsafe archive path: ' + name)
    return relative


def prepare(metadata, prepare_only):
    node = shutil.which('node') or str(Path.home() / '.local/node/bin/node')
    if not Path(node).is_file():
        raise RuntimeError('Node is required in PATH or ~/.local/node/bin/node.')
    before = source_hashes()
    run([sys.executable, 'scripts/check_site.py'], visible=True)
    run([node, 'scripts/check_interactions.cjs'], visible=True)
    run([sys.executable, 'scripts/package_site.py'], visible=True)
    report = read_json(REPORT)
    package = ROOT / report['archive']
    package_sha = sha(package.read_bytes())
    if package_sha != report['sha256']:
        raise RuntimeError('Package does not match its validation report.')
    check_consistency(report, before)
    files = {}
    with zipfile.ZipFile(package) as archive:
        if archive.testzip() is not None:
            raise RuntimeError('Package integrity check failed.')
        for member in archive.infolist():
            name = safe_member(member.filename, report['archiveRoot'])
            if name.endswith('.md'):
                continue
            files[name] = archive.read(member)
    files.pop('sitemap.xml', None)
    files['robots.txt'] = b'User-agent: *\nDisallow: /\n'
    configuration = {'$schema': 'https://openapi.vercel.sh/vercel.json',
                     'buildCommand': '', 'installCommand': '', 'framework': None,
                     'outputDirectory': '.', 'cleanUrls': False,
                     'headers': [{'source': '/(.*)', 'headers': [
                         {'key': 'X-Robots-Tag', 'value': 'noindex, nofollow, noarchive'}]}]}
    files['vercel.json'] = (json.dumps(configuration, indent=2) + '\n').encode()
    version = {'schemaVersion': 1, 'contentSha256': tree_hash(files)}
    root_commit = git('rev-parse', 'HEAD')
    files['preview-version.json'] = (json.dumps(version, indent=2) + '\n').encode()
    branch = metadata['sourceBranch']
    repository = metadata['sourceRepository']
    parsed = urlsplit(repository)
    parts = parsed.path.removesuffix('.git').strip('/').split('/')
    if parsed.scheme != 'https' or parsed.hostname != 'github.com' or len(parts) != 2:
        raise RuntimeError('Expected an HTTPS GitHub source repository.')
    with tempfile.TemporaryDirectory(prefix='publish-', dir=TMP) as directory:
        checkout = Path(directory)
        git('init', '--quiet', cwd=checkout)
        git('remote', 'add', 'origin', repository, cwd=checkout)
        git('fetch', '--quiet', '--depth=1', 'origin', 'refs/heads/' + branch, cwd=checkout)
        previous = git('rev-parse', 'FETCH_HEAD', cwd=checkout)
        git('checkout', '--quiet', '-b', 'snapshot', previous, cwd=checkout)
        for child in checkout.iterdir():
            if child.name != '.git':
                if child.is_dir() and not child.is_symlink():
                    shutil.rmtree(child)
                else:
                    child.unlink()
        for name, data in files.items():
            target = checkout / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        run([node, ROOT / 'scripts/check_interactions.cjs', checkout], visible=True)
        git('add', '--all', cwd=checkout)
        changed = bool(git('diff', '--cached', '--name-only', cwd=checkout))
        if changed:
            author = git('show', '-s', '--format=%an', 'HEAD')
            email = git('show', '-s', '--format=%ae', 'HEAD')
            git('-c', 'user.name=' + author, '-c', 'user.email=' + email,
                'commit', '--quiet', '-m', 'Update checked team preview', cwd=checkout)
        commit = git('rev-parse', 'HEAD', cwd=checkout)
        arguments = {'teamId': metadata['teamId'], 'requestBody': {
            'name': metadata['projectName'], 'project': metadata['projectId'],
            'target': 'production', 'gitSource': {
                'type': 'github', 'org': parts[0], 'repo': parts[1], 'ref': branch, 'sha': commit},
            'projectSettings': {'framework': None, 'buildCommand': '', 'installCommand': '',
                                'outputDirectory': '.', 'rootDirectory': None}}}
        check_consistency(report, before)
        if sha(package.read_bytes()) != package_sha:
            raise RuntimeError('Package changed during publication.')
        existing_pending = read_json(PENDING) if PENDING.exists() else {}
        if existing_pending and existing_pending.get('sourceCommit') != commit:
            raise RuntimeError('A different snapshot is pending; resume/finalize that publication first.')
        if changed and not prepare_only:
            git('push', '--quiet', 'origin', 'HEAD:refs/heads/' + branch, cwd=checkout)
        pending = {'sourceCommit': commit, 'previousCommit': previous, 'rootGitCommit': root_commit,
                   'contentSha256': version['contentSha256'], 'previewVersion': version,
                   'sourcePackageSha256': package_sha, 'sourcePackage': report['archive'],
                   'pageCount': report['pageCount'], 'localReferences': report['localReferencesChecked'],
                   'createDeploymentArgs': arguments}
        for key in ('deploymentId', 'deploymentUrl'):
            if key in existing_pending:
                pending[key] = existing_pending[key]
        deployment_required = (changed or metadata.get('sourceCommit') != commit
                               or metadata.get('contentSha256') != version['contentSha256'])
        if not prepare_only and deployment_required:
            atomic_json(PENDING, pending)
        result = {'preparedOnly': prepare_only, 'snapshotChanged': changed,
                'deploymentRequired': deployment_required,
                'sourceCommit': commit, 'contentSha256': version['contentSha256'],
                'nextStep': 'Run native create_deployment and wait for READY, then --finalize.'
                    if not prepare_only else 'Validation only; no push or pending publication saved.'}
        if deployment_required and not prepare_only:
            result.update({'tool': 'mcp__codex_apps__vercel_create_deployment', 'arguments': arguments})
        elif not deployment_required:
            result['nextStep'] = 'Already published; no deployment needed.'
        return result


def fetch(url):
    parsed = urlsplit(url)
    if parsed.scheme != 'https' or not parsed.hostname or parsed.username or parsed.password:
        raise RuntimeError('Expected an HTTPS URL without credentials.')
    request = Request(url, headers={'Cache-Control': 'no-cache', 'User-Agent': 'Novoferma-preview-check'})
    for attempt in range(3):
        try:
            with urlopen(request, timeout=12) as response:
                if urlsplit(response.url).netloc != parsed.netloc:
                    raise RuntimeError('Verification redirected away from the expected host.')
                body = response.read()
                indexing = response.headers.get('X-Robots-Tag', '').lower()
                if not all(token in indexing for token in ('noindex', 'nofollow', 'noarchive')):
                    raise RuntimeError('Missing preview indexing protection: ' + url)
                return body
        except OSError:
            if attempt == 2:
                raise
            time.sleep(attempt + 1)


def finalize(metadata, deployment_id, deployment_url):
    pending = read_json(PENDING)
    if pending.get('deploymentId', deployment_id) != deployment_id:
        raise RuntimeError('Deployment ID does not match the pending publication.')
    if pending.get('deploymentUrl', deployment_url) != deployment_url:
        raise RuntimeError('Deployment URL does not match the pending publication.')
    url = metadata['url'].rstrip('/')
    suffix = '?verification=' + pending['sourceCommit']
    version = json.loads(fetch(url + '/preview-version.json' + suffix))
    if version != pending['previewVersion']:
        raise RuntimeError('Permanent URL does not serve the pending snapshot yet.')
    parsed = urlsplit(deployment_url)
    if parsed.scheme != 'https' or not parsed.hostname or parsed.username or parsed.password:
        raise RuntimeError('Invalid deployment URL.')
    now = datetime.now(ZoneInfo('Europe/Moscow'))
    metadata.update({'publishedDate': now.date().isoformat(), 'updatedAt': now.isoformat(),
                     'deploymentId': deployment_id, 'deploymentUrl': deployment_url,
                     'state': 'READY', 'sourceCommit': pending['sourceCommit'],
                     'rootGitCommit': pending['rootGitCommit'],
                     'contentSha256': pending['contentSha256'],
                     'sourcePackage': pending['sourcePackage'],
                     'sourcePackageSha256': pending['sourcePackageSha256']})
    metadata.setdefault('checks', {})['latestPublish'] = {
        'staticSource': 'pass', 'interactionTests': 'pass', 'packagedInteractions': 'pass',
        'pages': pending['pageCount'], 'localReferences': pending['localReferences'],
        'permanentUrlVersion': 'pass', 'indexing': 'pass'}
    atomic_json(META, metadata)
    PENDING.unlink()
    return {'state': 'READY', 'url': url, 'sourceCommit': pending['sourceCommit'],
            'contentSha256': pending['contentSha256'], 'verification': 'pass'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--prepare-only', action='store_true', help='Validate without pushing or saving pending state.')
    mode.add_argument('--finalize', metavar='DEPLOYMENT_ID', help='Verify the pending snapshot after native READY.')
    parser.add_argument('--deployment-url', help='Native READY deployment URL, required with --finalize.')
    args = parser.parse_args()
    if bool(args.finalize) != bool(args.deployment_url):
        parser.error('--finalize and --deployment-url must be used together')
    with locked():
        metadata = read_json(META)
        result = finalize(metadata, args.finalize, args.deployment_url) if args.finalize else prepare(metadata, args.prepare_only)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, KeyError, RuntimeError, zipfile.BadZipFile) as error:
        print('Publication failed: ' + str(error), file=sys.stderr)
        sys.exit(1)
