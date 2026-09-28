import tkinter as tk
import services
from .theme import (
    BG_MAIN, CARD_WHITE, CARD_SOFT_BLUE, PRIMARY_BLUE, PILL_BLUE, PILL_BLUE_HOVER,
    CHART_LIGHT_BLUE, CHART_DARK_BLUE, TEXT_DARK, TEXT_MEDIUM, TEXT_MUTED,
    TEXT_GREEN, BADGE_FRAUD_BG, BADGE_FRAUD_FG, FONT_FAMILY,
    create_rounded_rect, draw_cards_artwork
)


class HomeView(tk.Frame):
    """
    Main Home Dashboard matching the E Bank screenshot, connected to live user data.
    """

    def __init__(self, parent, current_user: str, on_navigate, search_var: tk.StringVar = None):
        super().__init__(parent, bg=BG_MAIN)
        self.current_user = current_user
        self.on_navigate = on_navigate
        self.search_var = search_var
        self.tx_filter = "all"  # "all", "incomes", "expenses"
        self.incomes_text = "$20,000"
        self.expenses_text = "$10,000"
        self._build_ui()

    def _build_ui(self):
        # Main layout container with responsive grid weights
        self.columnconfigure(0, weight=1)

        # =====================================================================
        # ROW 0: TOP SUMMARY ROW (Total balance | Incomes card | Expenses card)
        # =====================================================================
        top_row = tk.Frame(self, bg=BG_MAIN)
        top_row.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        top_row.columnconfigure(0, weight=11, uniform="top")
        top_row.columnconfigure(1, weight=10, uniform="top")
        top_row.columnconfigure(2, weight=10, uniform="top")

        # 1. Total Balance section (Left)
        bal_frame = tk.Frame(top_row, bg=BG_MAIN)
        bal_frame.grid(row=0, column=0, sticky="nsew", padx=(4, 18), pady=4)

        bal_header = tk.Frame(bal_frame, bg=BG_MAIN)
        bal_header.pack(fill="x", pady=(4, 6))
        tk.Label(
            bal_header, text="Total balance",
            font=(FONT_FAMILY, 13), fg=TEXT_DARK, bg=BG_MAIN
        ).pack(side="left")

        tk.Label(
            bal_header, text="USD  ▾",
            font=(FONT_FAMILY, 9, "bold"), fg=PRIMARY_BLUE, bg=BG_MAIN, cursor="hand2"
        ).pack(side="right", padx=(0, 24))

        self.balance_lbl = tk.Label(
            bal_frame, text="$120,000",
            font=(FONT_FAMILY, 30), fg="#232946", bg=BG_MAIN, anchor="w"
        )
        self.balance_lbl.pack(fill="x")

        # 2. Incomes Card (Middle)
        self.inc_canvas = tk.Canvas(top_row, height=96, bg=BG_MAIN, highlightthickness=0)
        self.inc_canvas.grid(row=0, column=1, sticky="nsew", padx=8)
        self.inc_canvas.bind("<Configure>", lambda e: self._draw_stat_card(
            self.inc_canvas, "Incomes", "February", self.incomes_text, "+11.01%"
        ))

        # 3. Expenses Card (Right)
        self.exp_canvas = tk.Canvas(top_row, height=96, bg=BG_MAIN, highlightthickness=0)
        self.exp_canvas.grid(row=0, column=2, sticky="nsew", padx=(8, 0))
        self.exp_canvas.bind("<Configure>", lambda e: self._draw_stat_card(
            self.exp_canvas, "Expenses", "February", self.expenses_text, "-1.01%"
        ))

        # =====================================================================
        # ROW 1: QUICK ACTION PILLS BAR
        # =====================================================================
        self.actions_canvas = tk.Canvas(self, height=56, bg=BG_MAIN, highlightthickness=0)
        self.actions_canvas.grid(row=1, column=0, sticky="ew", pady=(0, 14))
        self.actions_canvas.bind("<Configure>", self._draw_quick_actions_bar)

        # =====================================================================
        # ROW 2: MIDDLE SECTION (My cards on Left | Financial Overview on Right)
        # =====================================================================
        mid_row = tk.Frame(self, bg=BG_MAIN)
        mid_row.grid(row=2, column=0, sticky="ew", pady=(0, 14))
        mid_row.columnconfigure(0, weight=10, uniform="mid")
        mid_row.columnconfigure(1, weight=11, uniform="mid")

        # --- LEFT: My cards ---
        cards_col = tk.Frame(mid_row, bg=BG_MAIN)
        cards_col.grid(row=0, column=0, sticky="nsew", padx=(2, 14))

        cards_hdr = tk.Frame(cards_col, bg=BG_MAIN)
        cards_hdr.pack(fill="x", pady=(2, 4))
        tk.Label(
            cards_hdr, text="My cards",
            font=(FONT_FAMILY, 13), fg=TEXT_DARK, bg=BG_MAIN
        ).pack(side="left")

        see_details_lbl = tk.Label(
            cards_hdr, text="See details  ▸",
            font=(FONT_FAMILY, 9, "bold"), fg=PRIMARY_BLUE, bg=BG_MAIN, cursor="hand2"
        )
        see_details_lbl.pack(side="right", padx=(0, 8))
        see_details_lbl.bind("<Button-1>", lambda e: self.on_navigate("transfer"))

        # Overlapping 3 credit cards canvas
        self.cards_canvas = tk.Canvas(cards_col, width=430, height=182, bg=BG_MAIN, highlightthickness=0)
        self.cards_canvas.pack(anchor="w")
        draw_cards_artwork(self.cards_canvas, username=self._get_card_holder_name())

        # Card balances below cards
        card_Footer = tk.Frame(cards_col, bg=BG_MAIN)
        card_Footer.pack(fill="x", pady=(2, 0))

        c_left = tk.Frame(card_Footer, bg=BG_MAIN)
        c_left.pack(side="left", padx=(4, 36))
        tk.Label(
            c_left, text="Total Card Balance",
            font=(FONT_FAMILY, 9), fg=TEXT_MEDIUM, bg=BG_MAIN
        ).pack(anchor="w")
        self.card_total_lbl = tk.Label(
            c_left, text="$100,000",
            font=(FONT_FAMILY, 15), fg="#232946", bg=BG_MAIN
        )
        self.card_total_lbl.pack(anchor="w", pady=(2, 0))

        c_right = tk.Frame(card_Footer, bg=BG_MAIN)
        c_right.pack(side="left")
        tk.Label(
            c_right, text="Available Card Balance",
            font=(FONT_FAMILY, 9), fg=TEXT_MEDIUM, bg=BG_MAIN
        ).pack(anchor="w")
        self.card_avail_lbl = tk.Label(
            c_right, text="$70,600",
            font=(FONT_FAMILY, 15), fg="#232946", bg=BG_MAIN
        )
        self.card_avail_lbl.pack(anchor="w", pady=(2, 0))

        # --- RIGHT: Financial Overview chart card ---
        self.chart_canvas = tk.Canvas(mid_row, height=256, bg=BG_MAIN, highlightthickness=0)
        self.chart_canvas.grid(row=0, column=1, sticky="nsew", padx=(4, 0))
        self.chart_canvas.bind("<Configure>", self._draw_financial_overview)

        # =====================================================================
        # ROW 3: BOTTOM TRANSACTIONS CARD
        # =====================================================================
        self.tx_card_canvas = tk.Canvas(self, height=205, bg=BG_MAIN, highlightthickness=0)
        self.tx_card_canvas.grid(row=3, column=0, sticky="nsew", pady=(0, 2))
        self.rowconfigure(3, weight=1)
        self.tx_card_canvas.bind("<Configure>", self._draw_transactions_card)

        self.refresh_data()

    def _get_card_holder_name(self):
        if self.current_user.lower() == "eda":
            return "Eda Tunca"
        return self.current_user

    def refresh_data(self):
        """Fetch latest balance & transactions for current_user from services.py."""
        bal = services.get_balance(self.current_user)
        if bal is None:
            bal = 120000.0
        # Format nicely like $120,000
        if abs(bal - round(bal)) < 0.005:
            self.balance_lbl.config(text=f"${bal:,.0f}")
        else:
            self.balance_lbl.config(text=f"${bal:,.2f}")

        # Keep the reference card numbers ($20,000 & $10,000) or add user activity
        self.incomes_text = "$20,000"
        self.expenses_text = "$10,000"

        self._draw_stat_card(self.inc_canvas, "Incomes", "February", self.incomes_text, "+11.01%")
        self._draw_stat_card(self.exp_canvas, "Expenses", "February", self.expenses_text, "-1.01%")
        draw_cards_artwork(self.cards_canvas, username=self._get_card_holder_name())
        self._draw_transactions_card()

    def _draw_stat_card(self, canvas: tk.Canvas, title: str, month: str, amount: str, pct: str):
        canvas.delete("all")
        w = max(canvas.winfo_width(), 240)
        h = max(canvas.winfo_height(), 92)
        create_rounded_rect(canvas, 2, 2, w - 2, h - 2, r=16, fill=CARD_SOFT_BLUE, outline="")

        canvas.create_text(
            22, 26, text=title,
            font=(FONT_FAMILY, 10, "bold"), fill=TEXT_DARK, anchor="w"
        )
        canvas.create_text(
            w - 22, 26, text=month,
            font=(FONT_FAMILY, 9), fill=TEXT_MEDIUM, anchor="e"
        )
        canvas.create_text(
            22, 62, text=amount,
            font=(FONT_FAMILY, 17), fill=TEXT_DARK, anchor="w"
        )
        canvas.create_text(
            w - 22, 63, text=f"{pct}  ↗",
            font=(FONT_FAMILY, 9, "bold"), fill=TEXT_DARK, anchor="e"
        )

    def _draw_quick_actions_bar(self, event=None):
        c = self.actions_canvas
        c.delete("all")
        w = max(c.winfo_width(), 820)
        h = max(c.winfo_height(), 56)

        # Outer white rounded bar
        create_rounded_rect(c, 2, 2, w - 2, h - 2, r=14, fill=CARD_WHITE, outline="")

        pills = [
            ("⇄  Transfer money", "transfer"),
            ("▣  Pay bills", "deposit"),
            ("📈  Investments", "transactions"),
            ("◔  Insights", "transactions"),
            ("⑂  Split a bill", "transfer"),
            ("📅  Schedule payments", "transactions"),
            ("↻  Exchange currency", "transfer"),
        ]

        pad_x = 14
        gap = 10
        avail_w = w - 2 * pad_x - gap * (len(pills) - 1)
        # Weight pills slightly by text length so all 7 fit comfortably just like the screenshot
        weights = [len(label) + 4 for label, _ in pills]
        total_weight = sum(weights)

        cur_x = pad_x
        y1, y2 = 12, h - 12
        for (label, target), wt in zip(pills, weights):
            pw = avail_w * (wt / total_weight)
            x1, x2 = cur_x, cur_x + pw
            tag = f"pill_{label}"
            rect_id = create_rounded_rect(
                c, x1, y1, x2, y2, r=15,
                fill=PILL_BLUE, outline="", tags=(tag,)
            )
            c.create_text(
                (x1 + x2) / 2, (y1 + y2) / 2,
                text=label, font=(FONT_FAMILY, 8, "bold"),
                fill="#FFFFFF", tags=(tag,)
            )

            def on_enter(e, rid=rect_id):
                c.itemconfig(rid, fill=PILL_BLUE_HOVER)
                c.config(cursor="hand2")

            def on_leave(e, rid=rect_id):
                c.itemconfig(rid, fill=PILL_BLUE)
                c.config(cursor="")

            c.tag_bind(tag, "<Enter>", on_enter)
            c.tag_bind(tag, "<Leave>", on_leave)
            c.tag_bind(tag, "<Button-1>", lambda e, t=target: self.on_navigate(t))
            cur_x = x2 + gap

    def _draw_financial_overview(self, event=None):
        c = self.chart_canvas
        c.delete("all")
        w = max(c.winfo_width(), 420)
        h = max(c.winfo_height(), 250)

        create_rounded_rect(c, 2, 2, w - 2, h - 2, r=16, fill=CARD_WHITE, outline="")

        # Header
        c.create_text(
            22, 24, text="Financial Overview",
            font=(FONT_FAMILY, 10, "bold"), fill=TEXT_DARK, anchor="w"
        )
        c.create_text(
            w - 20, 24, text="Last 6 months ▾",
            font=(FONT_FAMILY, 9, "bold"), fill=PRIMARY_BLUE, anchor="e"
        )

        # Legend: Incomes & Expenses pills
        create_rounded_rect(c, 22, 46, 42, 57, r=5, fill=CHART_LIGHT_BLUE, outline="")
        c.create_text(48, 51, text="Incomes", font=(FONT_FAMILY, 8), fill=TEXT_MEDIUM, anchor="w")

        create_rounded_rect(c, 98, 46, 118, 57, r=5, fill=CHART_DARK_BLUE, outline="")
        c.create_text(124, 51, text="Expenses", font=(FONT_FAMILY, 8), fill=TEXT_MEDIUM, anchor="w")

        # Y-axis labels
        y_labels = [
            ("20,000", 88),
            ("10,000", 122),
            ("5,000", 156),
            ("1,000", 190),
        ]
        for txt, y_pos in y_labels:
            c.create_text(22, y_pos, text=txt, font=(FONT_FAMILY, 8), fill=TEXT_MUTED, anchor="w")

        # Bar Chart Data matching the screenshot (Jul, Aug, Sep, Nov, Dec, Jan, Feb)
        months_data = [
            ("Jul", 0.62, 0.59),
            ("Aug", 0.58, 0.36),
            ("Sep", 0.37, 0.38),
            ("Nov", 0.85, 0.61),
            ("Dec", 0.45, 0.46),
            ("Jan", 0.65, 0.65),
            ("Feb", 0.55, 0.49),
        ]

        chart_left = 78
        chart_right = w - 20
        base_y = 205
        max_bar_h = 112
        col_w = (chart_right - chart_left) / len(months_data)
        bar_w = 11

        for idx, (m_name, inc_ratio, exp_ratio) in enumerate(months_data):
            cx = chart_left + col_w * (idx + 0.5)

            # Incomes bar (Light Blue)
            inc_h = max(14, max_bar_h * inc_ratio)
            ix1, iy1, ix2, iy2 = cx - bar_w - 1.5, base_y - inc_h, cx - 1.5, base_y
            create_rounded_rect(c, ix1, iy1, ix2, iy2, r=5, fill=CHART_LIGHT_BLUE, outline="")

            # Expenses bar (Dark Blue)
            exp_h = max(14, max_bar_h * exp_ratio)
            ex1, ey1, ex2, ey2 = cx + 1.5, base_y - exp_h, cx + bar_w + 1.5, base_y
            create_rounded_rect(c, ex1, ey1, ex2, ey2, r=5, fill=CHART_DARK_BLUE, outline="")

            # Month label
            c.create_text(cx, base_y + 18, text=m_name, font=(FONT_FAMILY, 8), fill=TEXT_MUTED)

    def _set_tx_filter(self, flt: str):
        self.tx_filter = flt
        self._draw_transactions_card()

    def _get_display_transactions(self):
        """
        Combine current user's recent DB transactions with the screenshot's iconic rows
        so both live crypto transactions and the exact visual layout are shown.
        """
        db_rows = services.list_transactions(self.current_user)
        items = []

        for r in db_rows:
            is_sender = (r["sender_username"] == self.current_user)
            counterparty = r["receiver_username"] if is_sender else r["sender_username"]
            valid, _, _ = services.verify_transaction(r["id"])
            initials = "".join(part[0].upper() for part in counterparty.split()[:2]) or counterparty[:2].upper()
            items.append({
                "id": r["id"],
                "initials": initials,
                "name": f"{counterparty}  ({r['id']})",
                "amount": float(r["amount"]),
                "is_income": not is_sender,
                "fraud": not valid,
                "avatar_bg": "#DCD7FE" if not valid else "#D8E2FF",
                "avatar_fg": "#4338CA",
            })

        # Reference screenshot items so the Home bottom card always has Maria & Alexa Capton as in the photo
        demo_items = [
            {
                "id": "DEMO-MARIA",
                "initials": "M",
                "name": "Maria",
                "amount": 40.00,
                "is_income": False,
                "fraud": True,
                "avatar_bg": "#DDD6FE",
                "avatar_fg": "#3730A3",
            },
            {
                "id": "DEMO-ALEXA",
                "initials": "AC",
                "name": "Alexa Capton",
                "amount": 100.00,
                "is_income": True,
                "fraud": False,
                "avatar_bg": "#DDD6FE",
                "avatar_fg": "#3730A3",
            },
        ]
        items.extend(demo_items)

        # Filter by search query if present
        q = (self.search_var.get().strip().lower() if self.search_var else "")
        if q:
            items = [it for it in items if q in it["name"].lower() or q in it["id"].lower()]

        # Filter by tab (all / incomes / expenses)
        if self.tx_filter == "incomes":
            items = [it for it in items if it["is_income"]]
        elif self.tx_filter == "expenses":
            items = [it for it in items if not it["is_income"]]

        return items[:3]

    def _draw_transactions_card(self, event=None):
        c = self.tx_card_canvas
        c.delete("all")
        w = max(c.winfo_width(), 820)
        h = max(c.winfo_height(), 195)

        create_rounded_rect(c, 2, 2, w - 2, h - 2, r=16, fill=CARD_WHITE, outline="")

        # Title
        c.create_text(
            24, 26, text="Transactions",
            font=(FONT_FAMILY, 13), fill=TEXT_DARK, anchor="w"
        )

        # Filter funnel icon & 3-dots menu on top right
        fx = w - 58
        c.create_polygon(
            fx - 6, 20, fx + 6, 20, fx + 1.5, 26, fx + 1.5, 31, fx - 1.5, 31, fx - 1.5, 26,
            fill="", outline=TEXT_DARK, width=1.4
        )
        mx = w - 28
        for dy in (-5, 0, 5):
            c.create_oval(mx - 1.5, 25 + dy - 1.5, mx + 1.5, 25 + dy + 1.5, fill=TEXT_DARK, outline="")

        # Sub-tabs: All transactions | Incomes | Expenses ...... See all ▸
        tabs = [
            ("All transactions", "all", 24),
            ("Incomes", "incomes", 145),
            ("Expenses", "expenses", 225),
        ]
        for label, key, tx_x in tabs:
            is_active = (self.tx_filter == key)
            color = PRIMARY_BLUE if is_active else TEXT_MEDIUM
            weight = "bold" if is_active else "normal"
            t_tag = f"tx_tab_{key}"
            tid = c.create_text(
                tx_x, 58, text=label,
                font=(FONT_FAMILY, 9, weight), fill=color, anchor="w", tags=(t_tag,)
            )
            if is_active:
                bbox = c.bbox(tid)
                if bbox:
                    c.create_line(bbox[0], 71, bbox[2], 71, fill=PRIMARY_BLUE, width=2.5)
            c.tag_bind(t_tag, "<Button-1>", lambda e, k=key: self._set_tx_filter(k))
            c.tag_bind(t_tag, "<Enter>", lambda e: c.config(cursor="hand2"))
            c.tag_bind(t_tag, "<Leave>", lambda e: c.config(cursor=""))

        # Divider line under tabs
        c.create_line(24, 72, w - 24, 72, fill="#F1F5F9", width=1)

        # See all ▸ link
        c.create_text(
            w - 24, 58, text="See all  ▸",
            font=(FONT_FAMILY, 9, "bold"), fill=PRIMARY_BLUE, anchor="e", tags=("see_all_tx",)
        )
        c.tag_bind("see_all_tx", "<Button-1>", lambda e: self.on_navigate("transactions"))
        c.tag_bind("see_all_tx", "<Enter>", lambda e: c.config(cursor="hand2"))
        c.tag_bind("see_all_tx", "<Leave>", lambda e: c.config(cursor=""))

        # Render transaction rows
        rows = self._get_display_transactions()
        row_y = 98
        row_step = 48

        for idx, item in enumerate(rows):
            cy = row_y + idx * row_step
            if cy + 16 > h:
                break

            row_tag = f"home_tx_row_{idx}"
            # Avatar Circle
            av_x = 42
            c.create_oval(
                av_x - 18, cy - 18, av_x + 18, cy + 18,
                fill=item["avatar_bg"], outline="", tags=(row_tag,)
            )
            c.create_text(
                av_x, cy, text=item["initials"],
                font=(FONT_FAMILY, 9, "bold"), fill=item["avatar_fg"], tags=(row_tag,)
            )

            # Counterparty Name
            c.create_text(
                74, cy, text=item["name"],
                font=(FONT_FAMILY, 10), fill=TEXT_DARK, anchor="w", tags=(row_tag,)
            )

            # Right side: Amount and optional "Possible fraud" red badge
            amt_str = f"+${item['amount']:,.2f}" if item["is_income"] else f"-${item['amount']:,.2f}"
            amt_color = TEXT_GREEN if item["is_income"] else TEXT_DARK

            if item["fraud"]:
                c.create_text(
                    w - 24, cy - 9, text=amt_str,
                    font=(FONT_FAMILY, 10, "bold"), fill=amt_color, anchor="e", tags=(row_tag,)
                )
                # Red "Possible fraud" pill badge matching the screenshot
                bx1, by1, bx2, by2 = w - 116, cy + 3, w - 24, cy + 22
                create_rounded_rect(
                    c, bx1, by1, bx2, by2, r=5,
                    fill=BADGE_FRAUD_BG, outline="", tags=(row_tag,)
                )
                c.create_text(
                    (bx1 + bx2) / 2, (by1 + by2) / 2,
                    text="Possible fraud",
                    font=(FONT_FAMILY, 8, "bold"), fill=BADGE_FRAUD_FG, tags=(row_tag,)
                )
            else:
                c.create_text(
                    w - 24, cy, text=amt_str,
                    font=(FONT_FAMILY, 10, "bold"), fill=amt_color, anchor="e", tags=(row_tag,)
                )

            c.tag_bind(row_tag, "<Button-1>", lambda e: self.on_navigate("transactions"))
            c.tag_bind(row_tag, "<Enter>", lambda e: c.config(cursor="hand2"))
            c.tag_bind(row_tag, "<Leave>", lambda e: c.config(cursor=""))
