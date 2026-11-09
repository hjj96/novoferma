from pathlib import Path
import json, hashlib
root=Path('output/research/novelty-color-match')
path=Path('output/concept/assets/novelty-packaging/provenance.json')
data=json.loads(path.read_text())
for slug,version in [('fibriki',8),('lulia-mini',3)]:
 old=next(r for r in data['records'] if r['slug']==slug)
 if old['version']!=version:
  data['history'][f'{slug}V{old["version"]}BeforeColorMatch']=old.copy()
 current=old.copy()
 current.update({
  'version':version,'file':f'assets/novelty-packaging/{slug}-pack-v{version}.webp',
  'native':str(root/f'{slug}-pack-v{version}.png'),
  'prompt':str(root/f'{slug}-pack-v{version}-prompt.txt'),
  'promptSet':str(root/'prompts.json'),
  'kind':'Color-matched front-packaging visual concept',
  'colorEditSource':old.get('colorEditSource',old['file']),
  'development':('Color grade of accepted F6: warmer brighter paper, orange logo and softer brown ink; v8 corrects food-texture drift from v7.' if slug=='fibriki' else 'Small paper-lightness correction of accepted Lulia v2, with logo, typography, character and food visually retained.'),
  'sha256':hashlib.sha256(Path(f'output/concept/assets/novelty-packaging/{slug}-pack-v{version}.webp').read_bytes()).hexdigest(),
 })
 data['records']=[current if r['slug']==slug else r for r in data['records']]
data['history']['fibrikiV7ColorCandidate']={'native':str(root/'fibriki-pack-v7.png'),'prompt':str(root/'fibriki-pack-v7-prompt.txt'),'reason':'Color closer to family; final v8 reduces incidental elongated food grains.'}
data['familyComparison']=str(root/'family-lineup.png')
data['analysis']=str(root/'color-match-report.json')
path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
stages=[('fibriki-pack-v7','Selective color match'),('fibriki-pack-v8','Food texture correction preserving color match'),('lulia-mini-pack-v3','Subtle paper lightness correction')]
(root/'prompts.json').write_text(json.dumps({'tool':'Built-in ImageGen','finalAssets':[r['file'] for r in data['records']],'stages':[{'asset':str(root/(stem+'.png')),'purpose':purpose,'prompt':(root/(stem+'-prompt.txt')).read_text().strip()} for stem,purpose in stages]},ensure_ascii=False,indent=2)+'\n')
report={'request':'Уточнить цвет новинок относительно существующей линейки и их вид на сайте','mode':'Built-in ImageGen edits','before':json.loads((root/'color-analysis-before.json').read_text()),'after':json.loads((root/'color-analysis-after.json').read_text()),'sitePalette':{'fibriki':'#f5e4be','lulia-mini':'#e8e9ce'},'note':'Pixel medians describe selected comparable regions, not flat fills or claims of pixel-identical editing. Approved subjects and layout were visually checked. Generative editing may introduce minor texture differences.','comparison':str(root/'family-lineup.png')}
(root/'color-match-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'versions':{r['slug']:r['version'] for r in data['records']},'promptStages':len(stages)}))
