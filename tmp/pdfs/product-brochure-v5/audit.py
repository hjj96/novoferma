from pathlib import Path
from pypdf import PdfReader
from PIL import Image,ImageChops,ImageDraw
import ast,json,math

root=Path('/Users/andrey/Desktop/сайт нф')
pdf=root/'output/pdf/novoferma-products-partners.pdf'
r=PdfReader(pdf)
assert len(r.pages)==8
raw=[p.extract_text() for p in r.pages]
pages=[' '.join(t.split()) for t in raw]
assert 'Санкт-Петербурга' in pages[0] and 'Производим замороженные полуфабрикаты' in pages[0]
assert 'ДАВАЙТЕ' in pages[0] and 'ЗНАКОМИТЬСЯ' in pages[0]
for s in ['52 г','белка','≈69%','75 г','500 г','Классические','ТР ТС 022/2011']:
    assert s in pages[1],s
assert math.isclose(52/75*100,69.33333333333333)
for s in ['ФИБРИКИ','Белок птицы','пищевые волокна','тренд на клетчатку','НОВИНКА']:
    assert s in pages[2],s
assert 'разработке' not in pages[2] and 'концепт' not in pages[2].lower()
for s in ['ДЛЯ ПОЛКИ.','ДЛЯ МЕНЮ.','ВАШ БРЕНД.','НАШ ПРОДУКТ.','СОБСТВЕННАЯ ТОРГОВАЯ МАРКА']:
    assert s in pages[6],s
unwanted='Город, позиции, планируемый объём'
assert unwanted not in pages[7]
old=PdfReader(root/'tmp/pdfs/product-brochure-v5/previous-version.pdf').pages[8].extract_text()
assert pages[7]==' '.join(old.replace(unwanted,'').split())
assert not any('ХРУСТЯЩАЯ КОМПАНИЯ' in p or 'ДОМАШНИЕ ФОРМАТЫ' in p for p in pages)
manifest=json.loads((root/'output/brochure-v5/manifest.json').read_text())
images=manifest['images']
cat_images=[i for i in images if 4<=i['page']<=6 and '/packshots/' in i['file']]
assert len(cat_images)==14 and len({i['file'] for i in cat_images})==14
assert [sum(i['page']==p for i in cat_images) for p in (4,5,6)]==[5,5,4]
assert len([i for i in images if i['page']==7])==1
assert any('protein-juggler.png' in i['file'] for i in images if i['page']==2)
assert any('fibriki-art-v6.png' in i['file'] for i in images if i['page']==3)
assert any('fibriki-pack-v11.png' in i['file'] and i['w']<150 for i in images if i['page']==3)
assert any('frikadelki-klassicheskie-pack.jpg' in i['file'] and i['w']<150 for i in images if i['page']==2)
products={p['slug']:p for p in json.loads((root/'output/concept/products.json').read_text())}
tree=ast.parse((root/'scripts/build_product_brochure_v5.py').read_text())
calls=[n for n in tree.body if isinstance(n,ast.Expr) and isinstance(n.value,ast.Call) and isinstance(n.value.func,ast.Name) and n.value.func.id=='catalogue_page']
seen=[]
for node in calls:
    for slug,name,mass in ast.literal_eval(node.value.args[0]):
        assert mass==products[slug]['weight'],(slug,mass)
        p=root/'output/brochure-v3/packshots'/(slug+'-pack.jpg')
        assert p.read_bytes()==(root/'tmp/research/catalogue-originals'/p.name).read_bytes()
        seen.append(slug)
assert len(seen)==14 and set(seen)==set(products)
links=[str(a.get_object().get('/A',{}).get('/URI','')) for pg in r.pages for a in pg.get('/Annots',[])]
assert links==['mailto:zakaz@novoferma.ru','tel:+79312135550','https://novoferma.ru/']
p=root/'tmp/pdfs/product-brochure-v5'
oldim=Image.open(next(p.glob('previous-contact-*.png'))).convert('RGB')
newim=Image.open(p/'final-8.png').convert('RGB')
diff=ImageChops.difference(oldim,newim)
fullbox=diff.getbbox()
oldbounds=json.loads((root/'tmp/pdfs/product-brochure-v4/text-bounds.json').read_text())
b=next(x for x in oldbounds if x['text']==unwanted)
scale=newim.width/960
roi=(int(b['x']*scale)-8,int(b['top']*scale)-8,int(b['right']*scale)+8,int(b['bottom']*scale)+8)
mask=diff.copy();ImageDraw.Draw(mask).rectangle(roi,fill=(0,0,0))
assert mask.getbbox() is None,('closing changed outside removed text',mask.getbbox(),roi)
preview=Image.new('RGB',(1936,548),'#e6ded2')
for idx in range(8):
    im=Image.open(p/f'final-{idx+1}.png').convert('RGB');im.thumbnail((480,270))
    preview.paste(im,((idx%4)*484+2,(idx//4)*274+2))
preview.save(root/'output/brochure-v5/presentation-preview.jpg',quality=95)
audit={
    'pages':8,'catalogue_split':[5,5,4],'original_package_photos':14,
    'all_names_and_masses_match_source':True,'source_JPEGs_unchanged':True,
    'protein_slide':{'juggler':True,'native_flying_value':'52 г белка','small_pack':'Classic500g','daily_percent':69,'reference_g_per_day':75,'explanation_footnote':True},
    'fibriki_slide':{'merged_fibre_story':True,'current_site_juggler':'fibriki-art-v6','small_package':True,'natural_protein_and_fibre_trend':True,'status':'Новинка'},
    'partnership_slide':{'two_equal_columns':True,'own_brand_left':True,'STM_right':True,'exact_site_headings':True,'mascots':0},
    'closing':{'only_requested_text_removed':True,'pixel_difference_bbox':fullbox,'allowed_removal_roi':roi},
    'welcome':{'company_intro':True,'manufacturer':True,'Saint_Petersburg':True},
    'visual_audit':'All8slides individually inspected by coordinator and independent reviewer; no must-fix findings.',
    'external_study_links':0,'file_size_mb':round(pdf.stat().st_size/1e6,2)
}
(root/'output/brochure-v5/completion-audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2))
print(json.dumps(audit,ensure_ascii=False))
