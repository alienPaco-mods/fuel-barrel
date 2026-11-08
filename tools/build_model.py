#!/usr/bin/env python3
"""Builds the 3D ground model (42/media/Models_X/*.glb) and texture for each barrel style.

The drum is a lathe: PROFILE is swept around Y. Units are metres, Y up, base on the ground.
The texture uses the same paint functions as the sprites in build_tileset.py. Its bands sit near the middle and
the lid is painted in both right-hand corners, so it looks right whichever way V runs.

Usage: python3 tools/build_model.py
Needs Pillow and numpy. Rerun after editing the tables below.
"""
import json
import math
import struct
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from build_tileset import BUNG_HOLE, CRUDE, LID_RIM, STANDARD, wear_map

SEGMENTS = 32
STYLES = [
    dict(STANDARD, mesh_radius=0.34, mesh_height=0.88, dent=0.0, wraps=1),
    dict(CRUDE, mesh_radius=0.29, mesh_height=0.635, dent=0.018, wraps=2),
]
HOOP_BULGE, HOOP_HALF_WIDTH = 0.006, 0.016
RIM_LIP, LID_DROP = 0.008, 0.014
RIM_WIDTH = 0.14  # as a fraction of the radius, matching the sprite
TEXTURE_SIZE = 512  # painted at this size, then reduced to SAVED_TEXTURE_SIZE
SAVED_TEXTURE_SIZE = 128  # about the sprite's level of detail, so it doesn't look too sharp
COLOUR_STEP = 10  # shades per channel, also to match the sprite
BODY_U = 0.75  # the body uses the left of the texture, the lid the right-hand corners
LID_V = 0.25
RIM_STRIP_U = 0.725
# The game lights this model far darker than the sprites, so the texture is painted brighter.
BODY_GAIN = 1.9
LID_GAIN = 1.65
TEXTURE_BLUR = 1.5  # pixels, so the bands have soft painted edges like the sprites
# wraps is how many times the paint repeats round the drum, so a crude plate isn't stretched.
# Only shading that runs around the drum is painted: dropped items can face any way.
BASE_SHADE = 0.72  # brightness at the foot, rising to 1 at the rim
HOOP_LIT, HOOP_DARK = 1.16, 0.74
HOOP_SHADE_WIDTH = 0.016  # as a fraction of the drum height


def body_profile(style):
    """(radius, height) up the outside, with any hoops as small bulges."""
    radius, height = style["mesh_radius"], style["mesh_height"]
    points = [(radius, 0.0)]
    # Extra rings give a dented drum enough vertices to look uneven.
    rings = [] if style["hoops"] else [i / 6 for i in range(1, 6)]
    for ring in rings:
        points.append((radius, ring * height))
    for hoop in style["hoops"]:
        y = hoop * height
        points += [(radius, y - HOOP_HALF_WIDTH), (radius + HOOP_BULGE, y), (radius, y + HOOP_HALF_WIDTH)]
    points += [(radius, height - RIM_LIP * 2), (radius + RIM_LIP, height - RIM_LIP), (radius + RIM_LIP, height)]
    return points


class Mesh:
    def __init__(self, style):
        self.height = style["mesh_height"]
        self.dent = style["dent"]
        self.positions, self.normals, self.uvs, self.indices = [], [], [], []

    def vertex(self, position, normal, uv):
        self.positions.append(position)
        self.normals.append(normal)
        self.uvs.append(uv)
        return len(self.positions) - 1

    def quad(self, a, b, c, d):
        self.indices += [a, b, c, a, c, d]

    def lathe(self, profile, u0, u1, flip=False):
        """Sweeps profile around Y, with normals smoothed along it so edges roll softly."""
        side = -1 if flip else 1
        steps = []
        for (r0, y0), (r1, y1) in zip(profile, profile[1:]):
            length = math.hypot(r1 - r0, y1 - y0) or 1
            steps.append((side * (y1 - y0) / length, side * (r0 - r1) / length))

        normals = []
        for i in range(len(profile)):
            near = steps[max(0, i - 1):i + 1]
            nr, ny = sum(s[0] for s in near), sum(s[1] for s in near)
            length = math.hypot(nr, ny) or 1
            normals.append((nr / length, ny / length))

        rows = []
        for (r, y), (nr, ny) in zip(profile, normals):
            row = []
            for i in range(SEGMENTS + 1):
                angle = 2 * math.pi * i / SEGMENTS
                c, s = math.cos(angle), math.sin(angle)
                u = u0 + (u1 - u0) * i / SEGMENTS
                # Dents fade out at the rim and foot, so those circles stay round.
                ends = math.sin(math.pi * min(1.0, y / self.height))
                dented = r * (1 + self.dent * ends * math.sin(3 * angle + y * 11) * math.cos(2 * angle - y * 7))
                row.append(self.vertex((dented * c, y, dented * s), (nr * c, ny, nr * s), (u, 1 - y / self.height)))
            rows.append(row)

        for lower, upper in zip(rows, rows[1:]):
            for i in range(SEGMENTS):
                a, b, c, d = lower[i], upper[i], upper[i + 1], lower[i + 1]
                if flip:
                    self.quad(a, d, c, b)
                else:
                    self.quad(a, b, c, d)

    def disc(self, radius, y, up):
        """A flat circle, mapped to the lid in the texture's corner."""
        centre_u, centre_v, half = (1 + BODY_U) / 2, LID_V / 2, (1 - BODY_U) / 2 * 0.96
        normal = (0.0, 1.0 if up else -1.0, 0.0)
        centre = self.vertex((0.0, y, 0.0), normal, (centre_u, centre_v))
        ring = []
        for i in range(SEGMENTS + 1):
            angle = 2 * math.pi * i / SEGMENTS
            c, s = math.cos(angle), math.sin(angle)
            ring.append(self.vertex((radius * c, y, radius * s), normal, (centre_u + half * c, centre_v + half * s)))
        for i in range(SEGMENTS):
            self.indices += [centre, ring[i + 1], ring[i]] if up else [centre, ring[i], ring[i + 1]]


def build_mesh(style):
    radius, height = style["mesh_radius"], style["mesh_height"]
    mesh = Mesh(style)
    mesh.lathe(body_profile(style), 0.0, BODY_U)
    inner = radius * (1 - RIM_WIDTH)
    mesh.lathe([(radius + RIM_LIP, height), (inner, height)], BODY_U - 0.01, BODY_U - 0.02)
    mesh.lathe([(inner, height), (inner, height - LID_DROP)], BODY_U - 0.01, BODY_U - 0.02, flip=True)
    mesh.disc(inner, height - LID_DROP, up=True)
    mesh.disc(radius, 0.0, up=False)
    return mesh


def brighten(colour, gain):
    """Scales a colour, keeping its hue if it would pass the maximum."""
    scaled = [c * gain for c in colour]
    limit = min(1.0, 255 / max(scaled))
    return tuple(int(c * limit) for c in scaled) + (255,)


def paint_lid(image, centre, lid):
    draw = ImageDraw.Draw(image)
    size = image.width
    half = int((1 - BODY_U) / 2 * size)
    cx, cy = centre
    draw.rectangle([cx - half, cy - half, cx + half, cy + half], fill=brighten(lid, LID_GAIN))
    bung = int(half * 0.14)
    bx, by = cx - int(half * 0.45), cy
    draw.ellipse([bx - bung, by - bung, bx + bung, by + bung], fill=BUNG_HOLE + (255,))


def reduce_detail(image):
    small = image.resize((SAVED_TEXTURE_SIZE, SAVED_TEXTURE_SIZE), Image.BOX)
    red, green, blue, alpha = small.split()
    bands = [band.point(lambda v: v // COLOUR_STEP * COLOUR_STEP) for band in (red, green, blue)]
    return Image.merge("RGBA", (*bands, alpha))


def paint_texture(style):
    size = TEXTURE_SIZE
    body_width = int(size * BODY_U)
    image = Image.new("RGBA", (size, size), brighten(style["lid"], BODY_GAIN))
    wear = wear_map(body_width, size, style["wear_seed"])
    pixels = image.load()
    for y in range(size):
        v = 1 - y / size
        shade = BASE_SHADE + (1 - BASE_SHADE) * v
        for hoop in style["hoops"]:
            d = (v - hoop) / HOOP_SHADE_WIDTH
            if abs(d) < 1.6:
                shade *= HOOP_LIT if d > 0 else HOOP_DARK
        for x in range(body_width):
            colour = style["colour"](x / body_width * style["wraps"] % 1, v, wear.getpixel((x, y)) / 255)
            pixels[x, y] = brighten([c * shade for c in colour], BODY_GAIN)

    image = image.filter(ImageFilter.GaussianBlur(TEXTURE_BLUR))
    # The rim's UVs sit in this strip. Round the drum it shows as a thin dark seam, as on vanilla's drums.
    ImageDraw.Draw(image).rectangle([int(size * RIM_STRIP_U), 0, body_width, size], fill=brighten(LID_RIM, BODY_GAIN))

    lid_centre_x = int(size * (1 + BODY_U) / 2)
    lid_half = int((1 - BODY_U) / 2 * size)
    paint_lid(image, (lid_centre_x, lid_half), style["lid"])
    paint_lid(image, (lid_centre_x, size - lid_half), style["lid"])
    return reduce_detail(image)


def write_glb(path, mesh):
    positions = np.array(mesh.positions, dtype="<f4")
    normals = np.array(mesh.normals, dtype="<f4")
    uvs = np.array(mesh.uvs, dtype="<f4")
    indices = np.array(mesh.indices, dtype="<u2")

    chunks, views, accessors = bytearray(), [], []

    def add(array, kind, component, target, bounds=False):
        offset = len(chunks)
        chunks.extend(array.tobytes())
        chunks.extend(b"\0" * (-len(chunks) % 4))
        views.append({"buffer": 0, "byteOffset": offset, "byteLength": array.nbytes, "target": target})
        accessor = {"bufferView": len(views) - 1, "componentType": component, "count": len(array), "type": kind}
        if bounds:
            accessor["min"] = array.min(axis=0).tolist()
            accessor["max"] = array.max(axis=0).tolist()
        accessors.append(accessor)
        return len(accessors) - 1

    primitive = {
        "attributes": {
            "POSITION": add(positions, "VEC3", 5126, 34962, bounds=True),
            "NORMAL": add(normals, "VEC3", 5126, 34962),
            "TEXCOORD_0": add(uvs, "VEC2", 5126, 34962),
        },
        "indices": add(indices, "SCALAR", 5123, 34963),
    }
    document = {
        "asset": {"version": "2.0", "generator": "FuelBarrel build_model.py"},
        "scene": 0,
        "scenes": [{"nodes": [0]}],
        "nodes": [{"mesh": 0, "name": "Drum"}],
        "meshes": [{"name": "Drum", "primitives": [primitive]}],
        "accessors": accessors,
        "bufferViews": views,
        "buffers": [{"byteLength": len(chunks)}],
    }
    text = json.dumps(document, separators=(",", ":")).encode("utf8")
    text += b" " * (-len(text) % 4)
    total = 12 + 8 + len(text) + 8 + len(chunks)
    with open(path, "wb") as out:
        out.write(struct.pack("<4sII", b"glTF", 2, total))
        out.write(struct.pack("<I4s", len(text), b"JSON") + text)
        out.write(struct.pack("<I4s", len(chunks), b"BIN\0") + bytes(chunks))


def main():
    media = Path(__file__).resolve().parent.parent / "42" / "media"
    (media / "Models_X").mkdir(parents=True, exist_ok=True)
    (media / "textures").mkdir(parents=True, exist_ok=True)
    for style in STYLES:
        write_glb(media / "Models_X" / f"{style['name']}.glb", build_mesh(style))
        paint_texture(style).save(media / "textures" / f"{style['name']}Model.png")
    print(f"wrote models and textures to {media}")


if __name__ == "__main__":
    main()
