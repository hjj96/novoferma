from pathlib import Path
from collections import deque
from PIL import Image, ImageDraw, ImageFilter
import numpy as np
import json
import sys

BASE=Path('/Users/andrey/Documents/ChatGPT/сайт нф')
SOURCE=BASE/'output/concept/assets/catalogue'
OUT=BASE/'output/concept/assets/catalogue-cutout';OUT.mkdir(exist_ok=True)
QA=BASE/'tmp/pdfs';QA.mkdir(exist_ok=True)

def flooded_exterior(a):
    ch=a.max(2)-a.min(2)
    possible=(a.min(2)>240)|(ch<12)
    h,w=possible.shape;exterior=np.zeros((h,w),bool)
    q=deque([(0,0)]);exterior[0,0]=True
    while q:
        y,x=q.popleft()
        for yy,xx in [(y-1,x),(y+1,x),(y,x-1),(y,x+1)]:
            if 0<=yy<h and 0<=xx<w and possible[yy,xx] and not exterior[yy,xx]:
                exterior[yy,xx]=True;q.append((yy,xx))
    return exterior

def blur_array(a,radius):
    return np.asarray(Image.fromarray(np.uint8(np.clip(a,0,255))).filter(ImageFilter.GaussianBlur(radius)),dtype=float)

def cutout(p):
    im=Image.open(p).convert('RGB');a=np.asarray(im,dtype=float)
    mask=Image.fromarray(np.uint8(~flooded_exterior(a))*255)
    # Close small discontinuities in the transparent tub, then remove isolated raster edge noise.
    mask=mask.filter(ImageFilter.MaxFilter(7)).filter(ImageFilter.MinFilter(7))
    mask=mask.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.MaxFilter(3))
    # The low-chroma plastic bottom fades into a shadow; smooth this contour rather than thresholding noisy pixels.
    smooth=np.asarray(mask.filter(ImageFilter.GaussianBlur(4)),dtype=float)>128
    hard=np.asarray(mask).copy()
    hard[700:]=smooth[700:]*255
    mask=Image.fromarray(hard)
    core=mask.filter(ImageFilter.MinFilter(7))
    inner=np.asarray(core,dtype=float)/255
    near=mask.filter(ImageFilter.MaxFilter(9))
    near_a=np.asarray(near,dtype=float)/255
    weight=blur_array(inner*255,3)/255
    foreground=np.zeros_like(a)
    for c in range(3):
        foreground[:,:,c]=blur_array(a[:,:,c]*inner,3)/np.maximum(weight,.001)
    foreground=np.clip(foreground,0,255)
    dc=255-a;df=255-foreground
    edge_alpha=np.sum(dc*df,2)/np.maximum(np.sum(df*df,2),1)
    edge_alpha=np.clip(edge_alpha,0,1)
    edge_alpha=np.where(inner>.99,1,edge_alpha)
    # Existing soft shadow is neutral/low-chroma and edge-connected. Recover it from white.
    shadow_color=np.array([60.,44.,33.])
    shadow_df=255-shadow_color
    shadow_alpha=np.sum(dc*shadow_df,2)/np.sum(shadow_df*shadow_df)
    shadow_alpha=np.clip(shadow_alpha,0,.72)
    shadow_alpha[shadow_alpha<.008]=0
    # Use genuine edge foreground within silhouette's antialias transition; use shadow farther out.
    blend=np.asarray(mask.filter(ImageFilter.GaussianBlur(1.25)),dtype=float)/255
    # Core + 1px antialias ring estimates foreground, exterior recovers original shadow.
    edge_zone=np.asarray(mask.filter(ImageFilter.GaussianBlur(.85)),dtype=float)/255
    alpha=edge_alpha*edge_zone + shadow_alpha*(1-edge_zone)
    # The matte is recovered from the original white composite, removing all white fringe.
    rgb=(a-255*(1-alpha[:,:,None]))/np.maximum(alpha[:,:,None],.001)
    rgb=np.clip(rgb,0,255)
    # Outer near-neutral shadow must remain dark on both cream and dark backgrounds.
    rgb=np.where((edge_zone<.01)[:,:,None],shadow_color[None,None,:],rgb)
    rgba=np.dstack([rgb,alpha*255]).astype('uint8')
    rgba[alpha<.008,:3]=0
    result=Image.fromarray(rgba)
    # Bound from core at fixed 736px width, then keep full softened shadow underneath.
    bbox=mask.getbbox();x0,y0,x1,y1=bbox
    scale=min(736/(x1-x0),680/(y1-y0),1)
    scaled=result.resize((round(im.width*scale),round(im.height*scale)),Image.Resampling.LANCZOS)
    # Common top and baseline produce an aligned catalogue; original objects are already near-equal.
    obj_cx=(x0+x1)/2*scale
    obj_cy=(y0+y1)/2*scale
    tx=round(400-obj_cx);ty=round(390-obj_cy)
    canvas=Image.new('RGBA',(800,800));canvas.alpha_composite(scaled,(tx,ty))
    target=OUT/p.name;canvas.save(target,format='WEBP',lossless=True,quality=100,method=6)
    return {'file':p.name,'sourceSize':im.size,'size':[800,800],'objectBox':bbox,'scale':scale,'alphaBox':canvas.getchannel('A').getbbox(),'bytes':target.stat().st_size}

files=[p for p in sorted(SOURCE.glob('*.webp')) if '-serving' not in p.stem]
records=[]
if len(sys.argv)>1: files=[p for p in files if p.stem==sys.argv[1]]
for p in files:
    rec=cutout(p);records.append(rec);print(p.name,rec['objectBox'],rec['alphaBox'],flush=True)
(OUT/'manifest.json').write_text(json.dumps({'source':'Official novoferma.ru product catalogue photos','canvas':[800,800],'count':len(records),'files':records},indent=2)+'\n')

# Quality sheets show every alpha over both brand cream and brand chocolate.
for theme,bg in [('cream',(253,245,226)),('dark',(62,33,19))]:
    cols=4;tilew=310;tileh=350;rows=(len(files)+cols-1)//cols
    sheet=Image.new('RGB',(cols*tilew,rows*tileh),bg)
    for i,p in enumerate(files):
        im=Image.open(OUT/p.name).convert('RGBA');im.thumbnail((300,300),Image.Resampling.LANCZOS)
        x=(i%cols)*tilew;y=(i//cols)*tileh
        sheet.paste(im,(x+5,y+5),im)
        txt=p.stem.replace('naggetsy','nagg.').replace('kotlety','kotl.')
        ImageDraw.Draw(sheet).text((x+10,y+310),txt,fill=(62,33,19) if theme=='cream' else (253,245,226))
    sheet.save(QA/('catalogue-cutout-'+theme+'.jpg'),quality=96)
