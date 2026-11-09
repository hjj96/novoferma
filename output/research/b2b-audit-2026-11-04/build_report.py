"""Build the complete GitHub-readable audit and an offline HTML copy. Stdlib only."""
from pathlib import Path
from html import escape
import json, re, base64, hashlib
BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[2]
def read(name): return json.loads((BASE/name).read_text())
def save(name,x): (BASE/name).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def vals(x): return '\n'.join('- '+str(v) for v in x) if isinstance(x,list) else str(x)
def link_sources(ids, sources):
    byid={s.get('id'):s for s in sources}
    return ', '.join('['+str(i)+']('+byid[i]['url']+')' if i in byid and byid[i].get('url') else str(i) for i in ids)
names = [
('01-home-desktop.png','Первое впечатление','1280×720','Главная','Выразительная еда и характер; B2B предложение и доказательства не видны в первом экране. Декор касается навигации.','Нужна доработка'),
('02-partners-entry-desktop.png','Вход в раздел партнёров','1280×720','Партнёрам','Направление найдено; лозунг и персонаж сильнее конкретного предложения поставщика.','Частично'),
('03-offers-and-specs.png','Фасовки и предложения','1280×720','Партнёрам','Таблица масс доступна. Розница и HoReCa объединены; процесса СТМ и закупочной спецификации недостаточно.','Частично'),
('04-stm-request.png','Переход к запросу СТМ','1280×720','Партнёрам','Действие корректно выбирает СТМ. Интерфейс готовит письмо; входящий лид не подтверждается.','Работает с ограничениями'),
('05-form-required-fields.png','Обязательные поля','1280×720','Партнёрам','Пустое копирование блокируется, фокус получает компания. Внешнее письмо не отправлялось.','Работает'),
('06-catalogue-desktop.png','Вход в каталог','1280×720','Каталог','Фильтры понятны, но первый ряд почти ниже экрана.','Частично'),
('07-catalogue-grid.png','Продуктовая витрина','1280×720','Каталог','Упаковочная семья и текстовые массы помогают; закупочные и пищевые характеристики не сравнить.','Хорошая основа'),
('08-product-passport.png','Серийный товар','1280×720','Котлеты куриные','Понятны имя и масса; состав и приготовление предлагается уточнить. Основной CTA розничный.','Нужна доработка'),
('09-fiber-concept.png','Фибрики и клетчатка','1280×720','Фибрики','Статус концепта виден. Количество клетчатки и серийная готовность не установлены.','Честный концепт'),
('10-about-company.png','Кто стоит за брендом','1280×720','О нас','Компания и категория названы; мало оснований для квалификации поставщика.','Частично'),
('11-about-proof.png','Упаковка и производство','1280×720','О нас','Фото упаковки подписано. Текст об оборудовании не заменяет производственный репортаж и документы.','Нужна доказательная часть'),
('12-purchase-links.png','Розничный путь','1280×720','Где купить','Есть ссылки на продавцов и ограничения; розничный раздел не заменяет оптовое предложение.','Работает в своём назначении'),
('13-home-mobile.png','Первый экран телефона','390×844','Главная','Название и действие читаются, вкладки подписаны; закупочный вход скрыт в меню.','Хорошая мобильная основа'),
('14-mobile-navigation.png','Мобильное меню','390×844','Главная','Названия разделов ясны, но нет прямого пункта СТМ/опт.','Работает, можно усилить'),
('15-partners-mobile.png','Мобильный B2B вход','390×844','Партнёрам','Композиция помещается, CTA заметен; смысл предложения остаётся общим.','Частично'),
('16-stm-mobile.png','Мобильная форма СТМ','390×844','Партнёрам','СТМ выбран, форма в одну колонку; заголовок и контакты занимают большую часть экрана перед полями.','Работает с трением'),
('17-product-mobile.png','Товар на телефоне','390×844','Котлеты куриные','Название перед упаковкой, факты и CTA доступны; пищевой паспорт отсутствует.','Частично'),
('18-reference-kazan-stm.png','Сравнение: вход в СТМ','1280×720','Казанские Деликатесы','Прямое название услуги и фото производства. Не основание переносить чужие claims или стиль.','Референс'),
('19-reference-kazan-process.png','Сравнение: этапы проекта','1280×720','Казанские Деликатесы','Видна последовательность от задания к образцам. Реальное исполнение не проверялось.','Референс'),
('20-reference-cp-manufacturing.png','Сравнение: производственный контекст','1280×720','CP Foods UK','Операционная тема и названные каналы связываются с производственным изображением.','Референс'),
('21-reference-tyson-product.png','Сравнение: продукт и идентификация','1280×720','Tyson Foodservice','Аппетитная подача соседствует с Product#/GTIN; необязательно копировать объём навигации.','Референс'),
('22-reference-tyson-packaging.png','Сравнение: закупочная упаковка','1280×720','Tyson Foodservice','Показаны вес, габариты, схема укладки и frozen статус. Чужие значения не переносятся.','Референс'),
('23-reference-shmpk.png','Сравнение: производитель','1280×720','Щёлковский МПК','Позиционирование производителя явно; тёмную премиальную палитру копировать не требуется.','Референс'),
('24-reference-shmpk-quality.png','Сравнение: контроль качества','1280×720','Щёлковский МПК','Отдельный путь к контролю сырья и производственной безопасности; сертификаты независимо не валидировались.','Референс'),
('25-delta-partners-mobile.png','Дельта05.11: компактный B2B вход','390×844','Партнёрам','Повторный просмотр обновлённой композиции: CTA рядом с персонажем, больше следующего блока в экране.','Улучшено05.11'),
('26-delta-catalogue-mobile.png','Дельта05.11: карточки без стрелок','390×844','Каталог','Название выше метаданных, масса выделена, одна ссылка сохранена. Hover эффект проверяется отдельно.','Улучшено05.11'),
]
urls={**{i:'http://127.0.0.1:8765/output/concept/'+p for i,p in [(1,'index.html'),(2,'partners.html'),(3,'partners.html'),(4,'partners.html#partner-contact'),(5,'partners.html#partner-contact'),(6,'catalogue.html'),(7,'catalogue.html'),(8,'product-kotlety-kurinye.html'),(9,'product-fibriki.html'),(10,'about.html'),(11,'about.html'),(12,'where-to-buy.html'),(13,'index.html'),(14,'index.html'),(15,'partners.html'),(16,'partners.html#partner-contact'),(17,'product-kotlety-kurinye.html')]},18:'https://kazandelikates.tatar/stm',19:'https://kazandelikates.tatar/stm#etap',20:'https://www.cpfoods.co.uk/manufacturing/',21:'https://www.tysonfoodservice.com/products/tyson/chicken/nuggets-%26-specialty-shapes/00023700061669',22:'https://www.tysonfoodservice.com/products/tyson/chicken/nuggets-%26-specialty-shapes/00023700061669',23:'https://shmpk.ru/',24:'https://shmpk.ru/quality_control',25:'http://127.0.0.1:8765/output/concept/partners.html',26:'http://127.0.0.1:8765/output/concept/catalogue.html'}
shots=[]
for i,(file,title,size,page,note,health) in enumerate(names,1):
    f=BASE/'screens'/file
    assert f.is_file(),f
    shots.append(dict(step=i,file='screens/'+file,title=title,viewport=size,page=page,url=urls[i],note=note,health=health,accepted=True,capturedOn='2026-11-04' if i<=24 else '2026-11-05',sha256=hashlib.sha256(f.read_bytes()).hexdigest(),bytes=f.stat().st_size))
save('screenshot-manifest.json',dict(capturedOn='2026-11-04–2026-11-05',reviewedOn='2026-11-05',method='CUA screenshot → save exact PNG → read saved file → visually inspect; no screenshot synthesis',screens=shots,blockers=[dict(url='https://novoferma.ru/',state='Browser navigation failed, no accepted visual evidence; web text extraction succeeded.',implication='No claim of a production visual audit or production downtime.')]))
technical=read('technical-commercial.json'); visual=read('visual-b2b-second-pass.json'); glob=read('global-research.json'); rus=read('russia-research.json')
md=(BASE/'strategy.md').read_text()
md+='\n\n## 18. Свежие экраны: пошаговая проверка\n\nКадры 1–17 — срез проекта от4ноября; 18–24 — выбранные функции референсов; 25–26 — повторный просмотр дельты от5ноября. Снимки не подтверждают фактическое качество производства и состав продукта.\n\n'
md+='| Шаг | Задача | Состояние |\n| --- | --- | --- |\n'
for s in shots:md+=f"| {s['step']} | [{s['title']}]({s['file']}) | {s['health']} |\n"
for s in shots:
    md+=f"\n### Экран {s['step']}. {s['title']}\n\n{s['page']} · {s['viewport']} · {s['health']}.\n\n![Экран {s['step']}: {s['title']}]({s['file']})\n\n{s['note']}\n\n[Источник экрана]({s['url']})\n"
md+='\n## 19. Подробные технические и коммерческие замечания\n\n18 карточек. Приоритет — важность готовности B2B пути, а не измеренная потеря выручки. Факты и коммерческие гипотезы разделены.\n'
for f in technical['findings']:
    md+=f"\n### {f['id']} · {f['priority']} · {f['title']}\n\n**Статус доказательства:** {f.get('classification','')}\n\n**Наблюдение:** {f.get('fact','')}\n\n**Возможное влияние:** {f.get('commercialEffectHypothesis','')}\n\n**Рекомендация:** {f.get('recommendation','')}\n\n**Приёмка:**\n\n{vals(f.get('acceptance',[]))}\n\n**Кодовые основания:**\n\n"
    for e in f.get('evidence',[]):
        md+=f"- [{e['path']}:{e.get('line','')}]({'../../../'+e['path']})\n"
md+='\n## 20. Независимый второй визуальный проход\n\n20 карточек по восьми свежим кадрам. Это второй экспертный просмотр, а не независимое исследование поведения покупателей. Часть тем пересекается с предыдущим разделом; складывать карточки как 38 независимых причин потерь нельзя.\n'
for f in visual['findings']:
    md+=f"\n### {f['id']} · {f['priority']} · {f['title']}\n\n**Видно на кадре:** {f.get('observation','')}\n\n**Эффект по экспертной оценке:** {f.get('effect','')}\n\n**Рекомендация:** {f.get('recommendation','')}\n\n**Приёмка:** {vals(f.get('acceptance',''))}\n\n"
    md+='Кадры: '+', '.join('['+Path(p).stem+']('+p+')' for p in f.get('screenshots',[]))+'\n'
md+='\n## 21. Россия: производители, рынок и границы сравнения\n\nПять досье, включая ограниченное доступом. Это текстовое исследование публичного предложения; визуально рассмотрены отдельно снятые страницы. Полный набор — [russia-research.json](russia-research.json).\n'
md+='\n### Границы российского рынка\n\n'+rus['market']['targetDefinition']+'\n\n'+rus['market']['targetMarketSizeReason']+'\n\n'+vals(rus['market']['boundaries'])+'\n'
for e in rus['market']['evidence']:
    md+=f"\n#### {e['id']} · {e['publisher']}: {e['category']}\n\nПубликация: {e['publicationDate']}.\n\n"
    for metric in e['metrics']:
        md+='- '+metric['period']+': '+str(metric.get('operator',''))+str(metric['value'])+' '+metric['unit']+' · '+metric['kind']+'.\n'
    md+='\n**Охват:** '+e['coverage']+'\n\n**Применимость:** '+e['useForNovoferma']+'\n\n'+link_sources(e['sourceIds'],rus['sources'])+'\n'
for d in rus['dossiers']:
    md+=f"\n### {d['name']}\n\n{d.get('scope','')} · {d.get('fit','')}\n\n[Входная страница]({d.get('entryUrl','')})\n"
    for key,label in [('offer','Предложение'),('quality','Основания качества'),('passport','Продуктовые данные'),('cta','Следующее действие')]:
        md+='\n**'+label+':**\n\n'
        for f in d.get(key,[]):
            md+='- '+f['text']+' '+link_sources(f.get('sourceIds',[]),rus['sources'])+'\n'
    md+='\n**Применить:**\n\n'+vals(d.get('take',[]))+'\n\n**Не копировать автоматически:**\n\n'+vals(d.get('doNotCopy',[]))+'\n\n**Не установлено:**\n\n'+vals(d.get('unknowns',[]))+'\n'
md+='\n\n## 22. Международные досье и измеряемые тренды\n\nЭто пять разных референсов: птица/foodservice, бренд/процесс, разработка ассортимента, контрактные операции и смежная СТМ. Их присутствие в сделках Новофермы не установлено.\n'
for d in glob['dossiers']:
    md+=f"\n### {d['name']}\n\n{d['relationship']}\n\n**Покупатель:** {'; '.join(d['buyers'])}.\n\n**Что заявлено/наблюдено:**\n\n"
    for f in d['facts']:md+='- '+f['statement']+' '+link_sources(f['sources'],glob['sources'])+'\n'
    md+=f"\n**Паспорт и CTA:** {d['catalogue_and_passport']}\n\n**СТМ:** {d['private_label_process']}\n\n**Применить:**\n\n{vals(d['apply_to_novoferma'])}\n\n**Не копировать автоматически:**\n\n{vals(d['do_not_copy'])}\n\n**Пределы:** {d['limitations']}\n"
md+='\n### Измеряемые международные сигналы\n'
for tr in glob['trends']:
    md+=f"\n#### {tr['id']} · {tr['topic']}\n\n**Публикация:** {tr['published']}. **Измерение:** {tr['measurement_period']}. **Кого/что измеряли:** {tr['population']}\n\n{vals(tr['facts'])}\n\n**Вывод для гипотезы:** {tr['interpretation']}\n\n**Применение:** {tr['application']}\n\n**Ограничение:** {tr['do_not_claim']}\n\n{link_sources(tr['sources'],glob['sources'])}\n"
md+='\n## 23. Источники, метод и повторяемость\n\nИспользованы текущий Git-проект, свежий захват браузера, код, открытые первичные страницы производителей, отраслевых организаций и официальные стандарты. Прямых данных CRM, кабинета аналитики, входящей почты и интервью клиентов нет. Закрытые отчёты не прочитаны и их содержимое не приписывается этому аудиту.\n\n'
md+='Существующие проверки: 21/21 сценарий Node VM; статическая структура 22 страниц и 1442 локальных ссылок без ошибок. Это не полный браузерный регрессионный тест и не проверка доставки заявок. Файлы runtime в ходе этого аудита не менялись.\n\n'
md+='Неполученный визуальный захват production — явно названное ограничение. Ошибка одной среды не доказывает массовую недоступность сайта. Сохраняются существенные неизвестные о продажах, рецептуре, производственных условиях и исполнении конкурентов. Аудит определяет, как их проверять; не выдаёт их отсутствие за отрицательный факт.\n\n'
sources=[]
for x in [glob,rus,technical]:
    ss=x.get('sources',[])
    if isinstance(ss,dict): ss=list(ss.values())
    for s in ss:
        if isinstance(s,dict) and s.get('url'):sources.append(s)
sources += [
dict(title='Публичный Novoferma: текстовое извлечение',url='https://novoferma.ru/',accessed_at='2026-11-04'),
dict(title='NN/G: B2B usability — исследование 2006, базовые принципы, не тренд 2026',url='https://www.nngroup.com/articles/b2b-usability/',accessed_at='2026-11-04'),
dict(title='NN/G: About Us, 2019',url='https://www.nngroup.com/articles/about-us-information-on-websites/',accessed_at='2026-11-05'),
dict(title='NN/G: Trustworthiness in Web Design, 2016',url='https://www.nngroup.com/articles/trustworthy-design/',accessed_at='2026-11-05'),
dict(title='W3C WCAG 2.2',url='https://www.w3.org/TR/WCAG22/',accessed_at='2026-11-04'),
dict(title='Google: оценка CWV и p75',url='https://support.google.com/webmasters/answer/9205520?hl=en-EN',accessed_at='2026-11-04'),
dict(title='EEC: первичный текст ТР ТС 022/2011; консолидация редакции не установлена',url='https://eec.eaeunion.org/upload/medialibrary/9db/TrTsPishevkaMarkirovka.pdf',accessed_at='2026-11-04'),
dict(title='BFFF Business Conference 2026: открытые выводы',url='https://bfff.co.uk/industry-leaders-come-together-at-the-bfff-business-conference-2026/',accessed_at='2026-11-05'),
]
unique={s['url']:s for s in sources}
save('sources.json',list(unique.values()))
for i,s in enumerate(unique.values(),1):
    title=s.get('title',s.get('name',s['url']));date=s.get('accessed_at',s.get('accessedAt',s.get('checkedAt','04–05.11.2026')))
    md+=f"{i}. [{title}]({s['url']}) — доступ: {date}.\n"
md+='\n## 24. Карта файлов полного аудита\n\n- [План и проверка требований](work-plan.json).\n- [Скриншоты и состояния](screenshot-manifest.json).\n- [Технические замечания и воронка](technical-commercial.json).\n- [Второй визуальный разбор](visual-b2b-second-pass.json).\n- [Российское исследование](russia-research.json).\n- [Международное исследование](global-research.json).\n- [Реестр источников](sources.json).\n- [Автономный HTML](audit.html).\n- [Генератор отчёта](build_report.py).\n\nПолные чужие страницы, cookies, браузерные журналы и временные загрузки не входят в публикацию. Снимки используются как иллюстрации анализа интерфейса, с адресом источника.\n'
md=re.sub(r'(?<=[А-Яа-яёЁ])(?=\d)', ' ', md)
md=re.sub(r'(?<=\d)(?=[А-Яа-яёЁ])', ' ', md)
(BASE/'audit.md').write_text(md)
# Restrained offline HTML: exactly the accepted PNGs, not recreated illustrations.
def inline(t):
    t=escape(t)
    t=re.sub(r'!\[([^]]*)\]\(([^)]+)\)',lambda m:'<figure><img loading="lazy" src="'+image_uri(m[2])+'" alt="'+m[1]+'"><figcaption>'+m[1]+'</figcaption></figure>',t)
    t=re.sub(r'\[([^]]+)\]\(([^)]+)\)',r'<a href="\2">\1</a>',t)
    t=re.sub(r'\*\*([^*]+)\*\*',r'<strong>\1</strong>',t)
    return re.sub(r'`([^`]+)`',r'<code>\1</code>',t)
def image_uri(path):
    p=BASE/path
    return 'data:image/png;base64,'+base64.b64encode(p.read_bytes()).decode() if p.is_file() and p.suffix=='.png' else path
lines=md.splitlines(); out=[]; toc=[]; used={}; i=0
while i<len(lines):
    line=lines[i]
    if not line.strip():i+=1;continue
    h=re.match(r'^(#{1,6}) (.+)',line)
    if h:
        level=len(h[1]);title=h[2];ident=re.sub(r'[^\w-]+','-',title.lower()).strip('-')
        if title.startswith('Экран '):ident='screen-'+title.split('.')[0].split()[-1]
        used[ident]=used.get(ident,0)+1
        if used[ident]>1:ident+='-'+str(used[ident])
        if level==2:toc.append((ident,title))
        out.append(f'<h{level} id="{ident}">'+inline(title)+f'</h{level}>');i+=1;continue
    if line.startswith('|'):
        rows=[]
        while i<len(lines) and lines[i].startswith('|'):
            cells=lines[i].strip().strip('|').split('|')
            if not all(re.fullmatch(r'\s*:?-+:?\s*',c) for c in cells):rows.append(cells)
            i+=1
        out.append('<div class="table-wrap"><table>')
        for n,row in enumerate(rows):
            tag='th' if n==0 else 'td';out.append('<tr>'+''.join('<'+tag+'>'+inline(c.strip())+'</'+tag+'>' for c in row)+'</tr>')
        out.append('</table></div>');continue
    if line.startswith('- ') or re.match(r'^\d+\. ',line):
        ordered=bool(re.match(r'^\d+\. ',line));tag='ol' if ordered else 'ul';out.append('<'+tag+'>')
        while i<len(lines) and (lines[i].startswith('- ') or re.match(r'^\d+\. ',lines[i])):
            t=re.sub(r'^(?:- |\d+\. )','',lines[i]);out.append('<li>'+inline(t)+'</li>');i+=1
        out.append('</'+tag+'>');continue
    if line.startswith('!['):out.append(inline(line));i+=1;continue
    paragraph=[line];i+=1
    while i<len(lines) and lines[i].strip() and not re.match(r'^(#|\||- |\d+\. |!\[)',lines[i]):
        paragraph.append(lines[i]);i+=1
    out.append('<p>'+inline(' '.join(paragraph))+'</p>')
style="""*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:#f5f6f8;color:#242b35;font:17px/1.7 system-ui,-apple-system,sans-serif}main{max-width:1120px;margin:auto;background:white;padding:52px 60px 90px}h1{font-size:42px;line-height:1.16;letter-spacing:-.03em}h2{margin-top:70px;font-size:29px;line-height:1.3;border-top:1px solid #e4e7ed;padding-top:26px}h3{margin-top:42px;font-size:23px;line-height:1.4}h4{font-size:20px}p{max-width:94ch}p,li,a{overflow-wrap:anywhere}a{color:#195ac5;text-underline-offset:3px}code{font-size:.88em;background:#eef1f5;padding:2px 5px;border-radius:4px;overflow-wrap:anywhere}li{margin-block:8px}.table-wrap{overflow:auto;margin-block:28px}table{border-collapse:collapse;width:100%;font-size:14px;line-height:1.55}th,td{padding:14px 16px;text-align:left;vertical-align:top;border-bottom:1px solid #e4e7ed}th{background:#eef1f5;font-weight:700}figure{margin:24px 0 14px}figure img{display:block;max-width:100%;max-height:850px;width:auto;height:auto;margin:auto;border:1px solid #e4e7ed;border-radius:8px}figcaption{color:#626e7c;font-size:13px;text-align:center;margin-top:8px}.contents{padding:24px;background:#eef1f5;border-radius:8px}.contents summary{font-weight:650;cursor:pointer;min-height:32px}.contents a{display:block;padding:4px 0}footer{font-size:13px;color:#626e7c;margin-top:60px}@media(max-width:700px){main{padding:24px 20px 50px}h1{font-size:30px}h2{font-size:25px;margin-top:48px}table{min-width:650px}}@media print{body,main{background:white}main{padding:0;max-width:none}.contents{display:none}h2,h3{break-after:avoid}figure,table{break-inside:avoid}a{color:inherit}figure img{max-height:700px}}"""
html='<!doctype html><html lang="ru"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Новоферма — B2B аудит 04–05.11.2026</title><style>'+style+'</style><main><details class="contents"><summary>Содержание · 24 раздела</summary>'+''.join('<a href="#'+id+'">'+escape(t)+'</a>' for id,t in toc)+'</details>'+''.join(out)+'<footer>Исследование 04.11.2026 · сведение 05.11.2026 · Новоферма · экспертный аудит, ограничения и источники внутри отчёта.</footer></main></html>'
(BASE/'audit.html').write_text(html)
print(json.dumps(dict(markdownBytes=len(md.encode()),htmlBytes=len(html.encode()),words=len(md.split()),screens=len(shots),sources=len(unique)),ensure_ascii=False))

