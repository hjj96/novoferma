"""Verify the published audit's links, structure, screenshots, and evidence files."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import re,json,hashlib,base64
BASE=Path(__file__).resolve().parent
errors=[]
for file in BASE.glob('*.json'):
    try:json.loads(file.read_text())
    except Exception as e:errors.append(str(file)+': '+str(e))
md=(BASE/'audit.md').read_text();markup=(BASE/'audit.html').read_text()
for label,target in re.findall(r'\[([^\]]*)\]\(([^)]+)\)',md+(BASE/'README.md').read_text()):
    u=urlsplit(target)
    if u.scheme or u.netloc or not u.path:continue
    if not (BASE/unquote(u.path)).resolve().exists():errors.append('Missing local link: '+target)
class Document(HTMLParser):
    def __init__(self):
        super().__init__();self.ids=[];self.images=[];self.links=[];self.h1=0;self.styles=0
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if a.get('id'):self.ids.append(a['id'])
        if tag=='img':self.images.append(a)
        if a.get('href'):self.links.append(a['href'])
        if tag=='h1':self.h1+=1
        if tag=='style':self.styles+=1
doc=Document();doc.feed(markup)
if len(set(doc.ids))!=len(doc.ids):errors.append('Duplicate HTML IDs')
errors+=['Missing HTML fragment '+x for x in doc.links if x.startswith('#') and x[1:] not in doc.ids]
if len(doc.images)!=26 or not all(i.get('src','').startswith('data:image/png;base64,') and i.get('alt') for i in doc.images):errors.append('Images not embedded and labelled')
for image,record in zip(doc.images,json.loads((BASE/'screenshot-manifest.json').read_text())['screens']):
    if hashlib.sha256(base64.b64decode(image['src'].split(',',1)[1])).hexdigest()!=record['sha256']:errors.append('Embedded image mismatch '+record['file'])
if doc.h1!=1:errors.append('Incorrect h1 count')
if doc.styles!=1:errors.append('Inline stylesheet missing')
for item in json.loads((BASE/'screenshot-manifest.json').read_text())['screens']:
    if hashlib.sha256((BASE/item['file']).read_bytes()).hexdigest()!=item['sha256']:errors.append('Screenshot changed: '+item['file'])
for phrase in ['Белок, клетчатка','Почему продажи','Метрики','СТМ','Россия:','Международные','18. Свежие','24. Карта']:
    if phrase not in md:errors.append('Missing required topic: '+phrase)
for name in ['technical-commercial.json','visual-b2b-second-pass.json','russia-research.json','global-research.json','work-plan.json','source-snapshot.json','publication.json']:
    if not (BASE/name).is_file():errors.append('Missing evidence file '+name)
previous=json.loads((BASE/'report-validation.json').read_text()) if (BASE/'report-validation.json').exists() else {}
result={'status':'pass' if not errors else 'fail','wordCount':len(md.split()),'screens':len(doc.images),'externalSourceCount':len(json.loads((BASE/'sources.json').read_text())),'h1':doc.h1,'inlineCss':doc.styles==1,'htmlImagePolicy':'26 exact accepted PNG files embedded; no external image dependencies','localLinks':'pass' if not errors else 'fail','errors':errors,'visualReview':previous.get('visualReview','pending'),'scope':'Report integrity only; website functional evidence is in technical-commercial.json and screenshot-manifest.json.'}
(BASE/'report-validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(result,ensure_ascii=False,indent=2))
raise SystemExit(bool(errors))

