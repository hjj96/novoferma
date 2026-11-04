"""Export floating product cutouts without the source's baked-in floor shadow.

The source alpha has a wide translucent brown floor shadow below the stack.
That is useful on a flat pale surface, but reads as a dirty paper patch when
the stack crosses two section colours. Keep only the product silhouette;
the website supplies a separate, consistent CSS shadow.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageChops
ROOT=Path('/Users/andrey/Documents/ChatGPT/сайт нф')
SOURCE=Path('/Users/andrey/Downloads/Новая папка/швед_мб.psd@3x (2).png')
OUT=ROOT/'output/concept/assets'
im=Image.open(SOURCE).convert('RGBA')


def product_alpha(art):
    """Remove translucent ground pixels and gently antialias the real edge.

    The photographed product is opaque; the unwanted ground shadow is below
    225/255. The short remap removes it without changing the food's RGB detail.
    A subpixel blur keeps the resulting craggy silhouette smooth when scaled.
    """
    alpha = art.getchannel('A')
    lut = [0 if value <= 225 else round((value - 225) * 255 / 30)
           for value in range(256)]
    silhouette = alpha.point(lut).filter(ImageFilter.GaussianBlur(.3))
    silhouette = ImageChops.darker(silhouette, alpha)
    # Avoid residual almost-transparent coloured pixels outside the contour.
    silhouette = silhouette.point(lambda value: 0 if value < 3 else value)
    clean = art.copy()
    clean.putalpha(silhouette)
    return clean


im = product_alpha(im)
# Retain the existing canvas and position so the page composition does not move.
cluster=Image.new('RGBA',(740,610))
cluster.alpha_composite(im.crop((0,60,698,650)),(16,10))
cluster.save(OUT/'meatball-cluster.webp',lossless=True,quality=100,method=6)
# The top meatball is fully visible. Its lower edge can be separated without reconstruction.
# Retain existing alpha along the natural craggy outer contour; trace only shared contacts.
box=(138,66,455,360)
ball=im.crop(box)
pts=[(155,212),(155,194),(161,175),(168,161),(170,150),(185,141),(192,123),
 (205,109),(215,98),(229,89),(249,84),(269,85),(282,80),(303,79),(317,83),
 (337,84),(353,89),(365,98),(375,108),(389,117),(400,117),(405,128),(417,140),
 (426,154),(433,172),(436,192),(439,214),(437,234),(431,254),(424,274),
 (414,289),(400,301),(387,311),(372,319),(357,324),(344,330),(328,336),
 (313,340),(296,342),(280,340),(264,337),(248,332),(233,323),(219,317),
 (204,310),(192,300),(183,289),(174,278),(168,264),(163,250),(158,232)]
mask=Image.new('L',(ball.width*4,ball.height*4))
ImageDraw.Draw(mask).polygon([((x-box[0])*4,(y-box[1])*4) for x,y in pts],fill=255)
mask=mask.resize(ball.size,Image.Resampling.LANCZOS).filter(ImageFilter.GaussianBlur(.25))
ball.putalpha(ImageChops.multiply(ball.getchannel('A'),mask))
# A 360px square leaves a consistent safe area for CSS rotation and floating animation.
canvas=Image.new('RGBA',(360,360));canvas.alpha_composite(ball,(22,27))
canvas.save(OUT/'meatball-float.webp',lossless=True,quality=100,method=6)
# QA shows both assets spanning the actual green/brown transition at intended display sizes.
preview=Image.new('RGB',(1100,640),(216,220,161))
ImageDraw.Draw(preview).rectangle((0,320,1100,640),fill=(64,33,17))
for file,xy,size in [('meatball-float.webp',(55,225),(240,240)),('meatball-cluster.webp',(360,220),(330,272)),('meatball-float.webp',(775,105),(260,260))]:
 art=Image.open(OUT/file);art.thumbnail(size,Image.Resampling.LANCZOS);preview.paste(art,xy,art)
preview.save(ROOT/'tmp/pdfs/meatball-transition-preview.jpg',quality=96)
for file in ['meatball-float.webp','meatball-cluster.webp']:
 art=Image.open(OUT/file);print(file,art.size,art.mode,(OUT/file).stat().st_size)
