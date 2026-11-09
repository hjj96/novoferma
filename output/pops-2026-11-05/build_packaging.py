from pathlib import Path
from base64 import b64encode
from html import escape
import json
ROOT=Path(__file__).resolve().parent
ASSETS=ROOT/'assets'; OUT=ROOT/'packaging'; OUT.mkdir(exist_ok=True)
CREAM='#F7EEDD'; BROWN='#55300B'; ORANGE='#F45C23'; MUTED='#80654D'
def embedded(p):
    suffix=p.suffix.lower(); mime={'.webp':'image/webp','.png':'image/png','.ttf':'font/ttf'}[suffix]
    return 'data:'+mime+';base64,'+b64encode(p.read_bytes()).decode()
def picture(p,x,y,w,h):
    return f'<image href="{embedded(p)}" x="{x}" y="{y}" width="{w}" height="{h}" preserveAspectRatio="xMidYMid meet"/>'
def text(value,x,y,size=35,fill=BROWN,anchor='start',family='Arial',weight='normal',extra=''):
    return f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" font-weight="{weight}" text-anchor="{anchor}" fill="{fill}" {extra}>{escape(value)}</text>'
def start(label):
    return f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="1800" height="1450" viewBox="0 0 1800 1450"><title>{label}</title><rect width="1800" height="1450" fill="{CREAM}"/>'
logo=ROOT.parent/'concept/assets/logo-reference.webp'
front=start('Новоферма. Попсы — лицевая сторона. Дизайн-концепт')
front+=picture(logo,620,95,560,110)
front+=text('ПОПСЫ',900,485,315,anchor='middle',family='Georgia',extra='letter-spacing="-8"')
front+=text('МИНИ-НАГГЕТСЫ ИЗ КУРИЦЫ',900,580,55,anchor='middle',weight='bold',extra='letter-spacing="4"')
front+=text('В ХРУСТЯЩЕЙ ПАНИРОВКЕ',900,650,41,anchor='middle',weight='bold',extra='letter-spacing="3"')
front+=picture(ASSETS/'pops-food-cutout.png',110,720,860,650)
front+=picture(ASSETS/'pops-mascot.png',950,680,730,740)
front+='</svg>'
(OUT/'pops-front-editable.svg').write_text(front)
back=start('Новоферма. Попсы — оборотная сторона. Рабочий макет')
back+=picture(logo,110,70,370,80)
back+=text('ПОПСЫ',110,310,154,family='Georgia')
back+=text('Мини-наггетсы из курицы в хрустящей панировке',115,390,44)
back+=text('Маленькие куриные кусочки. Подавайте с любимым соусом.',115,470,36)
back+=text('ОБОРОТНАЯ СТОРОНА · ПОЛЯ ДЛЯ ДАННЫХ ПРОИЗВОДСТВА',115,570,26,fill=MUTED,weight='bold',extra='letter-spacing="2"')
# Deliberately blank production fields; no invented values or symbols.
for x,y,title,lines in [
(115,665,'Состав и аллергены',['[Утверждённый состав и выделенные аллергены]']),
(115,835,'Приготовление',['[Способ, время и температура после испытаний]']),
(115,1005,'Хранение и срок годности',['[Режим хранения, срок, условия после вскрытия]']),
(115,1175,'Изготовитель',['[Наименование, адрес, контакты, документы]']),
(1045,665,'Пищевая ценность',['[Белки, жиры, углеводы на 100 г]', '[Энергетическая ценность]']),
(1045,875,'Масса нетто',['[Утверждённая масса]']),
(1045,1045,'Дата и партия',['[Зона нанесения переменных данных]']),
(1045,1215,'Штрихкод и знаки',['[Зона после регистрации и проверки]'])]:
    back+=text(title,x,y,39,weight='bold')
    for i,line in enumerate(lines): back+=text(line,x,y+58+45*i,26,fill=MUTED)
back+=text('РАБОЧИЙ МАКЕТ · ЗАПОЛНИТЬ И ПРОВЕРИТЬ ПЕРЕД ПЕЧАТЬЮ',115,1400,24,fill=MUTED,extra='letter-spacing="2"')
back+='</svg>'
(OUT/'pops-back-editable.svg').write_text(back)
html='''<!doctype html><html lang="ru"><meta charset="utf-8"><title>Попсы — макеты упаковки</title><style>@page{size:1800px 1450px;margin:0}html,body{margin:0;background:#F7EEDD}.sheet{width:1800px;height:1450px;page-break-after:always}.sheet:last-child{page-break-after:auto}svg{display:block;width:1800px;height:1450px}</style>'''
html+='<div class="sheet">'+front+'</div><div class="sheet">'+back+'</div>'
(OUT/'pops-packaging-review.html').write_text(html)
(OUT/'README.txt').write_text('ПОПСЫ / МАКЕТЫ УПАКОВКИ\n\nЛицевая сторона: законченная художественная композиция.\nОборот: редактируемые зоны для утвержденных производственных сведений.\nSVG содержит живой текст и встроенные изображения, внешние ссылки не нужны.\nОригинальный логотип сохранён. Georgia и Arial — системные шрифты macOS.\nРазмер артборда 1800 × 1450 px — пропорция дизайн-макета, не физический размер.\nЭто не контур вырубки: перенос на реальный рукав после замера лотка.\nПараметры печати, вылеты и цветовой профиль согласуются с типографией.\nПолный перечень незаполненных полей: ../product-brief.txt.\n')
print(json.dumps({'files':[str(p) for p in OUT.iterdir()]},ensure_ascii=False))
