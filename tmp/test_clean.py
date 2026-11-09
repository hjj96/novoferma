import sys; sys.path.insert(0,"scripts")
from PIL import Image,ImageChops,ImageDraw,ImageFilter
from extract_depth_assets import polygon_mask
source=Image.open('output/concept/assets/hero-reference.webp').convert('RGBA')
contour=[(0,0),(768,0),(768,430),(640,430),(612,428),(593,434),(583,439),(575,444),(564,448),(546,450),(514,450),(477,450),(441,450),(440,463),(437,476),(431,487),(424,495),(414,500),(401,507),(390,509),(377,511),(365,511),(351,509),(338,505),(329,501),(322,495),(313,484),(307,479),(300,482),(290,487),(278,489),(259,490),(244,489),(230,487),(218,484),(210,482),(210,545),(0,545)]
mask=polygon_mask(source.size,contour)
art=source.copy(); alpha=ImageChops.multiply(art.getchannel('A'),mask)
# remove orange floor in rooster foot area
for y in range(454,501):
 for x in range(0,230):
  r,g,b,a=source.getpixel((x,y))
  # only pixels with vivid orange/brown floor hue; preserve dark linework and meatball/product colors
  # remove orange matte below lower body; clipping to zones outside body
  if a and r>115 and g>42 and b<48 and r-g>65 and g-b>22:
   # avoid chicken body in upper area, only floor area based x/y contours manually
   if (x<110 and y>=466) or (120<=x<190 and y>=474):
    alpha.putpixel((x,y),0)
art.putalpha(alpha)
shadow=Image.new('L',source.size);d=ImageDraw.Draw(shadow);d.ellipse((308,500,440,519),fill=58);d.ellipse((184,480,309,496),fill=45);d.ellipse((442,440,579,455),fill=26);shadow=shadow.filter(ImageFilter.GaussianBlur(4));res=Image.new('RGBA',source.size,(62,33,19,0));res.putalpha(shadow);res.alpha_composite(art)
bg=Image.new('RGBA',source.size,(236,88,18,255));ImageDraw.Draw(bg).rectangle((0,470,768,545),fill=(253,245,226,255));bg.alpha_composite(res);bg.convert('RGB').save('tmp/test_clean.jpg',quality=97)
