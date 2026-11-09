from pathlib import Path
import shutil,json,hashlib,zipfile
R=Path(__file__).resolve().parent
P=Path('/Users/andrey/Library/Application Support/Codex/artifact-sessions/exports/latest/f65996abd32ba0309c54e4f1200b5086f80e11f08a0e12e74cc929ed420dc7fe')
for n,name in [(1,'pops-overview-v2.png'),(5,'pops-campaign-v2.png')]: shutil.copy2(P/f'slide-{n}.png',R/'assets'/name)
brief=(R.parent/'product-brief.txt').read_text().replace('Слева продуктовая группа, справа детальная рисованная курочка со стаканчиком.','Крупное ведёрко с попсами — главный сюжет, рядом небольшая рисованная курочка.').replace('Мелкая золотистая корочка; один срез показывает светлую однородную начинку.\nОстальные кусочки целые.', 'Мелкая золотистая корочка. Отдельный food-арт показывает светлую однородную\nначинку на срезе; в главной композиции упаковки кусочки целые.')
(R/'product-brief-v2.txt').write_text(brief)
entries=[(R/'README.txt','00_README.txt'),(R/'creative-direction.txt','03_Concept/creative-direction.txt'),(R/'product-brief-v2.txt','03_Concept/product-brief.txt')]
for p in sorted((R/'packaging').iterdir()):
    if p.name.startswith('pops-') and p.suffix in ['.svg','.png','.pdf']: entries.append((p,'01_Packaging/'+p.name))
entries.append((R/'packaging/README.txt','01_Packaging/README.txt'))
for name in ['pops-pack-v2-bucket.png','pops-bucket-mascot-v2.png','pops-campaign-v2.png','pops-overview-v2.png','pops-v2-comparison.png']:
    entries.append((R/'assets'/name,'02_Artwork/'+name))
entries.append((R/'assets/pops-pack-v2-classic.png','04_Alternative/pops-pack-v2-classic.png'))
for name in ['pops-food-cutout.png','pops-serving-scene.png']:
    entries.append((R.parent/'assets'/name,'02_Artwork/'+name))
for p in sorted((R/'assets').iterdir()):
    if (p.suffix=='.txt') or (p.suffix=='.json' and 'provenance' in p.name): entries.append((p,'05_Prompts/'+p.name))
for name in ['pops-website-v2.png','pops-website-v2-mobile.png']:entries.append((R/'assets'/name,'06_Website/'+name))
manifest={'title':'Новоферма — Попсы, версия 2','date':'2026-11-05','master':'pops-pack-v2-bucket.png','alternative':'pops-pack-v2-classic.png','status':'reviewed visual concept; production fields pending','image_generation':'built-in ImageGen','native_asset_px':[1254,1254],'presentation':{'artifactRef':'artifact_external_aba819cc-00a3-41cc-a894-124f9bbb63b4','page_id':'page_8c8f482026e481918ccabfa7d7654d5c','stateVersion':10,'slides':9},'files':[{'path':name,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}for p,name in entries]}
(R/'manifest-v2.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
archive=R/'novoferma-popsy-design-kit-v2.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
    for p,name in entries:z.write(p,name)
    z.write(R/'manifest-v2.json','manifest.json')
with zipfile.ZipFile(archive)as z:
    assert z.testzip() is None
    assert len(z.namelist())==len(entries)+1
print(json.dumps({'archive':str(archive),'files':len(entries)+1,'bytes':archive.stat().st_size},ensure_ascii=False))
