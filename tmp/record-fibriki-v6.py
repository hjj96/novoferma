from pathlib import Path
import json, hashlib

base=Path('output/research/fibriki-unique-v4')
provenance=Path('output/concept/assets/novelty-packaging/provenance.json')
data=json.loads(provenance.read_text())
old=next(r for r in data['records'] if r['slug']=='fibriki')
if old['version']!=6:
 data['history']['fibrikiV3FamilyAdaptation']=old.copy()
record=old.copy()
record.update({
 'file':'assets/novelty-packaging/fibriki-pack-v6.webp', 'version':6,
 'native':str(base/'fibriki-pack-v6.png'), 'prompt':str(base/'fibriki-pack-v6-prompt.txt'),
 'promptSet':str(base/'prompts.json'),
 'sha256':hashlib.sha256(Path('output/concept/assets/novelty-packaging/fibriki-pack-v6.webp').read_bytes()).hexdigest(),
 'kind':'Unique front-packaging visual concept in the existing brand family',
 'layoutSource':'assets/novelty-packaging/fibriki-pack-v3.webp',
 'printedMascotStyleSource':'assets/catalogue/stripsy.webp',
 'mascotMaster':str(base/'mascot-study-v6.png'),
 'foodMaster':str(base/'food-study-v5.png'),
 'development':'Separate food photography and a new standing chicken-with-spoon illustration; assembled in v5, then v6 corrects spoon ball and raw-ball textures. Upper label hierarchy retained.',
 'uniqueArtwork':'Standing chicken studies a Fibrik in a wooden spoon; asymmetric serving pair of one whole and one half.',
})
record.pop('layoutAndPrintedMascotSource',None)
data['records']=[record if r['slug']=='fibriki' else r for r in data['records']]
data['history']['fibrikiV4Rejected']={'native':str(base/'fibriki-pack-v4.png'),'prompt':str(base/'fibriki-pack-v4-prompt.txt'),'reason':'User rejected generic cartoon mascot and elongated rice-like food texture. Never used on the site.'}
data['history']['fibrikiV5AssemblyCandidate']={'native':str(base/'fibriki-pack-v5.png'),'prompt':str(base/'fibriki-pack-v5-prompt.txt'),'reason':'Corrected in v6 to remove rice-like strokes from raw balls and the small spoon ball.'}
data['analysis']=str(base/'direction.json')
data['familyComparison']=str(base/'family-lineup.png')
provenance.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
stages=[
 ('food-study-v5','Natural fine-minced chicken serving pair'),
 ('mascot-study-v6','Unique chicken-with-spoon, original Strips style reference'),
 ('fibriki-pack-v5','Assemble the approved label with separately developed food and illustration'),
 ('fibriki-pack-v6','Correct raw-ball and spoon-ball texture only')
]
prompts={'tool':'Built-in ImageGen','finalAsset':record['file'],'stages':[{'asset':str(base/(stem+'.png')),'purpose':purpose,'prompt':(base/(stem+'-prompt.txt')).read_text().strip()} for stem,purpose in stages]}
(base/'prompts.json').write_text(json.dumps(prompts,ensure_ascii=False,indent=2)+'\n')
direction=json.loads((base/'direction.json').read_text())
direction['decision']='Unique standing chicken-with-spoon; fine minced-chicken serving pair of one whole ball and one half'
direction['rejected']='Juggling chef v4: generic cartoon and incorrect fibrous/rice food; engraved study v5: inappropriate drawing and anatomy'
direction['currentVersion']=6
(base/'direction.json').write_text(json.dumps(direction,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'asset':record['file'],'version':6,'promptStages':len(stages)},ensure_ascii=False))
