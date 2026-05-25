"""
Baked with Love — Table-Stand Menu Builder
==========================================
Generates a 5" x 7" PDF with three different menu-display designs.
Each design uses one of the three color palettes from the address-label
project (Website Palette, Warm Rose, Terracotta) so all branding stays
consistent.

Output: baked_with_love_menu_5x7.pdf  (3 pages, one per design)

Print at 100% scale on 5"x7" cardstock (or print on letter and trim).

Run:
    pip install reportlab --break-system-packages
    python3 baked_with_love_menu_builder.py
"""

from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.units import inch
from reportlab.pdfbase.pdfmetrics import stringWidth

# ---------------------------------------------------------------------------
# Page geometry — 5" x 7" portrait
# ---------------------------------------------------------------------------
PAGE_W = 5.0 * inch
PAGE_H = 7.0 * inch

OUTPUT = "baked_with_love_menu_5x7.pdf"

# ---------------------------------------------------------------------------
# Color palettes (mirror the label builder)
# ---------------------------------------------------------------------------
PALETTES = {
    "website": {
        "name":     "Website Palette",
        "bg":       HexColor("#FAF6F0"),
        "surface":  HexColor("#F2E4D4"),
        "accent":   HexColor("#C9907A"),
        "deep":     HexColor("#9E5E4A"),
        "body":     HexColor("#5C3D2E"),
        "muted":    HexColor("#8C7060"),
    },
    "warm_rose": {
        "name":     "Warm Rose",
        "bg":       HexColor("#fff7f5"),
        "surface":  HexColor("#fbe7e2"),
        "accent":   HexColor("#c05848"),
        "deep":     HexColor("#a84838"),
        "body":     HexColor("#4a2a22"),
        "muted":    HexColor("#a07068"),
    },
    "terracotta": {
        "name":     "Terracotta",
        "bg":       HexColor("#fdf0e6"),
        "surface":  HexColor("#f7dcc4"),
        "accent":   HexColor("#c05830"),
        "deep":     HexColor("#9c4624"),
        "body":     HexColor("#4a2a18"),
        "muted":    HexColor("#a07058"),
    },
}

# ---------------------------------------------------------------------------
# Menu data
# ---------------------------------------------------------------------------
MENU_ITEMS = [
    {
        "name":  "Cookie — Single",
        "desc":  "Gluten-free · choc chip or peanut butter",
        "size":  "1 fresh-baked cookie",
        "price": "$4",
    },
    {
        "name":  "Cookie — Bag of 2 Jumbo",
        "desc":  "Gluten-free · your choice of flavor",
        "size":  "2 jumbo cookies",
        "price": "$10",
    },
    {
        "name":  "Cookie — Box of 4 Jumbo",
        "desc":  "Gluten-free · gift-ready",
        "size":  "4 jumbo cookies",
        "price": "$20",
    },
    {
        "name":  "Gluten Free Bread",
        "desc":  "Wholesome loaves baked fresh",
        "size":  "Full loaf",
        "price": "$12",
    },
    {
        "name":  "Multi-Veggie Protein Waffles",
        "desc":  "To order or frozen  ·  +$2 w/ extra protein",
        "size":  "Large round waffle",
        "price": "$5",
    },
]


# ---------------------------------------------------------------------------
# Helper — draw text with manual letter-spacing (ReportLab Canvas has no
# built-in setCharSpace, so we draw each char and advance the cursor).
# Returns the total width drawn.
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
    return cur - x - (spacing if text else 0)


def draw_letterspaced_centered(c, text, cx, y, font, size, spacing, color):
    w = letterspaced_width(text, font, size, spacing)
    draw_letterspaced(c, text, cx - w / 2.0, y, font, size, spacing, color)
    return w


# ---------------------------------------------------------------------------
# Heart SVG path used in the logo (replaces the 'O' in LOVE)
# ---------------------------------------------------------------------------
def draw_heart(c, cx, cy, scale, fill_color):
    """
    Original SVG path:
      M0,-14 C0,-20 -12,-23 -15,-15 C-18,-7 -15,0 0,14
      C15,0 18,-7 15,-15 C12,-23 0,-20 0,-14 Z
    SVG y is flipped relative to PDF, so we invert y.
    """
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
# Logo block — "BAKED WITH L[heart]VE" + "HOME BAKERY"
# ---------------------------------------------------------------------------
def draw_logo(c, cx, cy_top, palette,
              title_size=22, sub_size=8, title_spacing=2.2,
              sub_size_default=8, sub_spacing=3.0,
              draw_subtitle=True):
    """
    Draws the wordmark centered horizontally on cx.
    cy_top = baseline-y of the main wordmark text.
    Returns the y-coordinate of the bottom of the logo block.
    """
    body = palette["body"]
    accent = palette["accent"]
    deep = palette["deep"]

    left = "BAKED WITH L"
    right = "VE"
    font = "Helvetica"

    left_w = letterspaced_width(left, font, title_size, title_spacing)
    right_w = letterspaced_width(right, font, title_size, title_spacing)
    # Heart slot ~ width of capital "O" plus a touch of spacing
    heart_slot = stringWidth("O", font, title_size) + title_spacing * 1.2
    total_w = left_w + heart_slot + right_w
    start_x = cx - total_w / 2.0

    # Draw "BAKED WITH L"
    draw_letterspaced(c, left, start_x, cy_top, font, title_size,
                      title_spacing, body)

    # Heart in the O slot
    cap_height = title_size * 0.70
    heart_cx = start_x + left_w + heart_slot / 2.0
    heart_cy = cy_top + cap_height / 2.0
    heart_scale = title_size / 32.0
    draw_heart(c, heart_cx, heart_cy, heart_scale, accent)

    # "VE"
    draw_letterspaced(c, right, start_x + left_w + heart_slot, cy_top,
                      font, title_size, title_spacing, body)

    # Subtitle "HOME BAKERY"
    if draw_subtitle:
        sub_text = "HOME BAKERY"
        sub_y = cy_top - sub_size - 6
        draw_letterspaced_centered(c, sub_text, cx, sub_y,
                                   font, sub_size, sub_spacing, deep)
        return sub_y - 4
    return cy_top - 4


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def fill_background(c, palette):
    c.setFillColor(palette["bg"])
    c.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)


def draw_divider_line(c, cx, cy, width, color, weight=0.6):
    c.setStrokeColor(color)
    c.setLineWidth(weight)
    c.line(cx - width / 2.0, cy, cx + width / 2.0, cy)


def draw_dot_leader(c, x_start, x_end, y, color,
                    dot_radius=0.6, gap=3.5):
    c.setFillColor(color)
    x = x_start
    while x <= x_end:
        c.circle(x, y, dot_radius, stroke=0, fill=1)
        x += gap


PAYMENT_OPTIONS = [
    ("VENMO", "@Patrick-Nerbun"),
    ("ZELLE", "Elizabeth Nerbun"),
    ("CASH",  "accepted at pickup"),
]


def draw_payment_block(c, palette, cy_top,
                       header_size=6.5, header_spacing=2.6,
                       label_size=8.0, label_spacing=1.2,
                       value_size=9.0, row_gap=14,
                       header_gap=14, divider_width=70):
    """
    Draws a centered "ACCEPTED PAYMENTS" block:
        ──── ACCEPTED PAYMENTS ────
            VENMO   @Patrick-Nerbun
            ZELLE   Elizabeth Nerbun
            CASH    accepted at pickup
    Labels are right-aligned and values left-aligned around a center pivot
    so each row reads cleanly as a column.
    Returns the y of the bottom of the block.
    """
    accent = palette["accent"]
    body   = palette["body"]
    deep   = palette["deep"]

    cx = PAGE_W / 2.0

    # Header line: short divider ── ACCEPTED PAYMENTS ── short divider
    header = "ACCEPTED PAYMENTS"
    header_w = letterspaced_width(header, "Helvetica", header_size, header_spacing)
    side_pad = 8
    seg = (divider_width - header_w) / 2.0 - side_pad
    if seg > 6:
        c.setStrokeColor(accent)
        c.setLineWidth(0.4)
        c.line(cx - header_w / 2.0 - side_pad - seg, cy_top + 2,
               cx - header_w / 2.0 - side_pad,        cy_top + 2)
        c.line(cx + header_w / 2.0 + side_pad,        cy_top + 2,
               cx + header_w / 2.0 + side_pad + seg,  cy_top + 2)
    draw_letterspaced_centered(c, header, cx, cy_top,
                               "Helvetica", header_size, header_spacing, deep)

    # Determine column gap — pivot is the center of the page
    gutter = 14
    # Compute label widths to right-align them
    label_widths = [
        letterspaced_width(label, "Helvetica", label_size, label_spacing)
        for label, _ in PAYMENT_OPTIONS
    ]
    max_label_w = max(label_widths)

    y = cy_top - header_gap
    for (label, value), lw in zip(PAYMENT_OPTIONS, label_widths):
        # Label, right-aligned to (cx - gutter/2)
        label_x_start = cx - gutter / 2.0 - lw
        draw_letterspaced(c, label, label_x_start, y,
                          "Helvetica", label_size, label_spacing, accent)

        # Value, left-aligned at (cx + gutter/2)
        c.setFont("Helvetica-Oblique", value_size)
        c.setFillColor(body)
        c.drawString(cx + gutter / 2.0, y, value)

        y -= row_gap

    return y + (row_gap - 4)  # bottom of block ≈ last row baseline + descender


def draw_footer(c, palette, y, include_email=True):
    muted = palette["muted"]
    line1 = "ELIZABETH NERBUN  ·  ROCKWALL, TX"
    draw_letterspaced_centered(c, line1, PAGE_W / 2.0, y,
                               "Helvetica", 7, 1.4, muted)
    line2 = "262 · 366 · 4414"
    if include_email:
        line2 += "    elizabethnerbun@gmail.com"
    draw_letterspaced_centered(c, line2, PAGE_W / 2.0, y - 11,
                               "Helvetica", 7, 1.0, muted)


# ===========================================================================
# DESIGN 1 — CLASSIC ELEGANT (Website Palette)
# Two-column menu with dotted leaders.
# ===========================================================================
def design_1_classic(c):
    p = PALETTES["website"]
    fill_background(c, p)

    # Top eyebrow
    draw_letterspaced_centered(
        c, "FRESH FROM OUR KITCHEN",
        PAGE_W / 2.0, PAGE_H - 0.55 * inch,
        "Helvetica", 6.5, 2.6, p["accent"],
    )

    # Logo
    logo_bottom = draw_logo(
        c, cx=PAGE_W / 2.0, cy_top=PAGE_H - 0.95 * inch,
        palette=p, title_size=22, title_spacing=2.2,
        sub_size=8, sub_spacing=3.0,
    )

    # Divider
    draw_divider_line(c, PAGE_W / 2.0, logo_bottom - 12,
                      width=44, color=p["accent"], weight=0.7)

    # Section heading
    draw_letterspaced_centered(
        c, "OUR MENU",
        PAGE_W / 2.0, logo_bottom - 38,
        "Helvetica", 16, 1.6, p["body"],
    )

    # Italic flavor line
    c.setFont("Helvetica-Oblique", 9.5)
    c.setFillColor(p["muted"])
    flavor = "all gluten-free · baked fresh"
    fw = stringWidth(flavor, "Helvetica-Oblique", 9.5)
    c.drawString((PAGE_W - fw) / 2.0, logo_bottom - 53, flavor)

    # Menu items
    item_top_y = logo_bottom - 74
    row_height = 44
    margin_x = 0.55 * inch

    for i, item in enumerate(MENU_ITEMS):
        y = item_top_y - i * row_height

        # Item name (left)
        name_caps = item["name"].upper()
        name_w = letterspaced_width(name_caps, "Helvetica", 10, 0.5)
        draw_letterspaced(c, name_caps, margin_x, y,
                          "Helvetica", 10, 0.5, p["body"])

        # Price (right)
        c.setFont("Helvetica", 13)
        c.setFillColor(p["accent"])
        price_w = stringWidth(item["price"], "Helvetica", 13)
        price_x = PAGE_W - margin_x - price_w
        c.drawString(price_x, y, item["price"])

        # Dot leader
        draw_dot_leader(
            c,
            x_start=margin_x + name_w + 6,
            x_end=price_x - 6,
            y=y + 3,
            color=p["accent"],
            dot_radius=0.55,
            gap=3.6,
        )

        # Description
        c.setFont("Helvetica-Oblique", 8)
        c.setFillColor(p["muted"])
        c.drawString(margin_x, y - 12, item["desc"])

    # Payment block
    draw_payment_block(c, p, cy_top=1.62 * inch,
                       divider_width=160, row_gap=13)

    # Bottom note
    c.setFont("Helvetica-Oblique", 8)
    c.setFillColor(p["deep"])
    note = "dairy-free options available on request"
    nw = stringWidth(note, "Helvetica-Oblique", 8)
    c.drawString((PAGE_W - nw) / 2.0, 0.82 * inch, note)

    # Mini divider
    draw_divider_line(c, PAGE_W / 2.0, 0.68 * inch,
                      width=30, color=p["accent"], weight=0.5)

    # Footer
    draw_footer(c, p, y=0.44 * inch)

    c.showPage()


# ===========================================================================
# DESIGN 2 — STACKED HIGHLIGHT (Warm Rose Palette)
# Big prices, soft top band; great visibility on a table stand.
# ===========================================================================
def design_2_stacked(c):
    p = PALETTES["warm_rose"]
    fill_background(c, p)

    # Soft top band
    c.setFillColor(p["surface"])
    c.rect(0, PAGE_H - 1.5 * inch, PAGE_W, 1.5 * inch, stroke=0, fill=1)

    # Logo on top band
    draw_logo(
        c, cx=PAGE_W / 2.0, cy_top=PAGE_H - 0.65 * inch,
        palette=p, title_size=22, title_spacing=2.2,
        sub_size=8, sub_spacing=3.0,
    )

    # Heart row separator
    heart_y = PAGE_H - 1.5 * inch - 18
    for off in (-30, 0, 30):
        draw_heart(c, PAGE_W / 2.0 + off, heart_y, 0.35, p["accent"])

    # Items stacked
    block_top = heart_y - 20
    block_height = 50

    for i, item in enumerate(MENU_ITEMS):
        cy = block_top - i * block_height

        # Price — prominent
        c.setFont("Helvetica-Bold", 18)
        c.setFillColor(p["accent"])
        pw = stringWidth(item["price"], "Helvetica-Bold", 18)
        c.drawString((PAGE_W - pw) / 2.0, cy, item["price"])

        # Item name
        draw_letterspaced_centered(
            c, item["name"].upper(),
            PAGE_W / 2.0, cy - 13,
            "Helvetica", 9.5, 1.1, p["body"],
        )

        # Description
        c.setFont("Helvetica-Oblique", 8)
        c.setFillColor(p["muted"])
        dw = stringWidth(item["desc"], "Helvetica-Oblique", 8)
        c.drawString((PAGE_W - dw) / 2.0, cy - 25, item["desc"])

        # Mini divider
        if i < len(MENU_ITEMS) - 1:
            draw_divider_line(
                c, PAGE_W / 2.0, cy - 37,
                width=24, color=p["accent"], weight=0.5,
            )

    # Payment block — sits between items and footer
    last_cy = block_top - (len(MENU_ITEMS) - 1) * block_height
    draw_payment_block(c, p, cy_top=last_cy - 46,
                       divider_width=170, row_gap=12)

    # Footer
    draw_footer(c, p, y=0.48 * inch)

    c.showPage()


# ===========================================================================
# DESIGN 3 — FRAMED CARD (Terracotta Palette)
# Decorative double border + corner hearts; vintage cafe feel.
# ===========================================================================
def design_3_framed(c):
    p = PALETTES["terracotta"]
    fill_background(c, p)

    # Outer frame
    inset = 0.30 * inch
    c.setStrokeColor(p["accent"])
    c.setLineWidth(1.3)
    c.rect(inset, inset, PAGE_W - 2 * inset, PAGE_H - 2 * inset,
           stroke=1, fill=0)

    inset2 = 0.36 * inch
    c.setLineWidth(0.4)
    c.rect(inset2, inset2, PAGE_W - 2 * inset2, PAGE_H - 2 * inset2,
           stroke=1, fill=0)

    # Corner hearts
    for x, y in [
        (inset2 + 12, PAGE_H - inset2 - 12),
        (PAGE_W - inset2 - 12, PAGE_H - inset2 - 12),
        (inset2 + 12, inset2 + 12),
        (PAGE_W - inset2 - 12, inset2 + 12),
    ]:
        draw_heart(c, x, y, 0.30, p["accent"])

    # Eyebrow
    draw_letterspaced_centered(
        c, "MENU",
        PAGE_W / 2.0, PAGE_H - 0.78 * inch,
        "Helvetica", 6.5, 3.0, p["deep"],
    )

    # Logo
    logo_bottom = draw_logo(
        c, cx=PAGE_W / 2.0, cy_top=PAGE_H - 1.12 * inch,
        palette=p, title_size=20, title_spacing=2.0,
        sub_size=7.5, sub_spacing=2.8,
    )

    # Ornamental divider — line + heart + line
    div_y = logo_bottom - 15
    seg = 60
    c.setStrokeColor(p["accent"])
    c.setLineWidth(0.6)
    c.line(PAGE_W / 2.0 - seg - 8, div_y, PAGE_W / 2.0 - 8, div_y)
    c.line(PAGE_W / 2.0 + 8, div_y, PAGE_W / 2.0 + seg + 8, div_y)
    draw_heart(c, PAGE_W / 2.0, div_y + 1, 0.35, p["accent"])

    # Tagline
    c.setFont("Helvetica-Oblique", 9)
    c.setFillColor(p["muted"])
    tag = "all gluten-free · baked fresh from our kitchen"
    tw = stringWidth(tag, "Helvetica-Oblique", 9)
    c.drawString((PAGE_W - tw) / 2.0, div_y - 14, tag)

    # Items
    items_top = div_y - 38
    row_h = 44

    for i, item in enumerate(MENU_ITEMS):
        cy = items_top - i * row_h

        # Item name caps
        draw_letterspaced_centered(
            c, item["name"].upper(),
            PAGE_W / 2.0, cy,
            "Helvetica", 10, 1.2, p["body"],
        )

        # Italic size descriptor
        c.setFont("Helvetica-Oblique", 8)
        c.setFillColor(p["muted"])
        sw = stringWidth(item["size"], "Helvetica-Oblique", 8)
        c.drawString((PAGE_W - sw) / 2.0, cy - 11, item["size"])

        # Price
        c.setFont("Helvetica", 14)
        c.setFillColor(p["accent"])
        pw = stringWidth(item["price"], "Helvetica", 14)
        c.drawString((PAGE_W - pw) / 2.0, cy - 24, item["price"])

        # Tiny separator
        if i < len(MENU_ITEMS) - 1:
            draw_divider_line(c, PAGE_W / 2.0, cy - 36,
                              width=18, color=p["accent"], weight=0.4)

    # Payment block
    last_cy = items_top - (len(MENU_ITEMS) - 1) * row_h
    draw_payment_block(c, p, cy_top=last_cy - 44,
                       divider_width=160, row_gap=13)

    # Footer
    draw_footer(c, p, y=0.60 * inch)

    c.showPage()


# ---------------------------------------------------------------------------
# Build the PDFs
# ---------------------------------------------------------------------------
def build():
    # 3-design combined PDF
    c = canvas.Canvas(OUTPUT, pagesize=(PAGE_W, PAGE_H))
    c.setTitle("Baked with Love — 5x7 Menu (3 designs)")
    c.setAuthor("Baked with Love")
    design_1_classic(c)
    design_2_stacked(c)
    design_3_framed(c)
    c.save()
    print(f"Saved: {OUTPUT}")
    print("Pages:")
    print("  1. Classic Elegant   — Website Palette")
    print("  2. Stacked Highlight — Warm Rose Palette")
    print("  3. Framed Card       — Terracotta Palette")

    # Single-page terracotta export used by the website
    framed_out = "baked_with_love_menu_framed_terracotta.pdf"
    cf = canvas.Canvas(framed_out, pagesize=(PAGE_W, PAGE_H))
    cf.setTitle("Baked with Love — Menu")
    cf.setAuthor("Baked with Love")
    design_3_framed(cf)
    cf.save()
    print(f"Saved: {framed_out}")


if __name__ == "__main__":
    build()
