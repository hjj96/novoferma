"""Novoferma brand presentation: character-led infographics and range panoramas.

Original package JPEGs are embedded byte-for-byte and integrated with PDF blending.
New illustration assets contain mascots/backgrounds only, never generated food.
"""
from pathlib import Path
from io import BytesIO
from functools import lru_cache
import json, math, sys

ROOT=Path(__file__).resolve().parents[1]
A=ROOT/'output/concept/assets'
B=ROOT/'output/brochure-v4/assets'
P=ROOT/'output/brochure-v3/packshots'
T=ROOT/'tmp/pdfs/product-brochure-v4'
T.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(ROOT/'tmp/pdfs/fontdeps'))
from PIL import Image
from fontTools.ttLib import TTFont as Font
from fontTools.varLib.instancer import instantiateVariableFont
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfdoc import PDFImageXObject
from reportlab.lib.utils import ImageReader
from reportlab.lib.colors import HexColor

W,H=960,540
CREAM='#FFF5E3';INK='#402111';ORANGE='#EC5812';SAGE='#DCE1B3';MUTED='#795E4C'
OUT=ROOT/'output/pdf/novoferma-products-partners.pdf'
for alias,source,weight in [('Book','Onest-wght.ttf',450),('Semi','Onest-wght.ttf',650),('Bold','Onest-wght.ttf',850),('Hand','Caveat-wght.ttf',600),('Poster','RobotoFlex-Protein.woff2',None)]:
    target=T/(alias+'.ttf')
    if not target.exists():
        f=Font(A/'fonts'/source)
        if weight and 'fvar' in f:f=instantiateVariableFont(f,{'wght':weight},inplace=False)
        f.flavor=None
        for r in f['name'].names:
            if r.nameID in (1,3,4,6):r.string=('NFbrandV4-'+alias).encode(r.getEncoding())
            elif r.nameID==2:r.string='Regular'.encode(r.getEncoding())
        f.save(target)
    pdfmetrics.registerFont(TTFont(alias,str(target)))

c=canvas.Canvas(str(OUT),pagesize=(W,H),pageCompression=1)
c.setTitle('Новоферма | Продукты с характером')
c.setAuthor('Новоферма')
c.setSubject('Белок, клетчатка и ассортимент Новофермы для партнёров')
c.setCreator('Новоферма')
c.setViewerPreference('DisplayDocTitle','true')
page=0;bounds=[];placements=[];slides=[]

# JPEG-encode only colour planes of illustration assets; keep alpha lossless.
_original=PDFImageXObject.loadImageFromSRC
def _image_alpha(self,reader):
    _original(self,reader)
    if getattr(reader,'_alpha_jpeg',False):self.mask='auto';self._checkTransparency(reader)
PDFImageXObject.loadImageFromSRC=_image_alpha

@lru_cache(maxsize=70)
def load(path):
    path=Path(path)
    if path.suffix.lower() in ('.jpg','.jpeg'):
        reader=ImageReader(str(path));return reader,reader.getSize()
    im=Image.open(path).convert('RGBA')
    reader=ImageReader(im);reader.getRGBData()
    stream=BytesIO();im.convert('RGB').save(stream,format='JPEG',quality=95,subsampling=0,optimize=True)
    def jpeg():stream.seek(0);return stream
    reader.jpeg_fh=jpeg;reader._alpha_jpeg=True
    return reader,im.size

def fill(x,y,w,h,color):
    c.setFillColor(HexColor(color));c.rect(x,H-y-h,w,h,fill=1,stroke=0)

def text(s,x,y,size=18,face='Book',color=INK,leading=None,align='left'):
    c.setFillColor(HexColor(color));c.setFont(face,size)
    leading=leading or size*1.2
    for i,line in enumerate(s.split('\n')):
        width=pdfmetrics.stringWidth(line,face,size)
        xx=x-width/2 if align=='center' else x
        yy=y+i*leading
        bounds.append({'page':page,'text':line,'x':xx,'right':xx+width,'top':yy,'bottom':yy+size})
        c.drawString(xx,H-yy-size*.83,line)
    return y+len(s.split('\n'))*leading

def para(s,x,y,w,size=18,face='Book',color=INK,leading=None):
    lines=[]
    for p in s.split('\n'):
        line=''
        for word in p.split():
            trial=line+' '+word if line else word
            if line and pdfmetrics.stringWidth(trial,face,size)>w:lines.append(line);line=word
            else:line=trial
        lines.append(line)
    return text('\n'.join(lines),x,y,size,face,color,leading)

def image(path,x,y,w,h,crop=None,multiply=False):
    reader,(iw,ih)=load(str(path))
    l,t,r,b=crop or (0,0,iw,ih)
    scale=min(w/(r-l),h/(b-t));dw=(r-l)*scale;dh=(b-t)*scale
    xx=x+(w-dw)/2;yy=y+(h-dh)/2
    c.saveState()
    if multiply:c.setBlendMode('Multiply')
    clip=c.beginPath();clip.rect(xx,H-yy-dh,dw,dh);c.clipPath(clip,stroke=0,fill=0)
    c.drawImage(reader,xx-l*scale,H-(yy-t*scale)-ih*scale,iw*scale,ih*scale,mask='auto')
    c.restoreState()
    placements.append({'page':page,'file':str(path),'x':xx,'y':yy,'w':dw,'h':dh,'multiply':multiply})

def pack(slug,x,y,w,h):image(P/(slug+'-pack.jpg'),x,y,w,h,(60,150,1240,1190),True)
def art(rel,x,y,w,h,crop=None):image(A/rel,x,y,w,h,crop)
def logo(x=44,y=27,w=157):art('logo-reference.webp',x,y,w,w*76/377)

def start(subject,bg=CREAM,backdrop=None,folio=True,with_logo=True):
    global page
    page+=1;slides.append({'page':page,'subject':subject})
    fill(0,0,W,H,bg)
    if backdrop:image(B/backdrop,0,0,W,H)
    if with_logo:logo()
    if folio:text(f'{page:02}',895,38,11,'Semi',CREAM if bg in (INK,ORANGE) else MUTED)
def end():c.showPage()

def arrow(x1,y1,x2,y2,color=ORANGE,width=2.5,head=9):
    # Native infographic connector, not illustrative artwork.
    c.saveState();c.setStrokeColor(HexColor(color));c.setFillColor(HexColor(color));c.setLineWidth(width)
    c.line(x1,H-y1,x2,H-y2)
    angle=math.atan2(y2-y1,x2-x1)
    p=c.beginPath();p.moveTo(x2,H-y2)
    for d in (-.48,.48):p.lineTo(x2-head*math.cos(angle+d),H-y2+head*math.sin(angle+d))
    p.close();c.drawPath(p,fill=1,stroke=0);c.restoreState()

def link(label,url,x,y,size=20,face='Semi',color=INK):
    text(label,x,y,size,face,color)
    c.linkURL(url,(x,H-y-size*1.12,x+pdfmetrics.stringWidth(label,face,size),H-y+2),thickness=0)

nuggets=[
 ('naggetsy-kurinye','Куриные'),('naggetsy-kurinye-s-syrom','С сыром'),('naggetsy-ostrye','Острые'),
 ('naggetsy-dinozavry','«Динозавры»'),('naggetsy-s-indeykoy-fitnes','С индейкой «Фитнес»')]
snacks=[('stripsy','Стрипсы'),('kurinyj-popkorn','Куриный попкорн')]
home=[
 ('kotlety-kurinye','Котлеты куриные','522 г'),('kotlety-po-domashnemu','Котлеты по-домашнему','480 г'),
 ('kotlety-pikantnye','Котлеты пикантные','480 г'),('kotlety-po-italyanski','Котлеты по-итальянски','480 г'),
 ('bitochki-kurinye-s-ovoshchami','Биточки куриные с овощами','450 г'),
 ('frikadelki-klassicheskie','Фрикадельки «Классические»','500 г'),('ezhiki-iz-tsyplenka-s-risom','Ёжики из цыплёнка с рисом','480 г')]

# 01 / Character-led branded cover; unchanged real packages share the cream stage.
start('Компания и продукты',backdrop='cover-backdrop.png',folio=False,with_logo=False)
logo(w=200)
text('ПРОДУКТЫ ДЛЯ ПАРТНЁРОВ',46,99,10,'Semi')
text('ПРИВЫЧНЫЕ\nПРОДУКТЫ',42,130,74,'Poster',leading=72)
text('С характером Новофермы',45,291,32,'Hand',ORANGE)
para('Производим замороженные полуфабрикаты из курицы и индейки.',46,354,333,20,leading=27)
text('Санкт-Петербург',47,466,13,'Semi',MUTED)
for slug,x in [('naggetsy-kurinye',405),('frikadelki-klassicheskie',580),('kotlety-po-domashnemu',755)]:pack(slug,x,371,163,128)
end()

# 02 / Infographic: one named 500 g pack maps to the owner-supplied 52 g figure.
start('Белок',bg=SAGE)
fill(600,0,360,H,CREAM)
text('02',895,38,11,'Semi',MUTED)
text('В ОСНОВЕ',43,107,73,'Poster')
text('ПТИЦА',44,182,95,'Poster',ORANGE)
text('1 упаковка',47,324,20,'Semi')
text('500 г',47,357,30,'Bold')
arrow(213,372,278,372)
text('52 г',289,313,93,'Bold',ORANGE)
text('белка',293,421,27,'Semi')
para('Курица и индейка содержат белок от природы.',47,459,447,17,leading=23)
art('product-hero/running-mascot-v2.png',713,82,166,173)
pack('frikadelki-klassicheskie',623,262,310,235)
text('Фрикадельки «Классические»',778,501,11.5,'Semi',align='center')
end()

# 03 / A qualitative ingredient formula, with sources explicitly limited to Fibriki.
start('Клетчатка',backdrop='fibre-backdrop.png')
text('БЕЛОК + КЛЕТЧАТКА',43,97,48,'Poster')
text('БЕЛОК\nПТИЦЫ',46,179,48,'Poster',leading=48)
text('+',277,199,61,'Book',ORANGE)
text('ПИЩЕВЫЕ\nВОЛОКНА',349,179,48,'Poster',ORANGE,48)
text('Природная основа\nпродуктов из птицы',48,297,19,leading=25)
text('Клетчатка - заметный тренд\nсовременного питания',350,297,18,leading=25)
arrow(157,371,291,417,width=2)
arrow(481,371,347,417,width=2)
text('ОСНОВА ИДЕИ ФИБРИКОВ',46,439,29,'Poster')
text('Привычная еда. Новый акцент.',46,482,26,'Hand',ORANGE)
end()

# 04 / Every current SKU together: two seven-product panoramas plus native counts.
start('Весь ассортимент')
text('ВСЯ СЕМЬЯ',43,95,61,'Poster')
text('НОВОФЕРМЫ',44,155,49,'Poster',ORANGE)
text('14',676,89,88,'Bold',ORANGE)
text('продуктов',806,142,19,'Semi')
text('7',44,252,28,'Bold',ORANGE)
text('наггетсов\nи снеков',44,287,12,'Semi',leading=16)
for i,(slug,_) in enumerate(nuggets+snacks):pack(slug,133+i*111,224,105,97)
text('7',44,380,28,'Bold',ORANGE)
text('домашних\nформатов',44,416,12,'Semi',leading=16)
for i,(slug,_,_) in enumerate(home):pack(slug,133+i*111,354,105,97)
groups=[('5','наггетсов'),('5','котлет и биточков'),('2','фрикаделек и ёжиков'),('1','стрипсы'),('1','попкорн')]
for i,(n,label) in enumerate(groups):
    x=44+i*177
    text(n,x,476,31,'Bold',ORANGE)
    para(label,x+31,483,137,11,'Semi',leading=14)
end()

# 05 / Seven products as one expressive family, not seven isolated catalogue pages.
start('Наггетсы и снеки')
text('ХРУСТЯЩАЯ КОМПАНИЯ',43,95,54,'Poster')
text('7 позиций. Каждая по 400 г',44,157,19,'Semi')
for i,(slug,label) in enumerate(nuggets):
    x=43+i*178
    pack(slug,x,209,164,138)
    text(label,x+82,355,12,'Semi',align='center')
text('5',45,412,69,'Bold',ORANGE)
text('+',127,433,38,'Book')
text('2',177,412,69,'Bold',ORANGE)
text('наггетсов',47,491,12,'Semi')
text('формата снеков',177,491,12,'Semi')
art('product-hero/running-mascot-v2.png',334,391,121,128)
for (slug,label),x in zip(snacks,[560,750]):
    pack(slug,x,387,170,117)
    text(label,x+85,509,12,'Semi',align='center')
end()

# 06 / A 4+3 panorama links all seven domestic products, with readable mass labels.
start('Домашняя линейка')
text('ДОМАШНИЕ ФОРМАТЫ',43,95,57,'Poster')
text('Котлеты, биточки, фрикадельки и ёжики',44,158,18,'Semi')
for i,(slug,name,mass) in enumerate(home[:4]):
    x=42+i*224
    pack(slug,x,205,199,132)
    text(name,x+99.5,343,11.5,'Semi',align='center')
    text(mass,x+99.5,364,11,'Semi',ORANGE,align='center')
for i,(slug,name,mass) in enumerate(home[4:]):
    x=153+i*224
    pack(slug,x,355,199,132)
    text(name,x+99.5,501,10.6,'Semi',align='center')
    text(mass,x+99.5,520,10,'Semi',ORANGE,align='center')
art('protein-story/hen-layer-v2.png',812,380,105,111)
end()

# 07 / One dominant Fibriki innovation hero, with the other known concept secondary.
start('Развитие линейки')
text('ФИБРИКИ',42,102,88,'Poster')
art('product-hero/benefit-brush-v11.png',36,208,335,82)
text('Белок + клетчатка',99,233,29,'Hand',CREAM)
text('Куриные фрикадельки\nс пищевыми волокнами',46,310,22,'Semi',leading=28)
image(ROOT/'output/research/fibriki-herbs-v11/fibriki-pack-v11.png',460,164,448,333,(30,115,1220,1100))
text('Фибрики находятся в разработке',474,499,11,'Semi',MUTED)
image(ROOT/'output/research/novelty-color-match/lulia-mini-pack-v3.png',49,410,140,105,(30,115,1220,1120))
text('Люля мини',219,418,20,'Bold')
text('Куриные колбаски\nс зеленью и овощами',220,451,15,leading=20)
text('Показаны концепты продуктов и упаковок',220,501,10,'Book',MUTED)
end()

# 08 / A genuine business workflow is the second infographic, with the brand duo.
start('Сотрудничество',bg=ORANGE,with_logo=False)
text('НОВОФЕРМА / ПАРТНЁРАМ',45,34,11,'Semi',CREAM)
text('ВАША ПОЛКА.\nНАШ ХАРАКТЕР.',43,105,60,'Poster',CREAM,61)
text('Для магазинов, кафе и ресторанов',46,270,21,'Semi',CREAM)
text('Обсудим производство под вашей маркой',46,310,17,'Book',CREAM)
art('partners-hero-v4/brand-handshake-v1.png',556,156,356,251)
steps=[('01','Выбираем\nассортимент'),('02','Обсуждаем\nобъём и фасовки'),('03','Согласуем\nусловия поставки')]
for i,(n,label) in enumerate(steps):
    x=46+i*305
    text(n,x,417,34,'Bold',INK)
    text(label,x+61,421,17,'Semi',CREAM,22)
    if i<2:arrow(x+247,444,x+283,444,CREAM,2,7)
end()

# 09 / Brown brand close, large contacts, original mascot at the page edge.
start('Контакты',bg=INK,folio=False)
text('ПОЖМЁМ\nКРЫЛЬЯ?',43,113,75,'Poster',CREAM,76)
text('Начнём с вашего запроса',46,301,24,'Hand',ORANGE)
link('zakaz@novoferma.ru','mailto:zakaz@novoferma.ru',44,366,30,'Bold',ORANGE)
link('+7 (931) 213-55-50','tel:+79312135550',46,419,25,'Semi',CREAM)
link('novoferma.ru','https://novoferma.ru/',47,487,16,'Semi',CREAM)
text('Город, позиции, планируемый объём',289,491,12,'Book',CREAM)
art('mascot-contact-restored-v2.webp',722,156,238,390)
end()

c.save()
(T/'text-bounds.json').write_text(json.dumps(bounds,ensure_ascii=False,indent=2))
(ROOT/'output/brochure-v4/manifest.json').write_text(json.dumps({'slides':slides,'images':placements,'figures':{'products':14,'categories':5,'protein_g_per500g_pack':52,'source':'product records and brand-owner statement'},'note':'Generated art contains no food or packages. All series products use untouched original package JPEGs.'},ensure_ascii=False,indent=2))
errors=[b for b in bounds if b['x']<0 or b['right']>W-18 or b['bottom']>H-8]
if errors:raise RuntimeError(json.dumps(errors,ensure_ascii=False))
print(json.dumps({'path':str(OUT),'pages':page,'bytes':OUT.stat().st_size,'text_bounds':'passed'},ensure_ascii=False))
