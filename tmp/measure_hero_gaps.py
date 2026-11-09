from PIL import Image
from collections import deque,defaultdict
from array import array
from math import sqrt
from pathlib import Path
p=Path('output/concept/assets/product-hero/mobile-v4/lulia-mini-master.png')
im=Image.open(p).convert('RGBA');w,h=im.size
alpha=im.getchannel('A').tobytes()
for threshold in [32,128]:
 labels=array('I',[0])*(w*h);comps=[]
 for i,a in enumerate(alpha):
  if a<=threshold or labels[i]:continue
  cid=len(comps)+1;q=deque([i]);labels[i]=cid;area=0;left=w;right=0;top=h;bottom=0;edges=[]
  while q:
   n=q.popleft();y,x=divmod(n,w);area+=1
   left=min(left,x);right=max(right,x);top=min(top,y);bottom=max(bottom,y)
   neigh=[]
   if x:neigh.append(n-1)
   if x+1<w:neigh.append(n+1)
   if y:neigh.append(n-w)
   if y+1<h:neigh.append(n+w)
   if len(neigh)<4 or any(alpha[k]<=threshold for k in neigh):edges.append((x,y))
   for k in neigh:
    if alpha[k]>threshold and not labels[k]:labels[k]=cid;q.append(k)
  comps.append({'id':cid,'area':area,'bbox':(left,top,right+1,bottom+1),'edges':edges})
 big=sorted([c for c in comps if c['area']>10000],key=lambda c:-c['area'])
 print('threshold',threshold,'fill',sum(a>threshold for a in alpha)/(w*h))
 for c in big: print('component',c['id'],'area',c['area'],'bbox',c['bbox'])
 chicken=big[0]
 for food in big[1:]:
  bins=defaultdict(list)
  for x,y in food['edges']:bins[(x//32,y//32)].append((x,y))
  best=10**9;pair=None
  for x,y in chicken['edges']:
   bx,by=x//32,y//32
   for j in range(by-3,by+4):
    for k in range(bx-3,bx+4):
     for u,v in bins.get((k,j),[]):
      d=(x-u)**2+(y-v)**2
      if d<best:best=d;pair=((x,y),(u,v))
  print('chicken-food',food['id'],'minGapPixels',sqrt(best) if pair else '>96','at',pair,'at322',sqrt(best)*322/w if pair else None)
