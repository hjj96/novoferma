from pathlib import Path
import json,html,hashlib
ROOT=Path(__file__).resolve().parent.parent
SITE=ROOT/'output/concept'

def asset_url(name):
 return name+'?v='+hashlib.sha256((SITE/name).read_bytes()).hexdigest()[:10]

def esc(s): return html.escape(str(s),quote=True)
def icon(name,cls='ui-icon',size=24): return f'<img class="{cls}" src="assets/icons/{name}.svg" width="{size}" height="{size}" alt="" aria-hidden="true">'
def arrow(): return icon('arrow-up-right','ui-icon icon-arrow')
def btn(text,href,kind='dark'): return f'<a class="button button-{kind}" href="{href}">{text}{arrow()}</a>'
def hand(text,cls=''): return f'<p class="hand {cls}">{text}</p>'
def heart(): return icon('heart','heart ui-icon',45)
def depth_seam(kind, foods):
 # Decorative silhouettes belong to the boundary, not to the content grid.
 pieces=''.join(f'<span class="depth-object depth-object-{i+1}"><img class="depth-motion" data-depth="{36 if i == 0 else -24}" data-depth-turn="{4 if i == 0 else -6}" src="assets/depth/{food}.webp" width="400" height="400" alt="" loading="lazy" decoding="async"></span>' for i,food in enumerate(foods))
 return f'<span class="depth-seam depth-seam-{kind}" aria-hidden="true">{pieces}</span>'
nav=[('catalogue.html','Продукция'),('about.html','О нас'),('partners.html','Партнёрам'),('contacts.html','Контакты')]
def header(active):
 links=''.join(f'<a href="{url}"'+(' aria-current="page"' if active==url else '')+f'>{name}</a>' for url,name in nav)
 return f'''<a class="skip-link" href="#main">Перейти к содержанию</a><header class="site-header"><div class="wrap header-inner"><a class="brand" href="index.html" aria-label="Новоферма — главная"><img src="assets/logo-reference.webp" width="342" height="64" alt="NOVOferma"></a><nav class="desktop-nav" aria-label="Основная навигация">{links}</nav><div class="header-actions">{btn('Где купить','where-to-buy.html')}<button class="menu-toggle" aria-label="Открыть меню" aria-controls="site-menu" aria-expanded="false">{icon('menu-2')}</button></div></div></header><dialog id="site-menu" class="menu-dialog" aria-label="Меню сайта"><div class="menu-top"><a class="brand" href="index.html"><img src="assets/logo-reference.webp" width="342" height="64" alt="NOVOferma"></a><button class="menu-close icon-button" aria-label="Закрыть меню">{icon("x")}</button></div><nav aria-label="Мобильная навигация">{links}<a href="where-to-buy.html">Где купить</a></nav></dialog>'''
def footer():return f'''<footer class="site-footer"><div class="wrap"><div class="footer-top"><a class="brand" href="index.html"><img src="assets/logo-reference.webp" width="342" height="64" alt="NOVOferma"></a>{hand('Для ужина. Для кино. Для своих.')}<a class="footer-mail" href="mailto:info@novoferma.ru">info@novoferma.ru {arrow()}</a></div><div class="footer-bottom"><p>© 2026 ООО «НОВОФЕРМА»</p><nav aria-label="Навигация в подвале"><a href="catalogue.html">Продукция</a><a href="partners.html">Партнёрам</a><a href="contacts.html">Контакты</a></nav><a href="tel:+78129155454">+7 (812) 915-54-54</a></div></div></footer>'''
def page(filename,title,content,active='',desc='Замороженные полуфабрикаты из курицы и индейки. Новоферма — для ужина, для кино, для своих.'):
 extra = f'<link rel="stylesheet" href="{asset_url("product-hero.css")}"><script src="{asset_url("product-hero.js")}" defer></script>' if filename == 'index.html' else ''
 story_style = f'<link rel="stylesheet" href="{asset_url("protein-story.css")}">' if filename == 'index.html' else ''
 contact_style = f'<link rel="stylesheet" href="{asset_url("contacts.css")}">' if filename == 'contacts.html' else ''
 catalogue_style = f'<link rel="stylesheet" href="{asset_url("catalogue.css")}">' if filename == 'catalogue.html' else ''
 partner_style = f'<link rel="stylesheet" href="{asset_url("partnership.css")}">' if filename in ('partners.html','about.html','catalogue.html') else ''
 s=f'''<!doctype html><html lang="ru"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="theme-color" content="#fff5e3"><meta name="description" content="{esc(desc)}"><title>{esc(title)} — Новоферма</title><link rel="stylesheet" href="{asset_url('style.css')}"><link rel="stylesheet" href="{asset_url('depth.css')}"><link rel="stylesheet" href="{asset_url('design-system.css')}"><link rel="stylesheet" href="{asset_url('polish.css')}"><link rel="stylesheet" href="{asset_url('motion.css')}"><script src="{asset_url('script.js')}" defer></script><script src="{asset_url('depth.js')}" defer></script></head><body class="page-{filename.removesuffix(".html")}">{header(active)}<main id="main">{content}</main>{footer()}<button class="to-top icon-button" aria-label="Наверх">{icon("arrow-up")}</button></body></html>'''
 s=s.replace('</head>',extra+f'<link rel="stylesheet" href="{asset_url("mobile.css")}">'+story_style+contact_style+partner_style+catalogue_style+'</head>')
 (SITE/filename).write_text(s)

def crumb(name): return f'<nav class="breadcrumb wrap" aria-label="Хлебные крошки"><a href="index.html">Главная</a><span aria-hidden="true">/</span><span>{name}</span></nav>'
def contactband(): return f'<section class="cooperation-invite" aria-label="Сотрудничество с Новофермой"><div class="wrap cooperation-invite-inner"><div><p class="eyebrow">Для магазинов, кафе и ресторанов</p><h2>Хороший вкус<br>объединяет.</h2></div><div class="cooperation-invite-action"><p>Добавим Новоферму в ваш ассортимент?</p>{btn("Обсудить поставки","partners.html#partner-contact","cream")}</div></div></section>'

# Source data is replaced by the verified inventory when available.
fallback=[
 {'id':'meatballs','name':'Фрикадельки «Классические»','weight':'500 г','meat':'Из курицы','category':'Фрикадельки','image':'assets/meatballs-600.webp'},
 {'id':'nuggets','name':'Наггетсы куриные','weight':'400 г','meat':'Из курицы','category':'Наггетсы','image':'assets/pack-nuggets.webp'},
 {'id':'turkey','name':'Наггетсы с индейкой «Фитнес»','weight':'400 г','meat':'С индейкой','category':'Наггетсы','image':'assets/turkey-nuggets-600.webp'},
 {'id':'strips','name':'Стрипсы','weight':'400 г','meat':'Из курицы','category':'Стрипсы','image':'assets/pack-strips.webp'},
 {'id':'popcorn','name':'Куриный попкорн','weight':'400 г','meat':'Из курицы','category':'Попкорн','image':'assets/pack-popcorn.webp'}]
products=fallback
source=SITE/'products.json'
if source.exists():
 raw=json.loads(source.read_text())
 if isinstance(raw,dict):raw=raw.get('products',[])
 if raw:products=raw
# Stable normalisation permits a catalogue sourced by the independent inventory.
for i,p in enumerate(products):
 p['id']=p.get('id',p.get('slug',f'product-{i+1}'))
 p['name']=p.get('displayName',p.get('name',p.get('title','Продукт')))
 p['weight']=p.get('weight',p.get('mass',''))
 p['meatKey']=p.get('meat') or 'unknown'
 p['meat']=p.get('meatLabel') or ('С индейкой' if p['meatKey']=='turkey' else 'Из курицы' if p['meatKey']=='chicken' else 'Из мяса птицы')
 p['category']=p.get('categoryLabel',p.get('category','Наггетсы' if 'наггетс' in p['name'].lower() else 'Фрикадельки' if 'фрикадель' in p['name'].lower() else 'Попкорн' if 'попкорн' in p['name'].lower() else 'Стрипсы' if 'стрипс' in p['name'].lower() else 'Котлеты и биточки'))
 p['image']=p.get('image',p.get('local_image','assets/meatballs-600.webp'))
 if 'assets/' not in p['image']:p['image']='assets/catalogue/'+p['image'].split('/')[-1]
 # The reference PDF supplies the exact packaging art for these three products.
 low=p['name'].lower()
 if low in ['наггетсы куриные','куриные наггетсы']:p['image']='assets/pack-nuggets.webp'
 if 'попкорн' in low:p['image']='assets/pack-popcorn.webp'
 if 'стрипс' in low:p['image']='assets/pack-strips.webp'
 cutout=SITE/'assets/catalogue-cutout'/f"{p['id']}.webp"
 if cutout.exists():p['image']='assets/catalogue-cutout/'+p['id']+'.webp'
 # User-requested frontal composites preserve the official label and expose the tray.
 # Original photographs and products.json remain available as source material.
 if p['id'] in ('bitochki-kurinye-s-ovoshchami','ezhiki-iz-tsyplenka-s-risom'):
  frontal='assets/catalogue-cutout/'+p['id']+'-front-v1.webp'
  if (SITE/frontal).exists():p['image']=frontal
 p['url']='product-'+p['id']+'.html'

def find(part):return next((p for p in products if part in p['name'].lower()),products[0])
def card(p,n=1):
 turkey=p.get('meatKey','turkey' if 'индейк' in p['meat'].lower() else 'chicken')
 return f'''<article class="product-card reveal" data-meat="{turkey}" data-category="{esc(p['category'])}" data-name="{esc(p['name'].lower())}"><a class="product-image" data-tilt href="{p['url']}" aria-label="{esc(p['name'])}"><img class="tilt-plane" src="{p['image']}" width="600" height="500" loading="lazy" alt="{esc(p['name'])}"></a><div class="product-meta"><span>{p['meat']} · {p['weight']}</span></div><a class="product-title" href="{p['url']}"><h3>{p['name']}</h3><span class="circle-arrow" aria-hidden="true">{arrow()}</span></a></article>'''
def cards(items):return ''.join(card(p,i+1) for i,p in enumerate(items))

def home_card(p):
 label={'Наггетсы куриные':'Наггетсы','Куриный попкорн':'Попкорн','Фрикадельки «Классические»':'Фрикадельки'}.get(p['name'],p['name'])
 return f'''<article class="product-card home-product reveal" data-name="{esc(p['name'].lower())}"><a class="product-image" data-tilt href="{p['url']}" aria-label="{esc(p['name'])}"><img class="tilt-plane" src="{p['image']}" width="600" height="500" loading="lazy" alt="{esc(p['name'])}"></a><a class="product-title" href="{p['url']}"><h3>{esc(label)}</h3><span class="circle-arrow" aria-hidden="true">{arrow()}</span></a></article>'''

def product_hero():
 items=[
  dict(id='meatballs',name='Фрикадельки',subtitle='Есть вкусный<br>повод собраться.',description='Классические куриные фрикадельки.<br>Сочно. Натурально. Для своих.'),
  dict(id='nuggets',name='Наггетсы',subtitle='Классические куриные',description='Хрустящие куриные наггетсы.<br>Нежно внутри. Любимые с детства.'),
  dict(id='fibriki',name='Фибрики',kicker='Фрикадельки из курицы',subtitle='Белок + клетчатка',description='Сочные куриные фрикадельки<br>с пищевыми волокнами.',new=True),
  dict(id='lulia-mini',name='Люля мини',subtitle='Куриные колбаски<br>с зеленью и овощами',description='Нежные мини-люля из курицы.<br>С зеленью и овощами.',new=True)
 ]
 layout=json.loads((SITE/'assets/product-hero/title-layout.json').read_text())
 art_layout=json.loads((SITE/'assets/product-hero/art-layout-v4.json').read_text())
 panels='';controls=''
 for i,p in enumerate(items):
  t=layout[p.get('titleLayout',p['id'])];a=art_layout[p['id']];active=i==0
  artAttrs='decoding="sync" fetchpriority="high"' if active else 'decoding="async"'
  art=f'<div class="product-scene-art" aria-hidden="true"><span class="hero-art-frame" style="--art-ratio:{a["ratio"]};--art-size:{a["size"]}%;--art-left:{a["left"]}%;--art-top:{a["top"]}%"><img src="{asset_url("assets/product-hero/"+p["id"]+"-art-v4.webp")}" width="1672" height="941" alt="" {artAttrs}></span></div>'
  new='<p class="hero-new">Новинка</p>' if p.get('new') else ''
  kicker=f'<p class="product-scene-kicker">{p["kicker"]}</p>' if p.get('kicker') else ''
  heading='h2'
  titleFile=p.get('titleFile',p['id']+'-title.webp')
  title=f'<{heading} class="product-scene-title"><span class="sr-only">{p["name"]}</span><span class="product-title-art" aria-hidden="true" style="--title-ratio:{t["ratio"]};--title-size:{t["size"]}%;--title-left:{t["left"]}%;--title-top:{t["top"]}%;"><img src="{asset_url("assets/product-hero/"+titleFile)}" width="{t["width"]}" height="{t["height"]}" alt=""></span></{heading}>'
  subtitle=f'<p class="product-scene-subtitle">{p["subtitle"]}</p>'
  if p['id']=='fibriki':subtitle=f'<div class="benefit-ribbon"><span class="benefit-ribbon-art" aria-hidden="true"><img src="{asset_url("assets/product-hero/benefit-brush-v11.webp")}" width="2144" height="733" alt=""></span>{subtitle}</div>'
  panels+=f'<article class="product-scene product-scene-{p["id"]}{" is-active" if active else ""}" id="scene-{p["id"]}" role="tabpanel" aria-labelledby="pick-{p["id"]}" aria-hidden="{str(not active).lower()}"{"" if active else " inert"}>{art}<div class="product-scene-content">{new}<div class="hero-text-stack">{title}<div class="product-scene-copy"><div class="hero-subheading">{kicker}{subtitle}</div><p class="product-scene-description">{p["description"].replace("<br>","<br> ")}</p></div></div><a class="button product-scene-cta" href="catalogue.html">Перейти в каталог{arrow()}</a></div></article>'
  controls+=f'<button class="product-picker" id="pick-{p["id"]}" role="tab" aria-label="{p["name"]}" aria-selected="{str(active).lower()}" aria-controls="scene-{p["id"]}" tabindex="{0 if active else -1}" data-product-index="{i}" data-product-name="{p["name"]}"><span class="product-picker-mark" aria-hidden="true"></span></button>'
 return f'<section class="product-showcase" aria-label="Новоферма и наши продукты" aria-roledescription="карусель" data-product-carousel><h1 class="sr-only">Новоферма — продукты из курицы и индейки</h1><div class="product-controls"><div class="product-pickers" role="tablist" aria-label="Выбрать слайд">{controls}</div><div class="product-playback"><button class="product-arrow" data-product-prev aria-label="Предыдущий слайд">{icon("arrow-left",size=23)}</button><button class="product-arrow" data-product-next aria-label="Следующий слайд">{icon("arrow-right",size=23)}</button></div></div><div class="product-stage"><img class="product-stage-paper" src="{asset_url("assets/product-hero/background-v2.webp")}" width="1672" height="941" alt="" aria-hidden="true" fetchpriority="high"><img class="product-stage-background" src="{asset_url("assets/product-hero/shared-floor-v11.webp")}" width="1672" height="941" alt="" aria-hidden="true">{panels}</div><p class="sr-only" aria-live="polite" aria-atomic="true" data-product-announcement></p></section>'

def novelty_cards():
 items=[('fibriki','Фибрики','Фрикадельки из курицы с пищевыми волокнами.','fibriki-cut-v2.webp'),('lulia-mini','Люля мини','Куриные мини-колбаски с зеленью и овощами.','lulia-mini-piece-v2.webp')]
 return ''.join(f'<article class="product-card newcomer-card reveal"><a class="product-image" href="where-to-buy.html?product={id}" aria-label="Узнать о новинке: {name}"><img src="{asset_url("assets/product-hero/"+image)}" width="1280" height="1280" loading="lazy" decoding="async" alt="{name}, вариант сервировки"></a><div class="newcomer-copy"><p class="product-meta">Новинка</p><h3>{name}</h3><p class="product-caption">{copy}</p><a class="text-link" href="where-to-buy.html?product={id}">Узнать о новинке{arrow()}</a></div></article>' for id,name,copy,image in items)

def protein_poster():
 return f'''<section class="protein-poster" id="protein" aria-labelledby="protein-poster-heading"><div class="sr-only"><p>02 / Заглянем внутрь</p><h2 id="protein-poster-heading">В основе — птица.</h2><p>Курица и индейка — природные источники белка. Мы делаем из них то, что вы любите.</p><p>Вот что внутри!</p></div><picture aria-hidden="true"><source media="(max-width: 899px)" srcset="{asset_url('assets/protein-story/reveal-mobile-v1.webp')}" width="780" height="1200"><img src="{asset_url('assets/protein-story/reveal-desktop-v1.webp')}" width="1909" height="824" loading="lazy" decoding="async" alt=""></picture></section>'''

home=f'''{product_hero()}
<section class="section wrap home-products"><div class="section-heading reveal"><div><p class="eyebrow">01 / выбираем любимое</p><h2>У каждого —<br>свой вкус.</h2></div><div class="heading-aside">{btn('Весь каталог','catalogue.html')}</div></div><div class="product-grid featured">{''.join(home_card(p) for p in [find('наггетсы куриные'),find('попкорн'),find('стрипсы'),find('фрикадельки')])}</div></section>
{protein_poster()}
<section class="brand-story brand-partnership" id="cooperation" aria-labelledby="cooperation-heading"><div class="wrap brand-inner"><p class="eyebrow partnership-eyebrow reveal">03 / для вашего бизнеса</p><h2 class="partnership-title reveal" id="cooperation-heading"><span>Давайте</span><span>работать</span><em>вместе.</em></h2><div class="brand-copy reveal"><p class="partnership-lead">Производим замороженные продукты из курицы и индейки для вашего бизнеса.</p><dl class="partnership-formats"><div><dt>HoReCa</dt><dd>Для меню кафе, ресторанов и отелей.</dd></div><div><dt>СТМ</dt><dd>Продукция под вашей торговой маркой.</dd></div></dl><div class="partnership-actions">{btn('Обсудить сотрудничество','partners.html#partner-contact')}<a class="partnership-secondary" href="about.html">О производстве{arrow()}</a></div></div></div><img class="story-mascot" src="{asset_url('assets/mascot-partnership-v2.webp')}" width="1086" height="1448" loading="lazy" decoding="async" alt="" aria-hidden="true"></section>
<section class="section wrap where-preview"><div class="reveal"><p class="eyebrow">04 / осталось попробовать</p><h2>Встретимся<br>на полке.</h2><p>Поможем узнать, где искать<br>Новоферму в вашем городе.</p></div><div class="editorial-links reveal"><a href="where-to-buy.html"><h3>Где купить {arrow()}</h3><p>Уточните точки продаж в вашем городе</p></a><a href="contacts.html"><h3>Задать вопрос {arrow()}</h3><p>О продукте, приготовлении или сотрудничестве</p></a></div></section>'''
page('index.html','Есть повод собраться',home)

catalogue=crumb('Продукция')+f'''<section class="wrap catalogue-page" aria-labelledby="catalogue-heading">
<div class="page-heading catalogue-heading reveal"><div><p class="eyebrow">Продукция Новофермы</p><h1 id="catalogue-heading">Что сегодня?</h1><p class="catalogue-intro">Из курицы и индейки.<br>Для ужина и не только.</p></div><img class="catalogue-mascot" src="{asset_url('assets/product-hero/running-mascot-v2.webp')}" width="1280" height="1280" alt="" aria-hidden="true"></div>
<h2 class="sr-only">Выберите свой продукт</h2><div class="product-grid catalogue-grid">{cards(products)}</div>
<section class="catalogue-novelties" id="novelties" aria-labelledby="novelties-heading"><div class="section-heading reveal"><h2 id="novelties-heading">А вот и новинки.</h2></div><div class="product-grid catalogue-novelties-grid">{novelty_cards()}</div></section>
<p class="catalogue-note">Продукция продаётся замороженной. Изображения приготовленных блюд — варианты сервировки.</p></section>{contactband()}'''
page('catalogue.html','Продукция',catalogue,'catalogue.html')

for p in products:
 candidates=[q for q in products if q['id']!=p['id']]
 more=sorted(candidates,key=lambda q:q['category']!=p['category'])[:3]
 details=crumb(f'<a href="catalogue.html">Продукция</a> / {esc(p["name"])}')+f'''<section class="wrap product-detail"><figure class="detail-visual" data-tilt><img class="tilt-plane" src="{p['image']}" width="700" height="650" alt="{esc(p['name'])}"><figcaption>Упаковка продукта</figcaption></figure><div class="detail-copy reveal"><p class="eyebrow">{p['category']} / {p['meat']}</p><h1>{p['name']}</h1><div class="product-facts"><div><span>Масса нетто</span><strong>{p['weight']}</strong></div><div><span>Продукт</span><strong>Замороженный</strong></div><div><span>Упаковка</span><strong>{esc(p.get('packaging','контейнер')).capitalize()}</strong></div></div><div class="detail-actions">{btn('Где купить','where-to-buy.html?product='+p['id'])}<a class="text-link" href="partners.html">Для партнёров {arrow()}</a></div><div class="product-information"><h2>На этикетке</h2><p>Состав, аллергены, пищевая ценность, условия хранения и способ приготовления указаны на упаковке конкретного продукта.</p><a class="text-link" href="mailto:info@novoferma.ru?subject={esc(p['name'])}">Уточнить информацию {arrow()}</a></div></div></section><section class="related-section"><div class="section wrap"><div class="section-heading reveal"><h2>А ещё к столу…</h2>{btn('Весь каталог','catalogue.html')}</div><div class="product-grid featured">{cards(more)}</div></div></section>'''
 page(p['url'],p['name'],details,'catalogue.html')

about=crumb('О Новоферме')+f'''<section class="about-hero"><div class="wrap split"><div class="reveal"><p class="eyebrow">Это Новоферма</p><h1>Вкусно,<br>когда<br><em>вместе.</em></h1></div><div class="about-intro reveal"><p>Новоферма — компания из Санкт-Петербурга. Мы производим замороженные полуфабрикаты из курицы и индейки.</p><p>Котлеты и биточки, фрикадельки, наггетсы, куриный попкорн и стрипсы — выбирайте свой вкус.</p></div></div></section><section class="wrap section about-editorial"><figure class="reveal editorial-photo"><img src="assets/serving-company-crop.webp" width="1008" height="922" alt="Идея подачи: общая тарелка закусок" loading="lazy"><figcaption class="hand">Место для своих</figcaption></figure><div class="reveal"><p class="eyebrow">О нашем производстве</p><h2>Открыто.<br>По делу.</h2><p>В основе продукции — охлаждённое мясо птицы. На производстве используем австрийское и итальянское оборудование.</p><p>Упаковываем продукты в прозрачные контейнеры: содержимое видно до покупки.</p>{btn('Смотреть продукты','catalogue.html')}</div></section><section class="brand-character" aria-labelledby="character-heading"><div class="wrap brand-character-inner"><div class="brand-character-heading"><p class="eyebrow">Наши герои</p><h2 id="character-heading">С характером.<br>И аппетитом.</h2></div><p class="brand-character-copy">Наши курочки добавляют упаковке характер, а знакомым вкусам — немного домашнего тепла.</p><img class="brand-character-art" src="{asset_url('assets/product-hero/running-mascot-v2.webp')}" width="1254" height="1254" loading="lazy" decoding="async" alt="Фирменная курочка Новофермы в клетчатом фартуке расправляет крылья"></div></section>{contactband()}'''
page('about.html','О нас',about,'about.html')

where=crumb('Где купить')+f'''<section class="wrap section page-intro"><p class="eyebrow">Рядом с вами</p><div class="section-heading"><h1>Встретимся<br>на полке.</h1></div><p class="lead">Подскажем, где искать Новоферму<br>в вашем городе.</p></section><section class="wrap where-layout"><div class="city-panel reveal"><p class="eyebrow">Уточнить точки продаж</p><h2>В каком<br>вы городе?</h2><form id="city-form"><label for="city">Город</label><input id="city" name="city" autocomplete="address-level2" placeholder="Например, Санкт-Петербург" required maxlength="100"><label for="wanted-product">Что хотите найти?</label><select id="wanted-product" name="product"><option value="">Весь ассортимент</option>{''.join(f'<option value="{p["id"]}">{esc(p["name"])}</option>' for p in products)}<option value="fibriki">Фибрики — новинка</option><option value="lulia-mini">Люля мини — новинка</option></select><button class="button button-dark" type="submit">Составить письмо {arrow()}</button><p class="form-hint">Откроется ваша почта с готовым вопросом.<br>Письмо отправляете вы.</p></form><p class="form-feedback" role="status" hidden></p></div><div class="where-explanation reveal"><h3>Поможем с поиском</h3><p>Укажите город и продукт — подготовим вопрос для команды Новофермы.</p><p>Можно написать напрямую или позвонить в офис:</p><a class="large-link" href="mailto:info@novoferma.ru">info@novoferma.ru {arrow()}</a><a class="phone-link" href="tel:+78129155454">+7 (812) 915-54-54</a><div class="small-note">Наличие и ассортимент уточняйте в магазине перед поездкой.</div></div></section>'''
page('where-to-buy.html','Где купить',where,'where-to-buy.html')

partner_mail='mailto:zakaz@novoferma.ru?subject=Сотрудничество%20с%20Новофермой&body=Здравствуйте!%0AКомпания:%20%0AГород:%20%0AИнтересующие%20продукты:%20%0AПланируемый%20объём:%20%0AКонтакт%20для%20связи:%20'
partners=crumb('Партнёрам')+f'''<section class="partner-intro wrap" aria-labelledby="partner-heading">
<div class="partner-intro-copy"><p class="eyebrow">Новоферма / сотрудничество</p><h1 id="partner-heading"><span>Хороший вкус.</span> <em>Общее дело.</em></h1><p class="partner-intro-lead">Замороженные продукты из курицы и индейки для магазинов, кафе и ресторанов.</p><div class="partner-intro-actions">{btn('Обсудить поставки','#partner-contact')}<a class="partner-catalogue-link" href="catalogue.html">Посмотреть каталог{arrow()}</a></div></div>
<figure class="partner-intro-visual"><img src="{asset_url('assets/serving-movie-crop.webp')}" width="1008" height="922" fetchpriority="high" alt="Идея подачи: куриные закуски на тарелке с соусом"><figcaption>Идея подачи</figcaption></figure>
</section>
<section class="partner-range wrap" aria-labelledby="range-heading"><div class="partner-range-heading"><div><p class="eyebrow">От закусок до основного блюда</p><h2 id="range-heading">В ваш ассортимент.</h2></div><a class="partner-catalogue-link" href="catalogue.html">Все продукты{arrow()}</a></div><div class="product-grid partner-range-grid">{home_card(find('наггетсы куриные'))}{home_card(find('котлеты куриные'))}{home_card(find('фрикадельки'))}</div></section>
<section class="partner-enquiry" id="partner-contact" aria-labelledby="enquiry-heading"><div class="wrap partner-enquiry-inner"><div class="partner-enquiry-copy"><p class="eyebrow">Отдел приёма заказов</p><h2 id="enquiry-heading">Начнём<br>с разговора.</h2><p>Напишите, какие продукты вас интересуют<br class="enquiry-desktop-break"> и в какой город нужна поставка.</p></div><div class="partner-enquiry-details"><a class="partner-enquiry-email" href="mailto:zakaz@novoferma.ru">zakaz@novoferma.ru{arrow()}</a><a class="partner-enquiry-phone" href="tel:+79312135550">+7 (931) 213-55-50</a>{btn('Составить письмо',partner_mail,'cream')}<p class="partner-enquiry-note">Объём, упаковку и условия обсудим лично.</p></div></div></section>'''
page('partners.html','Партнёрам',partners,'partners.html',desc='Замороженные продукты из курицы и индейки для магазинов, кафе и ресторанов. Ассортимент Новофермы и контакты отдела приёма заказов.')

contacts=crumb('Контакты')+f'''<section class="contacts-main contacts-poster" aria-labelledby="contacts-heading"><div class="wrap contact-layout"><div class="contact-content"><div class="contact-heading reveal"><h1 id="contacts-heading">Мы<br><span class="no-wrap">на связи.</span></h1></div><div class="contact-groups"><section class="contact-group reveal" aria-labelledby="contact-buyers"><div class="contact-audience"><h2 id="contact-buyers">Покупателям</h2><p>О продуктах и точках продаж.</p></div><div class="contact-links"><a class="contact-email" href="mailto:info@novoferma.ru">info@novoferma.ru {arrow()}</a><a class="contact-phone" href="tel:+78129155454">+7 (812) 915-54-54</a></div></section><section class="contact-group reveal" aria-labelledby="contact-partners"><div class="contact-audience"><h2 id="contact-partners">Партнёрам</h2><p>Ассортимент и условия поставки.</p></div><div class="contact-links"><a class="contact-email" href="mailto:zakaz@novoferma.ru">zakaz@novoferma.ru {arrow()}</a><a class="contact-phone" href="tel:+79312135550">+7 (931) 213-55-50</a></div></section></div><a class="contact-map" href="https://yandex.ru/maps/?text=Санкт-Петербург%20Горелово%20Заречная%202" target="_blank" rel="noopener"><span>Открыть адрес на карте</span>{arrow()}</a></div></div><img class="contacts-mascot" src="{asset_url('assets/mascot-contact-restored-v2.webp')}" width="980" height="1605" decoding="async" alt="" aria-hidden="true"></section><section class="wrap requisites"><p class="eyebrow">Реквизиты компании</p><div><strong>ООО «НОВОФЕРМА»</strong><p>ИНН 7807396385<br>ОГРН 1147847409148</p></div><div><strong>Адрес компании</strong><p>198323, Санкт-Петербург,<br>ул. Заречная (тер. Горелово), д. 2</p></div></section>'''
page('contacts.html','Контакты',contacts,'contacts.html')
(SITE/'site-manifest.json').write_text(json.dumps({'pages':['index.html','catalogue.html','about.html','where-to-buy.html','partners.html','contacts.html']+[p['url'] for p in products],'products':products},ensure_ascii=False,indent=2))
print(f'Generated {6+len(products)} pages, {len(products)} products')
