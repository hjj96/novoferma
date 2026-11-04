from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
from collections import Counter
import json,re,hashlib,gzip
from PIL import Image
OUT=Path('/Users/andrey/Desktop/сайт нф/output/research/strict-audit-2026-10-16')
ROOT=OUT/'snapshot'
VOID=set('area base br col embed hr img input link meta param source track wbr'.split())
class Parser(HTMLParser):
 def __init__(self):
  super().__init__();self.nodes=[];self.stack=[]
 def handle_starttag(self,tag,attrs):
  n={'tag':tag,'a':dict(attrs),'line':self.getpos()[0],'col':self.getpos()[1],'text':'','children':[]};self.nodes.append(n)
  if self.stack:self.stack[-1]['children'].append(n)
  if tag not in VOID:self.stack.append(n)
 def handle_endtag(self,tag):
  for i in range(len(self.stack)-1,-1,-1):
   if self.stack[i]['tag']==tag:self.stack=self.stack[:i];break
 def handle_data(self,data):
  for n in self.stack:n['text']+=data
 def select(self,tag=None,attr=None):return [n for n in self.nodes if (not tag or n['tag']==tag) and (not attr or attr in n['a'])]
def local(path,ref):
 u=urlsplit(ref)
 if u.scheme or u.netloc:return None
 if not u.path:return path
 return (path.parent/unquote(u.path)).resolve()
def asset(p):
 o={'path':str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p),'bytes':p.stat().st_size,'gzip_bytes':len(gzip.compress(p.read_bytes()))}
 try:
  with Image.open(p) as im:o['image_dimensions']=list(im.size)
 except Exception:pass
 return o
def closure_css(files):
 seen=set();refs=set()
 def read(p):
  if p in seen or not p.exists():return
  seen.add(p)
  for ref in re.findall(r'url\(\s*[\'\"]?([^\)\'\"]+)',p.read_text()):
   q=local(p,ref)
   if q:
    if q.suffix=='.css':read(q)
    else:refs.add(q)
 for p in files:read(p)
 return seen,refs
pages=[p for p in sorted(ROOT.glob('*.html')) if p.name not in ['loading-concept.html','loading-story.html','typography-specimen.html']]
parsers={p:Parser() for p in pages}
for p,x in parsers.items():x.feed(p.read_text())
report={'date':'2026-10-16','scope':'20 current main pages. Static source inspection only; no browser, deployment, field metrics or full compliance certification.','pages':[],'broken_local_references':[],'broken_fragment_references':[]}
all_direct=set();all_css=set();all_css_refs=set()
for p,x in parsers.items():
 def get(tag):return x.select(tag)
 ids=Counter(n['a']['id'] for n in x.select(attr='id'))
 refs=[]
 for n in x.nodes:
  for key in ['src','href']:
   if key not in n['a']:continue
   ref=n['a'][key];q=local(p,ref)
   if not q:continue
   refs.append(q)
   if not q.exists():report['broken_local_references'].append({'page':p.name,'line':n['line'],'tag':n['tag'],'ref':ref})
   frag=unquote(urlsplit(ref).fragment)
   if frag and q in parsers and frag not in {n['a']['id'] for n in parsers[q].select(attr='id')}:
    report['broken_fragment_references'].append({'page':p.name,'line':n['line'],'ref':ref})
 css=[local(p,n['a']['href']) for n in get('link') if n['a'].get('rel')=='stylesheet'];css,cssrefs=closure_css(css)
 direct={q for q in refs if q.exists() and q.suffix!='.html'};all_direct|=direct;all_css|=css;all_css_refs|=cssrefs
 metas={n['a'].get('name',n['a'].get('property','')):n['a'].get('content') for n in get('meta')}
 ims=[]
 for n in get('img'):
  a=n['a'];q=local(p,a.get('src',''));im={'src':a.get('src'),'alt':a.get('alt'),'loading':a.get('loading','eager'),'width':a.get('width'),'height':a.get('height'),'fetchpriority':a.get('fetchpriority'),'srcset':a.get('srcset'),'line':n['line']}
  if q and q.exists():im.update(asset(q))
  ims.append(im)
 forms=[]
 for n in get('form'):forms.append({'attributes':n['a'],'text':n['text'],'line':n['line']})
 controls=[{'tag':n['tag'],'attributes':n['a'],'line':n['line']} for n in x.nodes if n['tag'] in ['input','textarea','select']]
 headings=[{'tag':n['tag'],'text':n['text'],'line':n['line']} for n in x.nodes if n['tag'] in ['h1','h2','h3','h4','h5','h6']]
 o={'page':p.name,'bytes':p.stat().st_size,'title':[n['text'] for n in get('title')],'lang':get('html')[0]['a'].get('lang'),'meta':metas,'links':[n['a'] for n in get('link')],'h1':[n['text'] for n in get('h1')],'headings':headings,'duplicate_ids':[k for k,v in ids.items() if v>1],'main_count':len(get('main')),'skip_link':any(n['a'].get('class')=='skip-link' for n in get('a')),'jsonld':[n['text'] for n in get('script') if n['a'].get('type')=='application/ld+json'],'css':[asset(q) for q in sorted(css)],'scripts':[n['a'] for n in get('script')],'images':ims,'image_bytes_unique':sum(q.stat().st_size for q in {local(p,n['a']['src']) for n in get('img')} if q and q.exists()),'eager_image_bytes_unique':sum(q.stat().st_size for q in {local(p,n['a']['src']) for n in get('img') if n['a'].get('loading')!='lazy'} if q and q.exists()),'css_bytes':sum(q.stat().st_size for q in css),'js_bytes':sum(q.stat().st_size for q in {local(p,n['a']['src']) for n in get('script') if 'src' in n['a']} if q and q.exists()),'forms':forms,'controls':controls,'links_external':[n['a']['href'] for n in get('a') if urlsplit(n['a'].get('href','')).scheme in ['https','http']],'nav_current':[{'href':n['a'].get('href'),'text':n['text'],'current':n['a']['aria-current']} for n in x.select(attr='aria-current')]}
 report['pages'].append(o)
report['all_direct_assets']=[asset(q) for q in sorted(all_direct)]
report['all_css_resources']=[asset(q) for q in sorted(all_css_refs) if q.exists()]
report['css_stats']=[{'path':q.name,'bytes':q.stat().st_size,'important_count':q.read_text().count('!important'),'rules_approx':q.read_text().count('{'),'media_count':q.read_text().count('@media'),'font_faces':q.read_text().count('@font-face')} for q in sorted(all_css)]
report['totals']={'pages':len(pages),'assets_on_disk':sum(1 for p in ROOT.rglob('*') if p.is_file()),'bytes_on_disk':sum(p.stat().st_size for p in ROOT.rglob('*') if p.is_file()),'direct_asset_count':len(all_direct),'direct_asset_bytes':sum(q.stat().st_size for q in all_direct),'all_css_bytes':sum(q.stat().st_size for q in all_css),'referenced_css_resource_bytes':sum(q.stat().st_size for q in all_css_refs if q.exists()),'image_instances':sum(len(p['images']) for p in report['pages']),'images_missing_alt':sum(i['alt'] is None for p in report['pages'] for i in p['images']),'images_missing_dimensions':sum(not i['width'] or not i['height'] for p in report['pages'] for i in p['images']),'images_with_srcset':sum(bool(i['srcset']) for p in report['pages'] for i in p['images'])}
(OUT/'technical-inventory.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps(report['totals'],ensure_ascii=False,indent=2))
print('broken files',report['broken_local_references']);print('broken fragments',report['broken_fragment_references'])
for p in report['pages']:print(p['page'],len(p['css']),p['css_bytes'],p['js_bytes'],p['image_bytes_unique'],p['eager_image_bytes_unique'],len(p['images']),len(p['jsonld']))
print('CSS',report['css_stats'])
