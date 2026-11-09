"""Novoferma partner brochure. Source site and original artwork remain unchanged."""
from pathlib import Path
import json
import sys
from io import BytesIO
from functools import lru_cache

ROOT = Path(__file__).resolve().parents[1]
TMP = ROOT / 'tmp/pdfs/product-brochure'
TMP.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(ROOT / 'tmp/pdfs/fontdeps'))
from fontTools.ttLib import TTFont as Font
from fontTools.varLib.instancer import instantiateVariableFont
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase.pdfdoc import PDFImageXObject

A = ROOT / 'output/concept/assets'
OUT = ROOT / 'output/pdf/novoferma-products-partners.pdf'
OUT.parent.mkdir(parents=True, exist_ok=True)
W, H = 960, 540
CREAM, INK, ORANGE, MUTED, GREEN = '#FFF5E3', '#402111', '#EC5812', '#795E4C', '#DCE1B3'

def font(name, source, weight=None):
    target = TMP / (name + '.ttf')
    if not target.exists():
        f = Font(A / 'fonts' / source)
        if 'fvar' in f and weight:
            f = instantiateVariableFont(f, {'wght': weight}, inplace=False)
        f.flavor = None
        f.save(target)
    # Variable instances must have distinct internal names as well as aliases.
    f=Font(target)
    for record in f['name'].names:
        if record.nameID in (1,3,4,6):
            record.string=('Novoferma-'+name).encode(record.getEncoding())
        elif record.nameID==2:
            record.string='Regular'.encode(record.getEncoding())
    f.save(target)
    pdfmetrics.registerFont(TTFont(name, str(target)))

font('Onest', 'Onest-wght.ttf', 450)
font('OnestSemi', 'Onest-wght.ttf', 650)
font('OnestBold', 'Onest-wght.ttf', 850)
font('Hand', 'Caveat-wght.ttf', 600)
font('Poster', 'RobotoFlex-Protein.woff2')

c = canvas.Canvas(str(OUT), pagesize=(W,H), pageCompression=1)
c.setTitle('Новоферма | Продукты для партнёров')
c.setAuthor('Новоферма')
c.setSubject('Ассортимент, белок и клетчатка, направления сотрудничества')
c.setCreator('Новоферма')
c.setViewerPreference('DisplayDocTitle', 'true')
checks = []
page_no = 0

# Keep an exact lossless alpha mask and JPEG-encode only the colour plane.
# This changes export encoding, not the existing brand artwork.
_load_src=PDFImageXObject.loadImageFromSRC
def _load_jpeg_alpha(self, im):
    _load_src(self, im)
    if getattr(im, '_keep_alpha', False):
        self.mask='auto'
        self._checkTransparency(im)
PDFImageXObject.loadImageFromSRC=_load_jpeg_alpha

def text(s, x, y, size=18, face='Onest', color=INK, leading=None):
    """Top-based text with explicit line breaks and measurable bounds."""
    leading = leading or size*1.2
    c.setFillColor(HexColor(color))
    c.setFont(face, size)
    for i, line in enumerate(s.split('\n')):
        width = pdfmetrics.stringWidth(line, face, size)
        yy = y + i*leading
        checks.append({'page':page_no, 'text':line, 'x':x,'top':yy,'right':x+width,'bottom':yy+size})
        c.drawString(x, H-yy-size*.83, line)
    return y + len(s.split('\n'))*leading

def para(s, x, y, width, size=18, face='Onest', color=INK, leading=None):
    lines=[]
    for segment in s.split('\n'):
        cur=''
        for word in segment.split():
            trial=cur+' '+word if cur else word
            if cur and pdfmetrics.stringWidth(trial,face,size)>width:
                lines.append(cur);cur=word
            else:cur=trial
        lines.append(cur)
    return text('\n'.join(lines), x,y,size,face,color,leading)

@lru_cache(maxsize=128)
def load_image(rel, trim):
    im=Image.open(A/rel).convert('RGBA')
    if trim:
        box=im.getchannel('A').getbbox()
        if box:im=im.crop(box)
    reader=ImageReader(im)
    reader.getRGBData()
    b=BytesIO();im.convert('RGB').save(b,format='JPEG',quality=94,subsampling=0,optimize=True)
    def jpeg():
        b.seek(0)
        return b
    reader.jpeg_fh=jpeg
    reader._keep_alpha=True
    return reader,im.size

def img(rel,x,y,w,h=None,trim=False):
    reader,(iw,ih)=load_image(rel,trim)
    h=h or w*ih/iw
    scale=min(w/iw,h/ih)
    dw,dh=iw*scale,ih*scale
    c.drawImage(reader,x+(w-dw)/2,H-y-(h+dh)/2,width=dw,height=dh,mask='auto')

def rect(x,y,w,h,color):
    c.setFillColor(HexColor(color));c.rect(x,H-y-h,w,h,fill=1,stroke=0)

def base(kicker='', bg=CREAM, logo=True, footer=True):
    global page_no
    page_no+=1
    rect(0,0,W,H,bg)
    if logo:img('logo-reference.webp',42,27,155,34)
    if kicker:text(kicker.upper(), 42,79,10,'OnestSemi',CREAM if bg==ORANGE else MUTED)
    if footer:
        color=INK if bg!=ORANGE else CREAM
        text('НОВОФЕРМА / ПРОДУКТЫ ДЛЯ ПАРТНЁРОВ',42,516,8,'OnestSemi',color)
        text(f'{page_no:02}',902,513,12,'OnestSemi',color)

def done():c.showPage()

def note(s, x=42, y=481, width=865, size=9):
    return para(s,x,y,width,size,'Onest',MUTED,size*1.25)

def pack(slug,x,y,w,h):
    img('catalogue-clean-v2/'+slug+'.webp',x,y,w,h,True)

def link(label,url,x,y,size=15,color=INK,face='OnestSemi'):
    text(label,x,y,size,face,color)
    width=pdfmetrics.stringWidth(label,face,size)
    c.linkURL(url,(x,H-y-size*1.15,x+width,H-y+2),relative=0,thickness=0)

# 01. Cover: existing brand scene, live title, no invented product figures.
base(footer=False)
img('product-hero/background-v2.webp',0,0,960,540)
img('logo-reference.webp',43,29,205,46)
img('product-hero/meatballs-art-v4.webp',0,0,960,540)
text('ПРОДУКТЫ ДЛЯ ВАШЕГО БИЗНЕСА',44,111,10,'OnestSemi')
text('Любимые блюда.\nНовые поводы\nдля выбора',42,148,47,'OnestBold',INK,49)
text('Белок + клетчатка',43,315,35,'Hand',ORANGE)
text('НАПРАВЛЕНИЕ РАЗВИТИЯ',46,351,8,'OnestSemi',MUTED)
para('Замороженные продукты из курицы и индейки.\nЗнакомые форматы для вашей полки и меню.',44,375,400,18,leading=25)
text('АССОРТИМЕНТ И НАПРАВЛЕНИЯ РАЗВИТИЯ',44,493,9,'OnestSemi')
text('НОЯБРЬ 2026',44,510,8,'Onest',MUTED)
done()

# 02. Consumer context, scoped to the actual research population.
base('Покупательский интерес')
text('Белок и клетчатка\nв фокусе питания',42,107,43,'OnestBold',INK,45)
text('70%',42,222,93,'OnestBold',ORANGE)
text('62%',365,222,93,'OnestBold',ORANGE)
para('стараются включать\nбелок в рацион',46,326,275,20,leading=25)
para('стараются включать\nклетчатку в рацион',369,326,285,20,leading=25)
text('56% в 2021 → 62% в 2026',368,390,17,'OnestSemi')
para('Понятная идея\nдля знакомой еды',707,241,211,29,'Hand',ORANGE,31)
para('Развивать привычные продукты, добавляя ещё один аргумент для выбора.',707,329,203,16,leading=22)
note('Источник [1]: IFIC Food & Health Survey 2026, стр. 36–37. США, n = 3 005, возраст 18–80 лет. Опрос: 22.03–08.04.2026.\nМеждународный ориентир; не оценка российского спроса. Доля по клетчатке в 2024–2025 составляла 64%.',y=463,size=8.8)
done()

# 03. Ingredient story, separate from quantitative claims for finished products.
base('О белке просто',GREEN)
text('В ОСНОВЕ',42,108,78,'Poster',INK,78)
text('ПТИЦА',42,190,103,'Poster',ORANGE)
para('Курица и индейка содержат белок от природы. Мы работаем со знакомыми форматами: от котлет до наггетсов.',46,319,345,20,leading=27)
img('protein-story/nuggets-layer-v2.webp',387,226,351,263,True)
img('protein-story/hen-layer-v2.webp',692,160,254,293,True)
text('Вот что внутри!',665,109,35,'Hand',ORANGE)
note('Пищевая ценность зависит от рецептуры. Точные показатели белка и пищевых волокон смотрите на актуальной этикетке конкретного продукта.',y=483,width=850,size=9)
done()

# 04. Explain fibre and connect the nutrient story to familiar formats.
base('О клетчатке просто')
text('Привычная еда.\nЕщё один важный\nингредиент.',42,108,44,'OnestBold',leading=46)
text('Клетчатка',44,268,39,'Hand',ORANGE)
para('Это пищевые волокна. Они важны для нормальной работы кишечника [2].',46,328,329,20,leading=27)
para('Наше направление развития: соединить белок птицы и пищевые волокна в знакомых продуктах.',46,414,369,17,leading=23)
c.saveState()
clip=c.beginPath();clip.rect(452,H-471,482,381)
c.clipPath(clip,stroke=0,fill=0)
img('product-hero/fibriki-art-v4.webp',130,73,800,450)
c.restoreState()
note('Общее свойство пищевых волокон не означает одинакового содержания клетчатки во всех продуктах. Источник [2]: EFSA, Dietary Reference Values.',y=483,size=8.7)
done()

# 05. Fibre proposition and the Fibriki concept.
base('Развитие линейки / концепт новинки')
text('Фибрики',42,108,64,'OnestBold')
text('Белок + клетчатка',45,184,35,'Hand',ORANGE)
para('Куриные фрикадельки\nс пищевыми волокнами',45,244,350,25,'OnestSemi',leading=29)
para('Идея продукта: сохранить знакомый формат и дополнить его клетчаткой. Привычное блюдо получает новую историю на полке.',45,326,330,18,leading=25)
img('novelty-packaging/fibriki-pack-v11.webp',425,143,474,333,True)
text('Знакомая форма.\nНовый акцент.',749,96,29,'Hand',ORANGE,28)
note('Концепт продукта и лицевой упаковки. Финальные состав, пищевая ценность, масса и дата начала продаж согласуются отдельно.',y=483,size=9)
done()

# 05. Full nuggets range, all five confirmed 400 g SKUs.
base('Ассортимент / наггетсы')
text('Пять вариантов\nлюбимого формата',42,109,43,'OnestBold',leading=44)
para('Классический вкус, сыр, острота и игровые формы. Все пять позиций по 400 г.',554,120,345,18,leading=25)
nuggets=[('naggetsy-kurinye','Куриные'),('naggetsy-kurinye-s-syrom','Куриные\nс сыром'),('naggetsy-ostrye','Куриные\nострые'),('naggetsy-dinozavry','Куриные\n«Динозавры»'),('naggetsy-s-indeykoy-fitnes','С индейкой\n«Фитнес»')]
for i,(slug,name) in enumerate(nuggets):
    x=39+i*178
    pack(slug,x,238,170,173)
    text(name,x+4,428,16,'OnestSemi',leading=20)
    text('400 г',x+4,477,11,'Onest',MUTED)
done()

# 06. Full cutlet range.
base('Ассортимент / котлеты и биточки')
text('Домашний стол\nс разными вкусами',42,109,43,'OnestBold',leading=44)
para('Пять позиций для основной части обеда или ужина. Удобно сочетать с привычными гарнирами.',554,120,345,18,leading=25)
cutlets=[('kotlety-kurinye','Котлеты\nкуриные','522 г'),('kotlety-po-domashnemu','Котлеты\nпо-домашнему','480 г'),('kotlety-pikantnye','Котлеты\nпикантные','480 г'),('kotlety-po-italyanski','Котлеты\nпо-итальянски','480 г'),('bitochki-kurinye-s-ovoshchami','Биточки куриные\nс овощами','450 г')]
for i,(slug,name,weight) in enumerate(cutlets):
    x=39+i*178
    pack(slug,x,238,170,173)
    text(name,x+4,428,16,'OnestSemi',leading=20)
    text(weight,x+4,477,11,'Onest',MUTED)
done()

# 07. Remaining four SKUs; no unverified cooking time.
base('Ассортимент / фрикадельки, ёжики и снеки')
text('Для обеда.\nДля вечера с друзьями.',42,108,41,'OnestBold',leading=44)
para('Ещё четыре формата дополняют линейку: от домашней классики до порционных снеков.',583,120,320,18,leading=25)
others=[('frikadelki-klassicheskie','Фрикадельки\n«Классические»','500 г'),('ezhiki-iz-tsyplenka-s-risom','Ёжики из цыплёнка\nс рисом','480 г'),('stripsy','Стрипсы','400 г'),('kurinyj-popkorn','Куриный\nпопкорн','400 г')]
for i,(slug,name,weight) in enumerate(others):
    x=42+i*224
    pack(slug,x,225,201,192)
    text(name,x+2,430,18,'OnestSemi',leading=21)
    text(weight,x+2,481,11,'Onest',MUTED)
done()

# 08. Second concept, clearly distinguished from existing 14 SKUs.
base('Развитие линейки / концепт новинки')
text('Люля мини',42,109,61,'OnestBold')
text('Больше идей для меню',45,184,32,'Hand',ORANGE)
para('Куриные колбаски\nс зеленью и овощами',45,251,335,25,'OnestSemi',leading=29)
para('Небольшой формат для разных подач: с гарниром, в лаваше или как часть общего стола.',45,335,318,19,leading=26)
img('novelty-packaging/lulia-mini-pack-v3.webp',436,157,451,309,True)
note('Концепт продукта и лицевой упаковки. Финальные состав, пищевая ценность, масса и дата начала продаж согласуются отдельно.',y=483,size=9)
done()

# 09. Brand language illustrated by distinct existing assets.
base('Бренд на полке')
text('Упаковка с характером',42,109,44,'OnestBold')
para('Тёплые фирменные цвета, крупное название продукта и курочки с собственной историей.',43,177,465,21,leading=28)
img('catalogue-clean-v2/kotlety-po-domashnemu.webp',27,265,285,209,True)
img('product-hero/nuggets-art-v4.webp',355,192,555,312)
text('Продукт видно',332,294,23,'OnestBold')
para('Прозрачный контейнер помогает рассмотреть форму и панировку до покупки.',333,337,210,17,leading=24)
text('У каждой курочки\nсвой характер',696,160,27,'Hand',ORANGE,27)
note('Изображения упаковок иллюстрируют фирменный стиль. При заказе ориентируйтесь на актуальную этикетку и согласованный макет.',y=483,size=9)
done()

# 10. The value to the buyer, without invented growth or margins.
base('Для торговой полки и меню',ORANGE,logo=False)
text('НОВОФЕРМА',42,30,16,'OnestBold',CREAM)
text('Понятный ассортимент.\nВыразительный бренд.',42,112,47,'OnestBold',CREAM,49)
text('14',42,268,105,'OnestBold',INK)
para('позиций в основном\nассортименте',46,387,256,20,'OnestSemi',CREAM,26)
text('ПРИВЫЧНЫЕ ФОРМАТЫ',386,280,12,'OnestSemi',INK)
para('Покупателю легко понять, что выбрать для своего обеда или ужина.',386,313,499,22,'OnestSemi',CREAM,29)
text('НАПРАВЛЕНИЕ РАЗВИТИЯ',386,401,12,'OnestSemi',INK)
para('Белок и клетчатка дают тему для знакомства с новой линейкой.',386,433,499,22,'OnestSemi',CREAM,29)
done()

# 11. Partner options and an actionable next conversation.
base('Сотрудничество')
text('Ваш ассортимент.\nНаши продукты.',42,108,48,'OnestBold',leading=49)
text('Под брендом Новоферма',44,249,25,'OnestBold')
para('Подберём позиции для магазинов, кафе и ресторанов. Обсудим цену, объём, документы и условия поставки.',45,291,445,19,leading=26)
text('Под вашей торговой маркой',44,400,24,'OnestBold')
para('Обсудим задачу СТМ и требования к продукту и упаковке.',45,440,445,18,leading=25)
img('partners-hero-v4/brand-handshake-v1.webp',548,205,371,265,True)
text('Пожмём крылья?',635,155,36,'Hand',ORANGE)
done()

# 12. Clear next action and working links.
base('Начнём с вашего запроса')
text('Выберем продукты\nдля вашего бизнеса',42,107,47,'OnestBold',leading=49)
para('Напишите, какие позиции вам интересны,\nукажите город и планируемый объём.',45,240,573,21,leading=28)
link('zakaz@novoferma.ru','mailto:zakaz@novoferma.ru',44,328,30,ORANGE,'OnestBold')
link('+7 (931) 213-55-50','tel:+79312135550',45,375,25,INK,'OnestSemi')
link('novoferma.ru','https://novoferma.ru/',45,430,17,INK)
text('Санкт-Петербург',45,468,13,'Onest',MUTED)
img('mascot-contact-restored-v2.webp',688,144,212,349,True)
done()

# 13. Compact sources and scope, kept separate from the commercial narrative.
base('Приложение / источники и сведения')
text('О продуктах и данных',42,108,39,'OnestBold')
text('Ассортимент и компания',43,182,20,'OnestBold')
para('14 позиций и массы упаковок: официальный каталог Новофермы, сверка 24 октября 2026. Охлаждённое мясо птицы и пшеничное волокно упомянуты в общей коммуникации компании; состав каждого SKU проверяется по этикетке.',44,219,414,13.5,leading=19)
link('Каталог Новофермы','https://novoferma.ru/catalogue',44,326,12,ORANGE)
link('О компании и продукции','https://novoferma.ru/',44,350,12,ORANGE)
link('Контакты','https://novoferma.ru/contact',44,374,12,ORANGE)
text('Статус новинок',44,419,17,'OnestBold')
para('Фибрики и Люля мини показаны как концепты развития. Они не входят в 14 позиций основного ассортимента.',44,448,411,12.5,leading=18)
text('Потребительское исследование [1]',509,182,20,'OnestBold')
para('IFIC Food & Health Survey 2026, раздел Nutrition, стр. 36–37. Онлайн-опрос 3 005 жителей США в возрасте 18–80 лет, 22 марта – 8 апреля 2026. Данные взвешены по населению США. Использованы как международный ориентир.',510,219,407,13.5,leading=19)
link('Открыть первичный отчёт IFIC','https://ific.org/wp-content/uploads/2026-IFIC-Food-Health-Survey-Nutrition.pdf',510,326,12,ORANGE)
link('[2] EFSA: пищевые волокна','https://www.efsa.europa.eu/sites/default/files/2017_09_DRVs_summary_report.pdf',510,350,12,ORANGE)
text('Пищевая ценность и поставка',510,390,17,'OnestBold')
para('Показатели белка и клетчатки, полный состав, хранение, приготовление и условия поставки уточняются по конкретному продукту. Иллюстрации не заменяют этикетку.',510,422,407,12.5,leading=18)
done()

c.save()
(TMP/'text-bounds.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2))
bad=[v for v in checks if v['x']<0 or v['right']>W-15 or v['bottom']>H-10]
if bad:raise RuntimeError('Text bounds: '+json.dumps(bad,ensure_ascii=False))
print(json.dumps({'output':str(OUT),'pages':page_no,'bytes':OUT.stat().st_size,'text_bounds':'passed'},ensure_ascii=False))
