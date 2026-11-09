from pathlib import Path
import hashlib, json

root = Path(__file__).resolve().parents[1]
path = root / 'output/concept/assets/novelty-packaging/provenance.json'
data = json.loads(path.read_text())
record = next(r for r in data['records'] if r['slug'] == 'fibriki')
if record['version'] != 9:
    data['history']['fibrikiV8BeforeNaturalEdge'] = dict(record)
record.update({
    'file': 'assets/novelty-packaging/fibriki-pack-v9.webp',
    'version': 9,
    'kind': 'Family-matched front-packaging visual concept with natural paper edges',
    'native': 'output/research/catalogue-grid-16/fibriki-pack-v9.png',
    'prompt': 'output/research/catalogue-grid-16/fibriki-pack-v9-prompt.txt',
    'promptSet': 'output/research/catalogue-grid-16/prompts.json',
    'sha256': hashlib.sha256((root / 'output/concept/assets/novelty-packaging/fibriki-pack-v9.webp').read_bytes()).hexdigest(),
    'development': 'Targeted ImageGen retouch of F8: remove the continuous brown upper/side sleeve outline, retain pale natural paper edges and the lower structural cardboard. Accepted chicken-with-spoon, typography, food arrangement and family paper colors retained. All 16 catalogue previews now use the same card component.',
    'edgeEditSource': 'assets/novelty-packaging/fibriki-pack-v8.webp',
    'physicalEdgeReference': 'assets/novelty-packaging/lulia-mini-pack-v3.webp'
})
data['familyComparison'] = 'output/research/catalogue-grid-16/family-lineup-v9.png'
data['catalogueIntegration'] = {'items': 16, 'confirmedSkuRecords': 14, 'component': 'card()/packshot-preview', 'checks': 'output/research/catalogue-grid-16/checks.json'}
path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
prompt = (root / record['prompt']).read_text()
prompts = {'tool': 'Built-in ImageGen', 'output': record['file'], 'native': record['native'], 'intent': 'precise-object-edit', 'prompt': prompt, 'inputImages': ['output/research/novelty-color-match/fibriki-pack-v8.png', 'output/research/novelty-color-match/lulia-mini-pack-v3.png'], 'postprocessing': 'Alpha-bounds canvas normalization and lossless WebP conversion only; no manual artwork/edge/color retouch.'}
(root / record['promptSet']).write_text(json.dumps(prompts, ensure_ascii=False, indent=2) + '\n')
print('Recorded Fibriki v9 provenance and exact prompt')
