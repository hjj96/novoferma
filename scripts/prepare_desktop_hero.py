"""Export ImageGen masters unchanged and describe their independent CSS placement."""
from pathlib import Path
import hashlib
import json
import shutil

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'output/concept/assets/product-hero/desktop-v8'
PRODUCTS = ('fibriki', 'meatballs', 'nuggets', 'lulia-mini', 'popsy')
CANVAS = (1100, 850)
# (left, bottom, width) for both the mascot and food: one shared stage plane.
COMPOSITION = {
    'fibriki': {'foodSource': 'fibriki-food-v2', 'hen': (665, 825, 435), 'food': (0, 825, 630), 'flip': True, 'accents': [(100, 35, 65, -15), (880, 205, 65, 18)]},
    'meatballs': {'foodSource': 'meatballs-food-v2', 'hen': (660, 825, 440), 'henSource': 'meatballs-hen-v4', 'food': (0, 825, 630), 'accents': [(100, 35, 65, -18), (900, 220, 65, 20)]},
    'nuggets': {'hen': (650, 825, 450), 'henSource': 'nuggets-hen-v3', 'food': (-80, 825, 700), 'foodSource': 'nuggets-food-v3', 'accents': [(100, 35, 70, -15), (915, 190, 65, 20)]},
    'lulia-mini': {'foodSource': 'lulia-mini-food-v2', 'hen': (665, 825, 435), 'food': (0, 825, 630), 'flip': True, 'accents': [(100, 35, 65, -18), (915, 220, 65, 18)]},
    'popsy': {'hen': (580, 825, 520), 'henSource': 'popsy-hen-v3', 'food': (-180, 825, 780), 'foodSource': 'popsy-food-v3', 'accents': [(-50, 90, 65, -15), (950, 45, 65, 18)]},
}


def export(name):
    master = ASSETS / f'{name}-master.png'
    output = ASSETS / f'{name}.webp'
    image = Image.open(master).convert('RGBA')
    if image.size != (1254, 1254):
        raise ValueError(f'{name}: expected the common 1254px square master, got {image.size}')
    if name == 'popsy-food' and not (ASSETS / 'popsy-food-v2-master.png').exists():
        shutil.copyfile(ROOT / 'output/concept/assets/popsy/popsy-food.webp', ASSETS / f'{name}.webp')
    elif not output.exists() or output.stat().st_mtime_ns < master.stat().st_mtime_ns:
        image.save(output, 'WEBP', quality=95, method=6)
    box = image.getchannel('A').point(lambda a: 255 if a >= 8 else 0).getbbox()
    box = [max(0, box[0] - 5), max(0, box[1] - 5), min(image.width, box[2] + 5), min(image.height, box[3] + 5)]
    return {'path': f'assets/product-hero/desktop-v8/{name}.webp', 'sourceWidth': image.width, 'sourceHeight': image.height, 'bbox': box}


def placed(source, left, top, width, bottom=None):
    box = source['bbox']
    height = width * (box[3] - box[1]) / (box[2] - box[0])
    return {**source, 'x': left, 'y': bottom - height if bottom is not None else top, 'width': width, 'height': height}


def main():
    accent = export('accent')
    layout = {'canvas': CANVAS, 'products': {}}
    for product in PRODUCTS:
        config = COMPOSITION[product]
        hen = export(config.get('henSource', product + '-hen-v2'))
        food = export(config.get('foodSource', product + '-food'))
        hx, hb, hw = config['hen']
        fx, fb, fw = config['food']
        # Keep the complete food group and its soft grounding shadow in view.
        max_food_height = fb - 30
        ratio = (food['bbox'][2] - food['bbox'][0]) / (food['bbox'][3] - food['bbox'][1])
        fw = min(fw, max_food_height * ratio)
        food_position = placed(food, fx, 0, fw, bottom=fb)
        accents = [{**placed(accent, x, y, width), 'rotation': angle} for x, y, width, angle in config['accents']]
        hen_position = placed(hen, hx, 0, hw, bottom=hb)
        if config.get('flip'): hen_position['flip'] = True
        shadows = []
        layout['products'][product] = {'hen': hen_position, 'food': {**food, 'pieces': [food_position]}, 'accents': accents, 'shadows': shadows}
        print(product, 'food width', round(fw, 1), 'hen width', hw)
    (ASSETS / 'layout.json').write_text(json.dumps(layout, ensure_ascii=False, indent=2))
    files = sorted(ASSETS.glob('*.webp'))
    (ASSETS / 'exports.json').write_text(json.dumps({'quality': 95, 'pixelResize': False, 'files': {f.name: {'bytes': f.stat().st_size, 'sha256': hashlib.sha256(f.read_bytes()).hexdigest()} for f in files}}, indent=2))


if __name__ == '__main__':
    main()
