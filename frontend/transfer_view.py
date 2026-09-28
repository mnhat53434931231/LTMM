import tkinter as tk
from database import fetch_all
import services
from .theme import (
    BG_MAIN, CARD_WHITE, CARD_SOFT_BLUE, PRIMARY_BLUE, PILL_BLUE, PILL_BLUE_HOVER,
    SIDEBAR_ACTIVE_BG, BORDER_COLOR, TEXT_DARK, TEXT_MEDIUM, TEXT_MUTED,
    TEXT_GREEN, FONT_FAMILY, create_rounded_rect
)


class TransferView(tk.Frame):
    """
    Sidebar 'Transfer' View:
    - Transfer money to another user (RSA-PSS digital signature via services.transfer)
    - Deposit money into current user's wallet (via services.deposit)
    """

    def __init__(self, parent, current_user: str, on_data_changed, on_navigate):
        super().__init__(parent, bg=BG_MAIN)
        self.current_user = current_user
        self.on_data_changed = on_data_changed
        self.on_navigate = on_navigate
        self._build_ui()

    def _build_ui(self):
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        # =====================================================================
        # TOP BALANCE & CRYPTO KEY BANNER
        # =====================================================================
        banner = tk.Frame(self, bg=CARD_SOFT_BLUE, padx=22, pady=16)
        banner.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 16))

        left_b = tk.Frame(banner, bg=CARD_SOFT_BLUE)
        left_b.pack(side="left")
        tk.Label(
            left_b, text="Available Balance",
            font=(FONT_FAMILY, 10, "bold"), fg=TEXT_MEDIUM, bg=CARD_SOFT_BLUE
        ).pack(anchor="w")
        self.bal_lbl = tk.Label(
            left_b, text="$0.00",
            font=(FONT_FAMILY, 24, "bold"), fg=TEXT_DARK, bg=CARD_SOFT_BLUE
        )
        self.bal_lbl.pack(anchor="w", pady=(2, 0))

        right_b = tk.Frame(banner, bg=CARD_SOFT_BLUE)
        right_b.pack(side="right")
        tk.Label(
            right_b, text="🔐 Digital Signature Engine: SHA-256 + RSA-PSS (2048-bit)",
            font=(FONT_FAMILY, 9, "bold"), fg=PRIMARY_BLUE, bg=CARD_SOFT_BLUE
        ).pack(anchor="e")
        self.key_lbl = tk.Label(
            right_b, text="",
            font=(FONT_FAMILY, 8), fg=TEXT_MUTED, bg=CARD_SOFT_BLUE
        )
        self.key_lbl.pack(anchor="e", pady=(4, 0))

        # =====================================================================
        # LEFT CARD: TRANSFER MONEY (CHUYỂN TIỀN)
        # =====================================================================
        tx_card = tk.Frame(
            self, bg=CARD_WHITE, padx=24, pady=22,
            highlightbackground=BORDER_COLOR, highlightthickness=1
        )
        tx_card.grid(row=1, column=0, sticky="nsew", padx=(0, 10))

        tk.Label(
            tx_card, text="⇄  Transfer Money (Chuyển tiền)",
            font=(FONT_FAMILY, 14, "bold"), fg=TEXT_DARK, bg=CARD_WHITE
        ).pack(anchor="w")
        tk.Label(
            tx_card, text="Mỗi giao dịch chuyển tiền được băm SHA-256 và ký số bằng RSA Private Key của bạn.",
            font=(FONT_FAMILY, 9), fg=TEXT_MUTED, bg=CARD_WHITE, wraplength=380, justify="left"
        ).pack(anchor="w", pady=(2, 16))

        # Recipient input
        tk.Label(
            tx_card, text="Người nhận (Receiver Username)",
            font=(FONT_FAMILY, 10, "bold"), fg=TEXT_DARK, bg=CARD_WHITE
        ).pack(anchor="w", pady=(0, 4))

        rec_box = tk.Frame(tx_card, bg="#F8FAFC", highlightbackground=BORDER_COLOR, highlightthickness=1)
        rec_box.pack(fill="x", pady=(0, 8))
        self.receiver_var = tk.StringVar()
        self.receiver_entry = tk.Entry(
            rec_box, textvariable=self.receiver_var,
            font=(FONT_FAMILY, 11), bg="#F8FAFC", fg=TEXT_DARK, relief="flat", bd=0
        )
        self.receiver_entry.pack(fill="x", padx=12, pady=8)

        # Quick recipient chips from DB
        self.recipients_frame = tk.Frame(tx_card, bg=CARD_WHITE)
        self.recipients_frame.pack(fill="x", pady=(0, 14))

        # Transfer Amount input
        tk.Label(
            tx_card, text="Số tiền chuyển (Amount)",
            font=(FONT_FAMILY, 10, "bold"), fg=TEXT_DARK, bg=CARD_WHITE
        ).pack(anchor="w", pady=(0, 4))

        amt_box = tk.Frame(tx_card, bg="#F8FAFC", highlightbackground=BORDER_COLOR, highlightthickness=1)
        amt_box.pack(fill="x", pady=(0, 8))
        self.tx_amount_var = tk.StringVar()
        self.tx_amount_entry = tk.Entry(
            amt_box, textvariable=self.tx_amount_var,
            font=(FONT_FAMILY, 11), bg="#F8FAFC", fg=TEXT_DARK, relief="flat", bd=0
        )
        self.tx_amount_entry.pack(fill="x", padx=12, pady=8)

        # Quick amount chips
        q_amt = tk.Frame(tx_card, bg=CARD_WHITE)
        q_amt.pack(fill="x", pady=(0, 14))
        for val in (10, 50, 100, 500, 1000):
            tk.Button(
                q_amt, text=f"${val:,}",
                font=(FONT_FAMILY, 8, "bold"),
                bg="#F1F5F9", fg=TEXT_MEDIUM,
                activebackground=SIDEBAR_ACTIVE_BG, activeforeground=PRIMARY_BLUE,
                relief="flat", bd=0, padx=8, pady=3, cursor="hand2",
                command=lambda v=val: self.tx_amount_var.set(str(v))
            ).pack(side="left", padx=(0, 6))

        self.tx_status_lbl = tk.Label(
            tx_card, text="", font=(FONT_FAMILY, 9, "bold"),
            fg=TEXT_GREEN, bg=CARD_WHITE, wraplength=380, justify="left"
        )
        self.tx_status_lbl.pack(anchor="w", pady=(0, 10))

        tk.Button(
            tx_card, text="⇄  Xác nhận Ký số & Chuyển tiền",
            font=(FONT_FAMILY, 10, "bold"),
            bg=PILL_BLUE, fg="#FFFFFF",
            activebackground=PILL_BLUE_HOVER, activeforeground="#FFFFFF",
            relief="flat", bd=0, pady=10, cursor="hand2",
            command=self._handle_transfer
        ).pack(fill="x")

        # =====================================================================
        # RIGHT CARD: DEPOSIT MONEY (NẠP TIỀN) & CRYPTO FLOW INFO
        # =====================================================================
        dep_card = tk.Frame(
            self, bg=CARD_WHITE, padx=24, pady=22,
            highlightbackground=BORDER_COLOR, highlightthickness=1
        )
        dep_card.grid(row=1, column=1, sticky="nsew", padx=(10, 0))

        tk.Label(
            dep_card, text="＋  Deposit Money (Nạp tiền vào ví)",
            font=(FONT_FAMILY, 14, "bold"), fg=TEXT_DARK, bg=CARD_WHITE
        ).pack(anchor="w")
        tk.Label(
            dep_card, text="Nạp thêm số dư vào tài khoản hiện tại để thực hiện giao dịch.",
            font=(FONT_FAMILY, 9), fg=TEXT_MUTED, bg=CARD_WHITE, wraplength=380, justify="left"
        ).pack(anchor="w", pady=(2, 16))

        tk.Label(
            dep_card, text="Số tiền nạp (Deposit Amount)",
            font=(FONT_FAMILY, 10, "bold"), fg=TEXT_DARK, bg=CARD_WHITE
        ).pack(anchor="w", pady=(0, 4))

        dep_box = tk.Frame(dep_card, bg="#F8FAFC", highlightbackground=BORDER_COLOR, highlightthickness=1)
        dep_box.pack(fill="x", pady=(0, 8))
        self.dep_amount_var = tk.StringVar()
        self.dep_amount_entry = tk.Entry(
            dep_box, textvariable=self.dep_amount_var,
            font=(FONT_FAMILY, 11), bg="#F8FAFC", fg=TEXT_DARK, relief="flat", bd=0
        )
        self.dep_amount_entry.pack(fill="x", padx=12, pady=8)

        # Quick deposit chips
        q_dep = tk.Frame(dep_card, bg=CARD_WHITE)
        q_dep.pack(fill="x", pady=(0, 14))
        for val in (100, 1000, 5000, 10000, 50000):
            tk.Button(
                q_dep, text=f"+${val:,}",
                font=(FONT_FAMILY, 8, "bold"),
                bg="#F1F5F9", fg=TEXT_MEDIUM,
                activebackground=SIDEBAR_ACTIVE_BG, activeforeground=PRIMARY_BLUE,
                relief="flat", bd=0, padx=8, pady=3, cursor="hand2",
                command=lambda v=val: self.dep_amount_var.set(str(v))
            ).pack(side="left", padx=(0, 6))

        self.dep_status_lbl = tk.Label(
            dep_card, text="", font=(FONT_FAMILY, 9, "bold"),
            fg=TEXT_GREEN, bg=CARD_WHITE, wraplength=380, justify="left"
        )
        self.dep_status_lbl.pack(anchor="w", pady=(0, 10))

        tk.Button(
            dep_card, text="＋  Nạp tiền ngay (Deposit)",
            font=(FONT_FAMILY, 10, "bold"),
            bg="#0F172A", fg="#FFFFFF",
            activebackground="#1E293B", activeforeground="#FFFFFF",
            relief="flat", bd=0, pady=10, cursor="hand2",
            command=self._handle_deposit
        ).pack(fill="x", pady=(0, 18))

        # Last signed transaction box
        info_box = tk.Frame(dep_card, bg="#F8FAFC", padx=14, pady=12, highlightbackground=BORDER_COLOR, highlightthickness=1)
        info_box.pack(fill="x")
        tk.Label(
            info_box, text="Luồng Mật Mã Giao Dịch (Cryptographic Flow):",
            font=(FONT_FAMILY, 9, "bold"), fg=TEXT_DARK, bg="#F8FAFC"
        ).pack(anchor="w")
        self.crypto_log_lbl = tk.Label(
            info_box,
            text="1. Canonical: sender|receiver|amount|timestamp|tx_id\n"
                 "2. Hash: SHA-256 digest (64 hex chars)\n"
                 "3. Sign: RSA-PSS (MGF1-SHA256) với Private Key người gửi\n"
                 "4. Verify: Kiểm tra bằng Public Key ở tab Transactions",
            font=("Consolas", 8), fg=TEXT_MEDIUM, bg="#F8FAFC", justify="left"
        )
        self.crypto_log_lbl.pack(anchor="w", pady=(4, 0))

        self.refresh_data()

    def focus_deposit(self):
        self.dep_amount_entry.focus_set()

    def refresh_data(self):
        bal = services.get_balance(self.current_user)
        if bal is None:
            bal = 0.0
        self.bal_lbl.config(text=f"${bal:,.2f}")

        u = services.get_user(self.current_user)
        if u:
            self.key_lbl.config(text=f"Private Key: {u['private_key_path']}  |  Public Key: {u['public_key_path']}")

        # Populate other users as quick recipient chips
        for w in self.recipients_frame.winfo_children():
            w.destroy()
        try:
            others = fetch_all(
                "SELECT username FROM users WHERE username != ? ORDER BY id ASC LIMIT 6",
                (self.current_user,)
            )
        except Exception:
            others = []

        if others:
            tk.Label(
                self.recipients_frame, text="Chọn nhanh người nhận:",
                font=(FONT_FAMILY, 8), fg=TEXT_MUTED, bg=CARD_WHITE
            ).pack(side="left", padx=(0, 6))
            for r in others:
                uname = r["username"]
                tk.Button(
                    self.recipients_frame, text=f"@{uname}",
                    font=(FONT_FAMILY, 8, "bold"),
                    bg=SIDEBAR_ACTIVE_BG, fg=PRIMARY_BLUE,
                    activebackground=PRIMARY_BLUE, activeforeground="#FFFFFF",
                    relief="flat", bd=0, padx=8, pady=2, cursor="hand2",
                    command=lambda name=uname: self.receiver_var.set(name)
                ).pack(side="left", padx=(0, 4))

    def _handle_transfer(self):
        receiver = self.receiver_var.get().strip()
        raw_amt = self.tx_amount_var.get().strip().replace(",", "")
        try:
            amount = float(raw_amt)
        except ValueError:
            self.tx_status_lbl.config(text="✗ Số tiền không hợp lệ.", fg="#DC2626")
            return

        ok, msg, tx_id = services.transfer(self.current_user, receiver, amount)
        if ok:
            self.tx_status_lbl.config(text=f"✓ {msg}\nMã giao dịch: {tx_id}", fg=TEXT_GREEN)
            self.tx_amount_var.set("")
            self.crypto_log_lbl.config(
                text=f"✓ Đã ký số thành công giao dịch {tx_id}\n"
                     f"• Người gửi: {self.current_user} -> Người nhận: {receiver}\n"
                     f"• Số tiền: ${amount:,.2f}\n"
                     f"• Trạng thái: SIGNED (RSA-PSS + SHA-256)"
            )
            self.refresh_data()
            self.on_data_changed()
        else:
            self.tx_status_lbl.config(text=f"✗ {msg}", fg="#DC2626")

    def _handle_deposit(self):
        raw_amt = self.dep_amount_var.get().strip().replace(",", "")
        try:
            amount = float(raw_amt)
        except ValueError:
            self.dep_status_lbl.config(text="✗ Số tiền nạp không hợp lệ.", fg="#DC2626")
            return

        ok, msg = services.deposit(self.current_user, amount)
        if ok:
            self.dep_status_lbl.config(text=f"✓ {msg}", fg=TEXT_GREEN)
            self.dep_amount_var.set("")
            self.refresh_data()
            self.on_data_changed()
        else:
            self.dep_status_lbl.config(text=f"✗ {msg}", fg="#DC2626")
