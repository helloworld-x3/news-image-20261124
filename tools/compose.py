#!/usr/bin/env python3
"""Compose the news-image-20261124 entry (v2.1).

Real photographs from Wikimedia Commons, laid out as a professional
daily-news card in the manner of a Reuters daily briefing / FT front:
warm-white paper, one restrained oxblood-red accent, serif headlines,
tracked small-caps kickers, generous whitespace, hairline rules, and a
one-line photo caption under every picture. No AI imagery, no gloss,
no template gradients.

Masthead (v2.1): a real newspaper nameplate, NOT a solid colour band.
The nameplate is large black serif set directly on the paper, with a
thin black rule above and below it and a single hairline oxblood-red
rule as the only red accent in the header. The red band of v2 looked
like an AI template; this is the FT / NYT nameplate treatment.

Layout (1024x1024):
  top row    date left, red REC dot right
  masthead   "THE WORLD TODAY" in large black serif, hairline rules
  grey box   one-line standfirst naming all four stories
  lead card  Huang portrait left, kicker + serif headline + subhead right
  three cards in a row, each: photo, kicker, headline, subhead, caption
  footer     photo credit left, news sources right

Deterministic: fixed layout, fixed fonts, no timestamps, no randomness.
Reads photos from <repo>/photos/ and writes entry.png (JPEG bytes under
the name entry.png) into the repository root.
"""

import os

from PIL import Image, ImageDraw, ImageFont, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
PHOTOS = os.path.join(REPO, "photos")

W = H = 1024
M = 36                      # side margin
CW = W - 2 * M              # content width: 952

PAPER = (253, 252, 248)     # warm white
INK = (25, 25, 25)          # headline ink
BODY = (58, 56, 52)         # subhead ink
GREY = (110, 106, 99)       # captions / footer
RED = (158, 27, 50)         # single accent: oxblood red
HAIR = (217, 212, 199)      # hairline rules
BOX = (241, 238, 230)       # standfirst box
WHITE = (255, 255, 255)

SERIF = "/usr/share/fonts/truetype/noto/NotoSerif-Bold.ttf"
SERIF_IT = "/usr/share/fonts/truetype/noto/NotoSerif-Italic.ttf"
SANS = "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf"
SANS_B = "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf"


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


def tracked_width(draw, text, font, tracking):
    """Width of text drawn with extra tracking between characters."""
    return sum(draw.textlength(c, font=font) for c in text) + tracking * max(
        len(text) - 1, 0)


def draw_tracked(draw, x, y, text, font, fill, tracking):
    """Draw text with letter tracking; returns the x just past the text."""
    cx = x
    for ch in text:
        draw.text((cx, y), ch, font=font, fill=fill)
        cx += draw.textlength(ch, font=font) + tracking
    return cx - tracking if text else cx


def crop_to(img, tw, th, y_bias=0.5):
    """Centre-crop to the target aspect; y_bias 0 = top, 1 = bottom."""
    sw, sh = img.size
    target = tw / th
    if sw / sh > target:  # too wide: trim sides
        nw = int(sh * target)
        x0 = (sw - nw) // 2
        return img.crop((x0, 0, x0 + nw, sh)).resize((tw, th), Image.LANCZOS)
    nw_h = int(sw / target)
    y0 = int((sh - nw_h) * y_bias)
    return img.crop((0, y0, sw, y0 + nw_h)).resize((tw, th), Image.LANCZOS)


def main():
    canvas = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(canvas)

    date_font = ImageFont.truetype(SANS_B, 19)
    rec_font = ImageFont.truetype(SANS_B, 19)
    masthead_font = ImageFont.truetype(SERIF, 66)
    stand_font = ImageFont.truetype(SERIF_IT, 20)
    kick_font = ImageFont.truetype(SANS_B, 16)
    kick_sm_font = ImageFont.truetype(SANS_B, 14)
    lead_head_font = ImageFont.truetype(SERIF, 46)
    lead_sub_font = ImageFont.truetype(SANS, 21)
    head_font = ImageFont.truetype(SERIF, 25)
    sub_font = ImageFont.truetype(SANS, 17)
    cap_font = ImageFont.truetype(SERIF_IT, 13)
    foot_font = ImageFont.truetype(SANS, 13)

    # --- Top row: date left, REC right (Weekly News header) ---
    draw_tracked(draw, M, 32, "TUESDAY, 24 NOVEMBER 2026", date_font, INK, 2)
    rec_w = draw.textlength("REC", font=rec_font)
    rec_x = W - M - int(rec_w)
    draw.ellipse([rec_x - 20, 36, rec_x - 9, 47], fill=RED)
    draw.text((rec_x, 32), "REC", font=rec_font, fill=RED)

    # --- Masthead: real newspaper nameplate, no solid colour block ---
    # thin black rule above the nameplate (below the date row)
    draw.rectangle([M, 62, W - M, 64], fill=INK)
    # nameplate in large black serif, centred on the paper
    mast = "THE WORLD TODAY"
    mw = draw.textlength(mast, font=masthead_font)
    draw.text(((W - mw) / 2, 104), mast, font=masthead_font, fill=INK,
              anchor="lm")
    # thin black rule below the nameplate, then a hairline oxblood-red
    # rule as the only red accent in the header
    draw.rectangle([M, 132, W - M, 134], fill=INK)
    draw.rectangle([M, 139, W - M, 141], fill=RED)

    # --- Standfirst box: all four stories in one line ---
    draw.rectangle([M, 152, W - M, 200], fill=BOX)
    stand = ("Nvidia's chief returns  \u00b7  NATO moves east  \u00b7  "
             "A warship sinks  \u00b7  Climate talks fail")
    sw = draw.textlength(stand, font=stand_font)
    draw.text((W / 2, 176), stand, font=stand_font, fill=BODY,
              anchor="mm")

    # --- Lead card: Huang portrait + headline ---
    lead_y = 214
    lead_ph_w, lead_ph_h = 400, 330
    huang = Image.open(os.path.join(PHOTOS, "huang-stanford.jpg")).convert("RGB")
    # Portrait original (3888x5184); keep the face in the upper-middle.
    huang_c = crop_to(huang, lead_ph_w, lead_ph_h, y_bias=0.06)
    canvas.paste(huang_c, (M, lead_y))

    tx = M + lead_ph_w + 28
    tw = W - M - tx
    draw.rectangle([tx, lead_y + 8, tx + 56, lead_y + 11], fill=RED)
    draw_tracked(draw, tx, lead_y + 24, "TECHNOLOGY", kick_font, RED, 2)
    hy = lead_y + 54
    for i, line in enumerate(["HUANG RETURNS", "TO NVIDIA"]):
        draw.text((tx, hy + i * 54), line, font=lead_head_font, fill=INK)
    sub_lines = wrap("Shares jump 31% as the board reinstates its chief "
                     "executive", lead_sub_font, tw, draw)
    sy = hy + 2 * 54 + 14
    for i, line in enumerate(sub_lines):
        draw.text((tx, sy + i * 28), line, font=lead_sub_font, fill=BODY)
    # Deck: one verified sentence, set under a short grey rule so the
    # lead column fills the photo height instead of ending in blank space.
    deck_y = sy + len(sub_lines) * 28 + 18
    draw.rectangle([tx, deck_y, tx + 56, deck_y + 3], fill=HAIR)
    deck_lines = wrap("The board restored Huang as chief executive on "
                      "23 November; shares closed up 31.48%.",
                      lead_sub_font, tw, draw)
    dy = deck_y + 3 + 16
    for i, line in enumerate(deck_lines):
        draw.text((tx, dy + i * 28), line, font=lead_sub_font, fill=BODY)
    cap_lines = wrap("Jensen Huang speaking at Stanford University, "
                     "April 2026.", cap_font, lead_ph_w, draw)
    cy = lead_y + lead_ph_h + 10
    for i, line in enumerate(cap_lines):
        draw.text((M, cy + i * 17), line, font=cap_font, fill=GREY)

    # --- Hairline rule, then three cards in a row ---
    draw.rectangle([M, 592, W - M, 593], fill=HAIR)

    cards = [
        ("awacs.jpg", "SECURITY", "NATO SENDS AWACS TO POLAND",
         "After three Russian missiles land",
         "A NATO E-3A Sentry in flight over Paine Field, USA, 2015."),
        ("merkury.jpg", "UKRAINE WAR", "UKRAINE SINKS RUSSIAN WARSHIP",
         "Seven sea drones hit Benghazi port",
         "The corvette Merkury during sea trials, 2022."),
        ("cop31.jpg", "CLIMATE", "CLIMATE TALKS COLLAPSE",
         "COP31 ends in Antalya with no deal",
         "COP31 President Murat Kurum on screen at the closing plenary, "
         "Antalya, 20 Nov 2026."),
    ]
    card_w = (CW - 2 * 20) // 3   # 304
    card_ph_h = 178
    card_y = 608
    for i, (photo, kicker, headline, subhead, caption) in enumerate(cards):
        x0 = M + i * (card_w + 20)
        img = Image.open(os.path.join(PHOTOS, photo)).convert("RGB")
        canvas.paste(crop_to(img, card_w, card_ph_h), (x0, card_y))
        ky = card_y + card_ph_h + 14
        draw_tracked(draw, x0, ky, kicker, kick_sm_font, RED, 2)
        hl = wrap(headline, head_font, card_w, draw)
        hy2 = ky + 26
        for j, line in enumerate(hl):
            draw.text((x0, hy2 + j * 30), line, font=head_font, fill=INK)
        sl = wrap(subhead, sub_font, card_w, draw)
        sy2 = hy2 + len(hl) * 30 + 6
        for j, line in enumerate(sl):
            draw.text((x0, sy2 + j * 22), line, font=sub_font, fill=BODY)
        cl = wrap(caption, cap_font, card_w, draw)
        cy2 = 928
        for j, line in enumerate(cl):
            draw.text((x0, cy2 + j * 17), line, font=cap_font, fill=GREY)

    # --- Footer rule + credits ---
    draw.rectangle([M, 966, W - M, 967], fill=HAIR)
    draw.text((M, 978), "Photos: Wikimedia Commons \u2014 full credits in "
              "photos/SOURCES.md", font=foot_font, fill=GREY)
    src = "Compiled from Reuters, CNN and official sources"
    draw.text((W - M - draw.textlength(src, font=foot_font), 978), src,
              font=foot_font, fill=GREY)

    out = os.path.join(REPO, "entry.png")
    canvas.save(out, format="JPEG", quality=88)
    size = os.path.getsize(out)
    print(f"wrote {out}: {W}x{H}, {size} bytes")
    assert size <= 1048576, "entry.png over the 1 MiB limit"
    assert W <= 1024 and H <= 1024, "entry.png over the 1024x1024 limit"


if __name__ == "__main__":
    main()
