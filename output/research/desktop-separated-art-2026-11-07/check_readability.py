"""Conservative alpha-contour intersection against browser text ranges."""
from pathlib import Path
from PIL import Image, ImageOps
from urllib.parse import urlsplit
import json,math
HERE=Path(__file__).parent;ROOT=HERE.parents[2]
layout=json.loads((ROOT/'output/concept/assets/product-hero/desktop-v8/layout.json').read_text())
sources={}
for p in layout['products'].values():
 for v in [p['hen'],*p['food']['pieces'],*p['accents'],*p.get('shadows',[])]:sources[Path(v['path']).name]=v
cases=json.loads((HERE/'after/desktop-metrics.json').read_text());hits=[];clipped=[]
for case in cases:
 if case['portrait']:continue
 for l in case['layers']:
  if 'shadow' in l['class']:continue
  source=sources[Path(urlsplit(l['source']).path).name]
  if 'accent' in l['class']:
   # Rotation gives a conservative box; no text may enter even that box.
   alpha=Image.new('L',(max(1,round(l['width'])),max(1,round(l['height']))),255)
  else:
   alpha=Image.open(ROOT/'output/concept'/source['path']).getchannel('A').crop(source['bbox'])
   alpha=alpha.resize((max(1,round(l['width'])),max(1,round(l['height']))),Image.Resampling.LANCZOS)
   if l['flip']:alpha=ImageOps.mirror(alpha)
   alpha=alpha.point(lambda a:255 if a>=64 else 0)
  for r in case['textRects']+[dict(case['header'],text='HEADER')]:
   x0=max(0,math.floor(r['x']-l['x']-1));y0=max(0,math.floor(r['y']-l['y']-1))
   x1=min(alpha.width,math.ceil(r['right']-l['x']+1));y1=min(alpha.height,math.ceil(r['bottom']-l['y']+1))
   if x1>x0 and y1>y0 and alpha.crop((x0,y0,x1,y1)).getbbox():hits.append({'viewport':case['viewport'],'scene':case['scene'],'layer':Path(source['path']).name,'text':r['text']})
  if l['x']<0 or l['right']>case['viewport']['width'] or l['y']<case['stage']['y'] or l['bottom']>case['stage']['bottom']:
   clipped.append({'viewport':case['viewport'],'scene':case['scene'],'layer':Path(source['path']).name})
result={'cases':len(cases),'textOrHeaderIntersections':hits,'potentialClippingBoxes':clipped,'method':'Browser DOM text ranges plus alpha>=64 source masks; accent rotation treated as solid bounding box. 1px conservative range expansion. Layout animation translation removed. Does not measure glyph pixels or aesthetic quality.'}
(HERE/'after/readability.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print(json.dumps(result,ensure_ascii=False,indent=2))
