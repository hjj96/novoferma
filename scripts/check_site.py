"""Portable checks of the generated site. Browser acceptance is separate."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import json,re
ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / 'output/concept'
manifest = json.loads((SITE/'site-manifest.json').read_text())
errors = []
def check(ok, message):
    if not ok: errors.append(message)
class Document(HTMLParser):
    def __init__(self, source):
        super().__init__()
        self.nodes=[]; self.ids=[]; self.title=''; self.in_title=False; self.text=[]
        self.feed(source)
    def handle_starttag(self, tag, attrs):
        a=dict(attrs); self.nodes.append((tag,a))
        if a.get('id'): self.ids.append(a['id'])
        if tag=='title': self.in_title=True
    def handle_endtag(self, tag):
        if tag=='title': self.in_title=False
    def handle_data(self,data):
        self.text.append(data)
        if self.in_title: self.title+=data
pages=manifest['pages']
check(len(pages)==len(set(pages)), 'Duplicate manifest pages')
inventory=manifest['products']+manifest.get('novelties',[])
check(len(pages)==6+len(inventory), 'Incorrect route count')
docs={name:Document((SITE/name).read_text()) for name in pages}
titles=[]; descriptions=[]; references=0; images=0
for name,doc in docs.items():
    titles.append(doc.title)
    check(len(doc.ids)==len(set(doc.ids)), f'{name}: duplicate IDs')
    check(sum(tag=='h1' for tag,a in doc.nodes)==1, f'{name}: exactly one h1 required')
    check(any(tag=='html' and a.get('lang')=='ru' for tag,a in doc.nodes), f'{name}: language')
    desc=[a.get('content','') for tag,a in doc.nodes if tag=='meta' and a.get('name')=='description']
    check(len(desc)==1 and len(desc[0])>=40, f'{name}: description')
    descriptions.extend(desc)
    check(any(tag=='link' and a.get('rel')=='icon' for tag,a in doc.nodes), f'{name}: favicon')
    for tag,a in doc.nodes:
        if a.get('aria-current')=='page' and tag=='a':
            check(urlsplit(a.get('href','')).path==name, f'{name}: incorrect aria-current')
        if tag=='img':
            images+=1
            check('alt' in a, f'{name}: image alt')
            check(a.get('width','').isdigit() and a.get('height','').isdigit(), f'{name}: image dimensions')
            if a.get('srcset'): check(bool(a.get('sizes')), f'{name}: srcset sizes')
        refs=[a[k] for k in ('src','href','data-src','poster') if a.get(k)]
        for key in ('srcset','data-srcset'):
            refs += [entry.strip().split()[0] for entry in a.get(key,'').split(',') if entry.strip()]
        for ref in refs:
            p=urlsplit(ref)
            if p.scheme or p.netloc: continue
            references+=1; target=unquote(p.path) or name
            check((SITE/target).is_file(), f'{name}: missing {target}')
            if p.fragment and target in docs: check(unquote(p.fragment) in docs[target].ids, f'{name}: fragment {ref}')
        if tag=='a' and a.get('target')=='_blank':
            check('noopener' in a.get('rel',''), f'{name}: external opener')
check(len(titles)==len(set(titles)), 'Duplicate titles')
check(len(descriptions)==len(set(descriptions)), 'Duplicate descriptions')
check(sum('product-card' in a.get('class','').split() for tag,a in docs['catalogue.html'].nodes)==len(inventory), 'Catalogue count')
catalogue_ids=[a.get('data-product-id') for tag,a in docs['catalogue.html'].nodes if tag=='article' and 'product-card' in a.get('class','').split()]
check(catalogue_ids==[p['id'] for p in inventory], 'Catalogue product identity and order')
for product in manifest.get('novelties',[]):
    slug=product['id']
    source=(SITE/f'product-{slug}.html').read_text()
    check('Новинка' in source and 'Внешний вид упаковки' in source, f'{slug}: product presentation')
    check('Где купить' in source, f'{slug}: purchase action')
for name in pages:
    source=(SITE/name).read_text().lower()
    check(not any(marker in source for marker in ('концепт', 'в разработке', 'готовим к выпуску', 'после утверждения продукта')), f'{name}: development language is visible')
home=docs['index.html']
home_source=(SITE/'index.html').read_text()
hero_sections=[a for tag,a in home.nodes if tag=='section' and 'data-popsy-hero' in a]
check(len(hero_sections)==1 and 'popsy-home-hero' in hero_sections[0].get('class','').split(), 'Home requires one Popсы hero section')
hero_markup=re.search(r'<section\b[^>]*\bdata-popsy-hero\b[^>]*>(.*?)</section>', home_source, re.S)
hero=Document(hero_markup.group(1) if hero_markup else '')
hero_headings=[a for tag,a in hero.nodes if tag=='h1']
check(len(hero_headings)==1 and hero_headings[0].get('id')=='popsy-home-title', 'Popсы hero requires its live h1')
heading_markup=re.search(r'<h1\b[^>]*\bid="popsy-home-title"[^>]*>(.*?)</h1>', home_source, re.S)
check(bool(heading_markup) and ''.join(Document(heading_markup.group(1)).text).strip().casefold()=='попсы', 'Popсы hero title must be live text')
check(all('hidden' not in a and 'inert' not in a and a.get('aria-hidden')!='true' and 'sr-only' not in a.get('class','').split() for a in hero_sections+hero_headings), 'Popсы hero and title must be visible without JavaScript')
for cls,filename in (('popsy-home-pack','pack.webp'),('popsy-home-food','food.webp')):
    artwork=[a for tag,a in hero.nodes if tag=='img' and cls in a.get('class','').split()]
    check(len(artwork)==1, f'Popсы hero requires one {cls} image')
    check(all(urlsplit(a.get('src','')).path==f'assets/popsy-home/{filename}' and not a.get('data-src') and a.get('loading')!='lazy' for a in artwork), f'{cls} must have real, eager artwork without JavaScript')
check(sum(tag=='img' and 'ui-icon' not in a.get('class','').split() for tag,a in hero.nodes)==2, 'Popсы hero contains only the package and ready-food artwork, plus UI icons')
hero_ctas=[a for tag,a in hero.nodes if tag=='a' and 'popsy-home-cta' in a.get('class','').split()]
check(len(hero_ctas)==1 and hero_ctas[0].get('href')=='product-popsy.html', 'Popсы hero CTA must open its product page')
check('Хрусти' in ''.join(hero.text) and 'ритме' in ''.join(hero.text), 'Popсы hero handwritten phrase must be live text')
check('Мини-наггетсы' in ''.join(hero.text) and 'панировке' in ''.join(hero.text), 'Popсы hero description must be live text')
for tag,key,filename in (('link','href','popsy-home.css'),('script','src','popsy-home.js')):
    check(any(t==tag and urlsplit(a.get(key,'')).path==filename for t,a in home.nodes), f'Home must load {filename}')
check(not any('data-product-carousel' in a or a.get('role') in ('tab','tablist','tabpanel') or {'product-scene','product-pickers','product-picker'}&set(a.get('class','').split()) for tag,a in home.nodes), 'Home must not retain carousel scenes or ghost tabs')
check('product-naggetsy-kurinye.html' in pages and 'naggetsy-kurinye' in catalogue_ids, 'Nuggets must remain available in the catalogue')
check(not any('title-art' in a.get('class','') for tag,a in home.nodes), 'Raster hero title remains')
where=(SITE/'where-to-buy.html').read_text()
product_select=re.search(r'<select\b[^>]*\bid="wanted-product"[^>]*>(.*?)</select>',where,re.S)
selected_ids=re.findall(r'<option\b[^>]*\bvalue="([^"]+)"',product_select.group(1)) if product_select else []
check(set(selected_ids)=={p['id'] for p in inventory}, 'Purchase form product inventory')
check('data-city-copy' in where and 'data-city-draft' in where, 'City copy fallback')
check('data-retailer-products' in where, 'Retailer links')
public_url=manifest.get('publicUrl')
if public_url:
    for name,doc in docs.items():
        check(any(tag=='link' and a.get('rel')=='canonical' and a.get('href')==public_url+'/'+name for tag,a in doc.nodes), f'{name}: canonical')
    check((SITE/'sitemap.xml').is_file() and (SITE/'robots.txt').is_file(), 'Production discovery files')
else:
    check(not any(a.get('rel')=='canonical' for d in docs.values() for tag,a in d.nodes), 'Preview must not guess canonical domain')
report={'pages':len(pages),'images':images,'localReferences':references,'uniqueTitles':len(set(titles)),
 'uniqueDescriptions':len(set(descriptions)),'publicUrl':public_url,'errors':errors,'result':'pass' if not errors else 'fail',
 'scope':'Generated source only; visual and interactive browser checks are separate.'}
target=ROOT/'output/research/implementation-2026-10-24/static-checks.json'
target.parent.mkdir(parents=True,exist_ok=True)
target.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False,indent=2))
raise SystemExit(bool(errors))

