# Текущая графика главного экрана — 8 ноября 2026

На главной пять ручных слайдов: Фибрики, фрикадельки, наггетсы, Люля мини
и Попсы. Фибрики открываются первыми, акцент «Белок + клетчатка» сохранён.
Названия, описания, кнопки и переключатели остаются живым HTML.

Финальное направление — единый тёплый кремовый фон **#F9EFDC**, без оранжевого
пола и без внешних падающих или контактных теней у еды, персонажей и предметов.
Собственные светотень и объём продуктов, а также перекрытия внутри группы еды
сохранены. Короткие красные акценты остаются отдельной деталью композиции.

Для ПК используется серия [desktop-v8](desktop-v8/README.md): макрокластер
фотореалистичной еды и сюжетная рисованная курочка расположены отдельными
прозрачными слоями. Сюжеты: Фибрики — книга рецептов и ложка; фрикадельки —
подросток-баскетболист; наггетсы — подросток со скейтом на паузе после катания;
Люля мини — гриль-мастер; Попсы — рок-барабанщик. Наггетсы собраны спокойной
группой для перекуса, их не бросают. Рисованная семья ориентируется на Попсов v3:
чёткий тёмный контур, тёплая охра и янтарь, оранжевые крылья и кремовые детали.
PNG-мастера — 1254 × 1254 RGBA; WebP для ПК — 1254 × 1254, quality 95.
Текущие источники еды: `fibriki-food-v2`, `meatballs-food-v2`,
`nuggets-food-v3`, `lulia-mini-food-v2`, `popsy-food-v3`.
Подготовка и размещение задаются `scripts/prepare_desktop_hero.py`
и `desktop-v8/layout.json`; `ground-shadow` и `shared-floor` не используются.

Для вертикального телефона подготовлена отдельная серия
[mobile-v6](mobile-v6/README.md): все пять сцен заново скомпонованы для квадратного
мобильного кадра, с теми же занятиями персонажей. Это самостоятельные сцены,
а не уменьшенные десктопные слои. Фрикадельки выбирают
`meatballs-basketball-master.png`, наггетсы — `nuggets-no-shadow-master.png`,
Попсы — `popsy-master.png` после правки просветов, без черновика с внешней тенью.
Мастера — 1254 × 1254 RGBA; мобильные WebP — 960 × 960, quality 92.
Подготовка — `scripts/prepare_mobile_hero.py`, размещение — `mobile-v6/layout.json`.
Серия [mobile-v4](mobile-v4/README.md) сохранена целиком как архив и больше
не является подключённой мобильной графикой.

Точные запросы встроенного ImageGen и сведения о происхождении сохранены рядом
с мастерами; параметры экспорта и контрольные суммы — в `exports.json` каждой
серии. Исходные PNG сохраняются при изменении размещения. Кнопка Попсов ведёт
на `product-popsy.html`, ряд из пяти мобильных вкладок прокручивается
горизонтально. Неактивные слои загружаются по выбору; переключение ожидает
декодирования всего набора и сохраняет прежнюю сцену видимой во время загрузки.

Раздельный черновик desktop-v7 был отклонён пользователем как слишком пустой.
Перед подготовкой новых слоёв были созданы полные визуальные эскизы экранов,
сохранённые в `output/research/desktop-separated-art-2026-11-07/vision/`.
Итоговая браузерная проверка собранного сайта фиксируется отдельно в
[отчёте итерации](../../../research/desktop-separated-art-2026-11-07/README.md).
Этот раздел описывает состав графики и не заявляет итогов ещё не завершённых
проверок сайта.

Ниже сохранено историческое описание предыдущих версий графики.

# Графика главного слайдера — v13

Главная использует четыре ручных статичных продуктовых слайда: классические фрикадельки, наггетсы, Фибрики и Люля мини. Первым открывается слайд фрикаделек. Вне панелей находится постоянный `sr-only h1` «Новоферма — продукты из курицы и индейки»; все четыре плакатных названия — `h2` с доступным текстовым дублем. У сцен общая шапка, кремовый фон, один прозрачный слой оранжевого пола и одинаковая кнопка «Перейти в каталог» → `catalogue.html`. Автопоказа, разлёта объектов и появления текста по частям нет.

Названия — прозрачная растровая графика с доступным дублем `sr-only`; подзаголовки, описания и CTA — живой HTML. Название и копия идут в `.hero-text-stack` по фактической высоте. Состав задаёт `product_hero()` в `scripts/build_site.py`, размещение и мобильную адаптацию — `product-hero.css`.

## Общий фон, пол и подложка Фибриков

| Графика | Runtime-WebP | Сохранённый PNG | Промпт |
|---|---|---|---|
| Кремовая база, RGB 1672 × 941 | [background-v2.webp](background-v2.webp) | [background-v2.png](background-v2.png) | [background-v2-prompt.txt](background-v2-prompt.txt) |
| Общий прозрачный оранжевый пол, RGBA 1672 × 941 | [shared-floor-v11.webp](shared-floor-v11.webp) | [shared-floor-v11.png](shared-floor-v11.png) | [shared-floor-v11-prompt.txt](shared-floor-v11-prompt.txt) |
| Оранжевый кистевой мазок без текста, RGBA 2144 × 733 | [benefit-brush-v11.webp](benefit-brush-v11.webp) | [benefit-brush-v11.png](benefit-brush-v11.png) | [benefit-brush-v11-prompt.txt](benefit-brush-v11-prompt.txt) |

`background-v2.webp` служит общей кремовой базой. Один `shared-floor-v11.webp` показывает одинаковую оранжевую дугу и тени на всех четырёх слайдах.

`benefit-brush-v11` содержит только прозрачный оранжевый мазок. Белая подпись Caveat «Белок + клетчатка» находится поверх него как HTML, редактируется в генераторе и сохраняется в доступном тексте.

## Четыре текущие продуктовые композиции

| Слайд | Runtime-WebP | Сохранённый PNG | Финальный промпт |
|---|---|---|---|
| Фрикадельки | [meatballs-art-v4.webp](meatballs-art-v4.webp) | [meatballs-art-v4.png](meatballs-art-v4.png) | [meatballs-art-v4-prompt.txt](meatballs-art-v4-prompt.txt) |
| Наггетсы | [nuggets-art-v4.webp](nuggets-art-v4.webp) | [nuggets-art-v4.png](nuggets-art-v4.png) | [nuggets-art-v4-prompt.txt](nuggets-art-v4-prompt.txt) |
| Фибрики | [fibriki-art-v4.webp](fibriki-art-v4.webp) | [fibriki-art-v4.png](fibriki-art-v4.png) | [fibriki-art-v4-prompt.txt](fibriki-art-v4-prompt.txt) |
| Люля мини | [lulia-mini-art-v4.webp](lulia-mini-art-v4.webp) | [lulia-mini-art-v4.png](lulia-mini-art-v4.png) | [lulia-mini-art-v4-prompt.txt](lulia-mini-art-v4-prompt.txt) |

Все четыре foreground-изображения — RGBA 1672 × 941. Встроенный **ImageGen (`image_gen`)** сначала удалил надписи и интерфейс пользовательских референсов в `*-plate-v3`, затем выделил еду, персонажа, зелень и штрихи в `*-art-v4`. Бумага, оранжевый пол и напольные тени удалены из этих изображений. Разные продукты и персонаж сохранены одной группой в полном кадре, с пустым левым участком. Сайт не клонирует одиночные кусочки и не переставляет объекты внутри группы.

Инструмент может слегка перерисовать фактуру еды или детали; результаты не объявляются точными пиксельными копиями источников. Оригинальные пользовательские PNG/JPG не изменены. PNG результатов сохранены; продуктовые WebP quality 94 получены форматным преобразованием с сохранением alpha.

## Названия продуктов и мобильное кадрирование

| Продукт | Растровое название | Промпт |
|---|---|---|
| Фрикадельки | [meatballs-title.webp](meatballs-title.webp) | [meatballs-title-prompt.txt](meatballs-title-prompt.txt) |
| Наггетсы | [nuggets-title.webp](nuggets-title.webp) | [nuggets-title-prompt.txt](nuggets-title-prompt.txt) |
| Фибрики | [fibriki-title.webp](fibriki-title.webp) | [fibriki-title-prompt.txt](fibriki-title-prompt.txt) |
| Люля мини | [lulia-mini-title.webp](lulia-mini-title.webp) | [lulia-mini-title-prompt.txt](lulia-mini-title-prompt.txt) |

Леттеринг подготовлен встроенным ImageGen; исходные прозрачные PNG сохранены рядом. [title-layout.json](title-layout.json) задаёт кадрирование прозрачных полей названий с сохранением пропорций букв. [art-layout-v4.json](art-layout-v4.json) описывает поля продуктовых композиций.

На телефоне используются те же `*-art-v4.webp`, что на десктопе. CSS-обёртка учитывает bbox основной группы и скрывает пустое пространство слева и отдельные краевые штрихи. Графика масштабируется пропорционально, без растягивания, перестановки или отдельной обработки bitmap. Общий фон, пол, высота сцены и единая CTA адаптируются в CSS.

## Исходные референсы

| Продукт | Файл пользователя | Копия для сравнения |
|---|---|---|
| Фрикадельки | «Изображение ChatGPT 8 окт. 2026 г., 11_20_33.png» | [meatballs-reference.webp](meatballs-reference.webp) |
| Наггетсы | «Изображение ChatGPT 8 окт. 2026 г., 11_21_02.jpg» | [nuggets-reference.webp](nuggets-reference.webp) |
| Фибрики | «Изображение ChatGPT 8 окт. 2026 г., 11_21_07.jpg» | [fibriki-reference.webp](fibriki-reference.webp) |
| Люля мини | «Изображение ChatGPT 8 окт. 2026 г., 11_20_52.jpg» | [lulia-mini-reference.webp](lulia-mini-reference.webp) |

Референсы определяют палитру, плакатную типографику, персонажа, исходные пропорции еды и расположение деталей. Они остаются источниками для визуального сравнения. Композиции еды в hero сохранены. Фибрики и Люля мини в общей сетке каталога используют текущие прозрачные концепты лицевой упаковки [fibriki-pack-v11.webp](../novelty-packaging/fibriki-pack-v11.webp) и [lulia-mini-pack-v3.webp](../novelty-packaging/lulia-mini-pack-v3.webp), 800 × 800 px, созданные встроенным ImageGen в стиле линейки Новофермы. Все 16 карточек каталога используют общий `card()`; вместе с четырьмя карточками главной и 42 рекомендациями это 62 общих превью. Отдельный блок новинок удалён. Карточки новых продуктов показывают «Из курицы» без веса и ведут в «Где купить» с выбранной новинкой; 14 подтверждённых продуктов, их страницы и превью сохранены, сайт содержит 20 страниц.

Фибрики v11 сохраняют верхнюю типографику и компоновку линейки, но получили уникальный сюжет со стоящей фирменной курочкой и деревянной ложкой. Новая группа еды состоит из целого шарика и половинки с натуральной мелкой структурой фарша без длинных полос; также исправлены сырые шарики в лотке и шарик на ложке. Люля мини v3 сохраняют геометрию упаковки и печатную курочку-повара с блюдом по образцу котлет по-домашнему, с небольшой группой овальных колбасок спокойного оттенка. Встроенный ImageGen сделал бумагу Фибриков светлее и теплее, вернул оранжевый логотип и смягчил коричневые чернила; у Люля мини слегка осветлена бумага, задуманный рисунок и компоновка визуально сохранены. У Фибриков v9 дополнительно уточнён чистый внешний край упаковки. 24 октября 2026 года у Фибриков v10 финально смягчены коричневые чернила, а логотип сделан оранжевее; принятые композиция, рисунок, фактура еды и естественные края сохранены. 4 ноября 2026 года в Фибриках v11 добавлены редкие мелкие зелёные вкрапления, похожие на рубленую зелень: на целом продукте и срезе, в маленьком шарике на ложке и в шариках внутри лотка. Сохранены принятые цвета, композиция и естественные края; новые надписи и сведения о составе не добавлены. Люля мини остаются в версии v3. Обе новинки используют общий компонент карточки и его пастельные подложки. Предыдущие варианты сохранены как история.

Концепты показывают лицевую сторону упаковки и не являются официальными фотографиями или печатными развёртками. Использованы предоставленные названия, описания продуктов, фраза «Белок + клетчатка» для Фибриков и небольшая коричневая подпись «МИНИ-ФОРМАТ», раскрывающая название Люля мини. Заявления «100%», масса, пищевая ценность, список ингредиентов, условия хранения, штрихкоды и новые SKU не добавлены. Финальные PNG Фибриков v11, точный `fibriki-pack-v11-prompt.txt` и сравнение после добавления зелёных вкраплений 4 ноября 2026 года сохранены в `output/research/fibriki-herbs-v11/` полного рабочего проекта. Цветовая коррекция v10 от 24 октября 2026 года сохранена как история в `output/research/fibriki-ink-match-v10/`. История правки краёв v9 и исходная проверка общей сетки из 16 упаковок остаются в `output/research/catalogue-grid-16/`; предыдущая цветовая итерация — в `output/research/novelty-color-match/`. [provenance.json](../novelty-packaging/provenance.json) записывает происхождение.

## Сохранённые предыдущие варианты

Промежуточные непрозрачные plates v3 сохранены для происхождения и истории, **не используются в runtime hero**:

| Продукт | Plate-WebP | PNG | Промпт |
|---|---|---|---|
| Фрикадельки | [meatballs-plate-v3.webp](meatballs-plate-v3.webp) | [meatballs-plate-v3.png](meatballs-plate-v3.png) | [meatballs-plate-v3-prompt.txt](meatballs-plate-v3-prompt.txt) |
| Наггетсы | [nuggets-plate-v3.webp](nuggets-plate-v3.webp) | [nuggets-plate-v3.png](nuggets-plate-v3.png) | [nuggets-plate-v3-prompt.txt](nuggets-plate-v3-prompt.txt) |
| Фибрики | [fibriki-plate-v3.webp](fibriki-plate-v3.webp) | [fibriki-plate-v3.png](fibriki-plate-v3.png) | [fibriki-plate-v3-prompt.txt](fibriki-plate-v3-prompt.txt) |
| Люля мини | [lulia-mini-plate-v3.webp](lulia-mini-plate-v3.webp) | [lulia-mini-plate-v3.png](lulia-mini-plate-v3.png) | [lulia-mini-plate-v3-prompt.txt](lulia-mini-plate-v3-prompt.txt) |

Послойный прототип v2 также сохранён для истории и **не подключён к текущему hero**:

- [running-mascot-v2.webp](running-mascot-v2.webp) — отдельная курочка; [промпт](running-mascot-v2-prompt.txt).
- [energy-marks-v2.webp](energy-marks-v2.webp) — отдельные штрихи; [промпт](energy-marks-v2-prompt.txt).
- [meatballs-piece-v2.webp](meatballs-piece-v2.webp) — одиночная фрикаделька; [промпт](meatballs-piece-v2-prompt.txt).
- [nuggets-piece-v2.webp](nuggets-piece-v2.webp), [nuggets-cut-v2.webp](nuggets-cut-v2.webp) — одиночные наггетсы; [целый](nuggets-piece-v2-prompt.txt), [разрез](nuggets-cut-v2-prompt.txt).
- [fibriki-piece-v2.webp](fibriki-piece-v2.webp), [fibriki-cut-v2.webp](fibriki-cut-v2.webp) — одиночные Фибрики; [целая](fibriki-piece-v2-prompt.txt), [разрез](fibriki-cut-v2-prompt.txt).
- [lulia-mini-piece-v2.webp](lulia-mini-piece-v2.webp) — одиночная мини-люля; [промпт](lulia-mini-piece-v2-prompt.txt).
- [piece-v2-layout.json](piece-v2-layout.json) — размеры и границы прозрачности части графики прежнего прототипа.

Прежние отдельные группы «еда + курочка» также больше не используются: [meatballs.webp](meatballs.webp), [nuggets.webp](nuggets.webp), [fibriki.webp](fibriki.webp), [lulia-mini.webp](lulia-mini.webp). Промпты: [фрикадельки](meatballs-prompt.txt), [наггетсы](nuggets-prompt.txt), [Фибрики](fibriki-prompt.txt), [Люля мини](lulia-mini-prompt.txt).

Ранние полные сцены `*-scene.webp` с растровым описанием оставлены для истории. Их промпты: [фрикадельки](meatballs-scene-prompt.txt), [наггетсы](nuggets-scene-prompt.txt), [Фибрики](fibriki-scene-prompt.txt), [Люля мини](lulia-mini-scene-prompt.txt).

Прежние intro «Белок к столу!», включая версии v11/v12, сохранены для истории и **не используются в текущем hero**. Их удаление не затрагивает утверждённый нижний этаж «В основе — птица».

| Предыдущий вариант | WebP | PNG | Промпт |
|---|---|---|---|
| Название со стоящей курочкой v12, RGBA 1825 × 862 | [protein-lockup-v12.webp](protein-lockup-v12.webp) | [protein-lockup-v12.png](protein-lockup-v12.png) | [protein-lockup-v12-prompt.txt](protein-lockup-v12-prompt.txt) |
| Классическая упаковка v12, RGBA 1254 × 1254 | [protein-pack-v12.webp](protein-pack-v12.webp) | [protein-pack-v12.png](protein-pack-v12.png) | [protein-pack-v12-prompt.txt](protein-pack-v12-prompt.txt) |
| Зелёная бумага прежнего intro, RGB 512 × 256 | [protein-paper.webp](../protein-paper.webp) | [PNG-экспорт PDF](../../../../tmp/pdfs/source-1.png) | [Скрипт извлечения](../../../../scripts/extract_protein_assets.py) |
| Связанное название и курочка v11 | [protein-lockup-v11.webp](protein-lockup-v11.webp) | [protein-lockup-v11.png](protein-lockup-v11.png) | [protein-lockup-v11-prompt.txt](protein-lockup-v11-prompt.txt) |
| Кластер из трёх фрикаделек v11 | [protein-cluster-v11.webp](protein-cluster-v11.webp) | [protein-cluster-v11.png](protein-cluster-v11.png) | [protein-cluster-v11-prompt.txt](protein-cluster-v11-prompt.txt) |
| Зелёный заголовок v4 | [protein-title-v4.webp](protein-title-v4.webp) | [protein-title-v4.png](protein-title-v4.png) | [protein-title-v4-prompt.txt](protein-title-v4-prompt.txt) |
| Прозрачная общая композиция v4 | [protein-art-v4.webp](protein-art-v4.webp) | [protein-art-v4.png](protein-art-v4.png) | [protein-art-v4-prompt.txt](protein-art-v4-prompt.txt) |
| Подготовительная полная сцена v4 | [protein-plate-v4.webp](protein-plate-v4.webp) | [protein-plate-v4.png](protein-plate-v4.png) | [protein-plate-v4-prompt.txt](protein-plate-v4-prompt.txt) |

Архивный `protein-lockup-v12` содержит коричневое слово с фрикаделькой вместо «О» и стоящую курочку с контактной тенью; bbox при alpha >16 — [60, 98, 1749, 780]. `protein-pack-v12` получен встроенным ImageGen EDIT из существующей [упаковки классических фрикаделек](../catalogue/frikadelki-klassicheskie.webp), без создания нового SKU «Белок+»; bbox при alpha >16 — [99, 199, 1167, 1112], WebP quality 95 с alpha, идентичным PNG. Исходники и промпты сохранены в таблице.

[protein-letter-art.webp](../protein-letter-art.webp) — прежняя небольшая вырезка курочки с фрикаделькой из PDF, источник позы архивного intro. Зелёная бумага `protein-paper.webp` также сохранена для истории; текущая карусель её не использует.

Отдельный этаж «В основе — птица» находится вне hero: [README его графики](../protein-story/README.md). Персонаж B2B-блока [mascot-partnership-v2.webp](../mascot-partnership-v2.webp) также относится к другой секции. Их состав и происхождение сохраняются независимо от обновления слайдера.
