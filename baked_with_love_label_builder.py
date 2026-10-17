"""
Baked with Love — Avery 18262 label builder
Recovered from the May 2, 2026 label-design session (final approved version).

Avery 18262 / 5162: 1-1/3" x 4", 14 labels per sheet (2 cols x 7 rows), US Letter.
Output: baked_with_love_avery18262.pdf (3 pages — Website Palette, Warm Rose, Terracotta)

Run:
    pip install reportlab
    python3 baked_with_love_label_builder.py              # labels
    python3 baked_with_love_label_builder.py --calibrate  # alignment test page
Print at 100% / "Actual size" (never "Fit to page").

Printer alignment:
    Printers rarely land a page exactly where the file puts it. Adjust X_OFFSET_PT /
    Y_OFFSET_PT below, print the --calibrate page on plain paper, hold it over a label
    sheet against a window, and repeat until the dashed lines sit on the label cut lines.
    1 pt = 1/72 inch (~0.35 mm).
"""
import os
import sys
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor

HERE = os.path.dirname(os.path.abspath(__file__))

# Poppins Light — looks next to this script first, then common install locations
FONT_CANDIDATES = [
    os.path.join(HERE, "fonts", "Poppins-Light.ttf"),
    os.path.expanduser("~/Library/Fonts/Poppins-Light.ttf"),
    "/Library/Fonts/Poppins-Light.ttf",
    "/usr/share/fonts/truetype/google-fonts/Poppins-Light.ttf",
]
font_path = next((p for p in FONT_CANDIDATES if os.path.exists(p)), None)
if not font_path:
    raise SystemExit("Poppins-Light.ttf not found — put it in a 'fonts' folder next to this script.")
pdfmetrics.registerFont(TTFont('Poppins-Light', font_path))

PAGE_W, PAGE_H = letter
LABEL_W     = 4.0   * 72
LABEL_H     = 1.333 * 72
COLS        = 2
ROWS        = 7
LEFT_MARGIN = 0.156 * 72
TOP_MARGIN  = 0.833 * 72   # Avery 18262 spec (0.5" printed too high)
COL_GAP     = 0.188 * 72
ROW_GAP     = 0.0

# --- Printer alignment (points). Positive X = move right, positive Y = move down. ---
# Oct 2026: first test print landed left of the die cuts; 2.5pt was still a hair left, so 3.0pt.
X_OFFSET_PT = 3.0
Y_OFFSET_PT = 0.0

# Printed outline sits this far inside the die cut so small misalignments don't show.
BORDER_INSET = 4.0
# Background color extends this far past the die cut so no white sliver shows if the print shifts.
BG_BLEED = 3.0

palettes = [
    {"name":"Website Palette","bg":"#FAF6F0","border":"#C9907A","inset":"#F2E4D4","main_txt":"#5C3D2E","heart":"#C9907A","sub_txt":"#9E5E4A","div":"#C9907A","foot_txt":"#8C7060"},
    {"name":"Warm Rose",      "bg":"#fff7f5","border":"#e0a090","inset":None,      "main_txt":"#a03828","heart":"#c05848","sub_txt":"#c05848","div":"#e0b0a0","foot_txt":"#a06858"},
    {"name":"Terracotta",     "bg":"#fdf0e6","border":"#c05830","inset":None,      "main_txt":"#c05830","heart":"#c05830","sub_txt":"#c05830","div":"#e0a888","foot_txt":"#a06040"},
]

def draw_heart(c, cx, cy, hw, hh, color):
    c.setFillColor(HexColor(color))
    p = c.beginPath()
    p.moveTo(cx, cy + hh * 0.6)
    p.curveTo(cx, cy + hh,              cx - hw*1.1, cy + hh,       cx - hw, cy + hh*0.5)
    p.curveTo(cx - hw*1.1, cy,          cx - hw*0.2, cy - hh*0.3,   cx,      cy - hh)
    p.curveTo(cx + hw*0.2, cy - hh*0.3, cx + hw*1.1, cy,            cx + hw, cy + hh*0.5)
    p.curveTo(cx + hw*1.1, cy + hh,     cx,           cy + hh,       cx,      cy + hh*0.6)
    p.close()
    c.drawPath(p, fill=1, stroke=0)

def draw_label(c, x, y, pal):
    W = LABEL_W
    H = LABEL_H

    # Background bleeds past the die cut (rows are flush, so overlap is same color)
    c.setFillColor(HexColor(pal["bg"]))
    c.rect(x - BG_BLEED, y - BG_BLEED, W + 2*BG_BLEED, H + 2*BG_BLEED, fill=1, stroke=0)

    # Outline inset from the die cut
    b = BORDER_INSET
    c.setStrokeColor(HexColor(pal["border"]))
    c.setLineWidth(0.8)
    c.roundRect(x+b, y+b, W-2*b, H-2*b, radius=5, fill=0, stroke=1)
    if pal["inset"]:
        c.setStrokeColor(HexColor(pal["inset"]))
        c.setLineWidth(0.5)
        c.roundRect(x+b+4, y+b+4, W-2*b-8, H-2*b-8, radius=3, fill=0, stroke=1)

    main_y = y + 66
    sub_y  = y + 46
    div_y  = y + 28
    foot_y = y + 16

    # Main text: BAKED WITH L ♥ VE
    main_fs    = 17
    char_space = 2.8
    part1, part2 = "BAKED WITH L", "VE"
    w1 = c.stringWidth(part1, 'Poppins-Light', main_fs) + char_space * len(part1)
    w2 = c.stringWidth(part2, 'Poppins-Light', main_fs) + char_space * len(part2)
    heart_w = heart_h = 5.5
    total_w = w1 + char_space + heart_w*2 + char_space + w2
    start_x = x + (W - total_w) / 2

    t = c.beginText(start_x, main_y)
    t.setFont('Poppins-Light', main_fs)
    t.setFillColor(HexColor(pal["main_txt"]))
    t.setCharSpace(char_space)
    t.textOut(part1)
    c.drawText(t)

    p1_end_x = start_x + w1 + char_space
    draw_heart(c, p1_end_x + heart_w, main_y + 6, heart_w, heart_h, pal["heart"])

    t = c.beginText(p1_end_x + heart_w*2 + char_space, main_y)
    t.setFont('Poppins-Light', main_fs)
    t.setFillColor(HexColor(pal["main_txt"]))
    t.setCharSpace(char_space)
    t.textOut(part2)
    c.drawText(t)

    # Subtitle
    sub_fs = 7.5
    sub_cs = 2.5
    raw_sw = c.stringWidth("HOME BAKERY", 'Poppins-Light', sub_fs) + sub_cs * len("HOME BAKERY")
    t = c.beginText(x + (W - raw_sw) / 2, sub_y)
    t.setFont('Poppins-Light', sub_fs)
    t.setFillColor(HexColor(pal["sub_txt"]))
    t.setCharSpace(sub_cs)
    t.textOut("HOME BAKERY")
    c.drawText(t)

    # Divider
    c.setStrokeColor(HexColor(pal["div"]))
    c.setLineWidth(0.4)
    c.line(x+12, div_y, x+W-12, div_y)

    # Footer — shifted left by 1.5 average character widths (~5pts)
    # (setFont must be called before every drawString — ReportLab keeps text-object font state separate)
    foot_fs = 6
    edge    = 24
    shift   = 4.978  # 1.5 avg char widths at 6pt Poppins

    # Left: name
    c.setFont('Poppins-Light', foot_fs)
    c.setFillColor(HexColor(pal["foot_txt"]))
    c.drawString(x + edge - shift, foot_y, "Elizabeth Nerbun")

    # Right: phone — moved a further 15pt left (approved by eye)
    c.setFont('Poppins-Light', foot_fs)
    c.setFillColor(HexColor(pal["foot_txt"]))
    c.drawRightString(x + W - edge - shift - 15, foot_y, "262-366-4414")

    # Center: Rockwall TX
    c.setFont('Poppins-Light', foot_fs)
    c.setFillColor(HexColor(pal["foot_txt"]))
    mw = c.stringWidth("Rockwall, TX", 'Poppins-Light', foot_fs)
    c.drawString(x + (W - mw) / 2 - shift, foot_y, "Rockwall, TX")


def label_origin(row, col):
    """Bottom-left corner of a label in PDF points, with printer offset applied."""
    lx = LEFT_MARGIN + col * (LABEL_W + COL_GAP) + X_OFFSET_PT
    ly = PAGE_H - TOP_MARGIN - (row+1)*LABEL_H - row*ROW_GAP - Y_OFFSET_PT
    return lx, ly

def build_sheet(c, pal):
    # A label's background bleed (3pt) only overlaps a neighbor's blank edge zone
    # (outline starts 4pt in), so drawing order is safe.
    for row in range(ROWS):
        for col in range(COLS):
            draw_label(c, *label_origin(row, col), pal)
    c.showPage()

def build_calibration(path):
    """Plain-paper test page: dashed lines on each label's exact die-cut position."""
    c = canvas.Canvas(path, pagesize=letter)
    c.setTitle("Baked with Love — Avery 18262 alignment test")
    c.setStrokeColor(HexColor("#5C3D2E"))
    c.setLineWidth(0.4)
    c.setDash(3, 2)
    for row in range(ROWS):
        for col in range(COLS):
            lx, ly = label_origin(row, col)
            c.rect(lx, ly, LABEL_W, LABEL_H, fill=0, stroke=1)
            # Center crosshair
            cx, cy = lx + LABEL_W/2, ly + LABEL_H/2
            c.setDash()
            c.line(cx-6, cy, cx+6, cy)
            c.line(cx, cy-6, cx, cy+6)
            c.setDash(3, 2)
    c.setDash()
    c.setFillColor(HexColor("#5C3D2E"))
    c.setFont('Poppins-Light', 7)
    note = (f"Alignment test — X_OFFSET_PT={X_OFFSET_PT}  Y_OFFSET_PT={Y_OFFSET_PT}.  "
            "Print on plain paper at 100%, hold over a label sheet against a window. "
            "Lines should sit on the cut lines.")
    c.drawCentredString(PAGE_W/2, PAGE_H - TOP_MARGIN + 20, note)
    c.save()

if __name__ == "__main__":
    if "--calibrate" in sys.argv:
        cal = os.path.join(HERE, "baked_with_love_avery18262_alignment_test.pdf")
        build_calibration(cal)
        print("Done:", cal)
        sys.exit(0)
    out = os.path.join(HERE, "baked_with_love_avery18262.pdf")
    c = canvas.Canvas(out, pagesize=letter)
    c.setTitle("Baked with Love — Avery 18262 Labels")
    for pal in palettes:
        build_sheet(c, pal)
    c.save()
    print("Done:", out)
