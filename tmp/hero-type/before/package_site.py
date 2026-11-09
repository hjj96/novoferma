"""Package only the reviewed static site, its linked assets, and font licenses.

Re-run after site edits: python3 scripts/package_site.py
This script reads output/concept without changing it.
"""
from pathlib import Path, PurePosixPath
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
from collections import Counter
import hashlib
import json
import re
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / 'output/concept'
TARGET = ROOT / 'output/novoferma-site.zip'
REPORT = ROOT / 'output/research/site-package-validation.json'
PREFIX = 'novoferma-site/'
manifest = json.loads((SITE / 'site-manifest.json').read_text())
assert len(manifest['pages']) == 20 and len(set(manifest['pages'])) == 20

class HTMLRefs(HTMLParser):
    def __init__(self):
        super().__init__(); self.refs = []; self.ids = set()
    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if d.get('id'): self.ids.add(d['id'])
        for key in ('href', 'src', 'poster', 'action', 'data-src'):
            if d.get(key): self.refs.append(d[key])
        if d.get('srcset'):
            self.refs.extend(x.strip().split()[0] for x in d['srcset'].split(',') if x.strip())
        if d.get('style'):
            self.refs.extend(css_refs(d['style']))

CSS_URL = re.compile(r'url\(\s*[\"\']?([^\"\')]+)[\"\']?\s*\)', re.I)
CSS_IMPORT = re.compile(r'@import\s+[\"\']([^\"\']+)[\"\']', re.I)
JS_LOCAL = re.compile(r'[\"\']((?:assets/|\.\.?/)[^\"\'\s]+\.(?:webp|png|jpg|jpeg|svg|gif|woff2?|css|js|json|html)(?:[?#][^\"\']*)?)[\"\']')
JS_HTML = re.compile(r'[\"\']([a-zA-Z0-9_.-]+\.html(?:[?#][^\"\']*)?)[\"\']')

def css_refs(text):
    return CSS_URL.findall(text) + CSS_IMPORT.findall(text)

def json_refs(value):
    refs = []
    if isinstance(value, dict):
        for k, v in value.items():
            if k == 'sourceSnapshot': continue  # Research provenance, never a runtime asset.
            refs.extend(json_refs(v))
    elif isinstance(value, list):
        for v in value: refs.extend(json_refs(v))
    elif isinstance(value, str) and (value.startswith('assets/') or re.fullmatch(r'[a-zA-Z0-9_.-]+\.html', value)):
        refs.append(value)
    return refs

def refs_for(name, data):
    suffix = PurePosixPath(name).suffix
    if suffix not in ('.html', '.css', '.js', '.json'): return []
    text = data.decode('utf-8')
    if suffix == '.html':
        parser = HTMLRefs(); parser.feed(text); return parser.refs
    if suffix == '.css': return css_refs(text)
    if suffix == '.js': return JS_LOCAL.findall(text) + JS_HTML.findall(text)
    return json_refs(json.loads(text))

def resolve(name, ref):
    parts = urlsplit(ref)
    if parts.scheme or parts.netloc or ref.startswith('//'): return None
    if not parts.path: return name, unquote(parts.fragment)
    path = PurePosixPath(name).parent / unquote(parts.path)
    # POSIX normalization without allowing an archive member to escape its root.
    normalized = []
    for part in path.parts:
        if part in ('', '.'): continue
        if part == '..':
            if not normalized: raise RuntimeError(f'Unsafe path from {name}')
            normalized.pop()
        else: normalized.append(part)
    result = '/'.join(normalized)
    if result.startswith('/'): raise RuntimeError('Absolute local asset in package')
    return result, unquote(parts.fragment)

seeds = [*manifest['pages'], 'style.css', 'script.js', 'products.json', 'site-manifest.json',
         'README.md', 'assets/fonts/OFL-Onest.txt', 'assets/fonts/OFL-Caveat.txt']
files = {}; pending = list(seeds); links = []
while pending:
    name = pending.pop()
    if name in files: continue
    file = SITE / name
    if not file.is_file(): raise RuntimeError(f'Missing local dependency: {name}')
    files[name] = file.read_bytes()
    for ref in refs_for(name, files[name]):
        resolved = resolve(name, ref)
        if resolved is None: continue
        target, fragment = resolved
        links.append((name, ref, target, fragment))
        if target not in files: pending.append(target)

zip_readme = '''# Новоферма — архив сайта

Распакуйте архив и откройте `novoferma-site/index.html` в современном браузере.
Сайт работает локально без установки библиотек, сборки и внешних шрифтов.

Для просмотра через HTTP откройте терминал в распакованной папке `novoferma-site`:

```sh
python3 -m http.server 8765 --bind 127.0.0.1
```

Затем откройте http://127.0.0.1:8765/.

В архиве 20 страниц: главная, каталог, о компании, где купить, партнёрам,
контакты и 14 страниц продуктов. На главной также есть анонс «Белок к столу!»
со статусом «Готовим новинку»; его графика взята из PDF. Общие стили и поведение находятся в
`style.css` и `script.js`, данные — в `products.json` и `site-manifest.json`.
Поиск, фильтры, меню, раскрывающиеся сведения, вкладки подачи и анимации
работают без сервера. Форма поиска магазинов открывает подготовленное
письмо в почтовом приложении; отправку выполняет пользователь.

Название, масса, фасовка, контакты и упаковки перенесены из официального
каталога novoferma.ru. Состав, аллергены, пищевая ценность, хранение,
приготовление и текущие точки продаж требуют актуальных данных компании;
на страницах вместо неподтверждённых сведений указаны этикетка и контакты.
Архив содержит локальный сайт, а не публикацию на домене или интеграцию с учётом.

Первый экран, персонаж и логотип подготовлены по предоставленному PDF и
графике компании. `assets/catalogue-cutout/` — 14 обработанных упаковок.
`assets/catalogue/` содержит фотографии, на которые ссылаются JSON-данные.
Три `assets/serving-*-crop.webp` — иллюстративные идеи подачи, сгенерированные
через OpenAI API; они не являются документальными фотографиями производства.
Все изображения сайта приложены; полные исходные PNG и промежуточные
материалы не включены. Шрифты Onest и Caveat загружаются локально;
их лицензии SIL OFL находятся в `assets/fonts/`.

`README.md` сохранён из рабочего проекта. Указанные в нём относительные
пути к исследованиям, PDF-аудиту, промптам и скрипту сборки относятся к
полному рабочему проекту, не к этому архиву. Поле `sourceSnapshot` в JSON
также является записью о происхождении данных, а не используемой ссылкой.
'''
files['ZIP-README.md'] = zip_readme.encode('utf-8')

# Assert exactly the agreed pages, font families, and no scratch or secret files.
assert set(x for x in files if x.endswith('.html')) == set(manifest['pages'])
assert set(x for x in files if x.endswith('.woff2')) == {
    'assets/fonts/Onest-wght.woff2', 'assets/fonts/Caveat-wght.woff2'}
for name in files:
    if any(x in name.lower() for x in ('.env', '.pem', '.key', 'secret', 'specimen', 'qa/', 'candidate')):
        raise RuntimeError(f'Excluded file selected: {name}')
    if name.endswith(('.png', '.ttf')): raise RuntimeError(f'Unnecessary source file: {name}')

# Validate all local references and all HTML fragment targets against packaged bytes.
ids = {}
for name, data in files.items():
    if name.endswith('.html'):
        parser = HTMLRefs(); parser.feed(data.decode('utf-8')); ids[name] = parser.ids
errors = []
for source, ref, target, fragment in links:
    if target not in files: errors.append({'source': source, 'target': target, 'kind': 'missing-file'})
    elif fragment and target.endswith('.html') and fragment not in ids[target]:
        errors.append({'source': source, 'target': target, 'fragment': fragment, 'kind': 'missing-fragment'})
assert not errors, errors

TARGET.parent.mkdir(exist_ok=True)
with zipfile.ZipFile(TARGET, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
    for name in sorted(files):
        archive.writestr(PREFIX + name, files[name])
with zipfile.ZipFile(TARGET) as archive:
    assert archive.testzip() is None
    assert set(archive.namelist()) == {PREFIX + x for x in files}
    for name, data in files.items(): assert archive.read(PREFIX + name) == data
    # Re-parse the archive itself, not only the source files.
    archive_set = {x.removeprefix(PREFIX) for x in archive.namelist()}
    for full_name in archive.namelist():
        name = full_name.removeprefix(PREFIX)
        for ref in refs_for(name, archive.read(full_name)):
            resolved = resolve(name, ref)
            if resolved: assert resolved[0] in archive_set, (name, ref)

report = {
    'archive': str(TARGET.relative_to(ROOT)),
    'archiveRoot': PREFIX,
    'bytes': TARGET.stat().st_size,
    'megabytes': round(TARGET.stat().st_size / 1000000, 3),
    'fileCount': len(files),
    'pageCount': len(manifest['pages']),
    'localReferencesChecked': len(links),
    'extensions': dict(Counter(PurePosixPath(n).suffix for n in files)),
    'sha256': hashlib.sha256(TARGET.read_bytes()).hexdigest(),
    'sourceHashes': {n: hashlib.sha256(d).hexdigest() for n, d in files.items() if n != 'ZIP-README.md'},
    'zipIntegrity': 'pass',
    'localLinks': 'pass',
    'fragmentLinks': 'pass',
    'excluded': ['full PNGs', 'font candidates and TTFs', 'typography specimen', 'QA and research', 'API keys and environment files'],
    'notes': ['products.json and site-manifest.json image dependencies included', 'sourceSnapshot is research provenance, intentionally not packaged', 'README.md project-only paths clarified in ZIP-README.md'],
    'files': sorted(files),
}
REPORT.parent.mkdir(exist_ok=True)
REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({k: report[k] for k in ['archive','bytes','megabytes','fileCount','pageCount','localReferencesChecked','extensions','sha256','zipIntegrity','localLinks','fragmentLinks']},ensure_ascii=False,indent=2))
