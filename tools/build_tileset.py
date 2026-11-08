#!/usr/bin/env python3
"""Builds the Fuel Barrel tileset (42/media/fuelbarrel.tiles and texturepacks/fuelbarrel.pack).

Tile 0 is the standard barrel on its own. Each barrel style then has 16 tiles from its
overlay_base: tile base + N is vanilla generator sprite appliances_misc_01_N with that
barrel and hose added. FuelBarrel.lua sets those as an overlay that covers the generator,
so vanilla still sees its own sprite. Each style's item icon is written alongside.

Usage: python3 tools/build_tileset.py [path/to/ProjectZomboid/projectzomboid]
Needs Pillow. Rerun after editing the tables or colours below.
"""
import io
import math
import random
import struct
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

NAME = "fuelbarrel"
TILESET = NAME + "_01"
COLUMNS, ROWS = 8, 5
PAGE_SIZE = 1024
TILE_W, TILE_H = 128, 256
SUPERSAMPLE = 4
GENERATOR_PREFIX = "appliances_misc_01_"
GENERATOR_SPRITES = 16

DRUM_SQUASH = 0.5  # height of the top ellipse as a fraction of its width
ALONE_FOOT = (64, 226)
BEHIND_GENERATOR_FOOT = (64, 212)

# Forms follow vanilla's metal drums: fat, a flat grey lid in a heavy dark rim, a small dark bung
# hole, soft vertical streaks and thin rolled ribs.
PAINT = (52, 84, 60)
RED = (122, 44, 36)
CREAM = (150, 142, 118)
RUST = (92, 58, 36)
GRIME = (40, 36, 30)
STEEL = (96, 98, 96)
LID = (122, 132, 128)
LID_RIM = (46, 48, 48)
BUNG_HOLE = (24, 24, 24)
BANDS = [(0.40, 0.45, RED), (0.45, 0.61, CREAM), (0.61, 0.66, RED)]
HOOPS = [0.33, 0.70]  # rolled ribs, as a fraction of the drum height
# Side lighting matches how the game lights the 3D model: a broad highlight left of centre.
LIGHT_PEAK, LIGHT_LEFT, LIGHT_RIGHT = 1.0, 0.74, 0.5
LIGHT_PEAK_AT = -0.4
RIB_LIT, RIB_DARK, RIB_WIDTH = 1.2, 0.62, 0.012
EDGE_DARK = 0.55  # the drum's sides and foot, which vanilla darkens instead of outlining
BUNG_OFFSET = (-0.42, -0.04)  # as a fraction of the radius

# The crude barrel is salvaged plate welded over a rusty drum, each plate left as it was found.
# (around from, around to, height from, height to, colour, how it's fixed on). Later plates sit on top.
OLD_RUST = (104, 62, 38)
DARK_RUST = (66, 42, 30)
PRIMER = (102, 100, 92)
OLIVE = (82, 86, 58)
SIGN_YELLOW = (150, 118, 48)
SIGN_BLACK = (42, 40, 36)
ROAD_ORANGE = (140, 78, 40)
TIN = (120, 122, 116)
WELD = (160, 152, 136)
WELD_SHADOW = (32, 26, 22)
RIVET = (30, 28, 26)
RIVET_LIT = (150, 146, 136)
PLATES = [
    (0.00, 0.40, 0.00, 0.46, OLD_RUST, "weld"),
    (0.40, 0.74, 0.00, 0.34, OLIVE, "weld"),
    (0.74, 1.00, 0.00, 0.56, PRIMER, "weld"),
    (0.00, 0.26, 0.46, 1.00, PRIMER, "weld"),
    (0.26, 0.62, 0.34, 0.72, "hazard", "rivet"),
    (0.62, 1.00, 0.56, 1.00, ROAD_ORANGE, "weld"),
    (0.26, 0.62, 0.72, 1.00, DARK_RUST, "weld"),
    (0.08, 0.30, 0.14, 0.38, TIN, "rivet"),
    (0.66, 0.90, 0.20, 0.42, DARK_RUST, "rivet"),
]
PLATE_WOBBLE = 0.012  # the plates were cut by hand
WELD_WIDTH = 0.012
RIVET_SPACING = 0.07
HAZARD_STRIPE = 0.09

HOSE = (153, 134, 91)  # the Rubber Hose icon, allowing for sprites rendering darker
HOSE_HIGHLIGHT = (194, 170, 115)
HOSE_WIDTH = 2.4
SHADOW = (0, 0, 0, 80)
ICON_SIZE = 64


def streak(around, v):
    """Soft vertical runs of dirt, heavier towards the foot, in 0..1."""
    run = 0.5 + 0.5 * math.sin(around * 67.0 + 1.3 * math.sin(around * 23.0))
    fine = 0.5 + 0.5 * math.sin(around * 171.0 + v * 2.0)
    return (0.6 * run + 0.4 * fine) * (0.35 + 0.65 * (1 - v))


def standard_colour(around, v, rust):
    """Paint at a point. around runs 0 to 1 around the drum, v from foot to rim."""
    colour = PAINT
    for low, high, band in BANDS:
        if low <= v < high:
            colour = band
    colour = mix(colour, GRIME, streak(around, v) * 0.42)
    return mix(colour, RUST, min(1.0, rust * (1.3 if v < 0.2 else 0.7)) * 0.75)


def plate_colour(paint, around, v):
    if paint != "hazard":
        return paint
    return SIGN_YELLOW if int((around * 2.2 + v) / HAZARD_STRIPE) % 2 else SIGN_BLACK


def crude_colour(around, v, rust):
    """Plates of different metal welded over the drum, each worn in its own way."""
    a = around + math.sin(v * 21.0) * PLATE_WOBBLE
    h = v + math.sin(around * 27.0) * PLATE_WOBBLE
    colour = DARK_RUST
    for left, right, low, high, paint, fixing in PLATES:
        inside = left <= a <= right and low <= h <= high
        if inside:
            colour = plate_colour(paint, a, h)
            colour = mix(colour, GRIME, streak(a, h) * 0.5)
            colour = mix(colour, OLD_RUST, min(1.0, rust * 1.5) * 0.85)
            edge = min(a - left, right - a, h - low, high - h)
            if edge < WELD_WIDTH and fixing == "weld" and 0 < left + (1 - right) + low + (1 - high):
                colour = mix(WELD, RUST, rust * 0.4) if (int(a * 90) + int(h * 90)) % 3 else WELD_SHADOW
            elif fixing == "rivet" and edge < WELD_WIDTH * 1.8:
                along = a if min(h - low, high - h) < min(a - left, right - a) else h
                dot = abs((along / RIVET_SPACING) % 1 - 0.5)
                if dot < 0.14:
                    colour = RIVET_LIT if dot < 0.05 else RIVET
        elif left - WELD_WIDTH <= a <= right + WELD_WIDTH and low - WELD_WIDTH <= h <= high + WELD_WIDTH:
            colour = mix(colour, WELD_SHADOW, 0.7)
    return colour


STANDARD = dict(
    name="FuelBarrel", radius=29.0, height=72.0, colour=standard_colour, hoops=HOOPS, lid=LID, lid_seam=False,
    wear_seed=7, overlay_base=1,
)
CRUDE = dict(
    name="CrudeFuelBarrel", radius=23.0, height=50.0, colour=crude_colour, hoops=[], lid=(86, 74, 62), lid_seam=True,
    wear_seed=23, overlay_base=17,
)
STYLES = [STANDARD, CRUDE]


def drum_props():
    return [
        ("BlocksPlacement", ""),
        ("CanScrap", ""),
        ("CustomName", "Fuel Barrel"),
        ("IsMoveAble", ""),
        ("Material", "MetalScrap"),
        ("PickUpWeight", "75"),
        ("solidtrans", ""),
    ]


TILE_PROPS = {0: drum_props()}
for style in STYLES:
    for sprite_index in range(GENERATOR_SPRITES):
        TILE_PROPS[style["overlay_base"] + sprite_index] = [("CustomName", "Generator Barrel")]


def read_string(f):
    (length,) = struct.unpack("<I", f.read(4))
    return f.read(length).decode("utf8", "replace")


def write_string(out, value):
    data = value.encode("utf8")
    out.write(struct.pack("<I", len(data)))
    out.write(data)


def extract_sprites(pack_path, wanted):
    """Returns {sprite name: full-size RGBA tile image}."""
    found = {}
    with open(pack_path, "rb") as f:
        if f.read(4) != b"PZPK":
            raise SystemExit(f"{pack_path}: not a PZPK pack")
        _version, pages = struct.unpack("<II", f.read(8))
        for _ in range(pages):
            read_string(f)
            count, _alpha = struct.unpack("<II", f.read(8))
            entries = []
            for _ in range(count):
                name = read_string(f)
                entries.append((name, struct.unpack("<8I", f.read(32))))
            (size,) = struct.unpack("<I", f.read(4))
            hits = [e for e in entries if e[0] in wanted]
            if not hits:
                f.seek(size, 1)
                continue
            page = Image.open(io.BytesIO(f.read(size))).convert("RGBA")
            for name, (x, y, w, h, ox, oy, full_w, full_h) in hits:
                tile = Image.new("RGBA", (full_w, full_h), (0, 0, 0, 0))
                tile.paste(page.crop((x, y, x + w, y + h)), (ox, oy))
                found[name] = tile
    missing = wanted - found.keys()
    if missing:
        raise SystemExit(f"sprites not found in {pack_path}: {sorted(missing)}")
    return found


def mix(a, b, amount):
    return tuple(a[i] + (b[i] - a[i]) * amount for i in range(3))


def wear_map(width, height, seed):
    """Soft blotches in 0..255, used to rub the paint back to rust."""
    rng = random.Random(seed)
    noise = Image.new("L", (width, height), 0)
    draw = ImageDraw.Draw(noise)
    for _ in range(width * height // 900):
        x, y, r = rng.uniform(0, width), rng.uniform(0, height), rng.uniform(2, 9)
        draw.ellipse([x - r, y - r * 0.6, x + r, y + r * 0.6], fill=rng.randint(120, 255))
    return noise.filter(ImageFilter.GaussianBlur(2.0))


def draw_drum(layer, foot, style):
    """Paints the drum on a supersampled layer. Shaded by light, with no outlines."""
    s = SUPERSAMPLE
    cx, fy = foot[0] * s, foot[1] * s
    r, height = style["radius"] * s, style["height"] * s
    ry = r * DRUM_SQUASH
    wear = wear_map(int(r * 2) + 2, int(height + ry * 2) + 2, style["wear_seed"])
    pixels = layer.load()
    x0 = int(cx - r)

    for x in range(x0, int(cx + r) + 1):
        u = (x - cx) / r
        if abs(u) >= 1:
            continue
        arc = ry * math.sqrt(1 - u * u)
        around = math.asin(u) / math.pi + 0.5
        light = side_light(u)
        for y in range(int(fy + arc - height), int(fy + arc) + 1):
            v = (fy + arc - y) / height  # 0 at the foot, 1 at the rim
            rust = wear.getpixel((x - x0, min(wear.height - 1, int(y - (fy - height - ry))))) / 255
            colour = style["colour"](around, v, rust)
            shade = light * (0.74 + 0.26 * v)
            for hoop in style["hoops"]:
                d = (v - hoop) / RIB_WIDTH
                if abs(d) < 1.6:
                    shade *= RIB_LIT if d > 0 else RIB_DARK
            if v < 0.03 or abs(u) > 0.965:
                shade *= EDGE_DARK
            pixels[x, y] = tuple(min(255, int(c * shade)) for c in colour) + (255,)

    draw = ImageDraw.Draw(layer)
    top = fy - height
    lid = style["lid"]
    rng = random.Random(style["wear_seed"])
    draw.ellipse([cx - r, top - ry, cx + r, top + ry], fill=LID_RIM + (255,))
    inner = 0.9
    draw.ellipse([cx - r * inner, top - ry * inner, cx + r * inner, top + ry * inner], fill=lid + (255,))
    for _ in range(int(r * ry / (s * s) * 0.5)):
        angle, reach = rng.uniform(0, math.tau), math.sqrt(rng.random()) * inner * 0.96
        x, y = cx + math.cos(angle) * r * reach, top + math.sin(angle) * ry * reach
        run = rng.uniform(1.5, 6) * s
        draw.line([(x, y), (x + run, y)], fill=tuple(int(c * rng.uniform(0.86, 1.1)) for c in lid) + (255,), width=max(1, s // 2))
    if style["lid_seam"]:
        y = top + ry * 0.42
        half = r * inner * math.sqrt(1 - 0.42 ** 2)
        for i in range(24):
            x = cx - half + 2 * half * i / 24
            draw.line([(x, y), (x + 2 * half / 24, y)], fill=(WELD if i % 3 else WELD_SHADOW) + (255,), width=s)
    bx, by = bung_position(foot, style)
    for x, y, size in ((bx * s, by * s, 2.4 * s), (cx + r * 0.5, top + ry * 0.1, 1.7 * s)):
        draw.ellipse([x - size, y - size * 0.6, x + size, y + size * 0.6], fill=BUNG_HOLE + (255,))


def side_light(u):
    """Brightness across the drum, u running from -1 at the left edge to 1 at the right."""
    if u < LIGHT_PEAK_AT:
        amount = (u - LIGHT_PEAK_AT) / (-1 - LIGHT_PEAK_AT)
        return LIGHT_PEAK + (LIGHT_LEFT - LIGHT_PEAK) * amount * amount
    amount = (u - LIGHT_PEAK_AT) / (1 - LIGHT_PEAK_AT)
    return LIGHT_PEAK + (LIGHT_RIGHT - LIGHT_PEAK) * amount * amount * (3 - 2 * amount)


def bung_position(foot, style):
    return foot[0] + BUNG_OFFSET[0] * style["radius"], foot[1] - style["height"] + BUNG_OFFSET[1] * style["radius"]


def draw_shadow(layer, foot, style):
    s = SUPERSAMPLE
    shadow = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    r = style["radius"] * 1.03 * s
    x, y = foot[0] * s + 1 * s, foot[1] * s + 1 * s
    ImageDraw.Draw(shadow).ellipse([x - r, y - r * 0.5, x + r, y + r * 0.5], fill=SHADOW)
    layer.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(s)))


def new_layer():
    return Image.new("RGBA", (TILE_W * SUPERSAMPLE, TILE_H * SUPERSAMPLE), (0, 0, 0, 0))


def shrink(layer):
    return layer.resize((TILE_W, TILE_H), Image.LANCZOS)


def paint_barrel(style):
    layer = new_layer()
    draw_shadow(layer, ALONE_FOOT, style)
    draw_drum(layer, ALONE_FOOT, style)
    return shrink(layer)


def hose_points(start, end):
    """A sagging curve that leaves the bung upward, then drops to the generator."""
    side = 24 if end[0] >= start[0] else -24
    c1 = (start[0] + side * 0.2, start[1] - 14)
    c2 = (end[0] + side, end[1] - 26)
    points = []
    for i in range(41):
        t = i / 40
        m = 1 - t
        points.append(tuple(m**3 * start[k] + 3 * m * m * t * c1[k] + 3 * m * t * t * c2[k] + t**3 * end[k] for k in (0, 1)))
    return points


def draw_hose(layer, start, end):
    s = SUPERSAMPLE
    points = [(x * s, y * s) for x, y in hose_points(start, end)]
    draw = ImageDraw.Draw(layer)
    draw.line(points, fill=HOSE + (255,), width=int(HOSE_WIDTH * s), joint="curve")
    draw.line([(x - s * 0.4, y - s * 0.4) for x, y in points], fill=HOSE_HIGHLIGHT + (255,), width=max(1, s // 2), joint="curve")


def paint_generator(generator, style):
    """Barrel behind, generator over it, hose over both."""
    layer = new_layer()
    draw_drum(layer, BEHIND_GENERATOR_FOOT, style)
    tile = shrink(layer)
    tile.alpha_composite(generator)

    left, top, right, _bottom = generator.getbbox()
    cap = ((left + right) / 2, top + 7)
    hose = new_layer()
    draw_hose(hose, bung_position(BEHIND_GENERATOR_FOOT, style), cap)
    tile.alpha_composite(shrink(hose))
    return tile


def write_icon(folder, tile, name):
    folder.mkdir(parents=True, exist_ok=True)
    drum = tile.crop(tile.getbbox())
    scale = ICON_SIZE / max(drum.size)
    drum = drum.resize((max(1, int(drum.width * scale)), max(1, int(drum.height * scale))), Image.LANCZOS)
    icon = Image.new("RGBA", (ICON_SIZE, ICON_SIZE), (0, 0, 0, 0))
    icon.paste(drum, ((ICON_SIZE - drum.width) // 2, (ICON_SIZE - drum.height) // 2))
    icon.save(folder / f"Item_{name}.png")


def write_pack(path, tiles):
    """tiles maps tile index -> full-size RGBA image."""
    page = Image.new("RGBA", (PAGE_SIZE, PAGE_SIZE), (0, 0, 0, 0))
    entries = []
    x = y = row_height = 0
    for index, tile in sorted(tiles.items()):
        ox, oy, right, bottom = tile.getbbox()
        image = tile.crop((ox, oy, right, bottom))
        if x + image.width > PAGE_SIZE:
            x, y, row_height = 0, y + row_height, 0
        if y + image.height > PAGE_SIZE:
            raise SystemExit("tiles do not fit on one page; raise PAGE_SIZE")
        page.paste(image, (x, y))
        entries.append((f"{TILESET}_{index}", (x, y, image.width, image.height, ox, oy, tile.width, tile.height)))
        x += image.width
        row_height = max(row_height, image.height)

    png = io.BytesIO()
    page.save(png, "PNG")
    with open(path, "wb") as out:
        out.write(b"PZPK")
        out.write(struct.pack("<II", 1, 1))
        write_string(out, NAME + "0")
        out.write(struct.pack("<II", len(entries), 1))
        for name, values in entries:
            write_string(out, name)
            out.write(struct.pack("<8I", *values))
        out.write(struct.pack("<I", len(png.getvalue())))
        out.write(png.getvalue())


def write_tiles(path):
    with open(path, "wb") as out:
        out.write(b"tdef")
        out.write(struct.pack("<II", 1, 1))
        out.write(f"{TILESET}\n{TILESET}.png\n".encode("utf8"))
        out.write(struct.pack("<IIII", COLUMNS, ROWS, 1, COLUMNS * ROWS))
        for index in range(COLUMNS * ROWS):
            props = TILE_PROPS.get(index, [])
            out.write(struct.pack("<I", len(props)))
            for key, value in props:
                out.write(f"{key}\n{value}\n".encode("utf8"))


def main():
    default_game = Path.home() / ".local/share/Steam/steamapps/common/ProjectZomboid/projectzomboid"
    game = Path(sys.argv[1]) if len(sys.argv) > 1 else default_game
    media = Path(__file__).resolve().parent.parent / "42" / "media"
    (media / "texturepacks").mkdir(parents=True, exist_ok=True)

    names = [f"{GENERATOR_PREFIX}{i}" for i in range(GENERATOR_SPRITES)]
    sprites = extract_sprites(game / "media/texturepacks/Tiles2x.pack", set(names))
    tiles = {0: paint_barrel(STANDARD)}
    for style in STYLES:
        for i, name in enumerate(names):
            tiles[style["overlay_base"] + i] = paint_generator(sprites[name], style)
    write_pack(media / "texturepacks" / f"{NAME}.pack", tiles)
    for style in STYLES:
        write_icon(media / "textures", paint_barrel(style), style["name"])
    write_tiles(media / f"{NAME}.tiles")
    print(f"wrote {NAME}.pack and {NAME}.tiles to {media}")


if __name__ == "__main__":
    main()
