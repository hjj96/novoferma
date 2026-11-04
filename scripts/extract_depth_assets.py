"""Extract two food accents from the supplied transparent brand artwork.

No photo synthesis, repainted texture or background removal service is involved.
Run with Pillow: python3 scripts/extract_depth_assets.py [--source-dir PATH].
The source folder defaults to the original, user-supplied Downloads folder.
"""

from argparse import ArgumentParser
from pathlib import Path
import json
from shutil import copyfile
from collections import deque

from PIL import Image, ImageChops, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output/concept/assets/depth"


def polygon_mask(size, points):
    """Supersampling retains a soft one-pixel contour on the traced silhouette."""
    scale = 4
    mask = Image.new("L", (size[0] * scale, size[1] * scale))
    ImageDraw.Draw(mask).polygon(
        [(round(x * scale), round(y * scale)) for x, y in points], fill=255
    )
    return mask.resize(size, Image.Resampling.LANCZOS)


def remove_orange_floor_fringe(image):
    """Remove the two flat orange scraps beneath the rooster's feet.

    The supplied hero artwork contains the section-colour matte as opaque
    pixels.  Most of it is covered by the orange hero background, but the
    small pieces below the feet become visible when the composition crosses
    into the cream section. Remove only those small floor zones, then restore
    enclosed colour matches to preserve highlights inside the illustrated toes.
    """
    width, height = image.size
    pixels = image.load()
    alpha = image.getchannel("A")
    alpha_pixels = alpha.load()
    removed = 0

    # Hand-traced floor zones from the supplied artwork.  The dark legs and
    # toes sit above these zones; the saturated orange pixels below them are
    # the baked section matte.  Keeping the test colour-based avoids cutting
    # the photographed meatball that overlaps the right side of the second
    # zone.
    for y in range(height):
        for x in range(width):
            left_zone = x < 112 and y >= 474
            right_zone = 118 <= x <= 212 and y >= 478
            if not (left_zone or right_zone):
                continue
            r, g, b, a = pixels[x, y]
            if a > 2 and r > 110 and r - g > 34 and g - b > 7 and g < 175:
                alpha_pixels[x, y] = 0
                removed += 1

    # Restore isolated colour matches enclosed by the illustration (toe highlights).
    # Only background-connected removed components are ground matte.
    visited = set()
    for y in range(height):
        for x in range(width):
            if alpha_pixels[x, y] or not pixels[x, y][3] or (x, y) in visited:
                continue
            queue = deque([(x, y)])
            visited.add((x, y))
            component = []
            connects_to_background = False
            while queue:
                xx, yy = queue.popleft()
                component.append((xx, yy))
                for nx, ny in ((xx - 1, yy), (xx + 1, yy), (xx, yy - 1), (xx, yy + 1)):
                    if not (0 <= nx < width and 0 <= ny < height):
                        connects_to_background = True
                        continue
                    if pixels[nx, ny][3] < 180:
                        connects_to_background = True
                    elif not alpha_pixels[nx, ny] and (nx, ny) not in visited:
                        visited.add((nx, ny))
                        queue.append((nx, ny))
            if not connects_to_background and len(component) < 18:
                for xx, yy in component:
                    alpha_pixels[xx, yy] = pixels[xx, yy][3]
                    removed -= 1
    image.putalpha(alpha)
    return removed


def extract(source_dir, filename, name, crop_box, outline, remove_shadow=False):
    source = Image.open(source_dir / filename).convert("RGBA")
    crop = source.crop(crop_box)
    alpha = crop.getchannel("A")
    if remove_shadow:
        # The supplied strip has a separate, low-opacity ground shadow. Remove
        # it without changing the RGB texture; CSS supplies the floating shadow.
        alpha = alpha.point(lambda value: max(0, min(255, round((value - 215) * 255 / 40))))
    alpha = ImageChops.multiply(alpha, polygon_mask(crop.size, outline))
    crop.putalpha(alpha)
    bbox = alpha.point(lambda value: 255 if value > 2 else 0).getbbox()
    crop = crop.crop(bbox)
    # Padding keeps the antialiased silhouette away from the image boundary.
    result = Image.new("RGBA", (crop.width + 24, crop.height + 24))
    result.alpha_composite(crop, (12, 12))
    path = OUT / f"{name}.webp"
    result.save(path, format="WEBP", lossless=True, method=6)
    return {
        "file": path.name,
        "size": list(result.size),
        "bytes": path.stat().st_size,
        "source": filename,
        "sourceSize": list(source.size),
        "cropBox": crop_box,
        "alphaBox": list(result.getchannel("A").getbbox()),
        "notes": "Original photographic texture. Transparent background; no embedded ground shadow.",
    }


def clean_hero_composition():
    """Remove orange floor baked into the PDF hero, preserving all objects.

    Its original orange matte is appropriate above the section boundary, but
    the foreground products cross into cream. The bottom outline excludes only
    the flat floor shadows; soft neutral shadows are composited behind it.
    """
    source = OUT.parent / "hero-reference.webp"
    artwork = Image.open(source).convert("RGBA")
    lower_contour = [
        (0, 0), (768, 0), (768, 430), (640, 430), (612, 428),
        (593, 434), (583, 439), (575, 444), (564, 448),
        (546, 450), (514, 450), (477, 450), (441, 450),
        (440, 463), (437, 476), (431, 487), (424, 495),
        (414, 500), (401, 507), (390, 509), (377, 511), (365, 511),
        (351, 509), (338, 505), (329, 501), (322, 495), (313, 484),
        (307, 479), (300, 482), (290, 487), (278, 489),
        (259, 490), (244, 489), (230, 487), (218, 484), (210, 482),
        (210, 545), (0, 545),
    ]
    contour = polygon_mask(artwork.size, lower_contour)
    artwork.putalpha(ImageChops.multiply(artwork.getchannel("A"), contour))

    remove_orange_floor_fringe(artwork)

    # Each shadow is deliberately low-opacity and neutral. No orange plane
    # remains when these foreground objects cross into a cream or green block.
    shadow_mask = Image.new("L", artwork.size)
    draw = ImageDraw.Draw(shadow_mask)
    draw.ellipse((308, 500, 440, 519), fill=58)
    draw.ellipse((184, 480, 309, 496), fill=45)
    draw.ellipse((442, 440, 579, 455), fill=26)
    shadow_mask = shadow_mask.filter(ImageFilter.GaussianBlur(4.0))
    result = Image.new("RGBA", artwork.size, (62, 33, 19, 0))
    result.putalpha(shadow_mask)
    result.alpha_composite(artwork)
    path = OUT / "hero-composition.webp"
    result.save(path, format="WEBP", lossless=True, method=6)

    # Exact requested seam plus a more demanding seam through both meatballs.
    proof = Image.new("RGB", (1536, 545))
    for index, seam in enumerate((495, 470)):
        canvas = Image.new("RGBA", artwork.size, (236, 88, 18, 255))
        ImageDraw.Draw(canvas).rectangle((0, seam, 768, 545), fill=(253, 245, 226, 255))
        canvas.alpha_composite(result)
        proof.paste(canvas.convert("RGB"), (index * 768, 0))
    proof.save(OUT / "hero-preview.jpg", quality=97)
    return {
        "file": path.name, "size": list(result.size), "bytes": path.stat().st_size,
        "source": "../hero-reference.webp", "sourceSize": list(artwork.size),
        "notes": "Original hero artwork. Orange floor shadows under the food replaced with soft neutral alpha shadows. Orange ground matte removed below both rooster feet, with enclosed toe highlights preserved. Cleanup runs before neutral shadows; same canvas and object positions.",
    }


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source-dir", type=Path, default=Path.home() / "Downloads/Новая папка"
    )
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)

    # The front nugget is fully visible on the plate. The outline follows its
    # craggy coating and excludes the plate and the two neighbouring pieces.
    nugget = extract(args.source_dir, "наггетсы@3x.png", "nugget", (660, 795, 1068, 1147), [
        (45, 162), (57, 154), (68, 150), (83, 143), (102, 136), (125, 126),
        (145, 119), (164, 110), (182, 100), (194, 90), (208, 77), (225, 63),
        (237, 59), (247, 51), (262, 43), (278, 34), (292, 29), (305, 23),
        (312, 18), (320, 19), (326, 13), (332, 13), (338, 17), (347, 18),
        (356, 22), (365, 27), (373, 34), (378, 44), (383, 55), (388, 65),
        (391, 82), (391, 103), (390, 124), (389, 141), (384, 161),
        (379, 181), (374, 201), (368, 220), (360, 238), (350, 256),
        (338, 274), (324, 289), (305, 303), (286, 315), (269, 323),
        (247, 329), (222, 332), (196, 332), (170, 331), (142, 330),
        (117, 329), (92, 329), (69, 328), (52, 323), (42, 314), (32, 299),
        (28, 284), (25, 267), (23, 253), (16, 246), (10, 233), (8, 225),
        (12, 210), (18, 199), (24, 189), (29, 179), (35, 170),
    ])

    # Exterior alpha preserves individual breading flakes. The broad clipping
    # polygon only separates the lower strip from another piece above it.
    strip = extract(args.source_dir, "Ресурс 11@3x (1).png", "strip", (810, 945, 1219, 1095), [
        (0, 0), (175, 0), (215, 10), (245, 17), (270, 34), (296, 55),
        (320, 64), (365, 70), (409, 80), (409, 150), (0, 150),
    ], remove_shadow=True)

    # Reuse the already isolated ball prepared for the protein page. Keeping a
    # single depth inventory lets all section accents share one asset API.
    ball_source = OUT.parent / "meatball-float.webp"
    ball_target = OUT / "meatball.webp"
    copyfile(ball_source, ball_target)
    ball_image = Image.open(ball_target).convert("RGBA")
    meatball = {
        "file": ball_target.name,
        "size": list(ball_image.size),
        "bytes": ball_target.stat().st_size,
        "source": "../meatball-float.webp",
        "originalArtwork": "швед_мб.psd@3x.png",
        "alphaBox": list(ball_image.getchannel("A").getbbox()),
        "notes": "Unmodified copy of the existing isolated meatball. Original photographic texture.",
    }
    records = [meatball, nugget, strip]
    hero = clean_hero_composition()
    (OUT / "manifest.json").write_text(json.dumps({
        "source": str(args.source_dir),
        "method": "Traced silhouettes from user-supplied brand artwork; original food texture retained.",
        "assets": records + [hero],
    }, ensure_ascii=False, indent=2) + "\n")

    # QA includes the three actual section colours plus the dark footer.
    sheet = Image.new("RGB", (1200, 900))
    colors = [(253, 245, 226), (216, 220, 161), (236, 88, 18), (62, 33, 19)]
    for index, background in enumerate(colors):
        x = index * 300
        ImageDraw.Draw(sheet).rectangle((x, 0, x + 300, 900), fill=background)
        for row, record in enumerate(records):
            food = Image.open(OUT / record["file"]).convert("RGBA")
            food.thumbnail((265, 255), Image.Resampling.LANCZOS)
            left, top = x + (300 - food.width) // 2, row * 300 + (270 - food.height) // 2
            sheet.paste(food, (left, top), food)
            ImageDraw.Draw(sheet).text((x + 18, row * 300 + 275), record["file"],
                                      fill=(253, 245, 226) if index == 3 else (62, 33, 19))
    sheet.save(OUT / "preview.jpg", quality=95)
    for record in records + [hero]:
        print(record["file"], record["size"], record["bytes"])


if __name__ == "__main__":
    main()
