# Новоферма — паспорт визуальной системы сайта

Версия 1.1 · 5 ноября 2026 · локальная сборка после responsive-оптимизации hero, 23 маршрута.

Это рабочий паспорт внедрённой системы: он фиксирует назначение шрифтов, персонажей, упаковок и фотографий, а также правила дальнейшего использования. Он развивает §9 B2B-аудита и замечания VB05/VB06/VB11/VB15. Документ **не является утверждённым правообладателем брендбуком** и не присваивает изображениям отсутствующее согласование. «Используется в сборке» означает технический факт, а не одобрение художественного решения, рецептуры или печатного макета.

Основа проверки — текущие HTML из [site-manifest.json](../output/concept/site-manifest.json), [генератор](../scripts/build_site.py), действующие CSS и сами изображения. Отдельно просмотрены четыре hero-композиции, самостоятельный персонаж в фартуке, персонажи белкового блока, партнёрского входа, тизера и контактов, обе концептуальные упаковки. Прежние аудиты используются как история решений, а не как доказательство текущего вида сайта.

## 1. Что объединяет систему

У сайта четыре разных визуальных задачи. Плакатная сцена вызывает аппетит и знакомит с продуктом. Каталог помогает сравнить названия, массу и статус. Карточка товара объясняет, что известно о конкретной позиции. Раздел для бизнеса помогает выбрать формат обращения и передать задачу. Эти задачи могут пользоваться одной палитрой и персонажами, но им не требуется одинаковая плотность декора.

Семейность выражается через совместный стол, знакомую еду, живой рисунок и тёплый язык. Она не означает детское питание, возрастную рекомендацию или необходимость уменьшать деловую серьёзность. Персонаж не заменяет технолога, сотрудника производства, документ или подтверждение состава. В разделе СТМ шаги процесса показываются текстом; новые нарисованные «технологи», «логисты» и «менеджеры» для каждого шага не нужны.

Сохраняются кремовый, коричневый и оранжевый цвета, выразительные короткие заголовки, предметная упаковка и свободные промежутки. Секции отделяются пространством и заливкой. Новые декоративные горизонтальные разделители не добавляются.

## 2. Роли шрифтов

| Роль | Семейство и действующий файл | Применение | Ограничение |
|---|---|---|---|
| Короткий плакат | Novoferma Protein; `assets/fonts/RobotoFlex-Protein.woff2` | Короткая фраза или название hero, основные плакатные заголовки; uppercase, статическое начертание 850 | Не использовать для длинного наименования SKU, абзаца или формы. Не сжимать `scaleX`, не растягивать и не дорисовывать жирность |
| Информационный текст | Onest, CSS-имя Novoferma Sans; `assets/fonts/Onest-wght.woff2` | Названия товаров, абзацы, навигация, поля и действия. Обычный регистр; вес по иерархии | Не превращать все элементы в жирный капс. Длинное название должно переноситься, а не обрезаться ради сетки |
| Рукописная подпись | Caveat, CSS-имя Novoferma Hand; `assets/fonts/Caveat-wght.woff2` | Короткая поддерживающая реплика, например подпись в белковом блоке или подвале | Не набирать так массу, статус концепта, состав, контакты, условие поставки или подпись поля |
| Вторичный акцент | Rubik, CSS-имя Novoferma Poster; `assets/fonts/Rubik-wght.woff2` | Вторичная плакатная реплика hero, нумерация и отдельные статусные акценты | Не заменять им Onest в длинных названиях. Это дополнительная роль внутри системы, не отдельный стиль для каждой страницы |

Общие имена ролей объявлены в [typography.css](../output/concept/typography.css): `--font-poster-short`, `--font-reading`, `--font-secondary`, `--font-note`. Файл подключается после компонентных стилей. Размеры и композиция конкретного блока остаются в его CSS: переносить все размеры в очередной общий override не следует.

Длинный заголовок карточки продукта использует Onest 750, обычный регистр и межстрочный интервал 1.16. На мобильном устройстве он начинается примерно с 30 px при базовом размере текста 16 px. Значения фактов — 16 px, подписи и важные статусы — 14 px. Факты перестраиваются по доступной ширине вместо принудительного уменьшения шрифта. Это параметры текущего интерфейса, а не универсальный стандарт для любого текста.

В обновлённых информационных компонентах размеры заданы через rem, высота строки — без фиксированного пиксельного ограничения. При недоступности локального шрифта резервный шрифт имеет право занять больше строк. Сначала увеличивается высота блока или меняется число колонок; скрывать текст, сжимать буквы и отменять увеличение текста нельзя. Шрифтовые надписи внутри bitmap-упаковки не являются частью живой типографической системы.

## 3. Палитра и читаемость

Основная информационная пара — `#402111` на `#fff5e3`; расчётный контраст 13.454:1. Второстепенный текст `#795e4c` на кремовом даёт 5.520:1; на более тёмном конце градиента карточки `#f0e0c4` — 4.594:1. Статус концепта `#ac3a09` на кремовом — 5.775:1. Пояснение формы `#efddc4` на коричневом — 10.951:1.

Белый плакатный заголовок `#fff5e3` на партнёрском оранжевом `#fa4b06` даёт 3.198:1. Эта пара сохраняется для крупного заголовка; её нельзя автоматически переносить на мелкие пояснения, подписи полей или статус товара. Числа получены из фактических непрозрачных CSS-цветов, а не из сглаженных краёв букв на скриншоте. Полная методика и 14 пар — в [типографическом evidence](../output/research/design-mobile-2026-11-05/typography-source-evidence.json).

У крупного заголовка каталога используется более тёмный оранжевый `#c94310` на `#f4e5c7`: 3.931:1. Он заменил прежний `#ee4b12`, дававший на этом фоне 2.987:1. Это локальное исправление конкретной пары, а не смена всей палитры; для обычного мелкого текста указанного контраста недостаточно. Актуальные вычисленные в браузере пары и контекст их проверки записаны в [протоколе цветов](../output/research/design-implementation-2026-11-05/computed-colors-browser.json).

Контраст сам по себе не доказывает удобство. У важных ограничений должна быть заметная позиция рядом с названием или изображением. Масса, категория и статус остаются текстом. Для действий в обновлённых компонентах используется проектная цель не менее 44 px по высоте; у checkbox доступная область включает подпись. Полного заявления о соответствии WCAG этот документ не делает.

## 4. Персонажи: назначение и текущие места

Ниже указаны файлы, реально встречающиеся в текущих HTML, включая responsive-кандидаты. В таблице приведён основной HTML `src`; полный список вариантов находится в инвентаре в конце документа. Все пути в таблицах относятся к `output/concept/`.

| Роль и место | Текущий файл | Что сохранять |
|---|---|---|
| Главная, Фибрики — первая hero-сцена | `assets/responsive/hero/fibriki-art-v5-800-q90-1b6cf1a2.webp` | Цельная композиция из курочки в клетчатом фартуке и фрикаделек. Статус «Концепт новинки» остаётся отдельным читаемым текстом |
| Главная, фрикадельки | `assets/responsive/hero/meatballs-art-v4-800-q90-8e04511a.webp` | Сюжет движения и еды внутри своей сцены; имя и действие находятся в независимой текстовой колонке |
| Главная, наггетсы | `assets/responsive/hero/nuggets-art-v4-800-q90-e6e41be3.webp` | Композиция еды, соуса, персонажа и нарисованных акцентов используется как единое artwork |
| Главная, Люля мини | `assets/responsive/hero/lulia-mini-art-v4-800-q90-7ed345d8.webp` | Концептуальный продуктовый сюжет; рисунок не доказывает рецептуру или запуск |
| Главная, объясняющий блок о птице | `assets/responsive/illustrations/hen-layer-v2-800-q90-bd32bcef.webp` | Курочка в фартуке с жестом «посмотреть внутрь»; не выдавать за изображение сотрудника или производства |
| Главная, тизер сотрудничества | `assets/responsive/illustrations/mascot-partnership-v2-800-q90-66fd6b8d.webp` | Небольшой портретный акцент. Текст форматов и действие важнее размера персонажа |
| Партнёрам, первый экран | `assets/responsive/partners/partner-host-v1-800-q90-283eb84c.webp` | Приглашающий персонаж в светлом жакете, с книгой/папкой; самостоятельная роль входа в B2B |
| О компании, блок «Наши герои» | `assets/responsive/illustrations/running-mascot-v2-800-q90-f2dbaa26.webp` | Курочка в светлом фартуке с зелёной клеткой, раскрытыми крыльями и динамичной позой |
| Контакты | `assets/responsive/illustrations/mascot-contact-restored-v2-800-q90-8fe205be.webp` | Компактный портретный акцент после контактной информации, без вытеснения реквизитов |
| Каталог и карточки товаров | Самостоятельного маскота в текущем каталоге нет; персонажи видны на упаковках | Не возвращать отдельную курочку в каждую карточку: визуальным предметом выбора остаётся упаковка |

Текущий блок «Наши герои» содержит **одну** самостоятельную курочку. Его семейный тон не является доказательством существования утверждённого рисунка группы персонажей. Старое правило, где `running-mascot` одновременно относился к каталогу, не описывает новую каталожную композицию.

У персонажей есть наблюдаемое сходство: тёплое оперение, красный гребень, тёмный рисованный контур. Но портретные варианты, персонаж в жакете, рисунок в фартуке и герои на концептуальных упаковках различаются пропорциями, характером лица и фактурой. Общая палитра не превращает их автоматически в унифицированную модель. В текущем паспорте они сохраняются как **ролевые варианты существующей сборки**. Утверждение единого модельного листа или права на произвольное новое изображение этим не устанавливается.

## 5. Правила повторного использования персонажа

Для нового размещения сначала использовать существующий файл, подходящий роли. Не создавать новую AI-курочку под каждую секцию и не поручать генерации «похожего героя» вместо выбора текущего источника. Не извлекать из цельной hero-композиции нового самостоятельного персонажа и не объявлять его каноническим без отдельного зафиксированного художественного решения.

Сохраняются пропорции, глаза, клюв, гребень, лапы, одежда, контур и фактура. Допустимы равномерное масштабирование, размещение и технические responsive-копии. Не допускаются независимое растяжение по осям, зеркалирование, CSS-фильтр для новой обводки, перекрашивание одежды или автоматическая дорисовка частей тела ради заполнения колонки. Ограничение относится к персонажам; растяжение фоновой текстуры не является изменением анатомии.

Рабочая композиционная единица — один герой с понятной задачей в секции. У цельной сцены не появляется второй standalone-персонаж. Навигация, заголовок, статус, кнопка, поля и фокус имеют собственные защищённые области. Если герой не помещается, уменьшается декоративная зона, а не служебный шрифт. На телефоне персонаж контактов не создаёт пустой экран до реквизитов; на странице партнёров крупная иллюстрация входа не повторяется внутри формы.

Подложка следует за изображением, а не становится самостоятельной темой. Овал партнёрского входа и подложки упаковок используют существующую палитру и пропорции. Не добавлять новый случайный blob, поворот и тень для каждого товара. Состояние hover может дать небольшой отклик подложки; существенные сведения, имя и масса не должны зависеть от наведения.

## 6. Упаковки, концепты и документальные изображения

В интерфейсе нужно различать три типа изображения.

| Тип | Текущий набор | Что изображение подтверждает |
|---|---|---|
| Обработанное превью упаковки | 14 серийных SKU, responsive packshots | Помогает узнавать и сравнивать товар. README фиксирует применение ImageGen в прошлых итерациях; мелкие надписи могли измениться. Превью не заменяет оригинальную этикетку |
| Визуальный концепт упаковки | Фибрики v11 и Люля мини v3, также в responsive packshots | Показывает дизайн-концепцию. Не является печатной развёрткой, спецификацией или подтверждением выпуска; маркировка концепта остаётся в HTML |
| Фото производителя | 14 оригинальных упаковок и 14 сопоставленных фотографий подачи из `assets/catalogue/` | Имеет предметный источник и привязку к SKU в `products.json`/manifest. Это локальные копии источника, а не новая проверка фактической партии или состава |

В каталоге упаковка помещается целиком в отведённую сцену. Один товар использует одно и то же превью в каталоге и связанных карточках; лёгкий наклон относится к представлению упаковки, а не к изменению этикетки. Название, масса и статус находятся отдельным живым текстом. Изображение карточки с пустым alt не теряет имя ссылки, потому что внутри этой же ссылки расположен заголовок товара. На PDP изображение имеет текстовое описание.

На 14 серийных PDP доступны оригинальное изображение и раскрываемый «Пример подачи производителя». Фото подачи не растягивается больше собственных 600×600, подпись остаётся читаемой: «Пример подачи с сайта производителя. Состав и способ приготовления сверяйте по актуальной этикетке». Сопоставление берётся из данных конкретного товара; фотографию соседнего SKU нельзя использовать как документальный пример без нового источника.

На странице «О компании» используется оригинальная фотография упаковки фрикаделек, а на СТМ — упаковка как подписанный пример продукции. Это не фотография цеха, линии, контроля качества или упаковки будущего заказчика. Таких документальных производственных кадров текущий набор не содержит. Сгенерированная еда в hero и иллюстрации не подменяют отсутствующие производственные доказательства.

Пищевые claims, состав, аллергены, хранение и способ приготовления публикуются только по отдельному содержательному правилу из [реестра готовности](b2b-content-readiness.md). Вписанная в bitmap надпись, вкрапление зелени или привлекательный срез не являются источником этих данных.

## 7. История выбора и реальные статусы

| Запись | Что действительно зафиксировано | Чего она не устанавливает |
|---|---|---|
| [Рабочие правила персонажей, 24.10](../output/research/implementation-2026-10-24/character-guidelines.txt) | Версия 0.1, выбранные рабочие ориентиры и исключения; документ прямо отрицает статус утверждённого брендбука | Согласование правообладателем и художественное единство всех героев |
| [Партнёрская сцена, 24.10](../output/research/partners-brand-2026-10-24/README.md) | Введение персонажа в жакете, техническая и визуальная приёмка исполнителями на перечисленных ширинах | Подпись владельца бренда. Старое описание mailto-формы уже не отражает нынешний API |
| [Уточнение партнёрской страницы, 04.11](../output/research/partners-refinement-2026-11-04/README.md) | Историческая адаптивная доработка существующей иллюстрации | Новый master или утверждение персонажа брендом; актуальность каждого старого размера после нынешних изменений |
| [Импорт рабочей версии, 05.11](../output/research/design-implementation-2026-11-05/imported-workspace.json) | Пути и SHA-256 импортированных hero/catalogue/card CSS, Fibriki art-v5 и его layout | Художественное согласование art-v5 или статус концепта «выпущен» |
| [Responsive host, 05.11](../output/research/design-mobile-2026-11-05/partner-host-optimization.json) | Техническое уменьшение/кодирование того же персонажа, сохранённый master и alpha | Новую иллюстрацию, изменение художественного статуса или измеренный эффект на production CWV |
| [Текущий README](../README.md) и [готовность контента](b2b-content-readiness.md) | Происхождение обработки превью, версии концептов, запрет неподтверждённых пищевых полей | Финальное продуктовое или печатное утверждение концептов |

Для действующих artwork в перечисленных источниках не найден именованный согласующий от владельца бренда с датой финального художественного утверждения. Статус такого утверждения в этом документе: **не подтверждено**. Это не вывод о наличии или отсутствии прав; это граница доступной записи. Внутренний PASS, выбор исполнителем и присутствие файла в сборке сохраняются как отдельные факты.

## 8. Как менять систему без расхождения версий

При замене изображения записываются прежний и новый путь, SHA-256, источник, причина, роль, затронутые страницы и фактический статус согласования. Если согласующий не указан, поле остаётся «не подтверждено». Техническая оптимизация, художественная замена и обновление этикетки — разные операции; их нельзя объединять одним статусом «готово».

Для Fibriki hero файл изображения v5 и `fibriki-art-v5-layout.json` переносятся парой. Для остальных трёх сцен текущая геометрия находится в `art-layout-v4.json`. Генератор выбирает эти файлы отдельно по наличию; неполный перенос может сопоставить изображение и рамку разных версий. В текущем срезе нужная пара присутствует. После изменения источника пересоздаются responsive-варианты и соответствующая запись `asset-variants.json`; нельзя вручную подменить один WebP, сохранив прежний manifest.

При художественной замене сравниваются голова, контур, глаза, клюв, лапы, одежда и фактура рядом с действующим персонажем при сопоставимом размере. Затем проверяется целая страница: текст, кнопки, соседние блоки и пустое пространство. На 320/390/768/1024/1440 px проверяются переносы, целостность силуэта и отсутствие пересечения служебных областей. Отдельно проверяются увеличение, отсутствие локальных шрифтов, клавиатура и reduced motion. Родная browser zoom-проверка и text-only увеличение — разные проверки; одна не должна записываться как другая.

Сейчас hero переключается вручную, artwork имеет короткий отклик на выбор; режим reduced motion его отключает. Товарные факты и действия видны без ожидания анимации. Новые переходы не должны скрывать информацию, вызывать автоматическую смену сцены во время чтения или делать интерфейс зависимым от движения.

Этот паспорт закрывает отсутствие рабочей карты ролей. Он не закрывает вопрос финального единого модельного листа персонажей и не превращает различающиеся существующие рисунки в художественно унифицированную семью.

## 9. Responsive-файлы, контрольные суммы и наблюдаемый выбор

Партнёрский персонаж имеет варианты шириной 240/400/640/800/1024 px; четыре hero-композиции — 640/800/1024/1280/1672 px. Таблица ролей выше показывает текущий HTML `src` по умолчанию. Реально загруженный кандидат выбирается через `srcset`/`sizes`; у неактивной hero-сцены они передаются через `data-srcset`/`data-sizes` при её подготовке. Width в имени файла — размер bitmap, не CSS-ширина персонажа или рамки.

Исходники оптимизации продолжают быть источниками этих же рисунков. Следующие SHA-256 относятся к исходным файлам, а не к responsive-копиям; совпадение фиксирует сохранение источника и не устанавливает художественного утверждения.

| Действующий источник оптимизации | SHA-256 источника |
|---|---|
| `assets/partners-brand-v1/partner-host-v1.webp` | `283eb84c820753b8aa8c61d4e9024f939d560f9f2d31ea23f0be46ddad81e2bd` |
| `assets/product-hero/fibriki-art-v5.webp` | `1b6cf1a289654f8fabee1b10cb4e8459380cbd4145734e2b287fa8fecabc8513` |
| `assets/product-hero/meatballs-art-v4.webp` | `8e04511ae7f89a89102daa20499a0c5d62f3f0f34687fc047dcefaec56d88958` |
| `assets/product-hero/nuggets-art-v4.webp` | `e6e41be33fa1b039a64cc72efd4d1803b9761716b927ab1345581a1da4598c68` |
| `assets/product-hero/lulia-mini-art-v4.webp` | `7ed345d89b4ca2bfa9cb93d07abc351478346c3e127f680eb712d8e83a2c63cc` |

В [локальном браузерном протоколе](../output/research/design-implementation-2026-11-05/responsive-image-browser-checks.json) записаны 18 наблюдений при **DPR 1**. Для партнёрского персонажа на 320/390 выбран вариант 240 px, encoded body 33 582 байта; на 768/1024/1280/1440 — 400 px, 72 726 байт. Для hero на 320 все четыре сцены выбрали 640 px: Фибрики 47 682, фрикадельки 47 624, наггетсы 57 682, Люля мини 60 708 байт. На 1440 все четыре выбрали 1280 px. Это размеры полученного тела отдельного ресурса, не общий сетевой вес страницы.

DPR 2/3 этим протоколом не проверены. Локальные currentSrc, timing, LCP и CLS не являются production p75 или доказательством полевого Core Web Vitals. Проверка настоящим VoiceOver/NVDA этими измерениями также не выполнялась. Методы и остатки сводятся в [отчёте реализации](../output/research/design-implementation-2026-11-05/implementation.md).

## 10. Инвентарь текущего использования

Срез составлен из 23 HTML в manifest: учитываются `src`, `data-src` и все кандидаты `srcset`/`data-srcset`; query-хеши убраны только для записи пути. Это **ссылки текущей сборки**, а не список всех файлов папки assets и не отчёт о загрузке каждого кандидата браузером. Старые изображения, PNG-черновики и master, подменённые в HTML responsive-вариантами, сюда не включены. Шрифты и favicon перечислены отдельно. Все перечисленные локальные файлы проверены на существование.

В последнем столбце указаны первые 12 знаков SHA-256 именно перечисленного runtime-файла. Для partner/hero полные контрольные суммы производных также находятся в `asset-variants.json` → `variants[].sha256`; они отличаются от checksum источника выше.

Всего: **114 уникальных текущих путей** — 109 изображений из HTML, 4 шрифта и favicon. В том числе 20 responsive hero-файлов и 5 вариантов партнёрского персонажа.

### Hero и фоновые слои

| Текущий путь | Использование | SHA-256, первые 12 знаков |
|---|---|---|
| `assets/product-hero/background-v2.webp` | index.html | `b9fdef9d25b7` |
| `assets/product-hero/shared-floor-v11.webp` | index.html | `e062992ed8c6` |
| `assets/responsive/hero/fibriki-art-v5-1024-q90-1b6cf1a2.webp` | index.html | `5c95c85ddd4f` |
| `assets/responsive/hero/fibriki-art-v5-1280-q90-1b6cf1a2.webp` | index.html | `a659c53e483e` |
| `assets/responsive/hero/fibriki-art-v5-1672-q90-1b6cf1a2.webp` | index.html | `629d8d04a647` |
| `assets/responsive/hero/fibriki-art-v5-640-q90-1b6cf1a2.webp` | index.html | `adf1c9d4ef8a` |
| `assets/responsive/hero/fibriki-art-v5-800-q90-1b6cf1a2.webp` | index.html | `6cd7e659b28e` |
| `assets/responsive/hero/lulia-mini-art-v4-1024-q90-7ed345d8.webp` | index.html | `504bc2eef125` |
| `assets/responsive/hero/lulia-mini-art-v4-1280-q90-7ed345d8.webp` | index.html | `17d475d3996a` |
| `assets/responsive/hero/lulia-mini-art-v4-1672-q90-7ed345d8.webp` | index.html | `e682551e78ca` |
| `assets/responsive/hero/lulia-mini-art-v4-640-q90-7ed345d8.webp` | index.html | `d093a047fb82` |
| `assets/responsive/hero/lulia-mini-art-v4-800-q90-7ed345d8.webp` | index.html | `9f6f3b2dc4e1` |
| `assets/responsive/hero/meatballs-art-v4-1024-q90-8e04511a.webp` | index.html | `5afc268099c2` |
| `assets/responsive/hero/meatballs-art-v4-1280-q90-8e04511a.webp` | index.html | `830a5850b6b0` |
| `assets/responsive/hero/meatballs-art-v4-1672-q90-8e04511a.webp` | index.html | `a609a2d9377c` |
| `assets/responsive/hero/meatballs-art-v4-640-q90-8e04511a.webp` | index.html | `bc05ad819bf5` |
| `assets/responsive/hero/meatballs-art-v4-800-q90-8e04511a.webp` | index.html | `78ee3697a929` |
| `assets/responsive/hero/nuggets-art-v4-1024-q90-e6e41be3.webp` | index.html | `ba9255185c3d` |
| `assets/responsive/hero/nuggets-art-v4-1280-q90-e6e41be3.webp` | index.html | `f24f947f4b85` |
| `assets/responsive/hero/nuggets-art-v4-1672-q90-e6e41be3.webp` | index.html | `1d06196a5bd3` |
| `assets/responsive/hero/nuggets-art-v4-640-q90-e6e41be3.webp` | index.html | `9d3b34afa328` |
| `assets/responsive/hero/nuggets-art-v4-800-q90-e6e41be3.webp` | index.html | `0cef3e8ed492` |

### Персонажи и объясняющие иллюстрации

| Текущий путь | Использование | SHA-256, первые 12 знаков |
|---|---|---|
| `assets/responsive/illustrations/hen-layer-v2-1254-q90-bd32bcef.webp` | index.html | `a3b9679e419c` |
| `assets/responsive/illustrations/hen-layer-v2-400-q90-bd32bcef.webp` | index.html | `70836b2abbfd` |
| `assets/responsive/illustrations/hen-layer-v2-800-q90-bd32bcef.webp` | index.html | `342ea8e37f33` |
| `assets/responsive/illustrations/mascot-contact-restored-v2-400-q90-8fe205be.webp` | contacts.html | `37e8a657e0f4` |
| `assets/responsive/illustrations/mascot-contact-restored-v2-800-q90-8fe205be.webp` | contacts.html | `ee09ae841004` |
| `assets/responsive/illustrations/mascot-contact-restored-v2-980-q90-8fe205be.webp` | contacts.html | `a76fc0431594` |
| `assets/responsive/illustrations/mascot-partnership-v2-1086-q90-66fd6b8d.webp` | index.html | `1ca4222abbf1` |
| `assets/responsive/illustrations/mascot-partnership-v2-400-q90-66fd6b8d.webp` | index.html | `53c4242b922d` |
| `assets/responsive/illustrations/mascot-partnership-v2-800-q90-66fd6b8d.webp` | index.html | `514a5fc47d35` |
| `assets/responsive/illustrations/nuggets-layer-v2-1448-q90-a648c271.webp` | index.html | `8d3296a30e21` |
| `assets/responsive/illustrations/nuggets-layer-v2-400-q90-a648c271.webp` | index.html | `341a3a657caa` |
| `assets/responsive/illustrations/nuggets-layer-v2-800-q90-a648c271.webp` | index.html | `29351d09906b` |
| `assets/responsive/illustrations/running-mascot-v2-1254-q90-f2dbaa26.webp` | about.html | `53323b04e03d` |
| `assets/responsive/illustrations/running-mascot-v2-400-q90-f2dbaa26.webp` | about.html | `bbe40576ea7f` |
| `assets/responsive/illustrations/running-mascot-v2-800-q90-f2dbaa26.webp` | about.html | `2eb4aa66b007` |
| `assets/responsive/partners/partner-host-v1-1024-q90-283eb84c.webp` | partners.html | `978fbe99cb19` |
| `assets/responsive/partners/partner-host-v1-240-q90-283eb84c.webp` | partners.html | `de216ed78460` |
| `assets/responsive/partners/partner-host-v1-400-q90-283eb84c.webp` | partners.html | `f441dd0bb987` |
| `assets/responsive/partners/partner-host-v1-640-q90-283eb84c.webp` | partners.html | `39bff86676d8` |
| `assets/responsive/partners/partner-host-v1-800-q90-283eb84c.webp` | partners.html | `3776708c8f61` |

### Превью упаковок — серийные и концепты

| Текущий путь | Использование | SHA-256, первые 12 знаков |
|---|---|---|
| `assets/responsive/packshots/bitochki-kurinye-s-ovoshchami-400-q94-5db59691.webp` | 11 страниц: каталог / связанные карточки / PDP | `4a1ecb3a7089` |
| `assets/responsive/packshots/bitochki-kurinye-s-ovoshchami-800-q94-5db59691.webp` | 11 страниц: каталог / связанные карточки / PDP | `a85f97f2ae45` |
| `assets/responsive/packshots/ezhiki-iz-tsyplenka-s-risom-400-q94-1d1a2e59.webp` | 7 страниц: каталог / связанные карточки / PDP | `8f0df745b973` |
| `assets/responsive/packshots/ezhiki-iz-tsyplenka-s-risom-800-q94-1d1a2e59.webp` | 7 страниц: каталог / связанные карточки / PDP | `5be581e202b1` |
| `assets/responsive/packshots/fibriki-pack-v11-400-q94-1c8ec286.webp` | catalogue.html, product-fibriki.html | `d249c192f40c` |
| `assets/responsive/packshots/fibriki-pack-v11-800-q94-1c8ec286.webp` | catalogue.html, product-fibriki.html | `7cc0ef9a9435` |
| `assets/responsive/packshots/frikadelki-klassicheskie-400-q94-e0ef4bbb.webp` | 6 страниц: каталог / связанные карточки / PDP | `ca1c4918f71c` |
| `assets/responsive/packshots/frikadelki-klassicheskie-800-q94-e0ef4bbb.webp` | 6 страниц: каталог / связанные карточки / PDP | `a01221413155` |
| `assets/responsive/packshots/kotlety-kurinye-400-q94-a1ed2899.webp` | 12 страниц: каталог / связанные карточки / PDP | `5d087814460d` |
| `assets/responsive/packshots/kotlety-kurinye-800-q94-a1ed2899.webp` | 12 страниц: каталог / связанные карточки / PDP | `2739408672a7` |
| `assets/responsive/packshots/kotlety-pikantnye-400-q94-aed06aa1.webp` | 5 страниц: каталог / связанные карточки / PDP | `13c5734ad82b` |
| `assets/responsive/packshots/kotlety-pikantnye-800-q94-aed06aa1.webp` | 5 страниц: каталог / связанные карточки / PDP | `b30a469be199` |
| `assets/responsive/packshots/kotlety-po-domashnemu-400-q94-4b30908e.webp` | 6 страниц: каталог / связанные карточки / PDP | `037569c6a8e8` |
| `assets/responsive/packshots/kotlety-po-domashnemu-800-q94-4b30908e.webp` | 6 страниц: каталог / связанные карточки / PDP | `4ef90cf6056e` |
| `assets/responsive/packshots/kotlety-po-italyanski-400-q94-4e765a90.webp` | catalogue.html, product-kotlety-po-italyanski.html | `9bd523ec91f9` |
| `assets/responsive/packshots/kotlety-po-italyanski-800-q94-4e765a90.webp` | catalogue.html, product-kotlety-po-italyanski.html | `97f57331b1b9` |
| `assets/responsive/packshots/kurinyj-popkorn-400-q94-d707c51a.webp` | catalogue.html, index.html, product-kurinyj-popkorn.html | `45ec0105bba1` |
| `assets/responsive/packshots/kurinyj-popkorn-800-q94-d707c51a.webp` | catalogue.html, index.html, product-kurinyj-popkorn.html | `b4c076806311` |
| `assets/responsive/packshots/lulia-mini-pack-v3-400-q94-5406742c.webp` | catalogue.html, product-lulia-mini.html | `5e507af6bec1` |
| `assets/responsive/packshots/lulia-mini-pack-v3-800-q94-5406742c.webp` | catalogue.html, product-lulia-mini.html | `5b986470f63b` |
| `assets/responsive/packshots/naggetsy-dinozavry-400-q94-d8f755c7.webp` | 6 страниц: каталог / связанные карточки / PDP | `62e3cc772f68` |
| `assets/responsive/packshots/naggetsy-dinozavry-800-q94-d8f755c7.webp` | 6 страниц: каталог / связанные карточки / PDP | `6f75a2156d17` |
| `assets/responsive/packshots/naggetsy-kurinye-400-q94-712fb649.webp` | 7 страниц: каталог / связанные карточки / PDP | `c01e818ffaa6` |
| `assets/responsive/packshots/naggetsy-kurinye-800-q94-712fb649.webp` | 7 страниц: каталог / связанные карточки / PDP | `40ea54c6ef0d` |
| `assets/responsive/packshots/naggetsy-kurinye-s-syrom-400-q94-070a49d8.webp` | 6 страниц: каталог / связанные карточки / PDP | `1137a14de82d` |
| `assets/responsive/packshots/naggetsy-kurinye-s-syrom-800-q94-070a49d8.webp` | 6 страниц: каталог / связанные карточки / PDP | `04bd46025905` |
| `assets/responsive/packshots/naggetsy-ostrye-400-q94-d5c86a9d.webp` | 5 страниц: каталог / связанные карточки / PDP | `8c99c36c9b59` |
| `assets/responsive/packshots/naggetsy-ostrye-800-q94-d5c86a9d.webp` | 5 страниц: каталог / связанные карточки / PDP | `e13b5fcc62e5` |
| `assets/responsive/packshots/naggetsy-s-indeykoy-fitnes-400-q94-68b47a02.webp` | catalogue.html, product-naggetsy-s-indeykoy-fitnes.html | `0aad829aa5de` |
| `assets/responsive/packshots/naggetsy-s-indeykoy-fitnes-800-q94-68b47a02.webp` | catalogue.html, product-naggetsy-s-indeykoy-fitnes.html | `f935fbcfb978` |
| `assets/responsive/packshots/stripsy-400-q94-04f43af0.webp` | catalogue.html, index.html, product-stripsy.html | `cd0e97ebc096` |
| `assets/responsive/packshots/stripsy-800-q94-04f43af0.webp` | catalogue.html, index.html, product-stripsy.html | `a65219aa93b8` |

### Оригинальные упаковки и фото подачи производителя

| Текущий путь | Использование | SHA-256, первые 12 знаков |
|---|---|---|
| `assets/catalogue/bitochki-kurinye-s-ovoshchami-serving.webp` | product-bitochki-kurinye-s-ovoshchami.html | `d482c09e021b` |
| `assets/catalogue/bitochki-kurinye-s-ovoshchami.webp` | product-bitochki-kurinye-s-ovoshchami.html | `1e5504b7fe14` |
| `assets/catalogue/ezhiki-iz-tsyplenka-s-risom-serving.webp` | product-ezhiki-iz-tsyplenka-s-risom.html | `c2a164d5083c` |
| `assets/catalogue/ezhiki-iz-tsyplenka-s-risom.webp` | product-ezhiki-iz-tsyplenka-s-risom.html | `825129ea51e8` |
| `assets/catalogue/frikadelki-klassicheskie-serving.webp` | product-frikadelki-klassicheskie.html | `af6598544763` |
| `assets/catalogue/frikadelki-klassicheskie.webp` | about.html, product-frikadelki-klassicheskie.html | `35ce01ebe7c6` |
| `assets/catalogue/kotlety-kurinye-serving.webp` | product-kotlety-kurinye.html | `ceaded4557da` |
| `assets/catalogue/kotlety-kurinye.webp` | product-kotlety-kurinye.html | `6b613b70ae92` |
| `assets/catalogue/kotlety-pikantnye-serving.webp` | product-kotlety-pikantnye.html | `933498c7c3ff` |
| `assets/catalogue/kotlety-pikantnye.webp` | product-kotlety-pikantnye.html | `0d04d00ad201` |
| `assets/catalogue/kotlety-po-domashnemu-serving.webp` | product-kotlety-po-domashnemu.html | `8ab29c8922a6` |
| `assets/catalogue/kotlety-po-domashnemu.webp` | product-kotlety-po-domashnemu.html | `7282d8d2ff6f` |
| `assets/catalogue/kotlety-po-italyanski-serving.webp` | product-kotlety-po-italyanski.html | `a54711e23e68` |
| `assets/catalogue/kotlety-po-italyanski.webp` | product-kotlety-po-italyanski.html | `8fca1df37736` |
| `assets/catalogue/kurinyj-popkorn-serving.webp` | product-kurinyj-popkorn.html | `5eb9ff8756a4` |
| `assets/catalogue/kurinyj-popkorn.webp` | product-kurinyj-popkorn.html | `4750a4b789c1` |
| `assets/catalogue/naggetsy-dinozavry-serving.webp` | product-naggetsy-dinozavry.html | `368e16a3005b` |
| `assets/catalogue/naggetsy-dinozavry.webp` | product-naggetsy-dinozavry.html | `4f10f8de9bd8` |
| `assets/catalogue/naggetsy-kurinye-s-syrom-serving.webp` | product-naggetsy-kurinye-s-syrom.html | `c8a342ffb4f7` |
| `assets/catalogue/naggetsy-kurinye-s-syrom.webp` | product-naggetsy-kurinye-s-syrom.html | `469c308fe903` |
| `assets/catalogue/naggetsy-kurinye-serving.webp` | product-naggetsy-kurinye.html | `a21a9a44ef20` |
| `assets/catalogue/naggetsy-kurinye.webp` | product-naggetsy-kurinye.html | `c72d8f0df15c` |
| `assets/catalogue/naggetsy-ostrye-serving.webp` | product-naggetsy-ostrye.html | `c020937eb339` |
| `assets/catalogue/naggetsy-ostrye.webp` | product-naggetsy-ostrye.html | `8e0ce90f8493` |
| `assets/catalogue/naggetsy-s-indeykoy-fitnes-serving.webp` | product-naggetsy-s-indeykoy-fitnes.html | `4789553ae033` |
| `assets/catalogue/naggetsy-s-indeykoy-fitnes.webp` | product-naggetsy-s-indeykoy-fitnes.html | `26bb87bae008` |
| `assets/catalogue/stripsy-serving.webp` | product-stripsy.html | `e1adf5e6726b` |
| `assets/catalogue/stripsy.webp` | product-stripsy.html | `f07d300cfb1f` |

### Шрифты

| Текущий путь | Использование | SHA-256, первые 12 знаков |
|---|---|---|
| `assets/fonts/Caveat-wght.woff2` | общие стили / head | `39a54b4ed307` |
| `assets/fonts/Onest-wght.woff2` | общие стили / head | `c986a41a2baa` |
| `assets/fonts/RobotoFlex-Protein.woff2` | общие стили / head | `044509f713cf` |
| `assets/fonts/Rubik-wght.woff2` | общие стили / head | `c3fb5e71208f` |

### Логотип и интерфейсная графика

| Текущий путь | Использование | SHA-256, первые 12 знаков |
|---|---|---|
| `assets/favicon.svg` | общие стили / head | `b5bf253063ce` |
| `assets/icons/arrow-left.svg` | index.html | `12af90f1bb49` |
| `assets/icons/arrow-right.svg` | index.html | `7e602a26d53e` |
| `assets/icons/arrow-up-right.svg` | 23 страниц | `b7d952b0b6fb` |
| `assets/icons/arrow-up.svg` | 23 страниц | `c0a58436629c` |
| `assets/icons/menu-2.svg` | 23 страниц | `bcef199c5e53` |
| `assets/icons/x.svg` | 23 страниц | `935078536041` |
| `assets/logo-reference.webp` | 23 страниц | `43e13b95e3cc` |

Оригинальные 14 фото подачи перечислены по фактически подключённым файлам `*-serving.webp`, а не по предположению о полном каталоге. Два концепта не имеют такого документального ряда. Режим srcset позволяет браузеру выбрать подходящий размер одного изображения; это не дополнительные варианты персонажа или упаковки.
