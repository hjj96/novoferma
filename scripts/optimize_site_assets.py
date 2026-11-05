#!/usr/bin/env python3
"""Build reviewed, non-generative WebP derivatives without changing their masters.

Outputs only assets/responsive/** and asset-variants.json. Full builds require
pre-change backups; scoped partner/hero builds verify pinned source hashes.
No HTML, CSS, product data or build output is rewritten by this tool.
"""
from __future__ import annotations
import argparse
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
}
DEST = SITE / 'assets/responsive'
PACK_QUALITY = 94
ILLUSTRATION_QUALITY = 90
# A baseline of the existing site artwork, not a new brand/artwork approval.
# A changed master must be inspected and explicitly re-baselined before encoding.
PARTNER_SOURCE = 'assets/partners-brand-v1/partner-host-v1.webp'
PARTNER_SOURCE_SHA256 = '283eb84c820753b8aa8c61d4e9024f939d560f9f2d31ea23f0be46ddad81e2bd'
PARTNER_WIDTHS = (240, 400, 640, 800, 1024)
HERO_SOURCE_HASHES = {
    'assets/product-hero/fibriki-art-v5.webp': '1b6cf1a289654f8fabee1b10cb4e8459380cbd4145734e2b287fa8fecabc8513',
    'assets/product-hero/meatballs-art-v4.webp': '8e04511ae7f89a89102daa20499a0c5d62f3f0f34687fc047dcefaec56d88958',
    'assets/product-hero/nuggets-art-v4.webp': 'e6e41be33fa1b039a64cc72efd4d1803b9761716b927ab1345581a1da4598c68',
    'assets/product-hero/lulia-mini-art-v4.webp': '7ed345d89b4ca2bfa9cb93d07abc351478346c3e127f680eb712d8e83a2c63cc',
}
HERO_WIDTHS = (640, 800, 1024, 1280)
ILLUSTRATIONS = [
    'assets/mascot-contact-restored-v2.webp',
    'assets/mascot-partnership-v2.webp',
    'assets/product-hero/running-mascot-v2.webp',
    'assets/protein-story/hen-layer-v2.webp',
    'assets/protein-story/nuggets-layer-v2.webp',
]


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


def partner_entry(prior_assets: dict) -> dict:
    """Re-encode the existing partner host; never regenerate or crop its art."""
    path = SITE / PARTNER_SOURCE
    original = path.read_bytes()
    source_hash = digest(original)
    if source_hash != PARTNER_SOURCE_SHA256:
        raise SystemExit('Partner-host master changed: inspect and update its baseline before encoding.')
    with Image.open(io.BytesIO(original)) as opened:
        image = opened.convert('RGBA')
    prior = prior_assets.get(PARTNER_SOURCE, {})
    variants = []
    for width in sorted({min(w, image.width) for w in PARTNER_WIDTHS}):
        candidate = resized_rgba(image, width)
        name = f'{path.stem}-{width}-q{ILLUSTRATION_QUALITY}-{source_hash[:8]}.webp'
        destination = DEST / 'partners' / name
        relative = str(destination.relative_to(SITE))
        old = next((v for v in prior.get('variants', [])
                    if v['width'] == width and v['quality'] == ILLUSTRATION_QUALITY
                    and v['src'] == relative), None)
        cached = destination.read_bytes() if destination.exists() and old and prior.get('sourceSha256') == source_hash else None
        if cached is not None and digest(cached) == old['sha256']:
            payload, metrics = cached, measure(candidate, cached)
        else:
            payload, metrics = encode(candidate, ILLUSTRATION_QUALITY)
            atomic_write(destination, payload)
        variants.append({'src': relative, 'width': candidate.width, 'height': candidate.height,
                         'bytes': len(payload), 'quality': ILLUSTRATION_QUALITY,
                         'sha256': digest(payload), **metrics})
    if digest(path.read_bytes()) != source_hash:
        raise SystemExit('Partner-host master changed concurrently; manifest was not published.')
    default = next(v for v in variants if v['width'] == 800)
    return {'src': default['src'], 'width': default['width'], 'height': default['height'],
            'srcset': ', '.join(f"{v['src']} {v['width']}w" for v in variants),
            'sourceWidth': image.width, 'sourceHeight': image.height,
            'sourceBytes': len(original), 'sourceSha256': source_hash,
            'kind': 'partners', 'variants': variants}


def asset_totals(assets: dict) -> dict:
    return {'sources': len(assets),
            'packagingSources': sum(a['kind'] == 'packshots' for a in assets.values()),
            'variants': sum(len(a['variants']) for a in assets.values()),
            'sourceBytes': sum(a['sourceBytes'] for a in assets.values()),
            'defaultSrcBytes': sum(next(v['bytes'] for v in a['variants'] if v['src'] == a['src']) for a in assets.values()),
            'allVariantsBytes': sum(v['bytes'] for a in assets.values() for v in a['variants'])}


def hero_entries(prior_assets: dict) -> dict:
    """Resize whole scene canvases; CSS retains responsibility for composition."""
    entries = {}
    for source, expected_hash in HERO_SOURCE_HASHES.items():
        path = SITE / source
        original = path.read_bytes()
        source_hash = digest(original)
        if source_hash != expected_hash:
            raise SystemExit(f'Hero master changed: inspect and update its baseline before encoding: {source}')
        with Image.open(io.BytesIO(original)) as opened:
            image = opened.convert('RGBA')
        prior = prior_assets.get(source, {})
        variants = []
        widths = sorted({min(w, image.width) for w in (*HERO_WIDTHS, image.width)})
        for width in widths:
            candidate = resized_rgba(image, width)
            name = f'{path.stem}-{width}-q{ILLUSTRATION_QUALITY}-{source_hash[:8]}.webp'
            destination = DEST / 'hero' / name
            relative = str(destination.relative_to(SITE))
            old = next((v for v in prior.get('variants', [])
                        if v['width'] == width and v['quality'] == ILLUSTRATION_QUALITY
                        and v['src'] == relative), None)
            cached = destination.read_bytes() if destination.exists() and old and prior.get('sourceSha256') == source_hash else None
            if cached is not None and digest(cached) == old['sha256']:
                payload, metrics = cached, measure(candidate, cached)
            else:
                payload, metrics = encode(candidate, ILLUSTRATION_QUALITY)
                atomic_write(destination, payload)
            variants.append({'src': relative, 'width': candidate.width, 'height': candidate.height,
                             'bytes': len(payload), 'quality': ILLUSTRATION_QUALITY,
                             'sha256': digest(payload), **metrics})
        default = next(v for v in variants if v['width'] == 800)
        entries[source] = {
            'src': default['src'], 'width': default['width'], 'height': default['height'],
            'srcset': ', '.join(f"{v['src']} {v['width']}w" for v in variants),
            'sourceWidth': image.width, 'sourceHeight': image.height,
            'sourceBytes': len(original), 'sourceSha256': source_hash,
            'kind': 'hero', 'variants': variants,
        }
    for source, expected_hash in HERO_SOURCE_HASHES.items():
        if digest((SITE / source).read_bytes()) != expected_hash:
            raise SystemExit(f'Hero master changed concurrently; manifest was not published: {source}')
    return entries


def build_hero_only() -> dict:
    """Update four hero entries, retaining independently managed manifest assets."""
    manifest_path = SITE / 'asset-variants.json'
    before = json.loads(manifest_path.read_text())
    entries = hero_entries(before['assets'])
    manifest = json.loads(manifest_path.read_text())
    manifest['assets'].update(entries)
    manifest['totals'] = asset_totals(manifest['assets'])
    atomic_write(manifest_path, (json.dumps(manifest, ensure_ascii=False, indent=2) + '\n').encode())
    return manifest


def build_partner_only() -> dict:
    """Preserve every other manifest entry, including independently added hero art."""
    manifest_path = SITE / 'asset-variants.json'
    before = json.loads(manifest_path.read_text())
    entry = partner_entry(before['assets'])
    # Re-read after encoding to retain unrelated entries added during this work.
    manifest = json.loads(manifest_path.read_text())
    manifest['assets'][PARTNER_SOURCE] = entry
    manifest['totals'] = asset_totals(manifest['assets'])
    atomic_write(manifest_path, (json.dumps(manifest, ensure_ascii=False, indent=2) + '\n').encode())
    return manifest


def build() -> dict:
    if not (BACKUP / 'script.js').is_file() or not (BACKUP / 'product-hero.js').is_file():
        raise SystemExit('Required implementation/before/concept backup is missing.')
    packshots = sorted((SITE / 'assets/catalogue-clean-v2').glob('*.webp'))
    if len(packshots) != 14:
        raise SystemExit(f'Expected 14 approved catalogue master paths, found {len(packshots)}.')
    packs = [str(p.relative_to(SITE)) for p in packshots] + [
        'assets/novelty-packaging/fibriki-pack-v11.webp',
        'assets/novelty-packaging/lulia-mini-pack-v3.webp',
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
    assets[PARTNER_SOURCE] = partner_entry(prior_assets)
    assets.update(hero_entries(prior_assets))
    manifest = {
        'version': 1,
        'method': 'Pillow WebP; packaging q94, illustrations q90; exact alpha; premultiplied resizing; no generative editing.',
        'integration': 'Keys are original site-relative paths without query strings. src is the 800px candidate; width/height describe it. Add an accurate sizes attribute in the consuming component. Packaging srcset is 400w/800w; illustrations also retain an optimized native-width candidate.',
        'assets': assets,
        'totals': asset_totals(assets),
    }
    atomic_write(SITE / 'asset-variants.json', (json.dumps(manifest, ensure_ascii=False, indent=2) + '\n').encode())
    return manifest


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    scope = parser.add_mutually_exclusive_group()
    scope.add_argument('--partner-only', action='store_true',
                       help='Update only existing partner-host derivatives and its manifest entry.')
    scope.add_argument('--hero-only', action='store_true',
                       help='Update only four pinned hero masters and their manifest entries.')
    args = parser.parse_args()
    result = build_hero_only() if args.hero_only else build_partner_only() if args.partner_only else build()
    print(json.dumps(result['totals'], ensure_ascii=False, indent=2))
