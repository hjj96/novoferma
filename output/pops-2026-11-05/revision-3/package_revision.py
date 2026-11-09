from pathlib import Path
import shutil,json,hashlib,zipfile
from PIL import Image
R=Path(__file__).resolve().parent
P=Path('/Users/andrey/Library/Application Support/Codex/artifact-sessions/exports/latest/f65996abd32ba0309c54e4f1200b5086f80e11f08a0e12e74cc929ed420dc7fe')
for n,name in [(1,'pops-overview-v3.png'),(5,'pops-campaign-v3.png'),(6,'pops-lifestyle-poster-v3.png')]:shutil.copy2(P/f'slide-{n}.png',R/'assets'/name)
brief=(R.parent/'product-brief.txt').read_text()
a=brief.index('Внешний вид\n');b=brief.index('Коммуникация\n')
brief=brief[:a]+'''Внешний вид — итерация 3
Опора на оригинальные фото классической линейки: тонкая антиква,
небольшой оранжевый логотип, кремовый рукав, светлый продукт внутри
невысокого прозрачного лотка. В печатной композиции — приготовленные
Попсы слева, рок-курочка с ведёрком справа. Она отбивает ритм двумя
палочками: чёрный жилет и энергичная поза добавляют молодёжный характер.
Ведёрко является печатным сюжетом и образом подачи, не комплектующей.
Отдельный food-арт первого комплекта показывает однородный срез.

'''+brief[b:]
brief=brief.replace('Короткая фраза для арта: «Маленькие. Хрустящие. Куриные.»','Короткая фраза для арта: «Хрусти в своём ритме».')
brief=brief.replace('Новые растровые изображения: встроенный ImageGen, точные prompts в assets/.','Новые растровые изображения: встроенный ImageGen, точные prompts в assets/.\nИтерация 3 сверяется с оригинальными фото catalogue/kurinyj-popkorn.webp,\nstripsy.webp и naggetsy-ostrye.webp. Прежние версии сохранены отдельно.')
(R/'product-brief-v3.txt').write_text(brief)
entries=[(R/'README.txt','00_README.txt'),(R/'creative-direction.txt','03_Concept/creative-direction.txt'),(R/'product-brief-v3.txt','03_Concept/product-brief.txt')]
for p in sorted((R/'packaging').iterdir()):
    if p.name.startswith('pops-') and p.suffix in ['.svg','.png','.pdf']:entries.append((p,'01_Packaging/'+p.name))
entries.append((R/'packaging/README.txt','01_Packaging/README.txt'))
for name in ['pops-v3-drummer.png','pops-v3-rock-art.png','pops-v3-lifestyle.png','pops-campaign-v3.png','pops-lifestyle-poster-v3.png','pops-overview-v3.png','pops-v3-family.png','pops-v3-comparison.png']:entries.append((R/'assets'/name,'02_Artwork/'+name))
entries.append((R/'assets/pops-v3-backstage.png','04_Alternative/pops-v3-backstage.png'))
for name in ['pops-food-cutout.png','pops-serving-scene.png']:entries.append((R.parent/'assets'/name,'02_Artwork/'+name))
for p in sorted((R/'assets').iterdir()):
    if p.suffix=='.txt' or(p.suffix=='.json' and 'provenance' in p.name):entries.append((p,'05_Prompts/'+p.name))
for name in ['pops-website-v3.png','pops-website-v3-mobile.png']:entries.append((R/'assets'/name,'06_Website/'+name))
files=[]
for p,name in entries:
    meta={'path':name,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
    if p.suffix=='.png':
        with Image.open(p)as im:meta.update({'width':im.width,'height':im.height})
    files.append(meta)
manifest={'title':'Новоферма — Попсы, версия 3','date':'2026-11-05','master':'pops-v3-drummer.png','alternative':'pops-v3-backstage.png','status':'reviewed visual concept; production fields pending','image_generation':'built-in ImageGen','presentation':{'artifactRef':'artifact_external_aba819cc-00a3-41cc-a894-124f9bbb63b4','page_id':'page_8c8f482026e481918ccabfa7d7654d5c','stateVersion':13,'slides':9},'files':files}
(R/'manifest-v3.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
archive=R/'novoferma-popsy-design-kit-v3.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED)as z:
    for p,name in entries:z.write(p,name)
    z.write(R/'manifest-v3.json','manifest.json')
with zipfile.ZipFile(archive)as z:
    assert z.testzip()is None
    assert len(z.namelist())==len(entries)+1
print(json.dumps({'archive':str(archive),'files':len(entries)+1,'bytes':archive.stat().st_size},ensure_ascii=False))
