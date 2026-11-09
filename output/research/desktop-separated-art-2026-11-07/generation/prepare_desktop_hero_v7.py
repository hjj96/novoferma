"""Export the generated layers and describe CSS crops; never repaint their pixels."""
from collections import deque
from pathlib import Path
import hashlib
import json

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'output/concept/assets/product-hero/desktop-v7'
PRODUCTS = ('fibriki', 'meatballs', 'nuggets', 'lulia-mini')

# Coordinates in a 1000 x 800 art board. Products have individual crops and
# positions, so composition changes do not require another raster generation.
PLACEMENTS = {
    'fibriki': {'hen': (35, 780, 490), 'food': [(115, 150, 145), (430, 100, 170), (780, 200, 195), (875, 555, 150)], 'marks': [(885, 95, 12), (930, 410, 35)]},
    'meatballs': {'hen': (490, 780, 490), 'food': [(155, 185, 180), (450, 105, 195), (770, 145, 150), (180, 565, 225)], 'marks': [(270, 110, 15), (312, 510, 35)]},
    'nuggets': {'hen': (270, 780, 490), 'food': [(145, 190, 220), (455, 100, 205), (795, 130, 175), (905, 550, 190)], 'marks': [(40, 40, -25), (916, 100, 30)]},
    'lulia-mini': {'hen': (490, 780, 490), 'food': [(145, 180, 220), (445, 105, 230), (790, 135, 185), (180, 565, 245)], 'marks': [(260, 105, 15), (322, 530, 40)]},
}


def components(image):
    width, height = image.size
    mask = bytearray(image.getchannel('A').point(lambda a: int(a >= 32)).tobytes())
    result = []
    while True:
        start = mask.find(1)
        if start < 0:
            break
        mask[start] = 0
        pending = deque([start])
        x0 = x1 = start % width
        y0 = y1 = start // width
        area = 0
        while pending:
            index = pending.pop()
            x, y = index % width, index // width
            x0, y0, x1, y1 = min(x0, x), min(y0, y), max(x1, x), max(y1, y)
            area += 1
            for neighbor in ((index - 1 if x else -1), (index + 1 if x + 1 < width else -1), index - width, index + width):
                if 0 <= neighbor < len(mask) and mask[neighbor]:
                    mask[neighbor] = 0
                    pending.append(neighbor)
        if area > 2000:
            result.append([max(0, x0 - 5), max(0, y0 - 5), min(width, x1 + 6), min(height, y1 + 6)])
    if len(result) != 4:
        raise ValueError(f'Expected four separate food objects, found {len(result)}')
    lower = max(result, key=lambda b: b[1] + b[3])
    return sorted((b for b in result if b is not lower), key=lambda b: b[0]) + [lower]


def source_info(name):
    image = Image.open(ASSETS / f'{name}-master.png').convert('RGBA')
    image.save(ASSETS / f'{name}.webp', 'WEBP', quality=95, method=6)
    return image, {'path': f'assets/product-hero/desktop-v7/{name}.webp', 'sourceWidth': image.width, 'sourceHeight': image.height}


def main():
    layout = {'canvas': [1000, 800], 'products': {}}
    for product in PRODUCTS:
        hen, hen_source = source_info(product + '-hen')
        food, food_source = source_info(product + '-food')
        box = hen.getchannel('A').point(lambda a: 255 if a >= 8 else 0).getbbox()
        box = [max(0, box[0] - 5), max(0, box[1] - 5), min(hen.width, box[2] + 5), min(hen.height, box[3] + 5)]
        ratio = (box[2] - box[0]) / (box[3] - box[1])
        x, bottom, width = PLACEMENTS[product]['hen']
        height = width / ratio
        items = []
        for bounds, (cx, cy, longest) in zip(components(food), PLACEMENTS[product]['food']):
            ratio_food = (bounds[2] - bounds[0]) / (bounds[3] - bounds[1])
            w, h = (longest, longest / ratio_food) if ratio_food >= 1 else (longest * ratio_food, longest)
            items.append({'bbox': bounds, 'x': cx - w / 2, 'y': cy - h / 2, 'width': w, 'height': h})
        layout['products'][product] = {'hen': {**hen_source, 'bbox': box, 'x': x, 'y': bottom - height, 'width': width, 'height': height}, 'food': {**food_source, 'pieces': items}, 'marks': PLACEMENTS[product]['marks']}
        print(product, 'hen', hen.size, 'food', food.size, 'pieces', [i['bbox'] for i in items])
    (ASSETS / 'layout.json').write_text(json.dumps(layout, ensure_ascii=False, indent=2))
    files = sorted(ASSETS.glob('*.webp'))
    (ASSETS / 'exports.json').write_text(json.dumps({'quality': 95, 'pixelResize': False, 'files': {f.name: {'bytes': f.stat().st_size, 'sha256': hashlib.sha256(f.read_bytes()).hexdigest()} for f in files}}, indent=2))


if __name__ == '__main__':
    main()
