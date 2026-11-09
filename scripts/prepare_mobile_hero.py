"""Export the phone-specific ImageGen scenes without changing their composition."""
from pathlib import Path
import hashlib
import json

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'output/concept/assets/product-hero/mobile-v6'
MASTERS = {
    'fibriki': 'fibriki-master.png',
    'meatballs': 'meatballs-basketball-master.png',
    'nuggets': 'nuggets-no-shadow-master.png',
    'lulia-mini': 'lulia-mini-master.png',
    'popsy': 'popsy-master.png',
}


def main():
    layout = {}
    exports = {}
    for product, filename in MASTERS.items():
        master = ASSETS / filename
        image = Image.open(master).convert('RGBA')
        if image.size != (1254, 1254):
            raise ValueError(f'{filename}: expected a native 1254px square, got {image.size}')
        target = ASSETS / f'{product}.webp'
        if not target.exists() or target.stat().st_mtime_ns < master.stat().st_mtime_ns:
            image.resize((960, 960), Image.Resampling.LANCZOS).save(target, 'WEBP', quality=92, method=6)
        layout[product] = {'width': 960, 'height': 960, 'ratio': 1, 'size': 100, 'left': 0, 'top': 0}
        exports[product] = {
            'master': filename, 'masterSha256': hashlib.sha256(master.read_bytes()).hexdigest(),
            'webp': target.name, 'webpSha256': hashlib.sha256(target.read_bytes()).hexdigest(),
            'bytes': target.stat().st_size,
        }
    (ASSETS / 'layout.json').write_text(json.dumps(layout, ensure_ascii=False, indent=2))
    (ASSETS / 'exports.json').write_text(json.dumps({'mode': 'builtin-imagegen', 'masterPixels': [1254, 1254], 'webpPixels': [960, 960], 'quality': 92, 'files': exports}, ensure_ascii=False, indent=2))
    print('Exported five phone-specific scenes (960px WebP, quality92).')


if __name__ == '__main__':
    main()
