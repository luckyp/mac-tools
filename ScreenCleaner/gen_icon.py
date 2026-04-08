#!/usr/bin/env python3
"""Generate ScreenCleaner app icon: 1024x1024 PNG. Modern, light macOS style."""

from PIL import Image, ImageDraw
import math

SIZE = 1024
img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))

# ── Background: light blue-to-white diagonal gradient ────────────────────────
RADIUS = 180

def rounded_rect_mask(size, radius):
    mask = Image.new("L", (size, size), 0)
    d = ImageDraw.Draw(mask)
    d.rounded_rectangle([0, 0, size - 1, size - 1], radius=radius, fill=255)
    return mask

# Diagonal gradient: top-left cornflower blue → bottom-right near-white
BG_TL = (180, 210, 255)   # light sky blue
BG_BR = (235, 245, 255)   # almost white with blue tint

bg_layer = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 255))
bg_pixels = bg_layer.load()
for y in range(SIZE):
    for x in range(SIZE):
        t = (x + y) / (2 * SIZE)  # 0..1 diagonal
        r = int(BG_TL[0] * (1 - t) + BG_BR[0] * t)
        g = int(BG_TL[1] * (1 - t) + BG_BR[1] * t)
        b = int(BG_TL[2] * (1 - t) + BG_BR[2] * t)
        bg_pixels[x, y] = (r, g, b, 255)

bg_mask = rounded_rect_mask(SIZE, RADIUS)
img.paste(bg_layer, (0, 0), bg_mask)

draw = ImageDraw.Draw(img)

# ── Monitor outline ───────────────────────────────────────────────────────────
MON_L, MON_T, MON_R, MON_B = 155, 185, 869, 660
MON_RADIUS = 28
BORDER_W = 20

# Bezel: clean dark outline color (deep navy-gray)
BEZEL_FILL  = (55, 65, 90, 255)
SCREEN_COLOR = (14, 16, 22, 255)   # near-black screen

# Outer bezel body
draw.rounded_rectangle(
    [MON_L, MON_T, MON_R, MON_B],
    radius=MON_RADIUS,
    fill=BEZEL_FILL,
)
# Inner screen area
INNER_RADIUS = max(MON_RADIUS - BORDER_W // 2, 8)
draw.rounded_rectangle(
    [MON_L + BORDER_W, MON_T + BORDER_W, MON_R - BORDER_W, MON_B - BORDER_W],
    radius=INNER_RADIUS,
    fill=SCREEN_COLOR,
)

# Neck / stand stem
STEM_W = 58
STEM_L = SIZE // 2 - STEM_W // 2
STEM_T = MON_B
STEM_B = STEM_T + 76
draw.rectangle([STEM_L, STEM_T, STEM_L + STEM_W, STEM_B], fill=BEZEL_FILL)

# Base
BASE_W = 230
BASE_H = 26
BASE_L = SIZE // 2 - BASE_W // 2
BASE_T = STEM_B
draw.rounded_rectangle(
    [BASE_L, BASE_T, BASE_L + BASE_W, BASE_T + BASE_H],
    radius=12,
    fill=BEZEL_FILL,
)

# ── Cleaning wipe streaks on the screen (bright white / light-blue) ───────────
SCREEN_L = MON_L + BORDER_W + 4
SCREEN_T = MON_T + BORDER_W + 4
SCREEN_R = MON_R - BORDER_W - 4
SCREEN_B = MON_B - BORDER_W - 4

screen_layer = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
sd = ImageDraw.Draw(screen_layer)

def draw_arc_streak(d, cx, cy, rx, ry, alpha, color_base, width_base=35):
    """Draw a clean wipe arc — pure white, single pass."""
    r, g, b = color_base
    d.arc(
        [cx - rx, cy - ry, cx + rx, cy + ry],
        start=205, end=345,
        fill=(r, g, b, alpha),
        width=width_base,
    )

# Two clean wipe arcs — pure white, well-separated
arc_specs = [
    # (cx,          cy,           rx,  ry,  alpha, color)
    (SIZE // 2 - 60, SIZE // 2 - 60, 270, 190, 200, (255, 255, 255)),   # upper arc
    (SIZE // 2 + 30, SIZE // 2 + 40, 230, 160, 185, (255, 255, 255)),   # lower arc
]
for (cx, cy, rx, ry, alpha, col) in arc_specs:
    draw_arc_streak(sd, cx, cy, rx, ry, alpha, col)

# Mask the screen overlay to the screen rect
screen_mask = Image.new("L", (SIZE, SIZE), 0)
ImageDraw.Draw(screen_mask).rounded_rectangle(
    [SCREEN_L - 4, SCREEN_T - 4, SCREEN_R + 4, SCREEN_B + 4],
    radius=INNER_RADIUS,
    fill=255,
)

import numpy as np
screen_arr = np.array(screen_layer)
mask_arr   = np.array(screen_mask)
screen_arr[..., 3] = np.minimum(screen_arr[..., 3], mask_arr)
screen_layer = Image.fromarray(screen_arr)

img = Image.alpha_composite(img, screen_layer)
draw = ImageDraw.Draw(img)

# ── Microfiber cloth in bottom-right corner ───────────────────────────────────
CLOTH_CX = SCREEN_R - 105
CLOTH_CY = SCREEN_B - 90
CLOTH_W, CLOTH_H = 116, 84
CLOTH_RADIUS = 16

# Vivid cyan-blue cloth
CLOTH_COLOR  = (60, 160, 240, 230)
CLOTH_HIGHLIGHT = (130, 200, 255, 180)
CLOTH_SHADOW = (30, 100, 180, 120)

# Shadow
draw.rounded_rectangle(
    [CLOTH_CX - CLOTH_W // 2 + 6, CLOTH_CY - CLOTH_H // 2 + 7,
     CLOTH_CX + CLOTH_W // 2 + 6, CLOTH_CY + CLOTH_H // 2 + 7],
    radius=CLOTH_RADIUS,
    fill=CLOTH_SHADOW,
)
# Cloth body
draw.rounded_rectangle(
    [CLOTH_CX - CLOTH_W // 2, CLOTH_CY - CLOTH_H // 2,
     CLOTH_CX + CLOTH_W // 2, CLOTH_CY + CLOTH_H // 2],
    radius=CLOTH_RADIUS,
    fill=CLOTH_COLOR,
)
# Top-left highlight stripe
draw.rounded_rectangle(
    [CLOTH_CX - CLOTH_W // 2 + 6, CLOTH_CY - CLOTH_H // 2 + 6,
     CLOTH_CX + CLOTH_W // 2 - 30, CLOTH_CY - CLOTH_H // 2 + 22],
    radius=6,
    fill=CLOTH_HIGHLIGHT,
)
# Waffle texture lines — lighter blue
GRID_COLOR = (130, 200, 255, 160)
step = 14
for gx in range(CLOTH_CX - CLOTH_W // 2 + step, CLOTH_CX + CLOTH_W // 2, step):
    draw.line(
        [(gx, CLOTH_CY - CLOTH_H // 2 + 8), (gx, CLOTH_CY + CLOTH_H // 2 - 8)],
        fill=GRID_COLOR, width=2,
    )
for gy in range(CLOTH_CY - CLOTH_H // 2 + step, CLOTH_CY + CLOTH_H // 2, step):
    draw.line(
        [(CLOTH_CX - CLOTH_W // 2 + 8, gy), (CLOTH_CX + CLOTH_W // 2 - 8, gy)],
        fill=GRID_COLOR, width=2,
    )

# ── Subtle blue glow around monitor bezel ────────────────────────────────────
glow_layer = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
gd = ImageDraw.Draw(glow_layer)
for g in range(14, 0, -1):
    a = int(22 * (1 - g / 14))
    expand = g * 3
    gd.rounded_rectangle(
        [MON_L - expand, MON_T - expand, MON_R + expand, MON_B + expand],
        radius=MON_RADIUS + expand,
        outline=(80, 160, 255, a),
        width=3,
    )
img = Image.alpha_composite(img, glow_layer)

# ── Apply rounded-rect app-icon shape mask (final) ───────────────────────────
final_mask = rounded_rect_mask(SIZE, RADIUS)
img.putalpha(final_mask)

out_path = "/Users/yanpeng/ai/mac-tools/ScreenCleaner/icon.png"
img.save(out_path, "PNG")
print(f"Icon saved to {out_path}")
