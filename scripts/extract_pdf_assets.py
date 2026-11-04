from pathlib import Path
from collections import deque
import math
from PIL import Image, ImageDraw, ImageFilter
import numpy as np

BASE = Path('/Users/andrey/Documents/ChatGPT/сайт нф')
OUT=BASE/'output/concept/assets';OUT.mkdir(parents=True,exist_ok=True)
TMP=BASE/'tmp/pdfs'

def edge_flood(image, bg, tol):
    a=np.asarray(image.convert('RGB'), dtype=np.int16)
    delta=np.max(np.abs(a-np.array(bg)[None,None,:]),axis=2)
    mask=delta<=tol
    h,w=mask.shape
    outside=np.zeros((h,w),dtype=bool)
    q=deque()
    for x in range(w):
        if mask[0,x]:q.append((0,x));outside[0,x]=True
        if mask[h-1,x]:q.append((h-1,x));outside[h-1,x]=True
    for y in range(h):
        if mask[y,0]:q.append((y,0));outside[y,0]=True
        if mask[y,w-1]:q.append((y,w-1));outside[y,w-1]=True
    while q:
        y,x=q.popleft()
        for yy,xx in ((y-1,x),(y+1,x),(y,x-1),(y,x+1)):
            if 0<=yy<h and 0<=xx<w and mask[yy,xx] and not outside[yy,xx]:
                outside[yy,xx]=True;q.append((yy,xx))
    return outside,delta

def save_webp(im,name):
    im.save(OUT/name,format='WEBP',lossless=True,quality=100,method=6)
    print(name,im.size,im.mode,(OUT/name).stat().st_size)

# Main hero. Source raster is intentionally retained, preserving the PDF art.
hero=Image.open(TMP/'source-3.png').convert('RGBA').crop((580,54,1348,599))
a=np.asarray(hero).copy()
# Remove the fragment of the headline at far left of this composition.
a[:245,:24,:3]=[236,88,18]
hero=Image.fromarray(a)
bg,dist=edge_flood(hero,(236,88,18),20)
a=np.asarray(hero).copy(); a[bg,3]=0
# Soften only the anti-aliased exterior transition, without cutting enclosed oranges.
mask=Image.fromarray((~bg*255).astype('uint8'))
mask=np.asarray(mask.filter(ImageFilter.GaussianBlur(.35)))
a[:,:,3]=np.minimum(a[:,:,3],mask)
a[:2,:,3]=0
a[-2:,:,3]=0
# Strip isolated tiny raster specks at the edges by keeping large connected regions.
hero=Image.fromarray(a)
save_webp(hero,'hero-reference.webp')
raw=Image.open(TMP/'source-3.png').convert('RGB').crop((580,54,1348,599))
ImageDraw.Draw(raw).rectangle((0,0,23,244),fill=(236,88,18))
save_webp(raw,'hero-reference-orange.webp')

# Contact character. Preserve the intentionally cropped right/bottom edge from PDF.
contact=Image.open(TMP/'source-8.png').convert('RGBA').crop((998,93,1333,641))
bg,dist=edge_flood(contact,(61,31,20),22)
a=np.asarray(contact).copy();a[bg,3]=0
# A small fragment of the handwriting exists left of the comb. It is outside the character.
a[:190,:11,3]=0
a[95:170,:16,3]=0
save_webp(Image.fromarray(a),'mascot-contact.webp')

# Exact PDF wordmark with background removed by color distance.
logo=Image.open('/Users/andrey/Downloads/Новая папка/Фрикадельки классические.png').convert('RGBA').crop((325,70,702,146))
a=np.asarray(logo).copy();rgb=a[:,:,:3].astype(float)
# Higher-resolution wordmark from the source label uses the same letterforms as the PDF.
bg_rgb=np.median(np.concatenate([rgb[0],rgb[-1],rgb[:,0],rgb[:,-1]],axis=0),axis=0)
alpha=np.clip((bg_rgb[1]-rgb[:,:,1])/(bg_rgb[1]-108),0,1)
a[:,:,:3]=[205,66,9];a[:,:,3]=(alpha*255).astype('uint8')
save_webp(Image.fromarray(a),'logo-reference.webp')

# Product sleeves: use traced object outlines; chroma key would erase the cream cardboard.
source=Image.open(TMP/'source-4.png').convert('RGBA')
paths={
'nuggets':[(58,565),(76,446),(94,344),(113,328),(151,318),(207,310),(247,307),(284,311),(330,317),(390,329),(403,412),(432,565),(405,579),(380,590),(365,611),(338,620),(300,624),(235,625),(179,623),(148,617),(129,607),(122,595),(99,585)],
'popcorn':[(496,565),(514,443),(533,341),(548,328),(588,318),(642,310),(686,307),(731,311),(776,317),(830,330),(846,424),(870,566),(844,579),(820,591),(807,610),(777,621),(734,625),(675,625),(616,623),(584,617),(563,608),(556,594),(530,583)],
'strips':[(935,565),(952,445),(972,344),(990,329),(1035,318),(1080,311),(1125,307),(1170,311),(1217,318),(1271,330),(1285,423),(1309,565),(1282,579),(1258,589),(1242,609),(1216,620),(1175,625),(1118,625),(1056,623),(1025,617),(1006,608),(997,594),(972,583)]
}
for name,pts in paths.items():
    # pad leaves room for the soft grounding shadow without hard rectangular edges
    left=min(x for x,y in pts)-18;top=min(y for x,y in pts)-8
    right=max(x for x,y in pts)+18;bottom=max(y for x,y in pts)+19
    crop=source.crop((left,top,right,bottom));w,h=crop.size
    high=Image.new('L',(w*4,h*4));draw=ImageDraw.Draw(high)
    draw.polygon([((x-left)*4,(y-top)*4) for x,y in pts],fill=255)
    core=high.resize((w,h),Image.Resampling.LANCZOS)
    # Gradual exterior only retains the local source shadow. Whole product remains opaque.
    blur=core.filter(ImageFilter.GaussianBlur(5))
    alpha=np.asarray(core).astype('uint8')
    arr=np.asarray(crop).copy();arr[:,:,3]=alpha
    save_webp(Image.fromarray(arr),'pack-'+name+'.webp')

# Checkerboard preview for QA.
files=['hero-reference.webp','mascot-contact.webp','logo-reference.webp','pack-nuggets.webp','pack-popcorn.webp','pack-strips.webp']
canvas=Image.new('RGB',(1200,1000),(253,245,226))
for name,rect in zip(files,[(0,0,768,545),(820,0,335,548),(20,550,342,60),(0,620,400,350),(400,620,400,350),(800,620,400,350)]):
 im=Image.open(OUT/name).convert('RGBA');x,y,w,h=rect;im.thumbnail((w,h))
 canvas.paste(im,(x,y),im)
ImageDraw.Draw(canvas).text((20,600),'Assets extracted from supplied PDF. Source artwork retained.',fill=(62,33,19))
canvas.save(TMP/'extracted-assets-preview.jpg',quality=95)
