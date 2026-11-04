# -*- coding: utf-8 -*-
from pathlib import Path
from html import escape, unescape
from html.parser import HTMLParser
import re, json

ROOT = Path(__file__).resolve().parent
main = (ROOT/'main-section.html').read_text()
visual = (ROOT/'visual-section.html').read_text()
technical = (ROOT/'technical-section.html').read_text()
research = (ROOT/'research-section.html').read_text()

# Keep the independent review as evidence; avoid counting its repeated findings twice.
for num in ['01','02','04','12','15','16','20']:
    visual = re.sub(r'<article class="finding"[^>]*id="ed-'+num+r'">.*?</article>', '', visual, flags=re.S)
visual = visual.replace('22 предметных замечания по страницам', '15 дополнительных замечаний по страницам')
visual = visual.replace('<div class="findings-list">', '<p class="note">Ещё семь замечаний независимого прохода подтвердили U01, U02, U04–U07 и проверку разреза; они не продублированы ниже. Полные 22 записи сохранены в <a href="editorial-review.txt">исходном разборе</a>.</p><div class="findings-list">')
research = research.replace('<a href="screens/42-fishwife-home.jpg">снимок главной</a>. Реальная доступность не установлена.', 'визуальный кадр перекрыт cookie-панелью и исключён из оценки композиции. Реальная доступность не установлена.')
research = research.replace('screens/45-this-product-facts.jpg', 'screens/49-this-product-nutrition.jpg')
research = research.replace('Осмысленное движение — Canva', 'Осмысленное движение — вывод аудитора')
research = research.replace('https://www.indilight.ru/', 'https://indilight.ru/')

def sections(text):
    return re.findall(r'<section\b.*?</section>', text, flags=re.S)

parts={re.search(r'<section id="([^"]+)"', s).group(1):s for fragment in [main,visual,technical,research] for s in sections(fragment)}
order=['verdict','method','journeys','motion','visual','page-review','technical','standards','benchmarks','trends','roadmap','conclusion']
names=['Вердикт','Охват и сценарии','Путь покупателя','Анимации','Визуальная система','Разбор страниц','Техника и скорость','Доступность','9 брендов','Тренды 2026','План исправлений','Итог']
body='\n'.join(parts[k] for k in order)

captions={
'01':'Главная целиком: сравните громкость последовательных блоков.',
'04':'Каталог: согласованные упаковки, 14 SKU и 2 концепта в одной сетке.',
'05':'Покупка: выбранные Фибрики сохраняются, следующий шаг — письмо.',
'06':'Пустой город: встроенная валидация и видимый фокус.',
'07':'Товар: основные факты есть, состав и приготовление отложены до этикетки.',
'08':'О компании: подача еды рядом с рассказом о производстве.',
'09':'B2B: спокойная типографика и деловая подача.',
'10':'СТМ: выбранное направление в форме.',
'11':'Копирование обращения: подтверждённое состояние с синтетическими тестовыми данными; письмо не отправлялось.',
'12':'Контакты: большой герой и два направления связи.',
'13':'Мобильная главная: фрикадельки.',
'14':'Мобильная главная: наггетсы, полный первый экран.',
'15':'Мобильная главная: Фибрики и claim «Белок + клетчатка».',
'16':'Мобильная главная: Люля мини.',
'17':'Мобильное меню; Escape и возврат фокуса проверены.',
'18':'Белковый блок: синтетически сжатый заголовок и разрез продукта.',
'19':'Мобильная главная после раскрытия всех блоков.',
'20':'Мобильный каталог: сравнение похожих упаковок.',
'21':'Первый экран товара с длинным названием: изображение занимает приоритет.',
'22':'Мобильная товарная страница целиком.',
'23':'Мобильная B2B-страница.',
'24':'Мобильные контакты: большая декоративная пауза до реквизитов.',
'25':'Мобильная покупка: инструкция о письме ниже крупного заголовка.',
'26':'320 CSS px: основной сценарий помещается по ширине.',
'27':'768 CSS px: промежуточная композиция.',
'28':'1024 CSS px: еда пересекает область ссылки «Контакты».',
'40':'Graza: главный экран, визуальное наблюдение 16.10.2026.',
'41':'Graza: карточки объясняют назначение, объём и характер масла.',
'43':'Вязанка: последовательный мир персонажей; композиция насыщеннее Новофермы.',
'44':'THIS: выразительный верх товарной страницы.',
'49':'THIS: рядом с образом есть состав и таблица пищевой ценности.',
'46':'Индилайт: продуктовая кампания на главной.',
'47':'Индилайт: подтверждённый список каналов покупки; наличие конкретного SKU не проверялось.',
'48':'Little Moons: разрез объясняет устройство продукта; slider не тестировался.'}
gallery=[]
for num,caption in captions.items():
    file=next((ROOT/'screens').glob(num+'-*.jpg'))
    rel='screens/'+file.name
    gallery.append(f'<figure><a href="{rel}" target="_blank"><img src="{rel}" loading="lazy" alt="Экран {num}. {escape(caption)}"></a><figcaption><strong>{num}</strong> {escape(caption)} <a href="{rel}">Открыть целиком ↗</a></figcaption></figure>')
gallery_section='<section id="evidence"><p class="eyebrow">11 / Визуальные доказательства</p><h2>Экраны и проверенные состояния</h2><p>Превью намеренно ограничены по высоте. Нажмите на изображение, чтобы увидеть полный оригинал. Здесь 34 ключевых кадра; ещё 3 принятых вспомогательных кадра доступны по ссылкам в отчёте и в папке screens. Кадр 42 с перекрытием исключён.</p><div class="gallery">'+''.join(gallery)+'</div></section>'
body += gallery_section
body += '<section id="files"><h2>Материалы аудита</h2><p><a href="report.txt">Текстовая копия отчёта</a> · <a href="findings.json">Реестр замечаний JSON</a> · <a href="snapshot-manifest.json">Версия и контрольные суммы</a> · <a href="technical-findings.json">Технические доказательства</a> · <a href="technical-inventory.json">Все 20 страниц</a> · <a href="technical-form-check.json">Воспроизведение ошибки формы</a> · <a href="research.txt">Исследование конкурентов</a> · <a href="editorial-review.txt">Независимый визуальный разбор</a> · <a href="sources.json">Реестр источников</a></p><p>Исходный сайт сохранён в snapshot для воспроизводимости. Изменения сайта и отправка обращений не выполнялись. Источники проверялись 16.10.2026; содержимое внешних сайтов может измениться.</p></section>'

# Linkable identifiers on every finding.
counter=0
def add_id(m):
    global counter
    tag=m.group(0)
    if ' id=' not in tag:
        counter+=1
        tag=tag[:-1]+f' id="finding-{counter}">'
    return tag
body=re.sub(r'<(?:article|details) class="finding"[^>]*>',add_id,body)
body=re.sub(r'<h3>([UT]\d{2}) · (?!P\d)(.*?)</h3>',r'<h3>\1 · \2</h3>',body)

nav=''.join(f'<a href="#{key}"><span>{i:02d}</span>{name}</a>' for i,(key,name) in enumerate(zip(order,names),1))+'<a href="#evidence"><span>13</span>Экраны</a><a href="#files"><span>14</span>Материалы</a>'
css='''
:root{--ink:#232722;--muted:#5c655c;--line:#d8ded4;--paper:#f4f6f0;--accent:#a4371d;--soft:#e8eddf}*{box-sizing:border-box}html{scroll-behavior:auto;scroll-padding-top:26px}body{margin:0;background:var(--paper);color:var(--ink);font:16px/1.7 -apple-system,BlinkMacSystemFont,"Segoe UI",Arial,sans-serif}a{color:#983719;text-underline-offset:3px}a:hover{color:#67220f}a:focus-visible,button:focus-visible,input:focus-visible{outline:3px solid #215fd0;outline-offset:4px}h1,h2,h3,p{overflow-wrap:break-word}h1,h2,h3{line-height:1.15;letter-spacing:-.035em}h1{font-size:clamp(44px,6vw,88px);max-width:880px;margin:28px 0}h2{font-size:clamp(28px,3.2vw,46px);margin:10px 0 28px;max-width:900px}h3{font-size:23px;margin:32px 0 15px;letter-spacing:-.02em}p,li{max-width:100ch}p{margin:15px 0}li{margin:9px 0}code{font-size:.86em;background:#e6eadd;padding:2px 5px;border-radius:4px;overflow-wrap:anywhere}aside{position:fixed;left:0;top:0;width:230px;height:100vh;padding:32px 22px;background:#e8eddf;border-right:1px solid #ccd3c3;overflow:auto}.brand{font-weight:750;font-size:17px;letter-spacing:-.03em}.brand small{display:block;font-weight:400;letter-spacing:.05em;font-size:10px;margin-top:4px;color:#59644e}.nav{display:grid;gap:2px;margin-top:32px}.nav a{display:flex;gap:10px;text-decoration:none;padding:7px 0;font-size:13px;color:#32402d}.nav a span{font-size:10px;color:#707b65;padding-top:3px}.nav a:hover{color:var(--accent)}main{margin-left:230px;max-width:1500px;padding:50px 64px 100px}.cover{padding:18px 0 50px;border-bottom:1px solid var(--line)}.eyebrow{text-transform:uppercase;letter-spacing:.13em;font-weight:650;font-size:11px;color:#6c755e;margin:0}.sub{font-size:20px;max-width:790px;color:#505b4a}.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-top:42px}.stat{padding:18px 0;border-top:2px solid #adb99d}.stat strong{display:block;font-size:34px;line-height:1.3;letter-spacing:-.04em}.stat span{font-size:12px;color:var(--muted)}section{padding:54px 0 25px;border-bottom:1px solid var(--line)}.lead{font-size:21px;line-height:1.6}.callout{background:#e5ebdc;border-left:4px solid #66764f;padding:24px 28px;font-size:18px;margin:28px 0}.note{font-size:13px;color:#5e6656}.table-wrap{overflow-x:auto;margin:25px 0;border:1px solid var(--line);border-radius:10px;background:#fbfcf8}table{border-collapse:collapse;width:100%;min-width:620px;font-size:13px;line-height:1.55}th,td{padding:16px 18px;vertical-align:top;text-align:left;border-bottom:1px solid var(--line)}thead th{font-size:11px;text-transform:uppercase;letter-spacing:.055em;background:#e8eddf}tbody th{font-weight:650}caption{padding:15px;text-align:left;color:#5d6755;font-size:12px}.status{font-weight:650}.good{color:#3c653c}.warn{color:#7c5817}.bad{color:#a4371d}.finding{border:1px solid #d5dbcf;background:#fffef9;border-radius:12px;padding:25px 28px;margin:18px 0}.finding[data-priority=P1]{border-left:5px solid #af4829}.finding[data-priority=P2]{border-left:5px solid #a58a4e}.finding[data-priority=P3]{border-left:5px solid #8d9f82}.finding h3{font-size:22px;margin:0 0 17px}.finding p{font-size:15px;margin:11px 0}summary{cursor:pointer}summary h3{display:inline}details.finding>p:first-of-type{margin-top:20px}.two-col{display:grid;grid-template-columns:1fr 1fr;gap:20px}.panel{padding:20px 25px;background:#e9eddf;border-radius:12px}.panel h3{margin-top:5px}.panel ul{padding-left:20px}.filter{display:flex;flex-wrap:wrap;gap:10px;align-items:center;padding:18px 0}.filter button{padding:9px 15px;background:#fffef9;border:1px solid #c8d0be;border-radius:30px;color:#283321;font:inherit;font-size:13px;cursor:pointer}.filter button[aria-pressed=true]{background:#2c3d26;color:white}.filter input{min-width:180px;flex:1;padding:11px 14px;border:1px solid #c8d0be;border-radius:8px;background:#fffef9;font:inherit;font-size:13px}.filter-status{font-size:12px;color:var(--muted)}[hidden]{display:none!important}.gallery{display:grid;grid-template-columns:repeat(3,1fr);gap:20px}.gallery figure{margin:0;border:1px solid var(--line);border-radius:10px;overflow:hidden;background:#fffef9}.gallery img{width:100%;height:230px;object-fit:cover;object-position:top;display:block;background:#e2e8d7}.gallery figcaption{padding:15px;font-size:12px;line-height:1.6}.gallery figcaption strong{display:block;color:var(--accent);font-size:18px}.gallery figcaption a{display:block;font-size:11px;margin-top:9px}.source-list{background:#e9eddf;padding:22px 25px;border-radius:10px;margin:25px 0}.source-list li{font-size:13px}.footer-note{font-size:12px;color:#727c68;margin-top:40px}.mobile-nav{display:none}.print-btn{border:0;padding:0;background:transparent;text-decoration:underline;font:inherit;font-size:12px;color:#5e6656;cursor:pointer} @media(max-width:1100px){aside{width:195px;padding:25px 17px}main{margin-left:195px;padding:35px}.gallery{grid-template-columns:1fr 1fr}}@media(max-width:760px){aside{display:none}main{margin:0;padding:25px 20px}h1{font-size:48px}.sub,.lead{font-size:18px}.stats{grid-template-columns:1fr 1fr}.mobile-nav{display:block;background:#e8eddf;padding:16px;border-radius:10px;margin:25px 0}.mobile-nav a{display:inline-block;font-size:12px;margin:5px 10px 5px 0}.mobile-nav span{display:none}.two-col{grid-template-columns:1fr}.gallery{grid-template-columns:1fr 1fr;gap:10px}.gallery img{height:180px}.finding{padding:20px 18px}.finding h3{font-size:20px}.callout{padding:20px}section{padding-top:40px}th,td{padding:12px}h2{font-size:31px}}@media(max-width:420px){.gallery{grid-template-columns:1fr}.gallery img{height:250px}}@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}}@media print{aside,.mobile-nav,.filter,.print-btn{display:none}main{margin:0;padding:0;max-width:none}body{background:white;font-size:11pt}.cover{page-break-after:always}h1{font-size:45pt}h2{font-size:24pt}h3{font-size:15pt}table{font-size:9pt;min-width:0}.table-wrap{overflow:visible}section{padding-top:24px}.finding{break-inside:avoid}.finding p{font-size:10pt}.gallery{grid-template-columns:repeat(2,1fr)}.gallery img{height:150px}.stats{grid-template-columns:repeat(4,1fr)}a{color:inherit}.callout{font-size:12pt}[hidden]{display:block!important}}
'''
script='''
const cards=[...document.querySelectorAll('.finding')];
let active='all';const search=document.querySelector('#finding-search');
function filter(){let count=0;const q=search.value.toLocaleLowerCase('ru');cards.forEach(c=>{const show=(active==='all'||c.dataset.priority===active)&&c.textContent.toLocaleLowerCase('ru').includes(q);c.hidden=!show;if(show)count++});document.querySelector('#filter-status').textContent=`Показано ${count} из ${cards.length} замечаний. Фильтр влияет только на карточки замечаний; остальные разделы остаются видимыми.`}
document.querySelectorAll('[data-filter]').forEach(b=>b.addEventListener('click',()=>{active=b.dataset.filter;document.querySelectorAll('[data-filter]').forEach(x=>x.setAttribute('aria-pressed',String(x===b)));filter()}));search.addEventListener('input',filter);document.querySelector('#print').addEventListener('click',()=>window.print());window.addEventListener('beforeprint',()=>document.querySelectorAll('details').forEach(d=>d.open=true));filter();
'''
counts={p:len(re.findall(r'class="finding"[^>]*data-priority="'+p+r'"',body)) for p in ['P1','P2','P3']}
filters='<div class="filter" aria-label="Фильтр замечаний"><button data-filter="all" aria-pressed="true">Все замечания</button>'+''.join(f'<button data-filter="{p}" aria-pressed="false">{p} · {n}</button>' for p,n in counts.items())+'<label for="finding-search" class="note">Поиск:</label><input id="finding-search" type="search" placeholder="Например: упаковка, шрифт, форма"></div><p id="filter-status" class="filter-status" role="status"></p>'
cover='''<header class="cover"><p class="eyebrow">NOVOFERMA / Аудит сайта / 16 октября 2026</p><h1>Характер есть.<br>Нужна точность.</h1><p class="sub">Строгий аудит дизайна, продукта и реализации: от формы букв и пластики персонажей до маршрута покупки и веса изображений.</p><div class="stats"><div class="stat"><strong>20</strong><span>страниц в техническом охвате</span></div><div class="stat"><strong>3</strong><span>прохода проверки</span></div><div class="stat"><strong>9</strong><span>брендов для сравнения</span></div><div class="stat"><strong>37</strong><span>принятых снимков</span></div></div><p class="note">Зафиксированная локальная версия · 14:40 MSK · сайт не изменён</p><button class="print-btn" id="print">Печать / сохранить PDF средствами браузера</button></header>'''
html='<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Новоферма — строгий аудит, 16.10.2026</title><meta name="description" content="Подробный аудит Новофермы: UX, дизайн, анимации, упаковки, доступность, скорость, конкуренты и тренды 2026."><style>'+css+'</style></head><body><aside><div class="brand">NOVOFERMA<small>НЕЗАВИСИМЫЙ АУДИТ / 2026</small></div><nav class="nav" aria-label="Разделы отчёта">'+nav+'</nav></aside><main>'+cover+'<details class="mobile-nav"><summary>Содержание отчёта</summary>'+nav+'</details>'+filters+body+'<p class="footer-note">Исследование и выводы подготовлены в текущем аудите. Стандарты, наблюдения, экспертные оценки и непроверенные риски разделены. Версия отчёта: 1.0.</p></main><script>'+script+'</script></body></html>'
(ROOT/'audit.html').write_text(html)

class TextExtractor(HTMLParser):
    def __init__(self): super().__init__(); self.out=[]; self.skip=0
    def handle_starttag(self,tag,attrs):
        if tag in ('style','script'):self.skip+=1
        if tag in ('p','h1','h2','h3','li','tr','section','summary'):self.out.append('\n')
        if tag in ('td','th'):self.out.append(' | ')
        if tag=='a':
            d=dict(attrs)
            if d.get('href','').startswith('http'):self.out.append(' ['+d['href']+'] ')
    def handle_endtag(self,tag):
        if tag in ('style','script'):self.skip-=1
        if tag in ('p','h1','h2','h3','li','tr','summary'):self.out.append('\n')
    def handle_data(self,data):
        if not self.skip:self.out.append(data)
x=TextExtractor();x.feed(cover+body)
plain=re.sub(r'\n[ \t]*\n(?:[ \t]*\n)+','\n\n',''.join(x.out))
(ROOT/'report.txt').write_text(plain)
findings=[]
for match in re.finditer(r'<(article|details) class="finding"([^>]*)>(.*?)</\1>',body,flags=re.S):
    attrs=dict(re.findall(r'([\w-]+)="([^"]*)"',match.group(2)))
    title=re.search(r'<h3>(.*?)</h3>',match.group(3)).group(1)
    x=TextExtractor();x.feed(match.group(3))
    findings.append({'id':attrs['id'],'priority':attrs['data-priority'],'title':unescape(title),'text':''.join(x.out).strip(),'evidence':re.findall(r'href="([^"]+)"',match.group(3))})
(ROOT/'findings.json').write_text(json.dumps({'version':'2026-10-16 14:40 MSK','counts':counts,'findings':findings},ensure_ascii=False,indent=2))
print(json.dumps({'sections':len(parts),'findings':len(findings),'priority_counts':counts,'gallery':len(gallery),'text_words':len(plain.split()),'html_bytes':len(html.encode())},ensure_ascii=False))
