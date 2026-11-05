"""Portable checks of the generated site. Browser acceptance is separate."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import argparse
import json
ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / 'output/concept'
manifest = json.loads((SITE/'site-manifest.json').read_text())
errors = []
def check(ok, message):
    if not ok: errors.append(message)
class Document(HTMLParser):
    def __init__(self, source):
        super().__init__()
        self.nodes=[]; self.ids=[]; self.title=''; self.in_title=False
        self.feed(source)
    def handle_starttag(self, tag, attrs):
        a=dict(attrs); self.nodes.append((tag,a))
        if a.get('id'): self.ids.append(a['id'])
        if tag=='title': self.in_title=True
    def handle_endtag(self, tag):
        if tag=='title': self.in_title=False
    def handle_data(self,data):
        if self.in_title: self.title+=data
pages=manifest['pages']
check(len(pages)==len(set(pages)), 'Duplicate manifest pages')
check(len(pages)==7+len(manifest['products'])+2, 'Incorrect route count')
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
check(sum('product-card' in a.get('class','').split() for tag,a in docs['catalogue.html'].nodes)==16, 'Catalogue count')
for slug in ('fibriki','lulia-mini'):
    source=(SITE/f'product-{slug}.html').read_text()
    check('Концепт новинки' in source and 'Визуальный концепт упаковки' in source, f'{slug}: concept status')
home=docs['index.html']
check(sum(tag=='img' and bool(a.get('data-src')) for tag,a in home.nodes)==3, 'Inactive hero art must defer')
check(sum(a.get('role')=='tab' for tag,a in home.nodes)==4, 'Four named tabs required')
check(not any('title-art' in a.get('class','') for tag,a in home.nodes), 'Raster hero title remains')
where=(SITE/'where-to-buy.html').read_text()
check('data-city-copy' in where and 'data-city-draft' in where, 'City copy fallback')
check('data-retailer-products' in where, 'Retailer links')
partners=docs['partners.html']
check({'partner-product','partner-intent','partner-consent','partner-request-feedback'}<=set(partners.ids), 'B2B request context and consent')
for product in manifest['products']+manifest.get('novelties',[]):
    source=(SITE/product['url']).read_text()
    check('partners.html?product='+product['id']+'&amp;intent=specification' in source, f'{product["id"]}: missing SKU specification journey')
check('private-label.html' in pages, 'Dedicated private-label journey')
check((SITE/'downloads/novoferma-supplier-catalogue.html').is_file(), 'Supplier download')
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
parser=argparse.ArgumentParser()
parser.add_argument('--report',default='output/research/design-implementation-2026-11-05/static-checks.json')
target=ROOT/parser.parse_args().report
target.parent.mkdir(parents=True,exist_ok=True)
target.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False,indent=2))
raise SystemExit(bool(errors))

