"""Novoferma partner presentation, revised to the detailed brand-owner brief.

Original package JPEGs are embedded byte-for-byte and integrated with PDF blending.
The protein juggler and the current website Fibriki artwork are brand illustrations.
Original photographs are used for all catalogue packages.
"""
from pathlib import Path
from io import BytesIO
from functools import lru_cache
import json, math, sys

ROOT=Path(__file__).resolve().parents[1]
A=ROOT/'output/concept/assets'
B=ROOT/'output/brochure-v5/assets'
P=ROOT/'output/brochure-v3/packshots'
T=ROOT/'tmp/pdfs/product-brochure-v5'
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
            if r.nameID in (1,3,4,6):r.string=('NFbrandV5-'+alias).encode(r.getEncoding())
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

# 01 / A welcoming introduction focused on the manufacturer and Saint Petersburg.
start('Знакомство с компанией',backdrop=str(ROOT/'output/brochure-v4/assets/cover-backdrop.png'),folio=False,with_logo=False)
logo(w=200)
text('НОВОФЕРМА / ЗНАКОМСТВО',46,99,10,'Semi')
text('ДАВАЙТЕ\nЗНАКОМИТЬСЯ',42,130,68,'Poster',leading=71)
text('Мы - Новоферма',45,291,32,'Hand',ORANGE)
para('Компания из Санкт-Петербурга.\nПроизводим замороженные полуфабрикаты из курицы и индейки.',46,350,344,19,leading=26)
text('Для торговли и общественного питания',47,472,12.5,'Semi',MUTED)
for slug,x in [('naggetsy-kurinye',405),('frikadelki-klassicheskie',580),('kotlety-po-domashnemu',755)]:pack(slug,x,371,163,128)
end()

# 02 / Juggler artwork, with live 52 g type in the intentionally empty flying slot.
start('Белок')
image(B/'protein-juggler.png',0,0,W,H)
text('В ОСНОВЕ',43,108,69,'Poster')
text('БЕЛОК',44,180,89,'Poster',ORANGE)
text('Природный белок мяса птицы\nв привычных форматах',47,291,19,leading=26)
text('52 г',685,105,88,'Bold',ORANGE,align='center')
text('белка',685,207,27,'Semi',align='center')
para('(≈69% от средней суточной\nпотребности*)',47,357,367,18,'Semi',ORANGE,24)
pack('frikadelki-klassicheskie',45,412,137,95)
text('Фрикадельки\n«Классические», 500 г',205,430,17,'Semi',leading=23)
text('*Справочная величина для взрослого: 75 г белка/сутки (ТР ТС 022/2011). Индивидуальная потребность может отличаться.',46,519,8.3,'Book',MUTED)
end()

# 03 / The main innovation story merges the former fibre and Fibriki slides.
start('Фибрики. Белок и клетчатка')
text('НАША НОВИНКА',46,98,10.5,'Semi',ORANGE)
text('ФИБРИКИ',42,124,81,'Poster')
text('Белок птицы',46,229,27,'Semi')
text('+ пищевые волокна',46,270,27,'Semi',ORANGE)
text('Клетчатка в привычном блюде',46,317,27,'Hand',ORANGE)
para('Естественный белок и тренд на клетчатку соединяем в знакомом формате - куриных фрикадельках.',46,365,366,18,leading=24)
art('product-hero/fibriki-art-v6.png',477,84,449,393,(720,25,1640,830))
image(ROOT/'output/research/fibriki-herbs-v11/fibriki-pack-v11.png',45,442,134,87,(30,115,1220,1100))
text('Фибрики',202,449,21,'Bold')
text('Куриные фрикадельки\nс пищевыми волокнами',203,481,13.5,leading=18)
end()

# 04-06 / Fourteen original packages, once each, with website-style warm underlays.
def underlay(x,y,w,h):
    # Native layout background matching the existing CSS organic packshot surface.
    c.saveState();c.setFillColor(HexColor('#f5e4be'))
    p=c.beginPath()
    def point(a,b):return (x+a*w,H-y-b*h)
    p.moveTo(*point(.035,.43))
    p.curveTo(*point(.01,.13),*point(.23,.015),*point(.51,.03))
    p.curveTo(*point(.81,.005),*point(.99,.19),*point(.975,.49))
    p.curveTo(*point(.99,.81),*point(.78,.995),*point(.48,.97))
    p.curveTo(*point(.20,.995),*point(.01,.80),*point(.035,.43))
    p.close();c.drawPath(p,fill=1,stroke=0);c.restoreState()

def catalogue_page(records,index):
    start('Наша продукция / '+str(index))
    text('НАША ПРОДУКЦИЯ',43,94,47,'Poster')
    text(f'{index} / 3',803,109,16,'Semi',ORANGE)
    positions=[(42,145),(348,145),(654,145),(195,340),(501,340)] if len(records)==5 else [(195,145),(501,145),(195,340),(501,340)]
    for (slug,name,mass),(x,y) in zip(records,positions):
        underlay(x+34,y+25,197,113)
        pack(slug,x,y,264,151)
        text(name,x+132,y+158,12.8,'Semi',align='center')
        text(mass,x+132,y+180,11.5,'Semi',ORANGE,align='center')
    end()

catalogue_page([
 ('naggetsy-kurinye','Наггетсы куриные','400 г'),
 ('naggetsy-kurinye-s-syrom','Наггетсы куриные с сыром','400 г'),
 ('naggetsy-ostrye','Наггетсы куриные острые','400 г'),
 ('naggetsy-dinozavry','Наггетсы куриные «Динозавры»','400 г'),
 ('naggetsy-s-indeykoy-fitnes','Наггетсы с индейкой «Фитнес»','400 г')],1)
catalogue_page([
 ('kotlety-kurinye','Котлеты куриные','522 г'),
 ('kotlety-po-domashnemu','Котлеты по-домашнему','480 г'),
 ('kotlety-pikantnye','Котлеты пикантные','480 г'),
 ('kotlety-po-italyanski','Котлеты по-итальянски','480 г'),
 ('bitochki-kurinye-s-ovoshchami','Биточки куриные с овощами','450 г')],2)
catalogue_page([
 ('frikadelki-klassicheskie','Фрикадельки «Классические»','500 г'),
 ('ezhiki-iz-tsyplenka-s-risom','Ёжики из цыплёнка с рисом','480 г'),
 ('stripsy','Стрипсы','400 г'),
 ('kurinyj-popkorn','Куриный попкорн','400 г')],3)

# 07 / Two offers, with the exact current website headings and no mascot or workflow.
start('Форматы сотрудничества')
fill(480,0,480,H,'#F7E8CC')
text('07',895,38,11,'Semi',MUTED)
text('СОТРУДНИЧЕСТВО',43,96,51,'Poster')
text('Выберите формат для вашего бизнеса',46,166,18,'Book')
text('ПРОДУКЦИЯ НОВОФЕРМЫ',46,232,11,'Semi',MUTED)
text('ДЛЯ ПОЛКИ.',43,269,49,'Poster')
text('ДЛЯ МЕНЮ.',44,323,49,'Poster',ORANGE)
para('Готовый ассортимент для магазинов, кафе и ресторанов.',46,402,381,20,leading=28)
text('СОБСТВЕННАЯ ТОРГОВАЯ МАРКА',523,232,11,'Semi',MUTED)
text('ВАШ БРЕНД.',520,269,49,'Poster')
text('НАШ ПРОДУКТ.',521,323,49,'Poster',ORANGE)
text('Выпускаем продукты\nпод вашей торговой маркой.',524,402,20,leading=28)
text('Обсудим ассортимент, фасовки и объём',46,492,15,'Semi',MUTED)
end()

# 08 / Preserve the approved closing; only the unwanted request-detail line is removed.
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
requirements={
 'welcome':'Manufacturer in Saint Petersburg, explicit company welcome',
 'protein':'Original-style juggling scene; live52g flying in numeric slot; small Classic500g pack;69% of75g reference with explanatoryfootnote',
 'fibriki':'Merged maininnovation, currentwebsitejugglingv6; naturalprotein+fibre/trend;smallFibrikipack;novinkastatus',
 'catalogue':'Original14JPEGs exactlyonce on3pages5/5/4;sitecreamorganicunderlays;no home/snackthemes',
 'offers':'Exactsiteheadings ownbrandleft/STMright;twoequalcolumns;no mascots or workflow',
 'closing':'Approvedv4brownclosewithoutcitypositionsvolumeline'}
manifest={'slides':slides,'images':placements,'requirements':requirements,
 'daily_reference':{'protein_g_per_day':75,'pack_protein_g':52,'percent':52/75*100,'caption_rounded_percent':69,'basis':'ТР ТС022/2011, приложение2, средняя суточная потребность взрослого длямаркировки','official_url':'https://eec.eaeunion.org/upload/medialibrary/9db/TrTsPishevkaMarkirovka.pdf','page':24,'verified':'2026-11-05'},
 'scope':'14 products explicitly requested by user. Current website hero images used only as brand illustrations; original package photos remain unchanged.'}
(ROOT/'output/brochure-v5/manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
errors=[b for b in bounds if b['x']<0 or b['right']>W-18 or b['bottom']>H-8]
if errors:raise RuntimeError(json.dumps(errors,ensure_ascii=False))
print(json.dumps({'path':str(OUT),'pages':page,'bytes':OUT.stat().st_size,'text_bounds':'passed'},ensure_ascii=False))
