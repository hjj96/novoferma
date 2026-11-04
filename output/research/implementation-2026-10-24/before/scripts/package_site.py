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
         'README.md', 'assets/fonts/OFL-Onest.txt', 'assets/fonts/OFL-Caveat.txt',
         'assets/fonts/OFL-Rubik.txt', 'assets/fonts/OFL-RobotoFlex.txt', 'assets/icons/LICENSE-Tabler.txt']
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
контакты и 14 страниц продуктов. Главная открывается четырьмя ручными
статичными слайдами: классические фрикадельки, наггетсы, Фибрики и Люля мини.
Первый слайд — фрикадельки. Вне панелей постоянно доступен скрытый h1
«Новоферма — продукты из курицы и индейки»; все четыре растровых названия — h2
с доступными текстовыми дублями. Шапка и оформление CTA общие для всех сцен.
После товаров расположен утверждённый этаж «В основе — птица»
с разломленным наггетсом и любопытной курочкой, затем B2B-блок.
Общие стили и поведение находятся в `style.css`, `design-system.css`,
`polish.css`, `mobile.css`, `motion.css`, `script.js`, `depth.css` и `depth.js`,
данные — в `products.json` и `site-manifest.json`.
`product-cards.css` подключён на главной, в каталоге и на 14 страницах
продуктов. Только главная подключает после него `home-unified.css`.
Один компонент `card()` формирует 62 карточки упаковок: четыре на главной,
16 в каталоге и 42 в рекомендациях. У них одинаковые органичные пастельные подложки,
размер упаковки, полное название, вид мяса и подтверждённая масса.
У новинок показано только «Из курицы», без веса и лишней точки. Цвет и наклон
закреплены за продуктом и сохраняются при смене его места в сетке.
Разделительные линии и рамки стрелок убраны; главная использует полные карточки
с названием и метаданными. Сетка главной содержит четыре столбца на компьютере
и два на телефоне, каталог — четыре/три/два, рекомендации — три на компьютере
и два на телефоне. Крупная упаковка первого экрана продукта, карусель главной
и растровые сцены партнёров сохраняют отдельное оформление.
`home-unified.css` объединяет четыре редакционных HTML-заголовка h2 секций
01–04 существующим шрифтом Novoferma Protein. Растровые названия продуктов
hero сохранены. Общая роль `.home-kicker`: Onest, 11 px, вес 650, трекинг
.12em, интерлиньяж 1.5. Текстовый край блока 02 совпадает с `.wrap`,
контейнер его сцены на широком экране ограничен 1392 px. Фирменный оранжевый —
#fa4b06, тёмный оранжевый для текста на цветных подложках — #c94310.
Новые изображения, шрифты и анимация для унификации не добавлены;
продуктовые композиции остаются статичными и переключаются вручную.
`catalogue.css` содержит только композицию каталога и единую галерею из 16 карточек;
отдельный блок новинок и его стили удалены, общий вид карточек задаёт `product-cards.css`.
Все четыре слайда сохраняют кремовую основу
`assets/product-hero/background-v2.webp` и один прозрачный общий оранжевый пол
`assets/product-hero/shared-floor-v11.webp`, 1672 × 941.
Прозрачные `*-art-v4.webp` сохраняют пропорции еды и персонажей.
Названия — отдельная растровая графика; подзаголовки, описания и кнопки —
настоящий HTML. У Фибриков прозрачный `benefit-brush-v11.webp`, 2144 × 733,
расположен за белым HTML-текстом Caveat «Белок + клетчатка».
Название и копия следуют друг за другом в `.hero-text-stack` по фактической высоте.
Все кнопки «Перейти в каталог» совпадают по позиции и размеру и ведут в каталог.
`product-hero.css` и `product-hero.js` управляют ручным переключением,
свайпом, клавиатурой и четырьмя полосками-индикаторами. Автопоказ и анимация текста
отключены. Мобильная версия сохраняет пропорции цельных продуктовых групп
и общую высоту сцены при переключении; сетка товаров — по два в ряд.
Прежние intro «Белок к столу!», включая v11/v12, сохранены в истории
рабочего проекта и не используются в текущей карусели.
`protein-story.css` собирает этаж из живого HTML-текста, CSS-фона,
векторной стрелки Tabler и двух прозрачных иллюстраций курочки и наггетса.
До 899 px композиция вертикальная, от 900 px — широкая.
Слои находятся в `assets/protein-story/`, локальный плакатный шрифт —
`assets/fonts/RobotoFlex-Protein.woff2`; его лицензия OFL приложена.
В каталоге сразу доступны все 16 упаковок в одной сетке: 14 подтверждённых
продуктов со ссылками на свои страницы, затем Фибрики и Люля мини.
Компактная визуальная галерея содержит четыре столбца
на компьютере, три на планшете и два на телефоне; фильтры, поиск,
счётчик и повторяющиеся горизонтальные разделители убраны.
Обе новинки используют тот же `card()` и показывают прозрачные концепты
лицевой упаковки в стиле линейки Новофермы. Их ссылки ведут
в `where-to-buy.html?product=fibriki` и `where-to-buy.html?product=lulia-mini`
с выбранной новинкой. На телефоне рекомендации карточек собраны в два столбца.
`assets/novelty-packaging/fibriki-pack-v9.webp` и `lulia-mini-pack-v3.webp`,
800 × 800 px, созданы встроенным ImageGen. Это визуальные концепты лицевой
стороны, а не официальные фотографии упаковок или печатные развёртки.
Фибрики v9 сохраняют верхнюю типографику и компоновку линейки, но получили
уникальный сюжет со стоящей фирменной курочкой и деревянной ложкой.
Новая группа еды состоит из целого шарика и половинки с натуральной мелкой
структурой фарша без длинных полос; исправлены сырые шарики в лотке
и шарик на ложке. Люля мини v3 сохраняют геометрию упаковки и печатную курочку-повара с блюдом
по образцу котлет по-домашнему, с небольшой группой овальных колбасок
спокойного оттенка. Встроенный ImageGen сделал бумагу Фибриков светлее и теплее,
вернул оранжевый логотип и смягчил коричневые чернила; у Люля мини слегка осветлена
бумага, задуманный рисунок и компоновка визуально сохранены. У Фибриков v9
дополнительно уточнён чистый внешний край упаковки. Обе новинки используют
общий компонент карточки и его пастельные подложки.
Предыдущие варианты сохранены в рабочем проекте как история.
Использованы предоставленные названия и описания продуктов, фраза
«Белок + клетчатка» для Фибриков и небольшая коричневая подпись «МИНИ-ФОРМАТ»,
раскрывающая название Люля мини. Заявления «100%», масса, пищевая ценность,
список ингредиентов, условия хранения, штрихкоды и новые SKU не добавлены.
Происхождение записано в `assets/novelty-packaging/provenance.json`;
Финальные PNG Фибриков v9, точный `fibriki-pack-v9-prompt.txt`, сравнение
с линейкой и проверка общей сетки хранятся в `output/research/catalogue-grid-16/`
полного рабочего проекта; предыдущая цветовая итерация сохранена в
`output/research/novelty-color-match/`.
Композиции еды в hero и превью 14 подтверждённых продуктов сохранены;
общее количество страниц — 20.
Страница партнёров содержит утверждённый первый экран «К делу. Со вкусом.»
с рукопожатием курочек, подписью «Пожмём крылья?» и кнопкой «Стать партнёром».
Далее — компактный текстовый СТМ «Ваш бренд. Наш продукт.» и форма
«Давайте обсудим». Магазинная сцена, мастерская СТМ и промежуточная
навигация убраны. Кнопка СТМ выбирает соответствующий формат в форме.
Запрос составляется как письмо или копируется; отправляет его пользователь.
Меню работает без сервера. Форма поиска магазинов открывает
подготовленное письмо в почтовом приложении; отправку выполняет пользователь.

Название, масса, фасовка и исходные фотографии 14 подтверждённых продуктов,
а также контакты перенесены из официального каталога novoferma.ru.
Все 14 текущих изображений этих упаковок повторно выделены встроенным ImageGen,
как описано ниже; возможна небольшая перерисовка мелких надписей и фактур.
Состав, аллергены, пищевая ценность, хранение,
приготовление и текущие точки продаж требуют актуальных данных компании;
на страницах вместо неподтверждённых сведений указаны этикетка и контакты.
Архив содержит локальный сайт, а не публикацию на домене или интеграцию с учётом.

Чистая графика четырёх продуктовых слайдов подготовлена встроенным ImageGen
по финальным изображениям пользователя; возможна небольшая перерисовка фактур. Логотип и остальные
персонажи опираются на предоставленный PDF и графику компании. Новый персонаж B2B-блока
`assets/mascot-partnership-v2.webp` нарисован встроенным ImageGen по фирменному референсу.
Все 14 текущих изображений упаковок находятся в `assets/catalogue-clean-v2/{slug}.webp`
на прозрачном холсте 800 × 800 px. Встроенный ImageGen убрал рваные края маски
и встроенные тени, восстановил цельный округлый нижний край пластикового лотка.
Исходниками стали 12 официальных фотографий и две предыдущие композиции `front-v1`.
Происхождение текущих версий записано в `assets/catalogue-clean-v2/provenance.json`.
Официальные фотографии сохранены в `assets/catalogue/`, на них ссылаются JSON-данные;
предыдущие вырезки и композиции сохранены в `assets/catalogue-cutout/` рабочего проекта.
Две предшествующие композиции созданы ImageGen по просьбе пользователя:
`bitochki-kurinye-s-ovoshchami-front-v1.webp` — с этикеткой биточков и прозрачным
лотком по образцу котлет по-домашнему; `ezhiki-iz-tsyplenka-s-risom-front-v1.webp` —
с этикеткой ёжиков и лотком по образцу классических фрикаделек. Их происхождение
записано в `assets/catalogue-cutout/front-view-edits.json` полного рабочего проекта.
PNG и точные промпты очистки хранятся в `output/research/catalogue-edge-cleanup/`,
PNG и промпты предшествующих композиций — в `output/research/catalogue-packshots/`
полного рабочего проекта; исходные PNG и промпты не включены в архив сайта.
`assets/serving-company-crop.webp` — иллюстративная подача на странице о компании,
сгенерированная через OpenAI API; она не является документальной фотографией производства.
Все изображения сайта приложены; полные исходные PNG и промежуточные
материалы не включены. Шрифты Onest, Rubik, Caveat и Roboto Flex загружаются локально;
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
    'assets/fonts/Onest-wght.woff2', 'assets/fonts/Caveat-wght.woff2',
    'assets/fonts/Rubik-wght.woff2', 'assets/fonts/RobotoFlex-Protein.woff2'}
for name in files:
    if any(x in name.lower() for x in ('.env', '.pem', '.key', 'secret', 'specimen', 'qa/', 'candidate')):
        raise RuntimeError(f'Excluded file selected: {name}')
    # Runtime imagery is WebP; source PNGs stay in the working project.
    if name.endswith(('.ttf', '.png')):
        raise RuntimeError(f'Unnecessary source file: {name}')

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
