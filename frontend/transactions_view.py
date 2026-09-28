import tkinter as tk
import services
from .theme import (
    BG_MAIN, CARD_WHITE, CARD_SOFT_BLUE, PRIMARY_BLUE, PILL_BLUE, PILL_BLUE_HOVER,
    SIDEBAR_ACTIVE_BG, BORDER_COLOR, TEXT_DARK, TEXT_MEDIUM, TEXT_MUTED,
    TEXT_GREEN, BADGE_FRAUD_BG, BADGE_FRAUD_FG, BADGE_VALID_BG, BADGE_VALID_FG,
    FONT_FAMILY
)


class TransactionsView(tk.Frame):
    """
    Sidebar 'Transactions' View:
    - Shows recent transactions of the current user (All transactions / Incomes / Expenses)
    - Live cryptographic verification (SHA-256 + RSA-PSS signature check)
    - Interactive Verify & [DEMO] Tamper Amount inspector
    """

    def __init__(self, parent, current_user: str, on_data_changed, search_var: tk.StringVar = None):
        super().__init__(parent, bg=BG_MAIN)
        self.current_user = current_user
        self.on_data_changed = on_data_changed
        self.search_var = search_var
        self.tx_filter = "all"
        self.selected_tx_id = None
        self._build_ui()

    def _build_ui(self):
        self.columnconfigure(0, weight=13)
        self.columnconfigure(1, weight=9)
        self.rowconfigure(0, weight=1)

        # =====================================================================
        # LEFT PANEL: RECENT TRANSACTIONS OF CURRENT USER
        # =====================================================================
        left_card = tk.Frame(
            self, bg=CARD_WHITE, padx=22, pady=20,
            highlightbackground=BORDER_COLOR, highlightthickness=1
        )
        left_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        left_card.columnconfigure(0, weight=1)
        left_card.rowconfigure(3, weight=1)

        # Header
        hdr = tk.Frame(left_card, bg=CARD_WHITE)
        hdr.grid(row=0, column=0, sticky="ew")
        tk.Label(
            hdr, text=f"Recent Transactions ({self.current_user})",
            font=(FONT_FAMILY, 14, "bold"), fg=TEXT_DARK, bg=CARD_WHITE
        ).pack(side="left")

        tk.Button(
            hdr, text="↻ Refresh",
            font=(FONT_FAMILY, 9, "bold"),
            bg=SIDEBAR_ACTIVE_BG, fg=PRIMARY_BLUE,
            activebackground=PRIMARY_BLUE, activeforeground="#FFFFFF",
            relief="flat", bd=0, padx=10, pady=4, cursor="hand2",
            command=self.refresh_data
        ).pack(side="right")

        # Filter Tabs (All transactions | Incomes | Expenses)
        tabs_bar = tk.Frame(left_card, bg=CARD_WHITE)
        tabs_bar.grid(row=1, column=0, sticky="ew", pady=(14, 4))

        self.tab_btns = {}
        for key, label in [("all", "All transactions"), ("incomes", "Incomes"), ("expenses", "Expenses")]:
            btn = tk.Button(
                tabs_bar, text=label,
                font=(FONT_FAMILY, 9, "bold" if key == "all" else "normal"),
                bg=CARD_WHITE,
                fg=PRIMARY_BLUE if key == "all" else TEXT_MEDIUM,
                activebackground=CARD_WHITE, activeforeground=PRIMARY_BLUE,
                relief="flat", bd=0, padx=8, pady=4, cursor="hand2",
                command=lambda k=key: self._set_filter(k)
            )
            btn.pack(side="left", padx=(0, 14))
            self.tab_btns[key] = btn

        tk.Frame(left_card, bg="#F1F5F9", height=1).grid(row=2, column=0, sticky="ew", pady=(0, 8))

        # Scrollable Transactions List
        list_container = tk.Frame(left_card, bg=CARD_WHITE)
        list_container.grid(row=3, column=0, sticky="nsew")
        list_container.columnconfigure(0, weight=1)
        list_container.rowconfigure(0, weight=1)

        self.list_canvas = tk.Canvas(list_container, bg=CARD_WHITE, highlightthickness=0)
        scrollbar = tk.Scrollbar(list_container, orient="vertical", command=self.list_canvas.yview)
        self.rows_frame = tk.Frame(self.list_canvas, bg=CARD_WHITE)

        self.rows_frame.bind(
            "<Configure>",
            lambda e: self.list_canvas.configure(scrollregion=self.list_canvas.bbox("all"))
        )
        self.rows_window = self.list_canvas.create_window((0, 0), window=self.rows_frame, anchor="nw")
        self.list_canvas.bind(
            "<Configure>",
            lambda e: self.list_canvas.itemconfig(self.rows_window, width=e.width)
        )
        self.list_canvas.configure(yscrollcommand=scrollbar.set)

        self.list_canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        # =====================================================================
        # RIGHT PANEL: CRYPTO VERIFY & [DEMO] TAMPER AMOUNT
        # =====================================================================
        right_card = tk.Frame(
            self, bg=CARD_WHITE, padx=22, pady=20,
            highlightbackground=BORDER_COLOR, highlightthickness=1
        )
        right_card.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        tk.Label(
            right_card, text="🛡 Verify & Tamper Inspector",
            font=(FONT_FAMILY, 13, "bold"), fg=TEXT_DARK, bg=CARD_WHITE
        ).pack(anchor="w")
        tk.Label(
            right_card, text="Chọn 1 giao dịch bên trái hoặc nhập Transaction ID để kiểm tra chữ ký số RSA-PSS hoặc giả lập tấn công sửa số tiền (Tamper).",
            font=(FONT_FAMILY, 9), fg=TEXT_MUTED, bg=CARD_WHITE, wraplength=330, justify="left"
        ).pack(anchor="w", pady=(2, 14))

        # Transaction ID input
        tk.Label(
            right_card, text="Transaction ID",
            font=(FONT_FAMILY, 9, "bold"), fg=TEXT_DARK, bg=CARD_WHITE
        ).pack(anchor="w", pady=(0, 4))

        txid_box = tk.Frame(right_card, bg="#F8FAFC", highlightbackground=BORDER_COLOR, highlightthickness=1)
        txid_box.pack(fill="x", pady=(0, 10))
        self.tx_id_var = tk.StringVar()
        tk.Entry(
            txid_box, textvariable=self.tx_id_var,
            font=("Consolas", 10), bg="#F8FAFC", fg=TEXT_DARK, relief="flat", bd=0
        ).pack(fill="x", padx=10, pady=7)

        tk.Button(
            right_card, text="🔍  Verify Giao Dịch (Kiểm tra chữ ký & Hash)",
            font=(FONT_FAMILY, 9, "bold"),
            bg=PILL_BLUE, fg="#FFFFFF",
            activebackground=PILL_BLUE_HOVER, activeforeground="#FFFFFF",
            relief="flat", bd=0, pady=8, cursor="hand2",
            command=self._handle_verify
        ).pack(fill="x", pady=(0, 12))

        # Verification Result Box
        self.verify_box = tk.Frame(
            right_card, bg="#F8FAFC", padx=12, pady=12,
            highlightbackground=BORDER_COLOR, highlightthickness=1
        )
        self.verify_box.pack(fill="x", pady=(0, 16))

        self.verify_badge_lbl = tk.Label(
            self.verify_box, text="Chưa chọn giao dịch",
            font=(FONT_FAMILY, 9, "bold"), fg=TEXT_MEDIUM, bg="#F8FAFC"
        )
        self.verify_badge_lbl.pack(anchor="w")

        self.verify_detail_lbl = tk.Label(
            self.verify_box,
            text="Nhấn vào một dòng giao dịch bên trái để xem chi tiết SHA-256 hash và chữ ký RSA-PSS.",
            font=("Consolas", 8), fg=TEXT_MEDIUM, bg="#F8FAFC",
            justify="left", wraplength=310
        )
        self.verify_detail_lbl.pack(anchor="w", pady=(6, 0))

        # Divider
        tk.Frame(right_card, bg=BORDER_COLOR, height=1).pack(fill="x", pady=(2, 14))

        # [DEMO] Tamper Amount Section
        tk.Label(
            right_card, text="⚠  [DEMO] Tamper Amount (Sửa DB trái phép)",
            font=(FONT_FAMILY, 10, "bold"), fg=BADGE_FRAUD_BG, bg=CARD_WHITE
        ).pack(anchor="w")
        tk.Label(
            right_card, text="Thay đổi số tiền trực tiếp trong DB mà không có Private Key để thấy Verify phát hiện Possible fraud (INVALID).",
            font=(FONT_FAMILY, 8), fg=TEXT_MUTED, bg=CARD_WHITE, wraplength=330, justify="left"
        ).pack(anchor="w", pady=(2, 8))

        tk.Label(
            right_card, text="Amount mới (New Tampered Amount)",
            font=(FONT_FAMILY, 9, "bold"), fg=TEXT_DARK, bg=CARD_WHITE
        ).pack(anchor="w", pady=(0, 4))

        tamp_box = tk.Frame(right_card, bg="#F8FAFC", highlightbackground=BORDER_COLOR, highlightthickness=1)
        tamp_box.pack(fill="x", pady=(0, 10))
        self.tamper_amount_var = tk.StringVar()
        tk.Entry(
            tamp_box, textvariable=self.tamper_amount_var,
            font=(FONT_FAMILY, 10), bg="#F8FAFC", fg=TEXT_DARK, relief="flat", bd=0
        ).pack(fill="x", padx=10, pady=7)

        self.tamper_msg_lbl = tk.Label(
            right_card, text="", font=(FONT_FAMILY, 8, "bold"),
            fg=BADGE_FRAUD_BG, bg=CARD_WHITE, wraplength=320, justify="left"
        )
        self.tamper_msg_lbl.pack(anchor="w", pady=(0, 6))

        tk.Button(
            right_card, text="⚠  Thực hiện Tamper Amount",
            font=(FONT_FAMILY, 9, "bold"),
            bg=BADGE_FRAUD_BG, fg="#FFFFFF",
            activebackground="#991B1B", activeforeground="#FFFFFF",
            relief="flat", bd=0, pady=8, cursor="hand2",
            command=self._handle_tamper
        ).pack(fill="x")

        self.refresh_data()

    def _set_filter(self, key: str):
        self.tx_filter = key
        for k, btn in self.tab_btns.items():
            if k == key:
                btn.config(fg=PRIMARY_BLUE, font=(FONT_FAMILY, 9, "bold"))
            else:
                btn.config(fg=TEXT_MEDIUM, font=(FONT_FAMILY, 9, "normal"))
        self.refresh_data()

    def refresh_data(self):
        for w in self.rows_frame.winfo_children():
            w.destroy()

        rows = services.list_transactions(self.current_user)
        q = (self.search_var.get().strip().lower() if self.search_var else "")

        filtered = []
        for r in rows:
            is_sender = (r["sender_username"] == self.current_user)
            if self.tx_filter == "incomes" and is_sender:
                continue
            if self.tx_filter == "expenses" and not is_sender:
                continue
            if q:
                haystack = f"{r['id']} {r['sender_username']} {r['receiver_username']} {r['timestamp']}".lower()
                if q not in haystack:
                    continue
            filtered.append(r)

        if not filtered:
            empty = tk.Frame(self.rows_frame, bg=CARD_WHITE, pady=36)
            empty.pack(fill="x")
            tk.Label(
                empty, text="Chưa có giao dịch nào cho bộ lọc này.",
                font=(FONT_FAMILY, 10), fg=TEXT_MUTED, bg=CARD_WHITE
            ).pack()
            return

        for idx, r in enumerate(filtered):
            self._create_tx_row(r)

        # Automatically select the first transaction if none selected
        if not self.tx_id_var.get().strip() and filtered:
            self._select_transaction(filtered[0]["id"], filtered[0]["amount"])

    def _create_tx_row(self, r):
        tx_id = r["id"]
        is_sender = (r["sender_username"] == self.current_user)
        counterparty = r["receiver_username"] if is_sender else r["sender_username"]
        direction_txt = f"{r['sender_username']}  →  {r['receiver_username']}"
        amount = float(r["amount"])
        valid, _, _ = services.verify_transaction(tx_id)

        row_frame = tk.Frame(self.rows_frame, bg=CARD_WHITE, pady=10, padx=6, cursor="hand2")
        row_frame.pack(fill="x")

        # Avatar circle via small canvas
        av_canvas = tk.Canvas(row_frame, width=38, height=38, bg=CARD_WHITE, highlightthickness=0)
        av_canvas.pack(side="left", padx=(0, 12))
        av_bg = "#FEE2E2" if not valid else "#DDD6FE"
        av_fg = "#991B1B" if not valid else "#3730A3"
        av_canvas.create_oval(2, 2, 36, 36, fill=av_bg, outline="")
        initials = "".join(p[0].upper() for p in counterparty.split()[:2]) or counterparty[:2].upper()
        av_canvas.create_text(19, 19, text=initials, font=(FONT_FAMILY, 9, "bold"), fill=av_fg)

        # Middle info: Name + TX ID + Timestamp
        mid = tk.Frame(row_frame, bg=CARD_WHITE)
        mid.pack(side="left", fill="x", expand=True)

        tk.Label(
            mid, text=f"{counterparty}   ({direction_txt})",
            font=(FONT_FAMILY, 10, "bold"), fg=TEXT_DARK, bg=CARD_WHITE, anchor="w"
        ).pack(fill="x")

        tk.Label(
            mid, text=f"{tx_id}   •   {r['timestamp']}",
            font=(FONT_FAMILY, 8), fg=TEXT_MUTED, bg=CARD_WHITE, anchor="w"
        ).pack(fill="x", pady=(2, 0))

        # Right side: Amount + Fraud/Valid badge
        right = tk.Frame(row_frame, bg=CARD_WHITE)
        right.pack(side="right", padx=(8, 4))

        amt_str = f"-${amount:,.2f}" if is_sender else f"+${amount:,.2f}"
        amt_col = TEXT_DARK if is_sender else TEXT_GREEN
        tk.Label(
            right, text=amt_str,
            font=(FONT_FAMILY, 10, "bold"), fg=amt_col, bg=CARD_WHITE, anchor="e"
        ).pack(anchor="e")

        if not valid:
            tk.Label(
                right, text=" Possible fraud ",
                font=(FONT_FAMILY, 8, "bold"),
                bg=BADGE_FRAUD_BG, fg=BADGE_FRAUD_FG, padx=6, pady=1
            ).pack(anchor="e", pady=(3, 0))
        else:
            tk.Label(
                right, text=" ✓ Verified ",
                font=(FONT_FAMILY, 8, "bold"),
                bg=BADGE_VALID_BG, fg=BADGE_VALID_FG, padx=6, pady=1
            ).pack(anchor="e", pady=(3, 0))

        # Divider
        tk.Frame(self.rows_frame, bg="#F1F5F9", height=1).pack(fill="x")

        # Click binding on row and children to inspect transaction
        def on_click(e, tid=tx_id, amt=amount):
            self._select_transaction(tid, amt)

        for widget in (row_frame, av_canvas, mid, right, *mid.winfo_children(), *right.winfo_children()):
            widget.bind("<Button-1>", on_click)

    def _select_transaction(self, tx_id: str, current_amt: float = None):
        self.selected_tx_id = tx_id
        self.tx_id_var.set(tx_id)
        if current_amt is not None:
            self.tamper_amount_var.set(str(current_amt))
        self.tamper_msg_lbl.config(text="")
        self._handle_verify()

    def _handle_verify(self):
        tx_id = self.tx_id_var.get().strip()
        if not tx_id:
            self.verify_badge_lbl.config(text="✗ Vui lòng nhập Transaction ID", fg=BADGE_FRAUD_BG)
            return

        valid, msg, details = services.verify_transaction(tx_id)
        if details is None:
            self.verify_badge_lbl.config(text=f"✗ {msg}", fg=BADGE_FRAUD_BG)
            self.verify_detail_lbl.config(text="")
            return

        if valid:
            self.verify_badge_lbl.config(text=f"✓ {msg}", fg=TEXT_GREEN)
        else:
            self.verify_badge_lbl.config(text=f"⚠ Possible fraud — {msg}", fg=BADGE_FRAUD_BG)

        info_lines = [
            f"Transaction ID : {tx_id}",
            f"Hash Match     : {'✓ OK' if details['hash_ok'] else '✗ MISMATCH (Data altered!)'}",
            f"RSA Signature  : {'✓ OK' if details['signature_ok'] else '✗ INVALID SIGNATURE'}",
            f"Stored Hash    : {details['stored_hash'][:28]}...",
            f"Recalc Hash    : {details['recalculated_hash'][:28]}...",
        ]
        self.verify_detail_lbl.config(text="\n".join(info_lines))

    def _handle_tamper(self):
        tx_id = self.tx_id_var.get().strip()
        if not tx_id:
            self.tamper_msg_lbl.config(text="✗ Vui lòng chọn hoặc nhập Transaction ID.", fg=BADGE_FRAUD_BG)
            return

        raw_amt = self.tamper_amount_var.get().strip().replace(",", "")
        try:
            new_amount = float(raw_amt)
        except ValueError:
            self.tamper_msg_lbl.config(text="✗ Số tiền mới không hợp lệ.", fg=BADGE_FRAUD_BG)
            return

        changed = services.tamper_transaction(tx_id, new_amount)
        if changed:
            self.tamper_msg_lbl.config(
                text=f"⚠ Đã tamper số tiền giao dịch {tx_id} thành ${new_amount:,.2f}!",
                fg=BADGE_FRAUD_BG
            )
            self._handle_verify()
            self.refresh_data()
            self.on_data_changed()
        else:
            self.tamper_msg_lbl.config(text="✗ Không tìm thấy giao dịch trong DB.", fg=BADGE_FRAUD_BG)
