import math
import tkinter as tk

# Color Palette matching the E Bank UI screenshot
BG_MAIN = "#F2F4FA"          # Soft lavender-gray main background
BG_SIDEBAR = "#F0F3FA"       # Sidebar background
SIDEBAR_ACTIVE_BG = "#DCE4FF" # Active pill background in sidebar
SIDEBAR_HOVER_BG = "#E6ECFF"
BORDER_COLOR = "#E2E7F4"

CARD_WHITE = "#FFFFFF"       # White card background
CARD_SOFT_BLUE = "#EAEFF9"   # Incomes / Expenses card background
SEARCH_BG = "#E6EAF5"        # Search bar and top icon circle background

PRIMARY_BLUE = "#2563EB"     # Primary E Bank blue
BRAND_BLUE = "#1E4DB7"       # "E Bank" logo color
PILL_BLUE = "#2F66E9"        # Quick action pill button color
PILL_BLUE_HOVER = "#1D4ED8"
CHART_LIGHT_BLUE = "#DCE5FB" # Incomes bar in chart
CHART_DARK_BLUE = "#2F66E9"  # Expenses bar in chart

TEXT_DARK = "#1E2640"        # Main dark navy/slate text
TEXT_MEDIUM = "#475569"      # Secondary text
TEXT_MUTED = "#64748B"       # Muted labels (e.g. February, chart axes)
TEXT_GREEN = "#16A34A"       # +$100.00 income green
BADGE_FRAUD_BG = "#C83E3B"   # "Possible fraud" red badge background
BADGE_FRAUD_FG = "#FFFFFF"
BADGE_VALID_BG = "#DCFCE7"
BADGE_VALID_FG = "#15803D"

FONT_FAMILY = "Segoe UI"


def create_rounded_rect(canvas: tk.Canvas, x1, y1, x2, y2, r=16, **kwargs):
    """Draw a smooth rounded rectangle on a Tkinter Canvas."""
    r = min(r, (x2 - x1) / 2, (y2 - y1) / 2)
    points = [
        x1 + r, y1,
        x1 + r, y1,
        x2 - r, y1,
        x2 - r, y1,
        x2, y1,
        x2, y1 + r,
        x2, y1 + r,
        x2, y2 - r,
        x2, y2 - r,
        x2, y2,
        x2 - r, y2,
        x2 - r, y2,
        x1 + r, y2,
        x1 + r, y2,
        x1, y2,
        x1, y2 - r,
        x1, y2 - r,
        x1, y1 + r,
        x1, y1 + r,
        x1, y1,
    ]
    return canvas.create_polygon(points, smooth=True, **kwargs)


def create_right_pill(canvas: tk.Canvas, x1, y1, x2, y2, r=22, **kwargs):
    """Draw a sidebar pill rounded on the right side (or all sides with smaller left radius)."""
    return create_rounded_rect(canvas, x1, y1, x2, y2, r=r, **kwargs)


def draw_contactless_icon(canvas: tk.Canvas, x, y, color="#D1D5DB", scale=1.0):
    """Draw the contactless payment wave icon on credit cards."""
    for i, radius in enumerate([4, 8, 12]):
        r = radius * scale
        canvas.create_arc(
            x - r, y - r, x + r, y + r,
            start=-45, extent=90, style=tk.ARC,
            outline=color, width=max(1, int(1.6 * scale))
        )


def draw_mastercard_circles(canvas: tk.Canvas, x, y, r=10, c1="#9CA3AF", c2="#D1D5DB"):
    """Draw the two overlapping circles at the bottom right of a card."""
    canvas.create_oval(x - r, y - r, x + r, y + r, fill=c1, outline="")
    canvas.create_oval(x, y - r, x + 2 * r, y + r, fill=c2, outline="")


def draw_cards_artwork(canvas: tk.Canvas, username: str = "Eda Tunca"):
    """
    Render the 3 overlapping credit/debit cards from the E Bank design onto `canvas`.
    Expected canvas size: ~430 x 195
    """
    canvas.delete("all")

    # --- CARD 3 (Back Right - Dark Navy/Indigo Card) ---
    c3_x1, c3_y1, c3_x2, c3_y2 = 205, 16, 415, 168
    create_rounded_rect(canvas, c3_x1 + 2, c3_y1 + 4, c3_x2 + 2, c3_y2 + 4, r=16, fill="#CBD5E1", outline="")
    create_rounded_rect(canvas, c3_x1, c3_y1, c3_x2, c3_y2, r=16, fill="#1E1B4B", outline="#312E81", width=1)
    # Decorative wave shapes on Card 3
    canvas.create_arc(280, -10, 440, 130, start=160, extent=130, style=tk.CHORD, fill="#4338CA", outline="")
    canvas.create_arc(310, 60, 440, 200, start=90, extent=150, style=tk.CHORD, fill="#3730A3", outline="")
    draw_contactless_icon(canvas, 386, 40, color="#E0E7FF", scale=0.95)
    canvas.create_text(
        355, 108, text="00 0000",
        font=(FONT_FAMILY, 12, "normal"), fill="#E0E7FF", anchor="e"
    )
    draw_mastercard_circles(canvas, 375, 145, r=9, c1="#818CF8", c2="#C7D2FE")

    # --- CARD 2 (Middle - Purple/Blue Marble Swirl Card) ---
    c2_x1, c2_y1, c2_x2, c2_y2 = 115, 14, 345, 170
    create_rounded_rect(canvas, c2_x1 + 2, c2_y1 + 4, c2_x2 + 2, c2_y2 + 4, r=16, fill="#94A3B8", outline="")
    create_rounded_rect(canvas, c2_x1, c2_y1, c2_x2, c2_y2, r=16, fill="#8B7CB8", outline="#A78BFA", width=1)
    # Marble / fluid abstract waves on Card 2
    marble_blobs = [
        (180, 18, 330, 115, "#60A5FA"),
        (210, 40, 342, 160, "#A78BFA"),
        (240, 20, 340, 95, "#C4B5FD"),
        (225, 85, 335, 165, "#6366F1"),
        (260, 55, 342, 135, "#93C5FD"),
    ]
    for bx1, by1, bx2, by2, bcol in marble_blobs:
        create_rounded_rect(canvas, bx1, by1, bx2, by2, r=28, fill=bcol, outline="")
    # Swirl lines on Card 2
    canvas.create_line(245, 22, 275, 65, 250, 110, 295, 155, smooth=True, fill="#E0E7FF", width=2)
    canvas.create_line(285, 20, 315, 75, 280, 125, 325, 162, smooth=True, fill="#DDD6FE", width=1.5)
    draw_contactless_icon(canvas, 316, 40, color="#1E1B4B", scale=0.95)
    draw_mastercard_circles(canvas, 305, 146, r=9, c1="#4B5563", c2="#9CA3AF")

    # --- CARD 1 (Front Left - Matte Black Debit Card with 3D Torus Ring) ---
    c1_x1, c1_y1, c1_x2, c1_y2 = 6, 10, 256, 176
    # Drop shadow
    create_rounded_rect(canvas, c1_x1 + 3, c1_y1 + 5, c1_x2 + 3, c1_y2 + 5, r=18, fill="#94A3B8", outline="")
    # Matte black body
    create_rounded_rect(canvas, c1_x1, c1_y1, c1_x2, c1_y2, r=18, fill="#0D1017", outline="#262B38", width=1)

    # Subtle glowing torus / spiral artwork in center-right of Card 1
    cx, cy = 142, 92
    for i in range(18):
        angle = i * (math.pi / 9)
        ox = math.cos(angle) * 10
        oy = math.sin(angle) * 10
        # Interpolate cyan -> indigo -> magenta
        if i % 3 == 0:
            ring_color = "#22D3EE"
        elif i % 3 == 1:
            ring_color = "#6366F1"
        else:
            ring_color = "#A855F7"
        canvas.create_oval(
            cx - 34 + ox, cy - 34 + oy,
            cx + 34 + ox, cy + 34 + oy,
            outline=ring_color, width=1
        )
    # Inner dark hole of torus
    canvas.create_oval(cx - 16, cy - 16, cx + 16, cy + 16, fill="#0D1017", outline="#1E293B")

    # Silver EMV Chip on left
    chip_x1, chip_y1, chip_x2, chip_y2 = 32, 68, 66, 94
    create_rounded_rect(canvas, chip_x1, chip_y1, chip_x2, chip_y2, r=5, fill="#9CA3AF", outline="#D1D5DB", width=1)
    canvas.create_line(chip_x1, (chip_y1 + chip_y2) / 2, chip_x2, (chip_y1 + chip_y2) / 2, fill="#4B5563", width=1)
    canvas.create_line((chip_x1 + chip_x2) / 2, chip_y1, (chip_x1 + chip_x2) / 2, chip_y2, fill="#4B5563", width=1)

    # Contactless icon top-right of Card 1
    draw_contactless_icon(canvas, 224, 36, color="#9CA3AF", scale=0.95)

    # Card text: DEBIT CARD, holder name, expiry
    canvas.create_text(
        32, 118, text="DEBIT CARD",
        font=(FONT_FAMILY, 8, "bold"), fill="#9CA3AF", anchor="w"
    )
    display_name = username if len(username) <= 14 else username[:14]
    canvas.create_text(
        32, 140, text=f"{display_name}    12/24",
        font=(FONT_FAMILY, 7, "normal"), fill="#D1D5DB", anchor="w"
    )

    # Mastercard overlapping circles bottom-right of Card 1
    draw_mastercard_circles(canvas, 214, 150, r=10, c1="#6B7280", c2="#D1D5DB")
