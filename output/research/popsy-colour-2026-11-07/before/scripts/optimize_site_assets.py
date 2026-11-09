#!/usr/bin/env python3
"""Build reviewed, non-generative WebP derivatives without changing their masters.

Outputs only assets/responsive/** and asset-variants.json. A full pre-change backup
must exist. No HTML, CSS, product data or build output is rewritten by this tool.
"""
from __future__ import annotations
import hashlib
import io
import json
import os
from pathlib import Path
from PIL import Image, ImageChops, ImageStat

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / 'output/concept'
BACKUP = ROOT / 'output/research/implementation-2026-10-24/before/concept'
APPROVED_BACKUPS = {
    'assets/novelty-packaging/fibriki-pack-v11.webp': ROOT / 'output/research/fibriki-herbs-v11/fibriki-pack-v11.webp',
    'assets/catalogue-family-v1/family-table-v1.webp': ROOT / 'output/research/catalogue-family-2026-11-05/family-table-v1.webp',
    'assets/novelty-packaging/popsy-pack-v1.webp': ROOT / 'output/pops-2026-11-05/assets/popsy-pack-v1.webp',
    'assets/novelty-packaging/popsy-pack-v2.webp': ROOT / 'output/pops-2026-11-05/revision-2/assets/popsy-pack-v2.webp',
    'assets/novelty-packaging/popsy-pack-v3.webp': ROOT / 'output/pops-2026-11-05/revision-3/assets/popsy-pack-v3.webp',
    'assets/popsy/popsy-food.webp': ROOT / 'output/pops-2026-11-05/assets/popsy-food.webp',
    'assets/popsy/popsy-serving.webp': ROOT / 'output/pops-2026-11-05/assets/popsy-serving.webp',
    'assets/popsy/popsy-rock-v3.webp': ROOT / 'output/pops-2026-11-05/revision-3/assets/popsy-rock-v3.webp',
    'assets/popsy/popsy-lifestyle-v3.webp': ROOT / 'output/pops-2026-11-05/revision-3/assets/popsy-lifestyle-v3.webp',
}
DEST = SITE / 'assets/responsive'
PACK_QUALITY = 94
ILLUSTRATION_QUALITY = 90
ILLUSTRATIONS = [
    'assets/catalogue-family-v1/family-table-v1.webp',
    'assets/mascot-contact-restored-v2.webp',
    'assets/mascot-partnership-v2.webp',
    'assets/product-hero/running-mascot-v2.webp',
    'assets/protein-story/hen-layer-v2.webp',
    'assets/protein-story/nuggets-layer-v2.webp',
]
ILLUSTRATIONS += [source for source in ('assets/popsy/popsy-food.webp', 'assets/popsy/popsy-serving.webp', 'assets/popsy/popsy-rock-v3.webp', 'assets/popsy/popsy-lifestyle-v3.webp') if (SITE / source).is_file()]


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + '.tmp')
    try:
        temporary.write_bytes(data)
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def resized_rgba(image: Image.Image, width: int) -> Image.Image:
    if width == image.width:
        return image.copy()
    height = round(image.height * width / image.width)
    # Resample premultiplied pixels to avoid dark/colored transparent fringes.
    return image.convert('RGBa').resize((width, height), Image.Resampling.LANCZOS).convert('RGBA')


def measure(image: Image.Image, payload: bytes) -> dict:
    with Image.open(io.BytesIO(payload)) as result:
        decoded = result.convert('RGBA')
    if decoded.size != image.size:
        raise ValueError('Derivative dimensions do not match the resized reference.')
    alpha_delta = ImageChops.difference(image.getchannel('A'), decoded.getchannel('A')).getextrema()[1]
    if alpha_delta:
        raise ValueError(f'WebP alpha unexpectedly changed by {alpha_delta}')
    foreground = image.getchannel('A').point(lambda alpha: 255 if alpha >= 16 else 0)
    difference = ImageChops.difference(image.convert('RGB'), decoded.convert('RGB'))
    mae = sum(ImageStat.Stat(difference, foreground).mean) / 3
    return {'alphaMaxDifference': alpha_delta, 'foregroundRgbMae8Bit': round(mae, 4)}


def encode(image: Image.Image, quality: int) -> tuple[bytes, dict]:
    buffer = io.BytesIO()
    image.save(buffer, format='WEBP', quality=quality, method=6, exact=True)
    payload = buffer.getvalue()
    return payload, measure(image, payload)


def build() -> dict:
    if not (BACKUP / 'script.js').is_file() or not (BACKUP / 'product-hero.js').is_file():
        raise SystemExit('Required implementation/before/concept backup is missing.')
    packshots = sorted((SITE / 'assets/catalogue-clean-v2').glob('*.webp'))
    if len(packshots) != 14:
        raise SystemExit(f'Expected 14 approved catalogue master paths, found {len(packshots)}.')
    packs = [str(p.relative_to(SITE)) for p in packshots] + [
        'assets/novelty-packaging/fibriki-pack-v11.webp',
        'assets/novelty-packaging/lulia-mini-pack-v3.webp',
        'assets/novelty-packaging/popsy-pack-v3.webp',
    ]
    prior_path = SITE / 'asset-variants.json'
    prior_assets = json.loads(prior_path.read_text()).get('assets', {}) if prior_path.exists() else {}
    assets = {}
    for source in packs + ILLUSTRATIONS:
        path = SITE / source
        master_backup = APPROVED_BACKUPS.get(source, BACKUP / source)
        if not master_backup.is_file():
            raise SystemExit(f'No pre-change backup exists for {source}.')
        original = path.read_bytes()
        if master_backup.read_bytes() != original:
            raise SystemExit(f'Master differs from its approved backup: {source}.')
        source_hash = digest(original)
        category = 'packshots' if source in packs else 'illustrations'
        quality = PACK_QUALITY if category == 'packshots' else ILLUSTRATION_QUALITY
        with Image.open(io.BytesIO(original)) as opened:
            image = opened.convert('RGBA')
        widths = [400, 800]
        if category == 'illustrations' and image.width > 800:
            widths.append(image.width)
        widths = sorted({min(w, image.width) for w in widths})
        variants = []
        prior = prior_assets.get(source, {})
        for width in widths:
            candidate = resized_rgba(image, width)
            name = f'{path.stem}-{width}-q{quality}-{source_hash[:8]}.webp'
            destination = DEST / category / name
            old = next((v for v in prior.get('variants', []) if v['width'] == width and v['quality'] == quality and v['src'] == str(destination.relative_to(SITE))), None)
            cached = destination.read_bytes() if destination.exists() and old and prior.get('sourceSha256') == source_hash else None
            if cached is not None and digest(cached) == old['sha256']:
                payload, metrics = cached, measure(candidate, cached)
            else:
                payload, metrics = encode(candidate, quality)
                atomic_write(destination, payload)
            variants.append({
                'src': str(destination.relative_to(SITE)),
                'width': candidate.width, 'height': candidate.height,
                'bytes': len(payload), 'quality': quality, 'sha256': digest(payload),
                **metrics,
            })
        default = next((v for v in variants if v['width'] == 800), variants[-1])
        assets[source] = {
            'src': default['src'], 'width': default['width'], 'height': default['height'],
            'srcset': ', '.join(f"{v['src']} {v['width']}w" for v in variants),
            'sourceWidth': image.width, 'sourceHeight': image.height,
            'sourceBytes': len(original), 'sourceSha256': source_hash,
            'kind': category, 'variants': variants,
        }
        if digest(path.read_bytes()) != source_hash:
            raise SystemExit(f'Master changed concurrently: {source}; manifest was not published.')
    manifest = {
        'version': 1,
        'method': 'Pillow WebP; packaging q94, illustrations q90; exact alpha; premultiplied resizing; no generative editing.',
        'integration': 'Keys are original site-relative paths without query strings. src is the 800px candidate; width/height describe it. Add an accurate sizes attribute in the consuming component. Packaging srcset is 400w/800w; illustrations also retain an optimized native-width candidate.',
        'assets': assets,
        'totals': {
            'sources': len(assets), 'packagingSources': len(packs),
            'variants': sum(len(a['variants']) for a in assets.values()),
            'sourceBytes': sum(a['sourceBytes'] for a in assets.values()),
            'defaultSrcBytes': sum(next(v['bytes'] for v in a['variants'] if v['src'] == a['src']) for a in assets.values()),
            'allVariantsBytes': sum(v['bytes'] for a in assets.values() for v in a['variants']),
        },
    }
    atomic_write(SITE / 'asset-variants.json', (json.dumps(manifest, ensure_ascii=False, indent=2) + '\n').encode())
    return manifest


if __name__ == '__main__':
    result = build()
    print(json.dumps(result['totals'], ensure_ascii=False, indent=2))
