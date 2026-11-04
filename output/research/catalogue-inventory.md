# Инвентаризация официального каталога Новофермы

Дата загрузки: 21.09.2026. Источник данных — сохранённый HTML `tmp/research/catalogue.html` со страницы https://novoferma.ru/catalogue (снимок 20.09.2026). Все 28 изображений заново скачаны с официального домена, получили HTTP 200 и проверены декодером Pillow. HTML/CSS сайта не менялись.

## Результат

- `output/concept/products.json`: массив из 14 SKU с точными публичными названиями, массой, контейнерной упаковкой, локальными и официальными URL изображений. `displayName` нормализует только регистр слова «Куриные» в двух названиях; исходный `name` сохранён.
- `output/concept/assets/catalogue/`: 14 упаковок 900×900 WebP и 14 изображений подачи 600×600 WebP (quality 90, без дорисовки и увеличения разрешения). Исходные упаковки 1300×1300 JPEG; serving-изображения источника 600×600.
- `tmp/research/catalogue-originals/`: скачанные исходники JPEG.
- `output/research/catalogue-downloads.json`: размеры, байты, HTTP status и SHA-256 каждого исходника.
- `output/research/catalogue-contact-sheet.jpg`: визуальная сверка всех упаковок.
- Суммарный размер 28 WebP: 1,833,634 байта.

## Поля и происхождение данных

- `category` — редакционная группа формы продукта, построена по названию. `categoryLabel` — читаемая подпись. На исходном сайте все товары имеют общую группу `polufabrikaty` (сохранена в `sourceCategory`).
- `meat` установлен только если название прямо содержит «куриные», «цыпленка», «Куриный» или «с индейкой». Для стрипсов, трёх общих котлет и фрикаделек оставлен null: общий брендовый рассказ не доказывает состав каждого SKU. Эти позиции можно пока фильтровать по форме.
- `ingredients`, `nutrition`, `storage`, `preparation` равны null. В очищенном от CSS/скриптов HTML нет совпадений по «состав», «аллерген», «белк», «жир», «углевод», «хранен», «приготов». Мелкий текст на упаковке не транскрибировался и не выдавался за актуальную этикетку.
- `image` — фотография официальной упаковки (предпочтён /images/catalog/); `servingImage` — официальная иллюстрация готового блюда. Они не являются новыми сгенерированными packshot.
- Slug создан для нового локального сайта. Старое название директории сохранено в `sourceSlug`; самостоятельные товарные URL на исходном сайте не заявлены.

## 14 SKU

| № | Точное публичное название | Масса | Категория | Мясо из названия | Локальная упаковка | Официальный оригинал |
|---:|---|---:|---|---|---|---|
| 1 | Котлеты Куриные | 522 г | Котлеты и биточки | Из курицы | `assets/catalogue/kotlety-kurinye.webp` | https://novoferma.ru/images/catalog/040-2.jpg |
| 2 | Биточки куриные с овощами | 450 г | Котлеты и биточки | Из курицы | `assets/catalogue/bitochki-kurinye-s-ovoshchami.webp` | https://novoferma.ru/images/catalog/041-2.jpg |
| 3 | Ёжики из цыпленка с рисом | 480 г | Фрикадельки и ёжики | Из курицы | `assets/catalogue/ezhiki-iz-tsyplenka-s-risom.webp` | https://novoferma.ru/images/catalog/208-1.jpg |
| 4 | Куриный попкорн | 400 г | Попкорн | Из курицы | `assets/catalogue/kurinyj-popkorn.webp` | https://novoferma.ru/images/catalog/165-2.jpg |
| 5 | Наггетсы Куриные | 400 г | Наггетсы | Из курицы | `assets/catalogue/naggetsy-kurinye.webp` | https://novoferma.ru/images/catalog/027-2.jpg |
| 6 | Наггетсы куриные с сыром | 400 г | Наггетсы | Из курицы | `assets/catalogue/naggetsy-kurinye-s-syrom.webp` | https://novoferma.ru/images/catalog/031-2.jpg |
| 7 | Наггетсы куриные «Динозавры» | 400 г | Наггетсы | Из курицы | `assets/catalogue/naggetsy-dinozavry.webp` | https://novoferma.ru/images/catalog/028-1.jpg |
| 8 | Наггетсы куриные острые | 400 г | Наггетсы | Из курицы | `assets/catalogue/naggetsy-ostrye.webp` | https://novoferma.ru/images/catalog/029-2.jpg |
| 9 | Наггетсы с индейкой «Фитнес» | 400 г | Наггетсы | С индейкой | `assets/catalogue/naggetsy-s-indeykoy-fitnes.webp` | https://novoferma.ru/images/catalog/033-2.jpg |
| 10 | Стрипсы | 400 г | Стрипсы | не уточнено | `assets/catalogue/stripsy.webp` | https://novoferma.ru/images/catalog/032-2.jpg |
| 11 | Котлеты по-домашнему | 480 г | Котлеты и биточки | не уточнено | `assets/catalogue/kotlety-po-domashnemu.webp` | https://novoferma.ru/images/catalog/163-2.jpg |
| 12 | Котлеты пикантные | 480 г | Котлеты и биточки | не уточнено | `assets/catalogue/kotlety-pikantnye.webp` | https://novoferma.ru/images/catalog/162-2.jpg |
| 13 | Котлеты по-итальянски | 480 г | Котлеты и биточки | не уточнено | `assets/catalogue/kotlety-po-italyanski.webp` | https://novoferma.ru/images/catalog/164-2.jpg |
| 14 | Фрикадельки «Классические» | 500 г | Фрикадельки и ёжики | не уточнено | `assets/catalogue/frikadelki-klassicheskie.webp` | https://novoferma.ru/images/catalog/030-2.jpg |

## Визуальные замечания

- Все 14 скачанных упаковок соответствуют названиям на контактном листе. Названия, иллюстрации, масса на этикетках требуют финальной актуализации владельцем перед публикацией; это официальный публичный каталог, а не складские данные.
- Биточки и ёжики сняты почти сверху, остальные упаковки в перспективе. При показе всех карточек нужны единые отступы и белое/светлое поле, без попытки обещать одинаковую новую съёмку.
- На исходном packshot ёжиков видна масса «480 г»; в публичном текстовом поле также 480 г. Визуальный ряд сохранён без ретуши.
- Файлы RGB на белом фоне; использовать `object-fit:contain`, а не crop или multiply на тёмных поверхностях.
