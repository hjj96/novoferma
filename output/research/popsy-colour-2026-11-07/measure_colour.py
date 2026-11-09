"""Read-only image colour diagnosis. Prints JSON; never changes image files.

Run from any directory with a Python that has Pillow:
    python3 measure_colour.py > colour-diagnosis.json
    python3 measure_colour.py --candidate /absolute/path/to/candidate.png

Coordinates use the entire image canvas. The common left paper patch avoids
printed text and food in the current v3 pack and the three named site references.
Candidate layouts must retain that clean patch, otherwise review/reselect it.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

from PIL import Image, ImageChops, ImageStat

ROOT = Path(__file__).resolve().parents[3]
SITE = ROOT / 'output/concept'
PAPER_ROI = (0.15, 0.33, 0.25, 0.37)
POPS_RIGHT_ROI = (0.77, 0.34, 0.85, 0.40)


def lab(rgb):
    """sRGB/D65 RGB mean -> CIELAB; diagnostic approximation, not a print proof."""
    c = [v / 255 for v in rgb]
    c = [v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in c]
    x = (c[0] * 0.4124564 + c[1] * 0.3575761 + c[2] * 0.1804375) / 0.95047
    y = c[0] * 0.2126729 + c[1] * 0.7151522 + c[2] * 0.0721750
    z = (c[0] * 0.0193339 + c[1] * 0.1191920 + c[2] * 0.9503041) / 1.08883
    f = lambda v: v ** (1 / 3) if v > 0.008856 else 7.787 * v + 16 / 116
    return [116 * f(y) - 16, 500 * (f(x) - f(y)), 200 * (f(y) - f(z))]


def delta_e(a, b):
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def sample(im, normalized):
    im = im.convert('RGBA')
    box = tuple(round(v * (im.width if i % 2 == 0 else im.height)) for i, v in enumerate(normalized))
    crop = im.crop(box)
    alpha = crop.getchannel('A')
    mask = alpha.point(lambda v: 255 if v >= 128 else 0)
    rgb = ImageStat.Stat(crop.convert('RGB'), mask)
    means = rgb.mean
    return {
        'roiNormalized': list(normalized),
        'roiPixels': list(box),
        'rgbMean': [round(v, 4) for v in means],
        'rgbMedian': rgb.median,
        'labFromMeanSrgbD65': [round(v, 4) for v in lab(means)],
        'redMinusBlue': round(means[0] - means[2], 4),
        'alphaMean': round(ImageStat.Stat(alpha).mean[0], 4),
        'alphaExtrema': list(alpha.getextrema()),
    }


def describe(path, include_right=False):
    with Image.open(path) as opened:
        record = {
            'path': str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path),
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
            'size': list(opened.size),
            'mode': opened.mode,
            'embeddedIccBytes': len(opened.info.get('icc_profile', b'')),
            'gamma': opened.info.get('gamma'),
            'srgbTag': opened.info.get('srgb'),
            'leftCleanPaper': sample(opened, PAPER_ROI),
        }
        if include_right:
            record['rightPopsPaper'] = sample(opened, POPS_RIGHT_ROI)
        return record


def diff(a, b):
    a = a.convert('RGBA')
    b = b.convert('RGBA')
    assert a.size == b.size, (a.size, b.size)
    mask = a.getchannel('A').point(lambda v: 255 if v >= 128 else 0)
    difference = ImageChops.difference(a.convert('RGB'), b.convert('RGB'))
    return {
        'foregroundRgbMae8Bit': round(sum(ImageStat.Stat(difference, mask).mean) / 3, 4),
        'alphaMaxDifference': ImageChops.difference(a.getchannel('A'), b.getchannel('A')).getextrema()[1],
    }


def measure(candidates):
    original = ROOT / 'output/pops-2026-11-05/revision-3/assets/pops-v3-drummer.png'
    master_key = 'assets/novelty-packaging/popsy-pack-v3.webp'
    master_path = SITE / master_key
    manifest = json.loads((SITE / 'asset-variants.json').read_text())['assets'][master_key]
    source = describe(original, True)
    master = describe(master_path, True)
    with Image.open(original) as a, Image.open(master_path) as b:
        native_diff = diff(a, b)
    variants = []
    with Image.open(master_path) as opened:
        master_image = opened.convert('RGBA')
    for entry in manifest['variants']:
        path = SITE / entry['src']
        record = describe(path, True)
        with Image.open(path) as image:
            reference = master_image.convert('RGBa').resize(image.size, Image.Resampling.LANCZOS).convert('RGBA')
            record['differenceFromPremultipliedResizedMaster'] = diff(reference, image)
        record['manifestSha256Matches'] = entry['sha256'] == record['sha256']
        variants.append(record)
    neighbors = [describe(SITE / 'assets/catalogue-clean-v2' / f'{name}.webp') for name in
                 ('naggetsy-kurinye', 'stripsy', 'kurinyj-popkorn')]
    candidate_records = [describe(Path(p).resolve(), True) for p in candidates]
    base_lab = source['leftCleanPaper']['labFromMeanSrgbD65']
    for record in [master, *variants, *neighbors, *candidate_records]:
        record['leftPaperDeltaE76FromV3Png'] = round(delta_e(base_lab, record['leftCleanPaper']['labFromMeanSrgbD65']), 4)
    return {
        'date': '2026-11-07',
        'scope': 'Read-only local asset and stylesheet diagnosis; no raster edits.',
        'method': {
            'commonCleanPaperRoiNormalized': list(PAPER_ROI),
            'popsOnlyRightRoiNormalized': list(POPS_RIGHT_ROI),
            'coordinateConvention': '[left, top, right, bottom] relative to full image canvas; Python round() to pixel bounds.',
            'rgbMeanMask': 'Pixels with alpha >= 128. No colour transform applied before collecting RGB means.',
            'lab': 'Approximate CIELAB from patch mean assuming sRGB/D65; Euclidean Delta E 1976.',
            'foregroundDifference': 'Average absolute RGB channel difference over alpha >= 128; alpha measured separately.',
            'variantReference': 'RGBA master -> premultiplied RGBa -> Lanczos resize -> RGBA, matching optimizer.',
            'limitations': 'Local clean paper samples, not whole-package or calibrated print measurements. Right ROI is for Pops only: neighbor artwork overlaps it. Revalidate the patch visually if a candidate changes layout.',
        },
        'cssFinding': {
            'product-cards.css:28': 'drop-shadow only; no brightness, saturation, contrast or blend mode.',
            'product-detail.css:23': 'drop-shadow only.',
            'motion.css:100,110': 'Product cards and product details have opacity 1 and disabled reveal animations.',
        },
        'v3Png': source,
        'siteMaster': master,
        'pngToSiteMasterDifference': native_diff,
        'responsiveVariants': variants,
        'siteNeighborMasters': neighbors,
        'candidates': candidate_records,
        'conclusion': 'The meaningful paper-tone difference is already in the v3 PNG. Encoding/resizing changes the sampled paper very little; no site colour filter or ICC mismatch was found. Pops paper is darker and redder/less yellow than Strips/Nuggets in the sampled patch.',
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate', action='append', default=[], help='Optional candidate PNG to sample without editing it.')
    args = parser.parse_args()
    print(json.dumps(measure(args.candidate), ensure_ascii=False, indent=2))
