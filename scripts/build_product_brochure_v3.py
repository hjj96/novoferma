"""Packaging-first Novoferma catalogue. Original official JPEGs, no generated food.

Public sequence: producer / protein / fibre / packaged range / innovation / contact.
The 52 g protein per pack figure was supplied by the brand owner in this chat.
"""
from pathlib import Path
from functools import lru_cache
from io import BytesIO
import json
import sys

ROOT=Path(__file__).resolve().parents[1]
A=ROOT/'output/concept/assets'
P=ROOT/'output/brochure-v3/packshots'
T=ROOT/'tmp/pdfs/product-brochure-v3'
T.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(ROOT/'tmp/pdfs/fontdeps'))
from PIL import Image
from fontTools.ttLib import TTFont as Font
from fontTools.varLib.instancer import instantiateVariableFont
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader

W,H=960,540
WHITE='#FFFFFF';CREAM='#FFF5E3';INK='#402111';ORANGE='#EC5812';MUTED='#795E4C'
OUT=ROOT/'output/pdf/novoferma-products-partners.pdf'
for alias,source,weight in [('Book','Onest-wght.ttf',450),('Semi','Onest-wght.ttf',650),('Bold','Onest-wght.ttf',800),('Hand','Caveat-wght.ttf',600)]:
    target=T/(alias+'.ttf')
    if not target.exists():
        f=Font(A/'fonts'/source)
        if 'fvar' in f:f=instantiateVariableFont(f,{'wght':weight},inplace=False)
        f.flavor=None
        for r in f['name'].names:
            if r.nameID in (1,3,4,6):r.string=('NFcatalogue-'+alias).encode(r.getEncoding())
            elif r.nameID==2:r.string='Regular'.encode(r.getEncoding())
        f.save(target)
    pdfmetrics.registerFont(TTFont(alias,str(target)))

c=canvas.Canvas(str(OUT),pagesize=(W,H),pageCompression=1)
c.setTitle('Новоферма | Ассортимент продукции')
c.setAuthor('Новоферма')
c.setSubject('Производитель замороженных полуфабрикатов из курицы и индейки')
c.setCreator('Новоферма')
c.setViewerPreference('DisplayDocTitle','true')
page=0;bounds=[];images=[];manifest=[]

def fill(x,y,w,h,color):
    c.setFillColor(HexColor(color));c.rect(x,H-y-h,w,h,stroke=0,fill=1)

def text(s,x,y,size=18,face='Book',color=INK,leading=None,align='left'):
    leading=leading or size*1.25
    c.setFont(face,size);c.setFillColor(HexColor(color))
    for i,line in enumerate(s.split('\n')):
        width=pdfmetrics.stringWidth(line,face,size)
        xx=x-width/2 if align=='center' else x
        yy=y+i*leading
        bounds.append({'page':page,'text':line,'x':xx,'right':xx+width,'top':yy,'bottom':yy+size})
        c.drawString(xx,H-yy-size*.83,line)
    return y+len(s.split('\n'))*leading

def para(s,x,y,width,size=18,face='Book',color=INK,leading=None):
    lines=[]
    for segment in s.split('\n'):
        line=''
        for word in segment.split():
            trial=line+' '+word if line else word
            if line and pdfmetrics.stringWidth(trial,face,size)>width:lines.append(line);line=word
            else:line=trial
        lines.append(line)
    return text('\n'.join(lines),x,y,size,face,color,leading)

@lru_cache(maxsize=40)
def raster(path):
    path=Path(path)
    if path.suffix.lower() in ('.jpg','.jpeg'):
        # Preserve source JPEG byte stream; no retouching or re-encoding.
        reader=ImageReader(str(path));return reader,reader.getSize()
    im=Image.open(path).convert('RGBA')
    stream=BytesIO();im.save(stream,format='PNG');stream.seek(0)
    return ImageReader(stream),im.size

def picture(path,x,y,w,h,crop=None):
    reader,(iw,ih)=raster(str(path))
    l,t,r,b=crop if crop else (0,0,iw,ih)
    cw,ch=r-l,b-t
    scale=min(w/cw,h/ch)
    dw,dh=cw*scale,ch*scale
    xx=x+(w-dw)/2;yy=y+(h-dh)/2
    c.saveState()
    clip=c.beginPath();clip.rect(xx,H-yy-dh,dw,dh);c.clipPath(clip,stroke=0,fill=0)
    c.drawImage(reader,xx-l*scale,H-(yy-t*scale)-ih*scale,iw*scale,ih*scale,mask='auto')
    c.restoreState()
    images.append({'page':page,'path':str(path),'x':xx,'top':yy,'width':dw,'height':dh,'crop':crop})

def pack(slug,x,y,w=272,h=250):
    path=P/(slug+'-pack.jpg')
    # Crop only the common outer white margin in the PDF viewport.
    # Source image pixels, perspective, labels and package remain unchanged.
    picture(path,x,y,w,h,(60,150,1240,1190))

def logo(w=161,x=48,y=27):picture(A/'logo-reference.webp',x,y,w,w*76/377)

def master(section='',catalogue=False,bg=WHITE,logo_w=161):
    global page
    page+=1
    fill(0,0,W,H,bg)
    if catalogue:fill(0,0,W,174,CREAM)
    logo(logo_w)
    if section:
        tw=pdfmetrics.stringWidth(section.upper(),'Semi',10)
        text(section.upper(),912-tw,39,10,'Semi',MUTED)
    text(f'{page:02}',892,514,11,'Semi',MUTED)

def end(label):
    manifest.append({'page':page,'subject':label})
    c.showPage()

def catalogue(title,subtitle,products):
    master('Каталог продукции',True)
    text(title,48,96,36,'Bold')
    if subtitle:text(subtitle,49,146,15,'Book',MUTED)
    xs=[48,344,640] if len(products)==3 else [178,510]
    for x,(slug,name,mass) in zip(xs,products):
        pack(slug,x,187)
        text(name,x+136,451,18,'Semi',leading=22,align='center')
        text(mass,x+136,505,14,'Semi',ORANGE,align='center')
    end(title)

def link(label,url,x,y,size=22,face='Semi',color=INK):
    text(label,x,y,size,face,color)
    c.linkURL(url,(x,H-y-size*1.12,x+pdfmetrics.stringWidth(label,face,size),H-y+2),thickness=0)

# 01 / Company and actual packaged range, without campaign imagery.
master('О компании',logo_w=226)
text('Производитель замороженных полуфабрикатов',48,111,30,'Bold')
text('из курицы и индейки',48,153,30,'Bold')
text('Санкт-Петербург. Продукты для торговли и общественного питания.',49,208,18)
for slug,x in [('naggetsy-kurinye',48),('frikadelki-klassicheskie',344),('kotlety-po-domashnemu',640)]:
    pack(slug,x,263,272,233)
end('Новоферма. Производитель полуфабрикатов')

# 02 / The exact brand-owner figure is tied to one named product and pack.
master('Белок')
text('Естественный белок птицы',48,103,36,'Bold')
text('В привычных продуктах на каждый день',49,155,18,'Book',MUTED)
text('52 г',43,231,101,'Bold',ORANGE)
text('белка в упаковке',49,352,25,'Semi')
text('Фрикадельки «Классические»\nМасса упаковки: 500 г',49,414,19,leading=27)
pack('frikadelki-klassicheskie',510,219,380,288)
end('Белок. 52 г в упаковке фрикаделек')

# 03 / A separate fibre slide, with the existing mascot and no cooked food art.
master('Клетчатка',bg=CREAM)
text('Клетчатка\nв привычных продуктах',48,105,36,'Bold',leading=42)
para('Клетчатка - это пищевые волокна.',49,249,487,21,'Semi',leading=28)
para('Интерес к клетчатке - один из заметных трендов современного питания.',49,315,465,20,leading=28)
para('Белок птицы и пищевые волокна объединяем в концепте Фибриков.',49,415,465,20,leading=28)
picture(A/'protein-story/hen-layer-v2.png',635,217,276,276)
end('Клетчатка. Пищевые волокна в привычной еде')

# 04–09 / One repeated catalogue grid, with 14 untouched official package photos.
catalogue('Наггетсы','Куриные, с сыром и острые',[
    ('naggetsy-kurinye','Наггетсы куриные','400 г'),
    ('naggetsy-kurinye-s-syrom','Наггетсы куриные\nс сыром','400 г'),
    ('naggetsy-ostrye','Наггетсы куриные\nострые','400 г')])
catalogue('Наггетсы','«Динозавры» и вариант с индейкой «Фитнес»',[
    ('naggetsy-dinozavry','Наггетсы куриные\n«Динозавры»','400 г'),
    ('naggetsy-s-indeykoy-fitnes','Наггетсы с индейкой\n«Фитнес»','400 г')])
catalogue('Котлеты','Куриные, по-домашнему и пикантные',[
    ('kotlety-kurinye','Котлеты куриные','522 г'),
    ('kotlety-po-domashnemu','Котлеты\nпо-домашнему','480 г'),
    ('kotlety-pikantnye','Котлеты пикантные','480 г')])
catalogue('Котлеты и биточки','По-итальянски и куриные с овощами',[
    ('kotlety-po-italyanski','Котлеты\nпо-итальянски','480 г'),
    ('bitochki-kurinye-s-ovoshchami','Биточки куриные\nс овощами','450 г')])
catalogue('Фрикадельки и ёжики','Для повседневного домашнего стола',[
    ('frikadelki-klassicheskie','Фрикадельки\n«Классические»','500 г'),
    ('ezhiki-iz-tsyplenka-s-risom','Ёжики из цыплёнка\nс рисом','480 г')])
catalogue('Стрипсы и куриный попкорн','Два формата из курицы',[
    ('stripsy','Стрипсы','400 г'),
    ('kurinyj-popkorn','Куриный попкорн','400 г')])

# 10 / Preserve the second existing concept as the end of the catalogue.
master('Развитие линейки')
text('Люля мини',48,107,36,'Bold')
text('Куриные колбаски\nс зеленью и овощами',49,194,25,'Semi',leading=32)
para('Новый формат для знакомого меню: с гарниром, в лаваше или для общего стола.',49,303,333,19,leading=27)
text('Концепт продукта и упаковки',49,462,13,'Semi',MUTED)
picture(A/'novelty-packaging/lulia-mini-pack-v3.webp',455,166,442,324,(20,65,780,710))
end('Люля мини. Концепт развития линейки')

# 11 / Fibriki is the separate innovation page requested by the brand owner.
master('Инновационный продукт')
text('Фибрики',48,106,38,'Bold')
text('Клетчатка\nв привычном блюде',49,181,29,'Semi',leading=35)
para('Куриные фрикадельки с пищевыми волокнами. Белок птицы и клетчатка в одном продукте.',49,296,338,20,leading=28)
text('Продукт находится в разработке',49,439,13,'Semi',MUTED)
text('Концепт упаковки',49,462,13,'Book',MUTED)
picture(ROOT/'output/research/fibriki-herbs-v11/fibriki-pack-v11.png',446,168,455,332,(30,115,1220,1100))
end('Фибрики. Инновационный продукт')

# 12 / A direct commercial close, without an additional partnership story.
master('Контакты',bg=CREAM)
text('Обсудим сотрудничество',48,106,36,'Bold')
para('Напишите, какие позиции вам интересны.\nУкажите город и планируемый объём.',49,200,575,20,leading=29)
link('zakaz@novoferma.ru','mailto:zakaz@novoferma.ru',48,324,30,'Bold',ORANGE)
link('+7 (931) 213-55-50','tel:+79312135550',49,378,25)
link('novoferma.ru','https://novoferma.ru/',49,460,18)
text('Санкт-Петербург',272,463,14,'Book',MUTED)
picture(A/'protein-story/hen-layer-v2.png',655,248,245,245)
end('Контакты отдела заказов')

c.save()
errors=[b for b in bounds if b['x']<0 or b['right']>W-22 or b['bottom']>H-10]
(T/'text-bounds.json').write_text(json.dumps(bounds,ensure_ascii=False,indent=2))
(ROOT/'output/brochure-v3/manifest.json').write_text(json.dumps({'slides':manifest,'image_placements':images,'policy':'14 original official JPEGs; no generated serving or product scenes; existing two packaging concepts explicitly marked'},ensure_ascii=False,indent=2))
if errors:raise RuntimeError(json.dumps(errors,ensure_ascii=False))
print(json.dumps({'path':str(OUT),'pages':page,'bytes':OUT.stat().st_size,'text_bounds':'passed'},ensure_ascii=False))
