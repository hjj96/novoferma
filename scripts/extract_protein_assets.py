from pathlib import Path
from collections import deque
from PIL import Image,ImageDraw,ImageFilter,ImageOps
import numpy as np

ROOT=Path('/Users/andrey/Documents/ChatGPT/сайт нф')
SRC=Image.open(ROOT/'tmp/pdfs/source-1.png').convert('RGB')
OUT=ROOT/'output/concept/assets'
BG=np.array([216.,220.,161.])

def flood(mask):
 h,w=mask.shape;out=np.zeros((h,w),bool);q=deque()
 for x in range(w):
  for y in (0,h-1):
   if mask[y,x]:out[y,x]=True;q.append((y,x))
 for y in range(h):
  for x in (0,w-1):
   if mask[y,x] and not out[y,x]:out[y,x]=True;q.append((y,x))
 while q:
  y,x=q.popleft()
  for yy,xx in [(y-1,x),(y+1,x),(y,x-1),(y,x+1)]:
   if 0<=yy<h and 0<=xx<w and mask[yy,xx] and not out[yy,xx]:out[yy,xx]=True;q.append((yy,xx))
 return out

def extract(crop,letter=False):
 a=np.asarray(crop,dtype=float)
 # Green paper has G>R and a warm pale-yellow cast; cream packaging has R>G.
 d=np.max(np.abs(a-BG),2)
 isgreen=(d<20)|((a[:,:,1]-a[:,:,0]>-5)&(a[:,:,0]-a[:,:,2]>27)&(a[:,:,1]>150))
 outside=flood(isgreen)
 if letter:
  # Brown typography touches the outer crop. Remove only its edge-connected flat fill.
  brown=np.max(np.abs(a-np.array([62,33,19])),2)<25
  outside |= flood(brown)
 mask=Image.fromarray(np.uint8(~outside)*255)
 # Gentle antialias at the cutout boundary; original internal colours remain opaque.
 alpha=np.asarray(mask.filter(ImageFilter.GaussianBlur(.55)),dtype=float)/255
 weight=np.asarray(mask.filter(ImageFilter.GaussianBlur(1.2)),dtype=float)/255
 edge_rgb=np.zeros_like(a)
 for c in range(3):
  weighted=Image.fromarray(np.uint8(a[:,:,c]*(~outside)))
  edge_rgb[:,:,c]=np.asarray(weighted.filter(ImageFilter.GaussianBlur(1.2)),dtype=float)/np.maximum(weight,.001)
 a=np.where((alpha<.99)[:,:,None],np.clip(edge_rgb,0,255),a)
 alpha[alpha<.012]=0
 rgba=np.dstack([a,alpha*255]).astype('uint8')
 return Image.fromarray(rgba)

pack=extract(SRC.crop((799,149,1338,620)))
pack.save(OUT/'protein-pack.webp',lossless=True,method=6)
letter=extract(SRC.crop((275,125,533,377)),True)
a=np.array(letter)
h,w=a.shape[:2];ys,xs=np.indices((h,w))
# Remove only the nearby type outlines; these rectangles are outside the art silhouette.
clear=(xs<53)&(ys<150)
clear|=(xs<20)&(ys<157)
clear|=(xs<9)&(ys>225)
clear|=(xs<108)&(ys<55)
clear|=(xs<105)&(ys<94)
clear|=(xs>=101)&(xs<106)&(ys<122)
clear|=(xs>=50)&(xs<55)&(ys<151)
# Remove the adjacent exclamation stroke below/left of the tail.
clear|=(xs<17)&(ys>205)&(ys<228)
clear|=(xs<8)&(ys>193)&(ys<228)
clear|=(xs<np.maximum(0,(ys-184)*.7))&(ys>184)&(ys<214)
a[clear,3]=0
# Remove isolated subpixel remnants of neighbouring print.
seen=np.zeros(a.shape[:2],bool)
active=a[:,:,3]>15
for yy,xx in zip(*np.where(active)):
 if seen[yy,xx]:continue
 q=deque([(yy,xx)]);seen[yy,xx]=True;component=[]
 while q:
  y,x=q.popleft();component.append((y,x))
  for dy in [-1,0,1]:
   for dx in [-1,0,1]:
    ny,nx=y+dy,x+dx
    if 0<=ny<h and 0<=nx<w and active[ny,nx] and not seen[ny,nx]:seen[ny,nx]=True;q.append((ny,nx))
 if len(component)<12:
  for y,x in component:a[max(0,y-1):min(h,y+2),max(0,x-1):min(w,x+2),3]=0
letter=Image.fromarray(a)
letter.save(OUT/'protein-letter-art.webp',lossless=True,method=6)
# Single mirrorable paper tile. Mirroring at each join makes a quiet seamless 512x256 repeat.
tile=SRC.crop((700,15,956,143))
paper=Image.new('RGB',(512,256));paper.paste(tile,(0,0));paper.paste(ImageOps.mirror(tile),(256,0));paper.paste(ImageOps.flip(tile),(0,128));paper.paste(ImageOps.flip(ImageOps.mirror(tile)),(256,128))
paper.save(OUT/'protein-paper.webp',quality=93,method=6)
# Self-contained crop is retained as fallback.
SRC.crop((785,125,1348,670)).save(OUT/'protein-pack-green.webp',quality=96,method=6)
canvas=Image.new('RGB',(1280,650),tuple(BG.astype('uint8')))
canvas.paste(pack,(680,60),pack)
letter3=letter.resize((516,504),Image.Resampling.LANCZOS);canvas.paste(letter3,(50,60),letter3)
canvas.save(ROOT/'tmp/pdfs/protein-assets-preview.jpg',quality=96)
for n in ['protein-pack.webp','protein-letter-art.webp','protein-paper.webp','protein-pack-green.webp']:
 im=Image.open(OUT/n);print(n,im.size,im.mode,(OUT/n).stat().st_size)
