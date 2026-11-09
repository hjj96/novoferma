from pathlib import Path
import json, hashlib, zipfile, shutil
R=Path(__file__).resolve().parent
preview=Path('/Users/andrey/Library/Application Support/Codex/artifact-sessions/exports/latest/f65996abd32ba0309c54e4f1200b5086f80e11f08a0e12e74cc929ed420dc7fe')
for n,name in [(1,'pops-overview.png'),(5,'pops-campaign-art.png'),(6,'pops-serving-art.png')]:
    shutil.copy2(preview/f'slide-{n}.png',R/'assets'/name)
(R/'README.txt').write_text('''НОВОФЕРМА / ПОПСЫ
Готовый комплект дизайна-концепта • 5 ноября 2026

01_Packaging: лицевая композиция и рабочий оборот в SVG, PNG, PDF.
SVG редактируется в векторном редакторе; текст и графика разделены.
PDF и PNG предназначены для просмотра дизайна.

02_Artwork: упаковка, продукт, персонаж, сцена подачи и два готовых арта.
Новые изображения созданы встроенным ImageGen. Это визуализации концепции.
PNG продукта, персонажа и упаковки содержат прозрачный фон.
Применять на тёплых кремовых фонах; перед иным фоном проверить края.

03_Brief: концепция продукта, тексты и перечень данных для выпуска.
04_Prompts: точные запросы ImageGen и история происхождения изображений.
05_Website: скриншот реализованной страницы.

Редактируемая презентация на 9 слайдах передана отдельным документом
в этом чате. Попсы также добавлены в текущий локальный сайт:
output/concept/product-popsy.html. Публичного размещения сайта нет.

ГОТОВНОСТЬ К ПЕЧАТИ
Комплект завершает визуальную концепцию. Он не заменяет согласованный
производственный оригинал-макет: оборот содержит рабочие поля.
Для выпуска нужны утверждённые данные продукта и развёртка под лоток.
Габариты, вылеты и цветовой профиль определяет поставщик упаковки.
Подробный список — в 03_Brief/product-brief.txt.
''')
entries=[(R/'README.txt','00_README.txt')]
for p in sorted((R/'packaging').iterdir()):
    if p.suffix in ['.svg','.png','.pdf'] or p.name=='README.txt': entries.append((p,'01_Packaging/'+p.name))
for name in ['pops-packshot.png','pops-food-cutout.png','pops-mascot.png','pops-serving-scene.png','pops-campaign-art.png','pops-serving-art.png','pops-overview.png']:
    entries.append((R/'assets'/name,'02_Artwork/'+name))
entries.append((R/'product-brief.txt','03_Brief/product-brief.txt'))
for p in sorted((R/'assets').iterdir()):
    if p.suffix in ['.txt','.json']: entries.append((p,'04_Prompts/'+p.name))
entries.append((R/'assets/pops-website-preview.png','05_Website/pops-website-preview.png'))
manifest={'title':'Новоферма — Попсы','date':'2026-11-05','status':'finished visual concept; production fields pending','presentation':{'artifactRef':'artifact_external_aba819cc-00a3-41cc-a894-124f9bbb63b4','page_id':'page_8c8f482026e481918ccabfa7d7654d5c','slides':9},'files':[{'path':name,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p,name in entries]}
(R/'deliverables-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
archive=R/'novoferma-popsy-design-kit.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
    for p,name in entries: z.write(p,name)
    z.write(R/'deliverables-manifest.json','manifest.json')
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    assert len(z.namelist())==len(entries)+1
print(json.dumps({'archive':str(archive),'bytes':archive.stat().st_size,'files':len(entries)+1},ensure_ascii=False))
