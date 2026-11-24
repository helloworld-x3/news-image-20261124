#!/usr/bin/env python3
"""Compose the news-image-20261124 entry.

Four generated illustrations plus real typeset headlines are laid out as one
1024x1024 newspaper-style image: a dark header naming the day, a 2x2 grid of
stories, and a small source line at the bottom.

Deterministic: fixed layout, fixed fonts, no timestamps, no randomness.
Reads the panel images from <repo>/../panels/ and writes entry.png
(JPEG bytes under the name entry.png) into the repository root.
"""

import os

from PIL import Image, ImageDraw, ImageFont, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
PANELS = os.path.join(os.path.dirname(REPO), "panels")

W = H = 1024
BG = (247, 245, 239)          # off-white paper
NAVY = (20, 33, 61)           # header band
GOLD = (232, 196, 104)        # subtitle accent
INK = (24, 24, 24)            # headline ink
SUB = (80, 80, 80)            # subhead grey
FOOT = (130, 130, 130)        # footer grey
WHITE = (255, 255, 255)
BORDER = (210, 208, 200)

HEADER_H = 150
FOOTER_H = 40
MARGIN = 16
GAP = 16

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

# (panel file, headline, subhead) in reading order: top-left, top-right,
# bottom-left, bottom-right.
STORIES = [
    ("media-generation-panel-nvidia-0-7aa6aeff-ad20-4e4d-886b-b76b3a783921.webp",
     "HUANG RETURNS TO NVIDIA",
     "Shares jump 31% as CEO reinstated"),
    ("media-generation-panel-nato-0-a047da05-e33e-4d82-885e-14e3314e9546.webp",
     "NATO SENDS AWACS TO POLAND",
     "After Russian missiles land"),
    ("media-generation-panel-warship-0-977f9044-794e-43db-90c9-6012d39f0b8d.webp",
     "UKRAINE SINKS RUSSIAN WARSHIP",
     "In Libya's Benghazi port"),
    ("media-generation-panel-climate-0-6bc98100-2e7a-4e32-8cc7-768cf51cd535.webp",
     "CLIMATE TALKS COLLAPSE",
     "COP ends without a deal"),
]


def wrap(text, font, max_width, draw):
    """Split text into lines that fit max_width, word by word."""
    words = text.split()
    lines = []
    current = ""
    for word in words:
        trial = word if not current else current + " " + word
        if draw.textlength(trial, font=font) <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def main():
    canvas = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(canvas)

    title_font = ImageFont.truetype(FONT_BOLD, 56)
    subtitle_font = ImageFont.truetype(FONT_BOLD, 25)
    headline_font = ImageFont.truetype(FONT_BOLD, 27)
    subhead_font = ImageFont.truetype(FONT_REG, 22)
    footer_font = ImageFont.truetype(FONT_REG, 19)

    # Header band: the day it sums up, and what the image is.
    draw.rectangle([0, 0, W, HEADER_H], fill=NAVY)
    draw.text((W // 2, 52), "TUESDAY 24 NOVEMBER 2026",
              font=title_font, fill=WHITE, anchor="mm")
    draw.text((W // 2, 112), "T H E   W O R L D   I N   O N E   I M A G E",
              font=subtitle_font, fill=GOLD, anchor="mm")

    # 2x2 grid of stories.
    grid_top = HEADER_H
    grid_bottom = H - FOOTER_H
    cell_w = (W - 2 * MARGIN - GAP) // 2
    cell_h = (grid_bottom - grid_top - GAP) // 2
    img_h = 296
    cap_h = cell_h - img_h
    text_pad = 18

    for i, (panel, headline, subhead) in enumerate(STORIES):
        row, col = divmod(i, 2)
        x0 = MARGIN + col * (cell_w + GAP)
        y0 = grid_top + row * (cell_h + GAP)

        img = Image.open(os.path.join(PANELS, panel)).convert("RGB")
        img = ImageOps.fit(img, (cell_w, img_h), Image.LANCZOS)
        canvas.paste(img, (x0, y0))

        # Caption bar under the picture.
        cap_y = y0 + img_h
        draw.rectangle([x0, cap_y, x0 + cell_w, cap_y + cap_h], fill=WHITE)
        draw.rectangle([x0, y0, x0 + cell_w, cap_y + cap_h],
                       outline=BORDER, width=1)

        lines = wrap(headline, headline_font, cell_w - 2 * text_pad, draw)
        line_h = 33
        # Vertically centre the whole text block inside the caption bar so
        # one-line headlines do not leave a dead gap at the bottom.
        block_h = len(lines) * line_h + 4 + 28
        text_top = cap_y + (cap_h - block_h) // 2
        for j, line in enumerate(lines):
            draw.text((x0 + text_pad, text_top + j * line_h), line,
                      font=headline_font, fill=INK)
        sub_y = text_top + len(lines) * line_h + 4
        draw.text((x0 + text_pad, sub_y), subhead,
                  font=subhead_font, fill=SUB)

    # Footer: where the facts came from.
    draw.text((W // 2, H - FOOTER_H // 2), "Sources: Reuters, Times of India",
              font=footer_font, fill=FOOT, anchor="mm")

    out = os.path.join(REPO, "entry.png")
    canvas.save(out, format="JPEG", quality=87)
    size = os.path.getsize(out)
    print(f"wrote {out}: {W}x{H}, {size} bytes")
    assert size <= 1048576, "entry.png over the 1 MiB limit"
    assert W <= 1024 and H <= 1024, "entry.png over the 1024x1024 limit"


if __name__ == "__main__":
    main()
