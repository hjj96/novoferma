"""Editorial, individually art-directed partner brochure, revision 2.

The 52 g per pack figure was supplied by the brand owner on 2026-11-05.
Research links and survey statistics are intentionally absent from the PDF.
"""
from pathlib import Path
from io import BytesIO
from functools import lru_cache
import json
import sys

ROOT=Path(__file__).resolve().parents[1]
A=ROOT/'output/concept/assets'
B=ROOT/'output/brochure-v2/assets'
T=ROOT/'tmp/pdfs/product-brochure-v2'
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

OUT=ROOT/'output/pdf/novoferma-products-partners.pdf'
W,H=960,540
CREAM='#FFF5E3';INK='#402111';ORANGE='#EC5812';SAGE='#DCE1B3';MUTED='#795E4C'
for name,filename,weight in [('Book','Onest-wght.ttf',450),('Semi','Onest-wght.ttf',650),('Bold','Onest-wght.ttf',850),('Hand','Caveat-wght.ttf',600),('Poster','RobotoFlex-Protein.woff2',None)]:
    target=T/(name+'.ttf')
    if not target.exists():
        f=Font(A/'fonts'/filename)
        if weight and 'fvar' in f:f=instantiateVariableFont(f,{'wght':weight},inplace=False)
        f.flavor=None
        for r in f['name'].names:
            if r.nameID in (1,3,4,6):r.string=('NovofermaV2-'+name).encode(r.getEncoding())
            elif r.nameID==2:r.string='Regular'.encode(r.getEncoding())
        f.save(target)
    pdfmetrics.registerFont(TTFont(name,str(target)))

c=canvas.Canvas(str(OUT),pagesize=(W,H),pageCompression=1)
c.setTitle('Новоферма | Еда с характером')
c.setAuthor('Новоферма')
c.setSubject('Продукция из курицы и индейки для партнёров')
c.setCreator('Новоферма')
c.setViewerPreference('DisplayDocTitle','true')
page=0;bounds=[];directions=[]

# JPEG colour planes plus original lossless alpha; pack typography is untouched.
_original=PDFImageXObject.loadImageFromSRC
def _with_alpha(self,reader):
    _original(self,reader)
    if getattr(reader,'_keep_alpha',False):
        self.mask='auto';self._checkTransparency(reader)
PDFImageXObject.loadImageFromSRC=_with_alpha

@lru_cache(maxsize=100)
def load(rel,trim):
    path=B/rel[1:] if rel.startswith('@') else A/rel
    im=Image.open(path).convert('RGBA')
    if trim:
        box=im.getchannel('A').getbbox()
        if box:im=im.crop(box)
    reader=ImageReader(im);reader.getRGBData()
    stream=BytesIO();im.convert('RGB').save(stream,format='JPEG',quality=94,subsampling=0,optimize=True)
    def jpeg():stream.seek(0);return stream
    reader.jpeg_fh=jpeg;reader._keep_alpha=True
    return reader,im.size

def im(rel,x,y,w,h,trim=False,cover=False):
    reader,(iw,ih)=load(rel,trim)
    scale=(max if cover else min)(w/iw,h/ih)
    dw,dh=iw*scale,ih*scale
    c.saveState()
    path=c.beginPath();path.rect(x,H-y-h,w,h);c.clipPath(path,stroke=0,fill=0)
    c.drawImage(reader,x+(w-dw)/2,H-y-(h+dh)/2,dw,dh,mask='auto')
    c.restoreState()

def block(x,y,w,h,color):
    c.setFillColor(HexColor(color));c.rect(x,H-y-h,w,h,fill=1,stroke=0)

def text(s,x,y,size=18,face='Book',color=INK,leading=None):
    leading=leading or size*1.2
    c.setFillColor(HexColor(color));c.setFont(face,size)
    for i,line in enumerate(s.split('\n')):
        yy=y+i*leading
        width=pdfmetrics.stringWidth(line,face,size)
        bounds.append({'page':page,'text':line,'x':x,'top':yy,'right':x+width,'bottom':yy+size})
        c.drawString(x,H-yy-size*.83,line)
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

def start(section,direction,bg=CREAM,background=None,logo=True,folio=True):
    global page
    page+=1
    directions.append({'slide':page,'section':section,'art_direction':direction})
    block(0,0,W,H,bg)
    if background:im(background,0,0,W,H,cover=True)
    if logo:im('logo-reference.webp',42,27,158,34)
    light=bg==INK
    color=CREAM if light else MUTED
    if section:
        width=pdfmetrics.stringWidth(section.upper(),'Semi',9)
        text(section.upper(),918-width,39,9,'Semi',color)
    if folio:text(f'{page:02}',895,511,11,'Semi',CREAM if light else INK)

def end():c.showPage()
def pack(slug,x,y,w,h):im('catalogue-clean-v2/'+slug+'.webp',x,y,w,h,True)
def link(label,url,x,y,size=20,color=INK,face='Semi'):
    text(label,x,y,size,face,color)
    c.linkURL(url,(x,H-y-size*1.12,x+pdfmetrics.stringWidth(label,face,size),H-y+2),thickness=0)

# 01 / A campaign cover with live type set into the scene's negative space.
start('', 'Full bleed bespoke campaign scene, large condensed left title',background='@cover-scene.png',logo=False,folio=False)
im('logo-reference.webp',42,28,207,46)
text('ПРОДУКТЫ ДЛЯ ПАРТНЁРОВ',45,109,11,'Semi')
text('ЕДА',41,131,108,'Poster',INK)
text('С ХАРАКТЕРОМ',43,237,56,'Poster',INK)
para('Из курицы и индейки.\nДля вашей полки и меню.',46,328,270,18,'Book',INK,25)
text('Привычно вкусно',44,437,31,'Hand',CREAM)
text('ЗАМОРОЖЕННЫЕ ПРОДУКТЫ / НОЯБРЬ 2026',45,506,8,'Semi',INK)
end()

# 02 / The familiar brand scene establishes what the company makes.
start('В основе продукта','Sage left editorial column, large nugget cross-section and curious mascot at right',SAGE)
text('В ОСНОВЕ',42,108,81,'Poster')
text('ПТИЦА',42,188,110,'Poster',ORANGE)
para('Мы делаем продукты из курицы и индейки в форматах, которые знают и любят.',46,326,352,21,leading=28)
para('Котлеты, наггетсы, фрикадельки и снеки для повседневного стола.',46,432,332,17,leading=23)
im('protein-story/nuggets-layer-v2.webp',407,250,323,239,True)
im('protein-story/hen-layer-v2.webp',686,169,255,294,True)
text('Заглянем внутрь?',617,109,34,'Hand',ORANGE)
end()

# 03 / Only the owner's confirmed meatball-pack claim is quantified.
start('','Full bleed macro food scene with oversized 52 g typography and exact existing pack',background='@protein-scene.png')
text('ФРИКАДЕЛЬКИ «КЛАССИЧЕСКИЕ»',44,104,11,'Semi')
text('52',35,143,166,'Bold',ORANGE)
text('г',250,237,51,'Semi',ORANGE)
text('БЕЛКА',44,310,57,'Poster')
para('в упаковке фрикаделек\n«Классические», 500 г',46,379,304,19,leading=26)
pack('frikadelki-klassicheskie',362,339,228,169)
end()

# 04 / A second bespoke scene integrates fibre, food and mascot in one light.
start('Белок + клетчатка','Full bleed sage food-and-mascot illustration, open left typography',background='@fibre-scene.png')
text('БЕЛОК +',42,115,86,'Poster')
text('КЛЕТЧАТКА',43,200,74,'Poster',ORANGE)
para('Клетчатка - пищевые волокна.\nОдин из заметных трендов\nсовременного питания.',46,313,302,20,leading=27)
para('Белок птицы и пищевые волокна - основа идеи Фибриков.',46,422,293,17,leading=23)
end()

# 05 / The innovation is packaged as a product story, not a technical appendix.
start('Новинка / концепт','Large Fibriki pack over the signature orange floor, controlled left typography',background='product-hero/background-v2.webp')
text('ФИБРИКИ',42,112,94,'Poster')
text('Белок + клетчатка',46,217,34,'Hand',ORANGE)
para('Куриные фрикадельки\nс пищевыми волокнами',46,293,351,25,'Semi',leading=31)
para('Новый акцент в знакомом продукте. Для покупателя, который смотрит на состав.',46,395,319,18,leading=25)
im('novelty-packaging/fibriki-pack-v11.webp',449,136,465,348,True)
text('КОНЦЕПТ ПРОДУКТА И УПАКОВКИ',47,507,8,'Semi')
end()

# 06 / Nuggets: one flagship and four variants, no five-identical-column strip.
start('Ассортимент / 5 позиций','Asymmetric catalogue spread: flagship left, four variants on a flat two-by-two field')
text('НАГГЕТСЫ',42,95,85,'Poster')
para('Классический вкус, сыр, острота\nи игровые формы. Все позиции по 400 г.',507,102,402,18,leading=25)
pack('naggetsy-kurinye',49,201,329,229)
text('Куриные',58,443,27,'Bold')
text('400 г',59,485,18,'Semi',ORANGE)
variants=[('naggetsy-kurinye-s-syrom','Куриные с сыром',447,176),('naggetsy-ostrye','Куриные острые',702,176),('naggetsy-dinozavry','Куриные «Динозавры»',447,348),('naggetsy-s-indeykoy-fitnes','С индейкой «Фитнес»',702,348)]
for slug,name,x,y in variants:
    pack(slug,x,y,202,129)
    para(name,x,y+137,204,14.5,'Semi',leading=18)
end()

# 07 / Four cutlets use bigger packshots and a single shared baseline.
start('Ассортимент / 4 позиции','Four generous package portraits, aligned editorial names and weights')
text('КОТЛЕТЫ',42,95,89,'Poster')
para('Домашние вкусы для обеда и ужина.\nДобавьте любимый гарнир.',487,104,412,19,leading=26)
cutlets=[('kotlety-kurinye','Куриные','522 г'),('kotlety-po-domashnemu','По-домашнему','480 г'),('kotlety-pikantnye','Пикантные','480 г'),('kotlety-po-italyanski','По-итальянски','480 г')]
for i,(slug,name,mass) in enumerate(cutlets):
    x=43+i*222
    pack(slug,x,230,207,179)
    text(name,x+4,438,19,'Semi')
    text(mass,x+4,478,15,'Semi',ORANGE)
end()

# 08 / A paired spread has its own pale sage / cream colour composition.
start('','Two large product packages over cream-and-sage halves',logo=False,folio=False)
block(480,0,480,540,SAGE)
im('logo-reference.webp',42,27,158,34)
text('Домашние сочетания',42,102,45,'Bold')
text('Курица + овощи',65,177,29,'Hand',ORANGE)
text('Цыплёнок + рис',541,177,29,'Hand',ORANGE)
pack('bitochki-kurinye-s-ovoshchami',65,226,343,224)
pack('ezhiki-iz-tsyplenka-s-risom',541,226,343,224)
text('Биточки куриные с овощами',65,471,18,'Semi')
text('450 г',65,501,13,'Semi',ORANGE)
text('Ёжики из цыплёнка с рисом',541,471,18,'Semi')
text('480 г',541,501,13,'Semi',ORANGE)
text('08',895,511,11,'Semi')
end()

# 09 / A darker food-ad spread gives snacks a distinctive occasion.
start('Ассортимент / для компании','Dark chocolate food photography, large left title, two exact package cutouts',INK,background='@snack-scene.png')
text('ПОВОД',42,104,88,'Poster',CREAM)
text('СОБРАТЬСЯ',43,189,72,'Poster',CREAM)
text('Похрустим?',45,278,32,'Hand',ORANGE)
pack('stripsy',45,346,210,136)
pack('kurinyj-popkorn',276,346,210,136)
text('Стрипсы',48,490,17,'Semi',CREAM)
text('Куриный попкорн',278,490,17,'Semi',CREAM)
text('400 г',49,515,10,'Semi',CREAM)
text('400 г',279,515,10,'Semi',CREAM)
end()

# 10 / A product concept with an airy, almost poster-sized package image.
start('Новинка / концепт','Large right package over branded warm floor, left poster headline and quiet copy',background='product-hero/background-v2.webp')
text('ЛЮЛЯ',42,112,91,'Poster')
text('МИНИ',43,200,94,'Poster',ORANGE)
text('Больше идей для меню',46,313,31,'Hand',ORANGE)
para('Куриные колбаски с зеленью и овощами. С гарниром, в лаваше или для общего стола.',46,380,323,19,leading=26)
im('novelty-packaging/lulia-mini-pack-v3.webp',448,148,465,333,True)
text('КОНЦЕПТ ПРОДУКТА И УПАКОВКИ',47,507,8,'Semi')
end()

# 11 / Packaging has one hero and one direct business implication.
start('Бренд на полке','Oversized exact strips packaging, restrained flat editorial copy')
text('На полке\nузнают своих',42,112,48,'Bold',leading=51)
para('Тёплые цвета и курочки с характером объединяют ассортимент.',46,279,346,21,leading=29)
text('Продукт видно',46,391,24,'Bold')
para('Прозрачный контейнер помогает рассмотреть его до покупки.',46,435,320,18,leading=25)
pack('stripsy',439,151,463,329)
text('У каждого продукта\nсвоя история',681,88,27,'Hand',ORANGE,28)
end()

# 12 / The business discussion gets one calm scene and practical topics.
start('Сотрудничество','Original illustrated handshake grounded on a lowered signature floor, two left offer blocks')
im('product-hero/shared-floor-v11.webp',0,45,W,H)
text('ПОЖМЁМ',42,108,88,'Poster')
text('КРЫЛЬЯ?',43,193,91,'Poster',ORANGE)
text('Под брендом Новоферма',46,310,23,'Bold')
para('Для магазинов, кафе и ресторанов. Обсудим ассортимент, цену, объём и поставку.',46,350,407,18,leading=25)
text('Под вашей торговой маркой',46,426,20,'Bold')
para('Обсудим задачу СТМ и требования к продукту.',46,461,410,15,leading=20)
im('partners-hero-v4/brand-handshake-v1.webp',528,224,383,269,True)
text('12',895,511,11,'Semi')
end()

# 13 / Contact details are the only links in the public sales document.
start('Для вашей полки и меню','Warm cream close with large live contact typography and the original peeking mascot',folio=False)
text('Давайте\nзнакомиться',42,111,55,'Bold',leading=58)
para('Расскажите, какие продукты вам интересны.\nУкажите город и планируемый объём.',46,277,573,20,leading=28)
link('zakaz@novoferma.ru','mailto:zakaz@novoferma.ru',44,375,31,ORANGE,'Bold')
link('+7 (931) 213-55-50','tel:+79312135550',46,426,26,INK)
link('novoferma.ru','https://novoferma.ru/',47,488,16,INK)
text('Санкт-Петербург',277,490,13,'Book',MUTED)
im('mascot-contact-restored-v2.webp',740,187,220,360,True)
end()

c.save()
(T/'text-bounds.json').write_text(json.dumps(bounds,ensure_ascii=False,indent=2))
(ROOT/'output/brochure-v2/slide-directions.json').write_text(json.dumps(directions,ensure_ascii=False,indent=2))
errors=[v for v in bounds if v['x']<0 or v['right']>W-20 or v['bottom']>H-10]
if errors:raise RuntimeError(json.dumps(errors,ensure_ascii=False))
print(json.dumps({'path':str(OUT),'pages':page,'bytes':OUT.stat().st_size,'text_bounds':'passed'},ensure_ascii=False))
