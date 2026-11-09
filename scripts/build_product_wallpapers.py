"""Compose catalogue artwork unchanged; render the HTML originals in Chrome.

This file writes layout code and embeds source bytes. It does not regenerate,
retouch, repaint, sharpen, or retype any part of a package.
"""
from pathlib import Path
import base64
import json
import math
import hashlib
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output/product-wallpapers-2026-11-07'
DEST = OUT / 'source-compositions'
DEST.mkdir(exist_ok=True)
manifest_path = OUT / 'references/high-res-manifest.json'
if not manifest_path.exists():
    manifest_path = OUT / 'references/manifest.json'
inventory = json.loads(manifest_path.read_text())
products = inventory['products'] if isinstance(inventory, dict) else inventory

for p in products:
    source = Path(p['path'])
    with Image.open(source) as im:
        p['width'], p['height'] = im.size
        bounds = p.get('alpha_bbox_64') or im.getchannel('A').getbbox()
        # Keep a small transparent margin around physical artwork. The native
        # images contain faint alpha noise far outside the real package.
        p['alpha_bbox'] = [max(0,bounds[0]-8), max(0,bounds[1]-8),
                           min(im.width,bounds[2]+8), min(im.height,bounds[3]+8)]
    mime = 'image/png' if source.suffix == '.png' else 'image/webp'
    p['data_uri'] = f'data:{mime};base64,' + base64.b64encode(source.read_bytes()).decode()

# Irregular staggered anchors, broad rotations, and edge crops create a field.
anchors = [
    (.091,.151,-17),(.251,.177,14),(.416,.138,-10),
    (.580,.178,22),(.741,.142,-18),(.903,.177,12),
    (.128,.455,20),(.310,.530,-14),(.493,.465,11),
    (.679,.555,-23),(.872,.475,19),
    (.086,.820,-13),(.250,.865,21),(.414,.805,-20),
    (.577,.870,12),(.744,.820,-12),(.912,.860,18),
]
diagonal_anchors = [
    (.100,.170,-27),(.302,.145,14),(.505,.178,-18),
    (.708,.150,24),(.903,.180,-31),
    (.195,.405,22),(.412,.393,-12),(.628,.425,32),(.838,.405,-17),
    (.096,.645,18),(.310,.645,-34),(.535,.655,16),(.760,.638,-23),
    (.201,.865,-15),(.429,.871,21),(.661,.858,-19),(.900,.850,29),
]
edge_anchors = [
    (-.060,.075,32),(.091,-.108,-28),(.349,-.115,143),
    (.641,-.100,-33),(.930,-.115,158),(1.063,.323,-30),
    (-.059,.650,32),(1.058,.848,-148),(.065,1.135,32),
    (.345,1.115,-155),(.635,1.125,34),(.937,1.145,-26),
]

themes = [
    dict(id='01-cream-original-art', width=3840, height=2160,
         colors=('#fff9ea','#f1dfbf'), shadow='84,49,19',
         order=[0,5,2,16,9,6,10,3,14,8,4,11,1,15,12,13,7], shift=0),
    dict(id='02-orange-original-art', width=3840, height=2160,
         colors=('#ffa33c','#ef7015'), shadow='91,33,0',
         order=[12,7,2,9,8,0,1,6,14,10,5,3,15,16,11,13,4], shift=1),
    dict(id='03-chocolate-original-art', width=3840, height=2160,
         colors=('#68432b','#392419'), shadow='8,3,0',
         order=[4,14,8,1,12,16,10,6,2,9,3,0,15,13,7,11,5], shift=2),
]

def pack_markup(p, x, y, body_width, angle, theme, rank, edge=False):
    x0,y0,x1,y1 = p['alpha_bbox']
    scale = body_width / (x1-x0)
    w,h = (x1-x0)*scale, (y1-y0)*scale
    tilt = 0 if edge else [-3,2,0,3,-2][rank%5]
    inner = (f'width:{w:.3f}px;height:{h:.3f}px;'
             f'transform:perspective(2600px) rotate({angle}deg) rotateY({tilt}deg);')
    image = (f'width:{p["width"]*scale:.3f}px;height:{p["height"]*scale:.3f}px;'
             f'left:{-x0*scale:.3f}px;top:{-y0*scale:.3f}px;')
    return (f'<div class="pack" data-product="{p["id"]}" '
            f'data-core="{str(not edge).lower()}" '
            f'style="left:{x-w/2:.3f}px;top:{y-h/2:.3f}px;'
            f'width:{w:.3f}px;height:{h:.3f}px;z-index:{rank}">'
            f'<div class="crop" style="{inner}">'
            f'<img draggable="false" alt="" src="{p["data_uri"]}" style="{image}">'
            f'</div></div>')

all_records = []
for theme in themes:
    W,H = theme['width'],theme['height']
    records, parts = [], []
    for i,(x,y,a) in enumerate(edge_anchors):
        p = products[(i*5+theme['shift']*3)%17]
        bw = W * (.142 if i%2 else .151)
        parts.append(pack_markup(p,x*W,y*H,bw,a,theme,i,True))
        records.append(dict(id=p['id'],core=False,x=x,y=y,width=bw,angle=a))
    selected_anchors = diagonal_anchors if theme['shift']==2 else anchors
    for i,(x,y,a) in enumerate(selected_anchors):
        p = products[theme['order'][i]]
        # Unequal sizes and tiny positional offsets keep the staggered rhythm loose.
        widths = [.155,.160,.156,.160,.156,.153] if theme['shift']!=2 else [.145,.150,.147,.153,.148,.145]
        bw = W * widths[(i+theme['shift'])%6]
        if theme['shift']:
            x += math.sin(i*2.1+theme['shift'])*.007
            y += math.cos(i*1.9+theme['shift'])*.009
            a = -a + [2,-4,6,-2,3][i%5]
        parts.append(pack_markup(p,x*W,y*H,bw,a,theme,30+i))
        records.append(dict(id=p['id'],core=True,x=x,y=y,width=bw,angle=a))
    c1,c2 = theme['colors']
    doc = f'''<!doctype html><html><head><meta charset="utf-8">
<title>Novoferma — original artwork composition</title>
<style>*{{box-sizing:border-box}}html,body{{margin:0;width:{W}px;height:{H}px;overflow:hidden}}
body{{background:radial-gradient(ellipse at 16% 7%,{c1},{c2} 105%)}}
.pack{{position:absolute;filter:drop-shadow(0px 4px 3px rgba({theme['shadow']},.17)) drop-shadow(10px 20px 14px rgba({theme['shadow']},.22))}}
.crop{{position:relative;overflow:hidden;transform-origin:50% 50%}}
img{{position:absolute;display:block;max-width:none}}
</style></head><body>{''.join(parts)}</body></html>'''
    (DEST/f'{theme["id"]}.html').write_text(doc)
    all_records.append(dict(id=theme['id'],width=W,height=H,placements=records))

provenance = dict(
    method='Deterministic source-only HTML/CSS composition; original package image bytes embedded unchanged; rotations, gentle planar perspective and cast shadows only. No image generation in the corrected exports.',
    source_manifest=str(manifest_path),
    products=[{k:v for k,v in p.items() if k!='data_uri'} for p in products],
    compositions=all_records,
)
(DEST/'provenance.json').write_text(json.dumps(provenance,ensure_ascii=False,indent=2))
print(f'Built {len(themes)} source-only compositions using {len(products)} original products.')
