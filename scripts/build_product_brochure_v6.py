"""Novoferma presentation: premium food editorials and a 6/6/2 original-photo catalogue.

Original package JPEGs are embedded byte-for-byte and integrated with PDF blending.
Food editorials are freshly generated; no juggling artwork is reused.
Original photographs are used for all catalogue packages.
"""
from pathlib import Path
from io import BytesIO
from functools import lru_cache
import json, math, sys

ROOT=Path(__file__).resolve().parents[1]
A=ROOT/'output/concept/assets'
B=ROOT/'output/brochure-v6/assets'
P=ROOT/'output/brochure-v3/packshots'
T=ROOT/'tmp/pdfs/product-brochure-v6'
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
            if r.nameID in (1,3,4,6):r.string=('NFbrandV6-'+alias).encode(r.getEncoding())
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

def pack(slug,x,y,w,h):image(P/(slug+'-pack.jpg'),x,y,w,h,(80,180,1230,1180),False)
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

# 01 / Welcome, with the exact approved side-peeking mascot and no packages.
start('Знакомство с компанией',folio=False,with_logo=False)
logo(w=194)
text('КОМПАНИЯ ИЗ САНКТ-ПЕТЕРБУРГА',47,108,11,'Semi',MUTED)
text('Давайте',44,150,51,'Bold')
text('знакомиться',44,208,51,'Bold',ORANGE)
text('Новоферма производит\nзамороженные полуфабрикаты\nиз курицы и индейки.',47,317,22,'Book',leading=30)
text('Для магазинов, кафе и ресторанов',47,452,17,'Semi',MUTED)
art('mascot-contact-restored-v2.webp',666,150,294,482)
end()

# 02 / A new editorial, with the nutritional figure clearly tied to the original pack.
start('Белок',backdrop='protein-editorial.png')
text('В основе\nбелок птицы',44,104,37,'Bold',leading=43)
text('52 г',42,224,108,'Bold',ORANGE)
text('белка в упаковке',47,346,23,'Semi')
text('(≈69% от средней суточной потребности*)',47,392,16.5,'Semi',ORANGE)
pack('frikadelki-klassicheskie',45,432,119,76)
text('Фрикадельки «Классические»\nУпаковка 500 г',182,442,15.5,'Semi',leading=22)
text('*Справочная величина для взрослого: 75 г белка/сутки (ТР ТС 022/2011).\nИндивидуальная потребность может отличаться.',46,510,8.3,'Book',MUTED,11)
end()

# 03 / A new green, three-angle product editorial, no old juggler or flying pieces.
start('Фибрики. Новинка',bg='#31563E',backdrop='fibriki-editorial.png',with_logo=False)
fill(31,18,183,50,CREAM)
logo()
text('03',895,38,11,'Semi',CREAM)
text('НАША НОВИНКА',47,99,11,'Semi','#F5E4BE')
text('Фибрики',43,128,56,'Bold',CREAM)
text('Белок птицы\n+ пищевые волокна',47,225,24,'Semi',CREAM,33)
text('Клетчатка в привычном блюде',47,310,20,'Hand','#F5E4BE')
text('Новый взгляд на состав\nзнакомых куриных фрикаделек.',47,359,17,'Book',CREAM,24)
image(ROOT/'output/research/fibriki-herbs-v11/fibriki-pack-v11.png',45,431,115,84,(30,115,1220,1100))
text('Фибрики',182,438,19,'Bold',CREAM)
text('Куриные фрикадельки\nс пищевыми волокнами',183,470,13,'Book',CREAM,18)
end()

# 04-06 / Six plus six plus two, normal blend and white fields preserve pack colours.
def catalogue_page(records,index):
    start('Наша продукция / '+str(index),bg='#FFFFFF')
    fill(0,0,W,133,CREAM)
    logo()
    text(f'{page:02}',895,38,11,'Semi',MUTED)
    text('Наша продукция',44,88,36,'Bold')
    text(f'{index} / 3',810,103,16,'Semi',ORANGE)
    if len(records)==6:
        positions=[(42,148),(348,148),(654,148),(42,341),(348,341),(654,341)]
        for (slug,name,mass),(x,y) in zip(records,positions):
            pack(slug,x,y,264,145)
            text(name,x+132,y+154,12.3,'Semi',align='center')
            text(mass,x+132,y+176,11.5,'Semi',ORANGE,align='center')
    else:
        for (slug,name,mass),x in zip(records,[106,522]):
            pack(slug,x,174,332,266)
            text(name,x+166,464,19,'Semi',align='center')
            text(mass,x+166,501,16,'Semi',ORANGE,align='center')
    end()

catalogue_page([
 ('naggetsy-kurinye','Наггетсы куриные','400 г'),
 ('naggetsy-kurinye-s-syrom','Наггетсы куриные с сыром','400 г'),
 ('naggetsy-ostrye','Наггетсы куриные острые','400 г'),
 ('naggetsy-dinozavry','Наггетсы куриные «Динозавры»','400 г'),
 ('naggetsy-s-indeykoy-fitnes','Наггетсы с индейкой «Фитнес»','400 г'),
 ('stripsy','Стрипсы','400 г')],1)
catalogue_page([
 ('kotlety-kurinye','Котлеты куриные','522 г'),
 ('kotlety-po-domashnemu','Котлеты по-домашнему','480 г'),
 ('kotlety-pikantnye','Котлеты пикантные','480 г'),
 ('kotlety-po-italyanski','Котлеты по-итальянски','480 г'),
 ('bitochki-kurinye-s-ovoshchami','Биточки куриные с овощами','450 г'),
 ('ezhiki-iz-tsyplenka-s-risom','Ёжики из цыплёнка с рисом','480 г')],2)
catalogue_page([
 ('frikadelki-klassicheskie','Фрикадельки «Классические»','500 г'),
 ('kurinyj-popkorn','Куриный попкорн','400 г')],3)

# 07 / Two offers begin immediately; no overall heading, no empty right-hand header.
start('Продукция Новофермы и СТМ')
fill(480,0,480,H,'#F7E8CC')
text('07',895,38,11,'Semi',MUTED)
text('ПРОДУКЦИЯ НОВОФЕРМЫ',46,111,11.5,'Semi',MUTED)
text('ДЛЯ ПОЛКИ.',43,153,51,'Poster')
text('ДЛЯ МЕНЮ.',44,210,51,'Poster',ORANGE)
text('Готовый ассортимент\nв фирменной упаковке\nНовофермы.',46,308,22,'Semi',leading=30)
text('Подберём продукты и фасовки\nдля магазина, кафе или ресторана.',46,434,17,'Book',leading=24)
text('СОБСТВЕННАЯ ТОРГОВАЯ МАРКА / СТМ',523,111,11.5,'Semi',MUTED)
text('ВАШ БРЕНД.',520,153,51,'Poster')
text('НАШ ПРОДУКТ.',521,210,51,'Poster',ORANGE)
text('Продукты Новофермы\nпод вашей торговой маркой,\nв упаковке с вашим дизайном.',524,308,22,'Semi',leading=30)
text('Адаптируем оформление. Согласуем\nассортимент, фасовки и объём.',524,434,17,'Book',leading=24)
end()

# 08 / The approved high-contrast closing is intentionally unchanged from v5.
start('Контакты',bg=INK,folio=False)
text('ПОЖМЁМ\nКРЫЛЬЯ?',43,113,75,'Poster',CREAM,76)
text('Начнём с вашего запроса',46,301,24,'Hand',ORANGE)
link('zakaz@novoferma.ru','mailto:zakaz@novoferma.ru',44,366,30,'Bold',ORANGE)
link('+7 (931) 213-55-50','tel:+79312135550',46,419,25,'Semi',CREAM)
link('novoferma.ru','https://novoferma.ru/',47,487,16,'Semi',CREAM)
art('mascot-contact-restored-v2.webp',722,156,238,390)
end()

c.save()
(T/'text-bounds.json').write_text(json.dumps(bounds,ensure_ascii=False,indent=2))
manifest={'slides':slides,'images':placements,
 'revision_requirements':{'welcome':'Exact side-peeking approved mascot; no packages; companySPbintro','protein':'Fresh premium stilllife, no juggler;52gand69%with75greference','fibriki':'Fresh deepgreen editorial, product from3angles;smalloriginalpack','catalogue':'14unchangedoriginalJPEGs,6/6/2,whitefields,Normalblend','offers':'No overallheading;ownbrandvsSTM;adaptedpackagingexplained;equalhighstart','closing':'Approvedv5unchanged'},
 'daily_reference':{'protein_g_per_day':75,'pack_protein_g':52,'percent':52/75*100,'caption_rounded_percent':69,'basis':'ТР ТС022/2011, приложение2, средняя суточная потребность взрослого длямаркировки','official_url':'https://eec.eaeunion.org/upload/medialibrary/9db/TrTsPishevkaMarkirovka.pdf','page':24,'verified':'2026-11-05'},
 'scope':'14 series products explicitly requested; separate Fibriki innovation.'}
(ROOT/'output/brochure-v6/manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
errors=[b for b in bounds if b['x']<0 or b['right']>W-18 or b['bottom']>H-8]
if errors:raise RuntimeError(json.dumps(errors,ensure_ascii=False))
print(json.dumps({'path':str(OUT),'pages':page,'bytes':OUT.stat().st_size,'text_bounds':'passed'},ensure_ascii=False))
