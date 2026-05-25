"""
Baked with Love — Business Card Builder
=======================================
Avery Easy-to-Use Business Cards — Template 28371
  • 3.5" × 2" standard business cards
  • 10 per sheet (2 columns × 5 rows)
  • US Letter (8.5" × 11")

Output: baked_with_love_business_cards.pdf  (3 pages, one per palette)

Run:
    pip install reportlab --break-system-packages
    python3 baked_with_love_business_card_builder.py

Print at 100% scale, no fit-to-page, on Avery 28371 card stock.
"""

from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.units import inch
from reportlab.pdfbase.pdfmetrics import stringWidth

# ---------------------------------------------------------------------------
# Page & card geometry — Avery 28371
# ---------------------------------------------------------------------------
PAGE_W      = 8.5 * inch
PAGE_H      = 11.0 * inch
CARD_W      = 3.5 * inch
CARD_H      = 2.0 * inch
COLS        = 2
ROWS        = 5
LEFT_MARGIN = 0.75 * inch
TOP_MARGIN  = 0.5 * inch
COL_GAP     = 0.0
ROW_GAP     = 0.0

OUTPUT = "baked_with_love_business_cards.pdf"

# ---------------------------------------------------------------------------
# Color palettes — mirror the label / menu palette system
# ---------------------------------------------------------------------------
PALETTES = [
    {
        "name":    "Website Palette",
        "bg":      HexColor("#FAF6F0"),
        "surface": HexColor("#F2E4D4"),
        "accent":  HexColor("#C9907A"),
        "deep":    HexColor("#9E5E4A"),
        "body":    HexColor("#5C3D2E"),
        "muted":   HexColor("#8C7060"),
    },
    {
        "name":    "Warm Rose",
        "bg":      HexColor("#fff7f5"),
        "surface": HexColor("#fbe7e2"),
        "accent":  HexColor("#c05848"),
        "deep":    HexColor("#c05848"),
        "body":    HexColor("#4a2a22"),
        "muted":   HexColor("#a07068"),
    },
    {
        "name":    "Terracotta",
        "bg":      HexColor("#fdf0e6"),
        "surface": HexColor("#f7dcc4"),
        "accent":  HexColor("#c05830"),
        "deep":    HexColor("#c05830"),
        "body":    HexColor("#4a2a18"),
        "muted":   HexColor("#a07058"),
    },
]

# ---------------------------------------------------------------------------
# Contact info
# ---------------------------------------------------------------------------
WEBSITE  = "bakedwithloverockwall.com"
EMAIL    = "elizabethnerbun@gmail.com"
PHONE    = "(262) 366-4414"
LOCATION = "Rockwall, TX"
TAGLINE  = "home-baked  ·  gluten-free & dairy-free options  ·  made with love"


# ---------------------------------------------------------------------------
# Letter-spacing helpers (same pattern as menu / label builders)
# ---------------------------------------------------------------------------
def letterspaced_width(text, font, size, spacing):
    if not text:
        return 0
    return sum(stringWidth(ch, font, size) for ch in text) + spacing * (len(text) - 1)


def draw_letterspaced(c, text, x, y, font, size, spacing, color):
    c.setFont(font, size)
    c.setFillColor(color)
    cur = x
    for ch in text:
        c.drawString(cur, y, ch)
        cur += stringWidth(ch, font, size) + spacing


def draw_letterspaced_centered(c, text, cx, y, font, size, spacing, color):
    w = letterspaced_width(text, font, size, spacing)
    draw_letterspaced(c, text, cx - w / 2.0, y, font, size, spacing, color)
    return w


# ---------------------------------------------------------------------------
# Heart path — same SVG as label / menu builders
# ---------------------------------------------------------------------------
def draw_heart(c, cx, cy, scale, fill_color):
    p = c.beginPath()

    def pt(x, y):
        return (cx + x * scale, cy - y * scale)

    p.moveTo(*pt(0, -14))
    p.curveTo(*pt(0, -20), *pt(-12, -23), *pt(-15, -15))
    p.curveTo(*pt(-18, -7), *pt(-15, 0), *pt(0, 14))
    p.curveTo(*pt(15, 0), *pt(18, -7), *pt(15, -15))
    p.curveTo(*pt(12, -23), *pt(0, -20), *pt(0, -14))
    p.close()
    c.setFillColor(fill_color)
    c.setStrokeColor(fill_color)
    c.drawPath(p, stroke=0, fill=1)


# ---------------------------------------------------------------------------
# Draw one 3.5" × 2" business card
# (ox, oy) = bottom-left corner in page coordinates
# ---------------------------------------------------------------------------
def draw_card(c, ox, oy, palette):
    p   = palette
    cx  = ox + CARD_W / 2.0   # horizontal center of card
    font = "Helvetica"

    # ── Background ──────────────────────────────────────────────────────────
    c.setFillColor(p["bg"])
    c.rect(ox, oy, CARD_W, CARD_H, stroke=0, fill=1)

    # ── Decorative inset border ──────────────────────────────────────────────
    inset = 6
    c.setStrokeColor(p["accent"])
    c.setLineWidth(0.4)
    c.rect(ox + inset, oy + inset,
           CARD_W - 2 * inset, CARD_H - 2 * inset, stroke=1, fill=0)

    # ── Corner hearts (sit at the four corners of the inset border) ──────────
    ho = 16    # offset from card edge to heart center
    hs = 0.23  # heart scale
    for dx, dy in [(ho, ho), (CARD_W - ho, ho),
                   (ho, CARD_H - ho), (CARD_W - ho, CARD_H - ho)]:
        draw_heart(c, ox + dx, oy + dy, hs, p["accent"])

    # ── Logo: BAKED WITH L[heart]VE ─────────────────────────────────────────
    title_size    = 17
    title_spacing = 1.8

    left_part  = "BAKED WITH L"
    right_part = "VE"
    lw         = letterspaced_width(left_part,  font, title_size, title_spacing)
    rw         = letterspaced_width(right_part, font, title_size, title_spacing)
    heart_slot = stringWidth("O", font, title_size) + title_spacing * 1.2
    logo_x     = cx - (lw + heart_slot + rw) / 2.0
    logo_y     = oy + CARD_H - 32.84   # baseline, shifted down ~1mm from original

    draw_letterspaced(c, left_part, logo_x, logo_y,
                      font, title_size, title_spacing, p["body"])

    cap_h    = title_size * 0.70
    heart_cx = logo_x + lw + heart_slot / 2.0 - 2
    heart_cy = logo_y + cap_h / 2.0 - 1
    draw_heart(c, heart_cx, heart_cy, title_size / 32.0 * 0.90, p["accent"])

    draw_letterspaced(c, right_part, logo_x + lw + heart_slot, logo_y,
                      font, title_size, title_spacing, p["body"])

    # ── Subtitle: HOME BAKERY ────────────────────────────────────────────────
    sub_y = logo_y - 7 - 5
    draw_letterspaced_centered(c, "HOME BAKERY", cx, sub_y,
                               font, 7, 2.5, p["deep"])

    # ── Ornamental divider: line — heart — line ──────────────────────────────
    div_y = sub_y - 13
    seg   = 30
    gap   = 8
    c.setStrokeColor(p["accent"])
    c.setLineWidth(0.45)
    c.line(cx - seg - gap, div_y, cx - gap, div_y)
    c.line(cx + gap, div_y, cx + seg + gap, div_y)
    draw_heart(c, cx, div_y, 0.27, p["accent"])

    # ── Website ──────────────────────────────────────────────────────────────
    web_y = div_y - 16
    draw_letterspaced_centered(c, WEBSITE, cx, web_y,
                               font, 7.5, 0.5, p["deep"])

    # ── Email ────────────────────────────────────────────────────────────────
    email_y = web_y - 12
    c.setFont(font, 7)
    c.setFillColor(p["muted"])
    ew = stringWidth(EMAIL, font, 7)
    c.drawString(cx - ew / 2.0, email_y, EMAIL)

    # ── Phone · Location ─────────────────────────────────────────────────────
    pl_y   = email_y - 11
    pl_str = f"{PHONE}  ·  {LOCATION}"
    c.setFont(font, 7)
    c.setFillColor(p["muted"])
    plw = stringWidth(pl_str, font, 7)
    c.drawString(cx - plw / 2.0, pl_y, pl_str)

    # ── Bottom tagline ────────────────────────────────────────────────────────
    tag_y = oy + 15.16
    c.setFont("Helvetica-Oblique", 6)
    c.setFillColor(p["accent"])
    tw = stringWidth(TAGLINE, "Helvetica-Oblique", 6)
    c.drawString(cx - tw / 2.0, tag_y, TAGLINE)


# ---------------------------------------------------------------------------
# Render all 10 card cells on one page
# ---------------------------------------------------------------------------
def draw_page(c, palette):
    for row in range(ROWS):
        for col in range(COLS):
            ox = LEFT_MARGIN + col * (CARD_W + COL_GAP)
            oy = PAGE_H - TOP_MARGIN - (row + 1) * (CARD_H + ROW_GAP)
            draw_card(c, ox, oy, palette)
    c.showPage()


# ---------------------------------------------------------------------------
# Build the PDF
# ---------------------------------------------------------------------------
def build():
    cv = canvas.Canvas(OUTPUT, pagesize=(PAGE_W, PAGE_H))
    cv.setTitle("Baked with Love — Business Cards (Avery 28371)")
    cv.setAuthor("Baked with Love")

    for palette in PALETTES:
        draw_page(cv, palette)

    cv.save()
    print(f"Saved: {OUTPUT}")
    print("Pages:")
    for i, palette in enumerate(PALETTES, 1):
        print(f"  {i}. {palette['name']}")


if __name__ == "__main__":
    build()
