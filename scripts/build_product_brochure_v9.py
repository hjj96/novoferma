"""Novoferma presentation: branded painted nutrition lockups and approved catalogue.

Original package JPEGs are embedded byte-for-byte and integrated with PDF blending.
Food editorials are freshly generated; no juggling artwork is reused.
Fourteen original photographs and the approved Popsy v3 artwork form the catalogue.
"""
from pathlib import Path
from io import BytesIO
from functools import lru_cache
import json, math, sys

ROOT=Path(__file__).resolve().parents[1]
A=ROOT/'output/concept/assets'
B=ROOT/'output/brochure-v7/assets'
PAINT=ROOT/'output/brochure-v9/assets'
P=ROOT/'output/brochure-v3/packshots'
T=ROOT/'tmp/pdfs/product-brochure-v9'
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
            if r.nameID in (1,3,4,6):r.string=('NFbrandV9-'+alias).encode(r.getEncoding())
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

def pack(slug,x,y,w,h):
    if slug=='popsy':
        image(A/'novelty-packaging/popsy-pack-v3.webp',x,y,w,h,(25,105,1225,1130))
    else:
        # PDF blending removes white photo fields without rewriting original JPEGs.
        image(P/(slug+'-pack.jpg'),x,y,w,h,(80,180,1230,1180),True)
def art(rel,x,y,w,h,crop=None):image(A/rel,x,y,w,h,crop)
def logo(x=44,y=27,w=157):art('logo-reference.webp',x,y,w,w*76/377)

def start(subject,bg=CREAM,backdrop=None,folio=False,with_logo=True):
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

# 01 / Opening and closing form a typographic pair with the same side-peeking mascot.
start('Знакомство с компанией',folio=False,with_logo=False)
logo()
text('ДАВАЙТЕ',43,113,80,'Poster')
text('ПОЗНАКОМИМСЯ',43,195,80,'Poster',ORANGE)
text('Новоферма — компания из Санкт-Петербурга.\nПроизводим замороженные полуфабрикаты из курицы\nи индейки для магазинов, кафе и ресторанов.',46,317,21,'Book',leading=29)
text('Продукция Новофермы и выпуск под вашей маркой',46,461,24,'Hand',ORANGE)
art('mascot-contact-restored-v2.webp',722,156,238,390)
end()

# 02 / A new editorial, with the nutritional figure clearly tied to the original pack.
start('Белок',backdrop='protein-lifestyle.png')
text('В основе\nбелок птицы',44,96,37,'Bold',leading=43)
text('Фрикадельки «Классические»',47,204,19,'Semi')
image(PAINT/'protein-paint-seal.png',34,234,400,148.5)
text('52 г',170,262,76,'Bold',CREAM)
text('белка в упаковке',176,329,17,'Semi',CREAM)
text('Естественный белок курицы',47,405,22,'Semi')
text('Охлаждённое мясо курицы,\nнатуральные специи. Никаких добавок.',47,451,18,'Book',leading=26)
end()

# 03 / A new green, three-angle product editorial, no old juggler or flying pieces.
start('Фибрики. Новинка',bg='#31563E',backdrop='fibriki-lifestyle.png',with_logo=False)
logo()
text('Фибрики',43,105,64,'Bold',CREAM)
text('Наша новинка',47,188,28,'Hand',ORANGE)
para('Куриные фрикадельки, в которых естественный белок птицы сочетается с пищевыми волокнами. Клетчатка — в знакомом блюде.',47,241,360,19,'Book',CREAM,27)
image(PAINT/'fibriki-paint-pair.png',35,346,388,170)
text('+',229,421,27,'Semi',CREAM,align='center')
text('БЕЛОК ПТИЦЫ',127,461,18,'Poster',INK,align='center')
text('КЛЕТЧАТКА',322,461,18,'Poster',CREAM,align='center')
end()

# 04-06 / Five products per page on a warm continuous brand field.
def catalogue_page(records,index,group):
    start('Наша продукция / '+str(index),bg='#F7E8CC')
    text('НАША ПРОДУКЦИЯ',310,27,38,'Poster')
    text(group,310,72,14,'Semi',ORANGE)
    positions=[(44,100),(350,100),(656,100),(197,318),(503,318)]
    for (slug,name,mass),(x,y) in zip(records,positions):
        pack(slug,x,y,260,160)
        text(name,x+130,y+172,14,'Semi',leading=18,align='center')
        text(mass if mass else 'Мини-наггетсы из курицы',x+130,y+199,12.5,'Book',MUTED,align='center')
    end()

catalogue_page([
 ('naggetsy-kurinye','Наггетсы куриные','400 г'),
 ('naggetsy-kurinye-s-syrom','Наггетсы с сыром','400 г'),
 ('naggetsy-ostrye','Наггетсы острые','400 г'),
 ('naggetsy-dinozavry','Наггетсы «Динозавры»','400 г'),
 ('naggetsy-s-indeykoy-fitnes','Наггетсы с индейкой «Фитнес»','400 г')],1,'Наггетсы')
catalogue_page([
 ('kotlety-kurinye','Котлеты куриные','522 г'),
 ('kotlety-po-domashnemu','Котлеты по-домашнему','480 г'),
 ('kotlety-pikantnye','Котлеты пикантные','480 г'),
 ('kotlety-po-italyanski','Котлеты по-итальянски','480 г'),
 ('bitochki-kurinye-s-ovoshchami','Биточки куриные с овощами','450 г')],2,'Котлеты и биточки')
catalogue_page([
 ('frikadelki-klassicheskie','Фрикадельки «Классические»','500 г'),
 ('ezhiki-iz-tsyplenka-s-risom','Ёжики из цыплёнка с рисом','480 г'),
 ('stripsy','Стрипсы','400 г'),
 ('kurinyj-popkorn','Куриный попкорн','400 г'),
 ('popsy','Попсы','')],3,'Фрикадельки, ёжики и снеки')

# 07 / Two offers begin immediately; no overall heading, no empty right-hand header.
start('Продукция Новофермы и СТМ')
fill(480,0,480,H,ORANGE)
text('ДЛЯ ПОЛКИ.',43,141,55,'Poster')
text('ДЛЯ МЕНЮ.',44,203,55,'Poster',ORANGE)
para('Готовая продукция в фирменной упаковке Новофермы для магазинов, кафе и ресторанов.',46,326,374,23,'Book',leading=33)
text('ВАШ БРЕНД.',520,141,55,'Poster',CREAM)
text('НАШ ПРОДУКТ.',521,203,55,'Poster',INK)
para('Наш продукт под вашей торговой маркой. Адаптируем упаковку, подберём ассортимент и фасовки.',524,326,374,23,'Book',CREAM,33)
end()

# 08 / Keep the approved closing, with a simpler contact-only lower half.
start('Контакты',bg=INK,folio=False)
text('ПОЖМЁМ\nКРЫЛЬЯ?',43,113,75,'Poster',CREAM,76)
link('zakaz@novoferma.ru','mailto:zakaz@novoferma.ru',44,366,30,'Bold',ORANGE)
link('+7 (931) 213-55-50','tel:+79312135550',46,419,25,'Semi',CREAM)
link('novoferma.ru','https://novoferma.ru/',47,487,16,'Semi',CREAM)
art('mascot-contact-restored-v2.webp',722,156,238,390)
end()

c.save()
(T/'text-bounds.json').write_text(json.dumps(bounds,ensure_ascii=False,indent=2))
manifest={'slides':slides,'images':placements,
 'revision_requirements':{'welcome':'Keep title and paragraph; replace three bottom facts with one line','protein':'52g perClassicpack; no500g/arrow; new paintedseal; poultrysource,naturalspices,noadditives narrowlyClassic','fibriki':'One paragraph plus generated bird/leaf paintedlockup; noarrows; lifestyleunchanged','catalogue':'Keepv8pixelidentical','offers':'Keepv8pixelidentical','closing':'Keepv8pixelidentical'},
 'evidence':{'protein_52g':'Earlier explicit owner value, retained over casual50g wording','classic_no_additives':'Latest owner instruction plus originalClassicpack wording;nottransferredtoFibriki','source_research':'output/brochure-v8/company-evidence.json;output/brochure-v8/nutrition-evidence.json','generated_art':'Built-inImageGen;prompts saved alongsidePNGassets'},
 'scope':'14 series products plus Popsy; separate Fibriki innovation.'}
(ROOT/'output/brochure-v9/manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
errors=[b for b in bounds if b['x']<0 or b['right']>W-18 or b['bottom']>H-8]
if errors:raise RuntimeError(json.dumps(errors,ensure_ascii=False))
print(json.dumps({'path':str(OUT),'pages':page,'bytes':OUT.stat().st_size,'text_bounds':'passed'},ensure_ascii=False))
