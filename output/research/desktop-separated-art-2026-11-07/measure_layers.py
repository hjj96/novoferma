"""Measure visible bitmap boundaries in the same virtual canvas used by the hero."""
from pathlib import Path
from PIL import Image, ImageFilter, ImageOps, ImageChops
import hashlib, json, math
ROOT=Path(__file__).resolve().parents[3]
ASSETS=ROOT/'output/concept/assets/product-hero/desktop-v8'
REPORT=Path(__file__).parent/'after'
layout=json.loads((ASSETS/'layout.json').read_text())
def mask(entry,threshold):
    alpha=Image.open(ROOT/'output/concept'/entry['path']).getchannel('A').crop(entry['bbox'])
    alpha=alpha.resize((round(entry['width']),round(entry['height'])),Image.Resampling.LANCZOS)
    if entry.get('flip'): alpha=ImageOps.mirror(alpha)
    board=Image.new('L',tuple(layout['canvas']))
    board.paste(alpha,(round(entry['x']),round(entry['y'])))
    return board.point(lambda a:255 if a>=threshold else 0)
def points(im):
    e=im.filter(ImageFilter.FIND_EDGES); w=e.width
    return [(i%w,i//w) for i,v in enumerate(e.tobytes()) if v][::2]
def tree(p,depth=0):
    if not p:return None
    axis=depth%2;p.sort(key=lambda x:x[axis]);mid=len(p)//2
    return p[mid],axis,tree(p[:mid],depth+1),tree(p[mid+1:],depth+1)
def nearest(t,p,best=1e12):
    if t is None:return best
    q,a,left,right=t;delta=p[a]-q[a]
    best=min(best,(p[0]-q[0])**2+(p[1]-q[1])**2)
    near,far=(left,right) if delta<0 else (right,left)
    best=nearest(near,p,best)
    if delta*delta<best:best=nearest(far,p,best)
    return best
rows=[]
for name,p in layout['products'].items():
    row={'product':name,'canvas':layout['canvas'],'foodBottom':round(p['food']['pieces'][0]['y']+p['food']['pieces'][0]['height'],1),'henBottom':round(p['hen']['y']+p['hen']['height'],1),'thresholds':{}}
    for threshold in (64,160):
        f=mask(p['food']['pieces'][0],threshold);h=mask(p['hen'],threshold)
        overlap=ImageChops.multiply(f,h).getbbox();t=tree(points(h));gap=math.sqrt(min(nearest(t,point) for point in points(f)))
        row['thresholds'][threshold]={'overlap':overlap,'approxMinGapVirtualPx':round(gap,1),'approxMinGapAt740pxFrame':round(gap*740/layout['canvas'][0],1)}
    rows.append(row)
(REPORT/'pixel-gaps.json').write_text(json.dumps({'method':'RGBA alpha mask boundary KD tree, every second edge pixel; approximate distance, not a browser overlap check','products':rows},ensure_ascii=False,indent=2))
protected=json.loads((Path(__file__).parent/'before/protected-hashes.json').read_text())
protected.pop('output/concept/product-hero.js',None)
hashes={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==expected for p,expected in protected.items()}
(REPORT/'protected-assets.json').write_text(json.dumps(hashes,ensure_ascii=False,indent=2))
print(json.dumps(rows,ensure_ascii=False,indent=2));print('Protected mobile/brush unchanged',all(hashes.values()))
