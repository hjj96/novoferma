# -*- coding: utf-8 -*-
from pathlib import Path
import json,html,hashlib,re,argparse
from urllib.parse import quote, urlparse
from site_sections import where_section
from b2b_sections import partners_section, private_label_section, request_url
ROOT=Path(__file__).resolve().parent.parent
SITE=ROOT/'output/concept'
parser=argparse.ArgumentParser(description='Build the Novoferma static site from verified content.')
parser.add_argument('--site-url',default='',help='Public HTTPS base URL, including any path prefix. Enables canonical URLs and sitemap.')
PUBLIC_URL=parser.parse_args().site_url.rstrip('/')
if PUBLIC_URL and (urlparse(PUBLIC_URL).scheme!='https' or not urlparse(PUBLIC_URL).netloc or urlparse(PUBLIC_URL).query or urlparse(PUBLIC_URL).fragment):
 raise SystemExit('--site-url must be an absolute HTTPS URL without query or fragment')
asset_manifest=SITE/'asset-variants.json'
image_variants=json.loads(asset_manifest.read_text()).get('assets',{}) if asset_manifest.exists() else {}
PAGE_META={
 'index.html':'Продукты Новофермы из курицы и индейки: наггетсы, котлеты, фрикадельки и стрипсы. Выберите продукт и узнайте, как уточнить наличие в вашем городе.',
 'catalogue.html':'Каталог Новофермы: продукты из курицы и индейки, названия и масса упаковок, отдельные страницы продуктов и концептов новинок.',
 'about.html':'О Новоферме: компания из Санкт-Петербурга, продукты из охлаждённого мяса птицы, прозрачная упаковка и фирменные персонажи.',
 'where-to-buy.html':'Где искать Новоферму: карточки товаров в интернет-магазинах, проверка наличия по адресу и запрос по выбранному продукту в вашем городе.',
 'partners.html':'Новоферма для магазинов, HoReCa и СТМ: ассортимент, форматы упаковки и запрос условий поставки в ваш город.',
 'contacts.html':'Контакты Новофермы: офис, отдел приёма заказов, телефоны и электронная почта. Адрес компании в Санкт-Петербурге и реквизиты.'}

def responsive_markup(markup):
 def replace(match):
  tag=match.group(0); found=re.search(r'\bsrc="([^"]+)"',tag)
  if not found:return tag
  entry=image_variants.get(html.unescape(found.group(1)).split('?')[0])
  if not entry:return tag
  sizes='(max-width: 699px) calc((100vw - 56px) / 2), (max-width: 1099px) 30vw, 320px' if 'tilt-plane' in tag else '(max-width: 699px) 70vw, 600px'
  if 'hero-scene-image' in tag:
   hint=re.search(r'data-hero-sizes="([^"]+)"',tag)
   if hint:sizes=html.unescape(hint.group(1))
  elif 'partners-host' in tag:sizes='(max-width: 699px) min(180px, 40vw), (max-width: 1099px) min(36vw, 267px), 327px'
  elif 'catalogue-mascot' in tag:sizes='(max-width: 699px) 86px, (max-width: 1099px) 170px, 210px'
  elif 'contacts-mascot' in tag:sizes='(max-width: 699px) 84px, (max-width: 959px) 27vw, (max-width: 1199px) 25vw, (max-width: 1499px) 24vw, 360px'
  elif 'brand-character-art' in tag:sizes='(max-width: 699px) min(74vw, 280px), (max-width: 1099px) 270px, 300px'
  elif 'story-mascot' in tag:sizes='240px'
  elif 'nuggets-layer-v2' in found.group(1):sizes='(max-width: 899px) 92vw, (max-width: 1392px) 63vw, 875px'
  elif 'hen-layer-v2' in found.group(1):sizes='(max-width: 899px) 50vw, (max-width: 1392px) 32vw, 445px'
  tag=tag.replace(found.group(0),f'src="{entry["src"]}" srcset="{entry["srcset"]}" sizes="{sizes}"')
  tag=re.sub(r'\bwidth="\d+"',f'width="{entry["width"]}"',tag)
  tag=re.sub(r'\bheight="\d+"',f'height="{entry["height"]}"',tag)
  if 'class="detail-packshot"' in tag:tag=tag.replace(sizes,'(max-width: 699px) 280px, 550px')
  return tag
 return re.sub(r'<img\b[^>]*>',replace,markup)

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
def header(active,current):
 action=btn('Написать','partners.html#partner-contact') if active=='partners.html' else btn('Где купить','where-to-buy.html')
 links=''.join(f'<a href="{url}"'+(' class="is-section-active"' if active==url else '')+(' aria-current="page"' if current==url else '')+f'>{name}</a>' for url,name in nav)
 return f'''<a class="skip-link" href="#main">Перейти к содержанию</a><header class="site-header"><div class="wrap header-inner"><a class="brand" href="index.html" aria-label="Новоферма — главная"><img src="assets/logo-reference.webp" width="342" height="64" alt="NOVOferma"></a><nav class="desktop-nav" aria-label="Основная навигация">{links}</nav><div class="header-actions">{action}<button class="menu-toggle" aria-label="Открыть меню" aria-controls="site-menu" aria-expanded="false">{icon('menu-2')}</button></div></div></header><dialog id="site-menu" class="menu-dialog" aria-label="Меню сайта"><div class="menu-top"><a class="brand" href="index.html"><img src="assets/logo-reference.webp" width="342" height="64" alt="NOVOferma"></a><button class="menu-close icon-button" aria-label="Закрыть меню">{icon("x")}</button></div><nav aria-label="Мобильная навигация">{links}<a href="where-to-buy.html">Где купить</a></nav></dialog>'''
def footer():return f'''<footer class="site-footer"><div class="wrap"><div class="footer-top"><a class="brand" href="index.html"><img src="assets/logo-reference.webp" width="342" height="64" alt="NOVOferma"></a>{hand('Для ужина. Для кино. Для своих.')}<a class="footer-mail" href="mailto:info@novoferma.ru">info@novoferma.ru {arrow()}</a></div><div class="footer-bottom"><p>© 2026 ООО «НОВОФЕРМА»</p><nav aria-label="Навигация в подвале"><a href="catalogue.html">Продукция</a><a href="partners.html">Партнёрам</a><a href="contacts.html">Контакты</a></nav><a href="tel:+78129155454">+7 (812) 915-54-54</a></div></div></footer>'''
def page(filename,title,content,active='',desc=''):
 desc=desc or PAGE_META.get(filename,f'{title}. Продукция Новофермы из курицы и индейки: информация о продукте и контакты для уточнения наличия.')
 extra = f'<link rel="stylesheet" href="{asset_url("product-hero.css")}"><script src="{asset_url("product-hero.js")}" defer></script>' if filename == 'index.html' else ''
 story_style = f'<link rel="stylesheet" href="{asset_url("protein-story.css")}">' if filename == 'index.html' else ''
 contact_style = f'<link rel="stylesheet" href="{asset_url("contacts.css")}">' if filename == 'contacts.html' else ''
 catalogue_style = f'<link rel="stylesheet" href="{asset_url("catalogue.css")}">' if filename == 'catalogue.html' else ''
 partner_style = f'<link rel="stylesheet" href="{asset_url("partnership.css")}">' if filename in ('about.html','catalogue.html') else ''
 partner_scenes = f'<link rel="stylesheet" href="{asset_url("partners-scenes.css")}"><script src="{asset_url("partners-scenes.js")}" defer></script>' if filename == 'partners.html' else ''
 b2b_style = f'<link rel="stylesheet" href="{asset_url("b2b.css")}">'
 s=f'''<!doctype html><html lang="ru"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="theme-color" content="#fff5e3"><meta name="description" content="{esc(desc)}"><title>{esc(title)} — Новоферма</title><link rel="icon" href="assets/favicon.svg" type="image/svg+xml"><meta property="og:type" content="website"><meta property="og:locale" content="ru_RU"><meta property="og:site_name" content="Новоферма"><meta property="og:title" content="{esc(title)} — Новоферма"><meta property="og:description" content="{esc(desc)}"><link rel="stylesheet" href="{asset_url('assets/fonts/font-face.css')}"><link rel="stylesheet" href="{asset_url('style.css')}"><link rel="stylesheet" href="{asset_url('depth.css')}"><link rel="stylesheet" href="{asset_url('design-system.css')}"><link rel="stylesheet" href="{asset_url('polish.css')}"><link rel="stylesheet" href="{asset_url('motion.css')}"><script src="{asset_url('script.js')}" defer></script><script src="{asset_url('depth.js')}" defer></script></head><body class="page-{filename.removesuffix(".html")}">{header(active,filename)}<main id="main">{content}</main>{footer()}<button class="to-top icon-button" aria-label="Наверх">{icon("arrow-up")}</button></body></html>'''
 typography_style=f'<link rel="stylesheet" href="{asset_url("typography.css")}">'
 preview_style = f'<link rel="stylesheet" href="{asset_url("product-cards.css")}">' if filename in ('index.html','catalogue.html') or filename.startswith('product-') else ''
 home_style = f'<link rel="stylesheet" href="{asset_url("home-unified.css")}">' if filename == 'index.html' else ''
 detail_style=f'<link rel="stylesheet" href="{asset_url("product-detail.css")}">' if filename.startswith('product-') else ''
 where_assets=f'<link rel="stylesheet" href="{asset_url("where-to-buy.css")}"><script src="{asset_url("where-to-buy.js")}" defer></script>' if filename=='where-to-buy.html' else ''
 catalogue_script='' # The compact catalogue exposes every product without controls.
 metadata=''
 if PUBLIC_URL:
  canonical=PUBLIC_URL+'/'+filename
  metadata=f'<link rel="canonical" href="{esc(canonical)}"><meta property="og:url" content="{esc(canonical)}"><meta property="og:image" content="{esc(PUBLIC_URL)}/assets/product-hero/meatballs-art-v4.webp"><meta property="og:image:alt" content="Фрикадельки Новофермы — вариант подачи">'
  crumbs=[{'@type':'ListItem','position':1,'name':'Главная','item':PUBLIC_URL+'/index.html'}]
  if filename.startswith('product-'):crumbs.append({'@type':'ListItem','position':2,'name':'Продукция','item':PUBLIC_URL+'/catalogue.html'})
  elif filename=='private-label.html':crumbs.append({'@type':'ListItem','position':2,'name':'Партнёрам','item':PUBLIC_URL+'/partners.html'})
  if filename!='index.html':crumbs.append({'@type':'ListItem','position':len(crumbs)+1,'name':title,'item':canonical})
  data={'@context':'https://schema.org','@type':'BreadcrumbList','itemListElement':crumbs}
  metadata+='<script type="application/ld+json">'+json.dumps(data,ensure_ascii=False).replace('<','\\u003c')+'</script>'
 s=s.replace('</head>',extra+f'<link rel="stylesheet" href="{asset_url("mobile.css")}">'+story_style+contact_style+partner_style+catalogue_style+partner_scenes+preview_style+home_style+detail_style+catalogue_script+where_assets+b2b_style+typography_style+metadata+'</head>')
 (SITE/filename).write_text(responsive_markup(s))

def crumb(name): return f'<nav class="breadcrumb wrap" aria-label="Хлебные крошки"><a href="index.html">Главная</a><span aria-hidden="true">/</span><span>{name}</span></nav>'
def contactband(context):
 invites={
  'catalogue':('Для вашей полки.','Для вашего меню.',''),
  'about':('Познакомимся','как партнёры?','Расскажите о вашем магазине или заведении — обсудим сотрудничество.')
 }
 title,accent,copy=invites[context]
 eyebrow='<p class="eyebrow">Магазинам, кафе и ресторанам</p>' if context!='catalogue' else ''
 description=f'<p>{copy}</p>' if copy else ''
 return f'''<section class="cooperation-invite cooperation-invite-{context}" aria-labelledby="invite-{context}-heading"><div class="wrap cooperation-invite-inner"><div class="cooperation-invite-heading">{eyebrow}<h2 id="invite-{context}-heading"><span>{title}</span><em>{accent}</em></h2></div><div class="cooperation-invite-response">{description}<a class="cooperation-invite-cta" href="partners.html#partner-contact"><span>Обсудить поставки</span><span class="cooperation-invite-arrow" aria-hidden="true">{arrow()}</span></a></div></div></section>'''

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
# A nonempty imported recipe is not manufacturer approval. A reviewed publication
# workflow and renderer are required before publishing these safety-relevant fields.
for product in products:
 for field in ('ingredients','allergens','nutrition','storage','preparation'):
  if product.get(field) is not None:
   raise SystemExit(f"Unapproved food information: {product.get('slug', product.get('id'))}.{field}. Review the exact SKU specification, content registry and renderer before publication.")
# Stable normalisation permits a catalogue sourced by the independent inventory.
for i,p in enumerate(products):
 p['id']=p.get('id',p.get('slug',f'product-{i+1}'))
 p['name']=p.get('displayName',p.get('name',p.get('title','Продукт')))
 p['weight']=p.get('weight',p.get('mass',''))
 p['meatKey']=p.get('meat') or 'unknown'
 p['meat']=p.get('meatLabel') or ('С индейкой' if p['meatKey']=='turkey' else 'Из курицы' if p['meatKey']=='chicken' else 'Из мяса птицы')
 p['category']=p.get('categoryLabel',p.get('category','Наггетсы' if 'наггетс' in p['name'].lower() else 'Фрикадельки' if 'фрикадель' in p['name'].lower() else 'Попкорн' if 'попкорн' in p['name'].lower() else 'Стрипсы' if 'стрипс' in p['name'].lower() else 'Котлеты и биточки'))
 p['image']=p.get('image',p.get('local_image','assets/meatballs-600.webp'))
 p['officialImage']=p['image']
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
 # Clean native-alpha exports replace the previous ragged matte and baked shadow.
 clean='assets/catalogue-clean-v2/'+p['id']+'.webp'
 if (SITE/clean).exists():p['image']=clean
 # A product keeps its catalogue backdrop and lean wherever its preview appears.
 p['previewTone']=i%4+1
 p['previewLean']='right' if i%2 else 'left'
 p['url']='product-'+p['id']+'.html'

def find(part):return next((p for p in products if part in p['name'].lower()),products[0])
def card(p):
 turkey=p.get('meatKey','turkey' if 'индейк' in p['meat'].lower() else 'chicken')
 meat=f'<span class="product-meat">{esc(p["meat"])}</span>' if p.get('meat') else ''
 weight=f'<span class="product-weight">{esc(p["weight"]).replace(" ", "&nbsp;")}</span>' if p.get('weight') else ''
 anchor=f' id="{esc(p["anchor"])}"' if p.get('anchor') else ''
 status='<span class="product-status">Концепт новинки</span>' if p.get('concept') else ''
 return f'''<article class="product-card packshot-preview"{anchor} data-product-id="{p['id']}" data-meat="{turkey}" data-category="{esc(p['category'])}" data-name="{esc(p['name'].lower())}"><a class="product-image product-card-link" href="{p['url']}"><span class="packshot-stage" data-tilt><img class="tilt-plane" src="{p['image']}" width="800" height="800" loading="lazy" decoding="async" alt=""></span><h3 class="product-title">{esc(p['name'])}</h3><span class="product-meta">{meat}{weight}{status}</span></a></article>'''
def cards(items):return ''.join(card(p) for p in items)

def product_hero():
 # Keep the original playful food-and-chicken campaign, with a protected header
 # and an independent text column. Fibriki is the opening product.
 items=[
  dict(id='fibriki',name='Фибрики',subtitle='Новая идея<br>для своих.',description='Идея куриных фрикаделек с пищевыми волокнами. Знакомьтесь с концептом.',label='Концепт новинки',action='Знакомьтесь с Фибриками',url='product-fibriki.html'),
  dict(id='meatballs',name='Фрикадельки',subtitle='Есть вкусный<br>повод собраться.',description='Классические куриные фрикадельки. В домашний суп, к любимому гарниру — и всех за стол.',label='Для ужина. Для своих.',action='О фрикадельках',url='product-frikadelki-klassicheskie.html'),
  dict(id='nuggets',name='Наггетсы',subtitle='Хрустим<br>в хорошей компании.',description='Золотистая корочка, нежная курица внутри. Добавьте любимый соус — и зовите своих.',label='Любимые вкусы',action='О наггетсах',url='product-naggetsy-kurinye.html'),
  dict(id='lulia-mini',name='Люля мини',subtitle='Маленький формат.<br>Большой аппетит.',description='Концепт мини-колбасок из курицы с зеленью и овощами. Характеристики и выпуск уточняются.',label='Концепт новинки',action='О Люля мини',url='product-lulia-mini.html')
 ]
 art_layout=json.loads((SITE/'assets/product-hero/art-layout-v4.json').read_text())
 updated_layout=SITE/'assets/product-hero/fibriki-art-v5-layout.json'
 updated_image=SITE/'assets/product-hero/fibriki-art-v5.webp'
 if updated_layout.exists()!=updated_image.exists():raise SystemExit('Fibriki artwork image and layout must be transferred together')
 use_updated_art=updated_layout.exists() and updated_image.exists()
 if use_updated_art:art_layout['fibriki']=json.loads(updated_layout.read_text())
 panels='';controls=''
 for i,p in enumerate(items):
  active=i==0;a=art_layout[p['id']]
  art_path='assets/product-hero/'+p['id']+'-art-v4.webp'
  if p['id']=='fibriki' and use_updated_art:art_path='assets/product-hero/fibriki-art-v5.webp'
  # sizes describes the complete transparent canvas, enlarged inside the
  # art bounding box. Describing only the frame would undersample the drawing.
  scale=a['size']/100
  cap=lambda h:f"{h*a['ratio']*scale:.2f}px"
  canvas=lambda gap:f"calc({scale*100:.4f}vw - {gap*scale:.2f}px)"
  sizes=', '.join([
   f"(max-width: 359px) min({canvas(24)}, {cap(240)})",
   f"(max-width: 479px) min({canvas(32)}, {cap(270)})",
   f"(max-width: 699px) min({canvas(32)}, {cap(315)})",
   f"(max-width: 1099px) min(calc({53*scale:.4f}vw - {20*scale:.2f}px), {cap(570)})",
   f"(max-width: 1599px) min(calc({53*scale:.4f}vw - {24*scale:.2f}px), {cap(570)})",
   cap(570)])
  src=asset_url(art_path)
  entry=image_variants.get(art_path)
  if active:
   attrs=f'src="{src}" data-hero-sizes="{esc(sizes)}" decoding="async" fetchpriority="high"'
  elif entry:
   attrs=f'src="data:image/svg+xml,%3Csvg xmlns=%27http://www.w3.org/2000/svg%27/%3E" data-src="{entry["src"]}" data-srcset="{entry["srcset"]}" data-sizes="{esc(sizes)}" decoding="async"'
  else:
   attrs=f'src="data:image/svg+xml,%3Csvg xmlns=%27http://www.w3.org/2000/svg%27/%3E" data-src="{src}" decoding="async"'
  art=f'<div class="product-scene-art" aria-hidden="true"><span class="hero-art-frame" style="--art-ratio:{a["ratio"]};--art-size:{a["size"]}%;--art-left:{a["left"]}%;--art-top:{a["top"]}%"><img class="hero-scene-image" {attrs} width="{a["width"]}" height="{a["height"]}" alt=""></span></div>'
  label=f'<p class="hero-new{ " hero-new-accent" if i in (0,3) else ""}">{p["label"]}</p>'
  panels+=f'<article class="product-scene product-scene-{p["id"]}{" is-active" if active else ""}" id="scene-{p["id"]}" role="tabpanel" aria-labelledby="pick-{p["id"]}" aria-hidden="{str(not active).lower()}"{"" if active else " inert"}><div class="product-scene-content">{label}<div class="hero-text-stack"><h2 class="product-scene-title"><span class="product-title-live">{p["name"]}</span></h2><p class="product-scene-subtitle">{p["subtitle"]}</p><p class="product-scene-description">{p["description"]}</p></div><div class="hero-actions"><a class="button product-scene-cta" href="{p["url"]}">{p["action"]}{icon("arrow-right","ui-icon icon-arrow")}</a></div></div>{art}</article>'
  controls+=f'<button class="product-picker" id="pick-{p["id"]}" role="tab" aria-label="{p["name"]}" aria-selected="{str(active).lower()}" aria-controls="scene-{p["id"]}" tabindex="{0 if active else -1}" data-product-index="{i}" data-product-name="{p["name"]}"><span class="product-picker-mark" aria-hidden="true">0{i+1}</span><span class="product-picker-label">{p["name"]}</span></button>'
 return f'<section class="product-showcase" aria-label="Новоферма и наши продукты" aria-roledescription="карусель" data-product-carousel><h1 class="sr-only">Новоферма — продукты из курицы и индейки</h1><div class="product-stage"><img class="product-stage-paper" src="{asset_url("assets/product-hero/background-v2.webp")}" width="1672" height="941" alt="" aria-hidden="true"><img class="product-stage-background" src="{asset_url("assets/product-hero/shared-floor-v11.webp")}" width="1672" height="941" alt="" aria-hidden="true">{panels}</div><div class="product-controls"><div class="product-pickers" role="tablist" aria-label="Выбрать продукт">{controls}</div><div class="product-playback"><button class="product-arrow" data-product-prev aria-label="Предыдущий слайд">{icon("arrow-left",size=22)}</button><button class="product-arrow" data-product-next aria-label="Следующий слайд">{icon("arrow-right",size=22)}</button></div></div><p class="sr-only" aria-live="polite" aria-atomic="true" data-product-announcement></p></section>'

# Catalogue-only previews keep the two novelties out of the verified SKU inventory.
catalogue_products=products+[
 dict(id='fibriki',name='Фибрики',meat='Из курицы',meatKey='chicken',weight='',category='Фрикадельки и ёжики',image=asset_url('assets/novelty-packaging/fibriki-pack-v11.webp'),url='product-fibriki.html',previewTone=3,previewLean='left',anchor='novelties',concept=True,description='Концепт куриных фрикаделек с пищевыми волокнами.'),
 dict(id='lulia-mini',name='Люля мини',meat='Из курицы',meatKey='chicken',weight='',category='Люля мини',image=asset_url('assets/novelty-packaging/lulia-mini-pack-v3.webp'),url='product-lulia-mini.html',previewTone=4,previewLean='right',concept=True,description='Концепт мини-колбасок из курицы с зеленью и овощами.')
]

def protein_poster():
 return f'''<section class="protein-poster" id="protein" aria-labelledby="protein-poster-heading"><div class="protein-poster-inner"><div class="protein-poster-copy"><p class="protein-poster-eyebrow home-kicker">02 / Заглянем внутрь</p><h2 id="protein-poster-heading" class="protein-poster-title home-editorial-title"><span>В основе —</span> <em>птица.</em></h2><p class="protein-poster-description">Курица и индейка — природные источники белка. Мы делаем из них то, что вы любите.</p></div><div class="protein-poster-scene"><p class="protein-poster-caption">Вот что<br>внутри!<span class="protein-caption-arrow" aria-hidden="true"></span></p><div class="protein-poster-art" aria-hidden="true"><div class="protein-food"><img src="{asset_url('assets/protein-story/nuggets-layer-v2.webp')}" width="1448" height="1086" loading="lazy" decoding="async" alt=""></div><div class="protein-hen"><img src="{asset_url('assets/protein-story/hen-layer-v2.webp')}" width="1254" height="1254" loading="lazy" decoding="async" alt=""></div></div></div></div></section>'''

home=f'''{product_hero()}
<section class="section wrap home-products" id="products"><div class="section-heading reveal"><div><p class="eyebrow home-kicker">01 / выбираем любимое</p><h2 class="home-editorial-title"><span>У каждого —</span> <span>свой вкус.</span></h2></div><div class="heading-aside">{btn('Весь каталог','catalogue.html')}</div></div><div class="product-grid featured">{cards([find('наггетсы куриные'),find('попкорн'),find('стрипсы'),find('фрикадельки')])}</div></section>
{protein_poster()}
<section class="brand-story brand-partnership" id="cooperation" aria-labelledby="cooperation-heading"><div class="wrap brand-inner"><p class="eyebrow home-kicker partnership-eyebrow reveal">03 / для вашего бизнеса</p><h2 class="partnership-title home-editorial-title reveal" id="cooperation-heading"><span>Давайте</span> <span>работать</span> <em>вместе.</em></h2><div class="brand-copy reveal"><p class="partnership-lead">Производим замороженные продукты из курицы и индейки для вашего бизнеса.</p><dl class="partnership-formats"><div><dt>Розница</dt><dd>Основной ассортимент для вашей полки.</dd></div><div><dt>HoReCa</dt><dd>Для меню кафе, ресторанов и отелей.</dd></div><div><dt>СТМ</dt><dd>Обсудим выпуск под вашей торговой маркой.</dd></div></dl><div class="partnership-actions">{btn('Обсудить сотрудничество','partners.html#partner-contact')}<a class="partnership-secondary" href="private-label.html">Обсудить свою марку{arrow()}</a></div></div></div><img class="story-mascot" src="{asset_url('assets/mascot-partnership-v2.webp')}" width="1086" height="1448" loading="lazy" decoding="async" alt="" aria-hidden="true"></section>
<section class="section wrap where-preview"><div class="reveal"><p class="eyebrow home-kicker">04 / осталось попробовать</p><h2 class="home-editorial-title"><span>Встретимся</span> <span>на полке.</span></h2><p>Поможем узнать, где искать<br>Новоферму в вашем городе.</p></div><div class="editorial-links reveal"><a href="where-to-buy.html"><h3>Где купить {arrow()}</h3><p>Уточните точки продаж в вашем городе</p></a><a href="contacts.html"><h3>Задать вопрос {arrow()}</h3><p>О продукте, приготовлении или сотрудничестве</p></a></div></section>'''
page('index.html','Есть повод собраться',home)

catalogue=f'''<section class="catalogue-header" aria-labelledby="catalogue-heading"><div class="wrap catalogue-header-inner">
<div class="catalogue-heading"><h1 id="catalogue-heading">Каталог</h1></div>
<p class="catalogue-intro">Продукты из курицы и индейки.<br>Для вашего ассортимента.</p>
</div></section><section class="wrap catalogue-page" aria-labelledby="catalogue-products-heading">
<h2 class="sr-only" id="catalogue-products-heading">Выберите свой продукт</h2><div class="product-grid catalogue-grid">{cards(catalogue_products)}</div>
</section>{contactband('catalogue')}'''
page('catalogue.html','Продукция',catalogue,'catalogue.html')

def product_information(p):
 request=f'Здравствуйте! Пришлите, пожалуйста, актуальный состав, информацию об аллергенах, пищевую ценность, хранение и способ приготовления продукта: {p["name"]}, {p.get("weight","")}. Спасибо!'
 return f'<div class="product-information"><h2>Состав и приготовление</h2><p>Перед покупкой проверьте состав и способ приготовления на актуальной этикетке. Если упаковки нет под рукой, запросите подробности у нашей команды.</p><a class="text-link" href="mailto:info@novoferma.ru?subject={quote("Информация о продукте: "+p["name"])}&amp;body={quote(request)}">Запросить информацию{arrow()}</a></div>'

for p in catalogue_products:
 candidates=[q for q in products if q['id']!=p['id']]
 more=sorted(candidates,key=lambda q:q['category']!=p['category'])[:3]
 concept=p.get('concept',False)
 status='<p class="product-status">Концепт новинки</p>' if concept else ''
 facts=f'<p class="detail-intro">{esc(p["description"])}</p><p class="concept-note">Представлен концепт упаковки. Окончательный вид, характеристики и начало продаж уточняйте у команды Новофермы.</p>' if concept else f'<div class="product-facts"><div><span>Масса нетто</span><strong>{p["weight"]}</strong></div><div><span>Продукт</span><strong>Замороженный</strong></div><div><span>Упаковка</span><strong>{esc(p.get("packaging","контейнер")).capitalize()}</strong></div></div>'
 action='Уточнить о новинке' if concept else 'Где купить'
 info='' if concept else product_information(p)
 original='' if concept else f'<details class="label-reference"><summary>Фото из каталога производителя</summary><img src="{p["officialImage"]}" width="{p.get("imageWidth",900)}" height="{p.get("imageHeight",900)}" alt="{esc(p["name"])} — фото производителя" loading="lazy"><p>Внешний вид и сведения на упаковке могут обновляться. Перед покупкой сверяйте этикетку выбранного товара.</p></details>'
 serving='' if concept or not p.get('servingImage') else f'<details class="label-reference serving-reference"><summary>Пример подачи производителя</summary><figure><img src="{esc(p["servingImage"])}" width="{p.get("servingImageWidth",600)}" height="{p.get("servingImageHeight",600)}" loading="lazy" decoding="async" alt="{esc(p["name"])} — пример подачи на фото производителя"><figcaption>Пример подачи с сайта производителя. Состав и способ приготовления сверяйте по актуальной этикетке.</figcaption></figure></details>'
 caption='Визуальный концепт упаковки' if concept else 'Внешний вид упаковки'
 buyer_note='Обсудить возможность выпуска и характеристики концепта.' if concept else 'Уточните состав, аллергены, пищевую ценность, хранение и приготовление для вашей закупки.'
 buyer_action='Обсудить новинку' if concept else 'Запросить спецификацию'
 buyer=f'<section class="detail-b2b" aria-labelledby="buyer-{p["id"]}"><h2 id="buyer-{p["id"]}">Покупаете для бизнеса?</h2><p>{buyer_note}</p><div class="detail-b2b-actions"><a class="text-link" href="{request_url(p["id"],"specification")}">{buyer_action}{arrow()}</a><a class="text-link" href="{request_url(p["id"],"samples")}">Обсудить образцы{arrow()}</a></div></section>'
 details=crumb(f'<a href="catalogue.html">Продукция</a> / <span aria-current="page">{esc(p["name"])}</span>')+f'''<section class="wrap product-detail"><div class="detail-heading">{status}<p class="eyebrow">{esc(p['category'])} / {esc(p['meat'])}</p><h1>{esc(p['name'])}</h1></div><figure class="detail-visual"><img class="detail-packshot" src="{p['image']}" width="800" height="800" alt="{esc(p['name'])}"><figcaption>{caption}</figcaption></figure><div class="detail-copy">{facts}<div class="detail-actions">{btn(action,request_url(p['id'],'specification') if concept else 'where-to-buy.html?product='+p['id'])}<a class="text-link" href="{request_url(p['id'])}">Условия поставки {arrow()}</a></div>{buyer}{info}{original}{serving}</div></section><section class="related-section"><div class="section wrap"><div class="section-heading"><h2>А ещё к столу…</h2>{btn('Весь каталог','catalogue.html')}</div><div class="product-grid featured">{cards(more)}</div></div></section>'''
 description=p['description']+' Информация о концепте и контакт для уточнения начала продаж.' if concept else f'{p["name"]}, {p["weight"]}. {p["meat"]}, замороженный продукт в контейнере. Фото упаковки, информация о продукте и поиск покупки.'
 page(p['url'],p['name'],details,'catalogue.html',desc=description)

about=crumb('О Новоферме')+f'''<section class="about-hero"><div class="wrap split"><div class="reveal"><p class="eyebrow">Это Новоферма</p><h1>Вкусно,<br>когда<br><em>вместе.</em></h1></div><div class="about-intro reveal"><p>Новоферма — компания из Санкт-Петербурга. Мы производим замороженные полуфабрикаты из курицы и индейки.</p><p>Котлеты и биточки, фрикадельки, наггетсы, куриный попкорн и стрипсы — выбирайте свой вкус.</p></div></div></section><section class="wrap section about-editorial"><figure class="reveal editorial-photo"><img src="assets/catalogue/frikadelki-klassicheskie.webp" width="900" height="900" alt="Прозрачный контейнер фрикаделек Новофермы — фото из каталога производителя" loading="lazy"><figcaption>Фото из каталога производителя</figcaption></figure><div class="reveal"><p class="eyebrow">Прозрачная упаковка</p><h2>Продукт,<br>который видно.</h2><p>Упаковываем продукты в прозрачные контейнеры: содержимое видно до покупки.</p><p>По информации компании, в основе продукции — охлаждённое мясо птицы, а на производстве используется австрийское и итальянское оборудование.</p>{btn('Смотреть продукты','catalogue.html')}</div></section><section class="brand-character" aria-labelledby="character-heading"><div class="wrap brand-character-inner"><div class="brand-character-heading"><p class="eyebrow">Наши герои</p><h2 id="character-heading">С характером.<br>И аппетитом.</h2></div><p class="brand-character-copy">Наши курочки добавляют упаковке характер, а знакомым вкусам — немного домашнего тепла.</p><img class="brand-character-art" src="{asset_url('assets/product-hero/running-mascot-v2.webp')}" width="1254" height="1254" loading="lazy" decoding="async" alt="Фирменная курочка Новофермы в клетчатом фартуке расправляет крылья"></div></section>{contactband('about')}'''
page('about.html','О нас',about,'about.html')

retailer_file=SITE/'retailers.json'
retailers=json.loads(retailer_file.read_text()) if retailer_file.exists() else []
where=crumb('Где купить')+where_section(catalogue_products,retailers,arrow)
page('where-to-buy.html','Где купить',where,'where-to-buy.html')

partners=crumb('Партнёрам')+partners_section(catalogue_products,arrow,asset_url)
page('partners.html','Партнёрам',partners,'partners.html',desc='Новоферма для розницы, HoReCa и собственной торговой марки: основной ассортимент, материалы закупщику, спецификации и запрос условий поставки.')
private_label=crumb('<a href="partners.html">Партнёрам</a> / <span aria-current="page">Собственная торговая марка</span>')+private_label_section(arrow,asset_url)
page('private-label.html','Собственная торговая марка',private_label,'partners.html',desc='Обсуждение выпуска продуктов под вашей торговой маркой: что подготовить для обсуждения, этапы согласования продукта, упаковки и условий проекта СТМ.')

contacts=crumb('Контакты')+f'''<section class="contacts-main contacts-poster" aria-labelledby="contacts-heading"><div class="wrap contact-layout"><div class="contact-content"><div class="contact-heading reveal"><h1 id="contacts-heading">Мы<br><span class="no-wrap">на связи.</span></h1></div><div class="contact-groups"><section class="contact-group reveal" aria-labelledby="contact-buyers"><div class="contact-audience"><h2 id="contact-buyers">Покупателям</h2><p>О продуктах и точках продаж.</p></div><div class="contact-links"><a class="contact-email" href="mailto:info@novoferma.ru">info@novoferma.ru {arrow()}</a><a class="contact-phone" href="tel:+78129155454">+7 (812) 915-54-54</a></div></section><section class="contact-group reveal" aria-labelledby="contact-partners"><div class="contact-audience"><h2 id="contact-partners">Партнёрам</h2><p>Ассортимент и условия поставки.</p></div><div class="contact-links"><a class="contact-email" href="mailto:zakaz@novoferma.ru">zakaz@novoferma.ru {arrow()}</a><a class="contact-phone" href="tel:+79312135550">+7 (931) 213-55-50</a></div></section></div><a class="contact-map" href="https://yandex.ru/maps/?text=Санкт-Петербург%20Горелово%20Заречная%202" target="_blank" rel="noopener"><span>Открыть адрес на карте</span>{arrow()}</a></div></div><img class="contacts-mascot" src="{asset_url('assets/mascot-contact-restored-v2.webp')}" width="980" height="1605" decoding="async" alt="" aria-hidden="true"></section><section class="wrap requisites"><p class="eyebrow">Реквизиты компании</p><div><strong>ООО «НОВОФЕРМА»</strong><p>ИНН 7807396385<br>ОГРН 1147847409148</p></div><div><strong>Адрес компании</strong><p>198323, Санкт-Петербург,<br>ул. Заречная (тер. Горелово), д. 2</p></div></section>'''
page('contacts.html','Контакты',contacts,'contacts.html')
(SITE/'site-manifest.json').write_text(json.dumps({'pages':['index.html','catalogue.html','about.html','where-to-buy.html','partners.html','private-label.html','contacts.html']+[p['url'] for p in catalogue_products],'products':products,'novelties':catalogue_products[len(products):],'publicUrl':PUBLIC_URL or None},ensure_ascii=False,indent=2))
routes=['index.html','catalogue.html','about.html','where-to-buy.html','partners.html','private-label.html','contacts.html']+[p['url'] for p in catalogue_products]
if PUBLIC_URL:
 (SITE/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join(f'<url><loc>{esc(PUBLIC_URL+"/"+route)}</loc></url>' for route in routes)+'</urlset>')
 (SITE/'robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: '+PUBLIC_URL+'/sitemap.xml\n')
else:
 for generated in ['sitemap.xml','robots.txt']:
  (SITE/generated).unlink(missing_ok=True)
print(f'Generated {len(routes)} pages, {len(products)} catalogue products and 2 concepts')
