import ctypes
import tkinter as tk
from .theme import (
    BG_MAIN, BG_SIDEBAR, SIDEBAR_ACTIVE_BG, SIDEBAR_HOVER_BG, BORDER_COLOR,
    PRIMARY_BLUE, BRAND_BLUE, SEARCH_BG, TEXT_DARK, TEXT_MEDIUM, TEXT_MUTED,
    FONT_FAMILY, create_rounded_rect
)
from .auth_view import AuthView
from .home_view import HomeView
from .transfer_view import TransferView
from .transactions_view import TransactionsView


class EBankApp(tk.Tk):
    """Main Window Application for E Bank Crypto E-Wallet."""

    def __init__(self):
        # Enable High-DPI crisp rendering on Windows
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            pass

        super().__init__()
        self.title("E Bank — Cryptographic E-Wallet")
        self.geometry("1280x820")
        self.minsize(1100, 740)
        self.configure(bg=BG_MAIN)

        self.current_user = None
        self.active_tab = "home"
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self._on_search_changed())

        self.root_container = tk.Frame(self, bg=BG_MAIN)
        self.root_container.pack(fill="both", expand=True)

        self.show_auth()

    def show_auth(self):
        self.current_user = None
        for w in self.root_container.winfo_children():
            w.destroy()

        auth = AuthView(self.root_container, on_login_success=self.show_dashboard)
        auth.pack(fill="both", expand=True)

    def show_dashboard(self, username: str):
        self.current_user = username
        self.active_tab = "home"

        for w in self.root_container.winfo_children():
            w.destroy()

        # Main 2-column layout: Left Sidebar (fixed width 230px) | Right Main Area
        self.root_container.columnconfigure(0, weight=0, minsize=230)
        self.root_container.columnconfigure(1, weight=1)
        self.root_container.rowconfigure(0, weight=1)

        # =====================================================================
        # 1. LEFT SIDEBAR (Home, Transfer, Transactions)
        # =====================================================================
        self.sidebar = tk.Frame(self.root_container, bg=BG_SIDEBAR, width=230)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)

        # Subtle vertical border on right edge of sidebar
        tk.Frame(self.sidebar, bg=BORDER_COLOR, width=1).pack(side="right", fill="y")

        sidebar_inner = tk.Frame(self.sidebar, bg=BG_SIDEBAR)
        sidebar_inner.pack(side="left", fill="both", expand=True)

        # Brand Logo "E Bank"
        logo_frame = tk.Frame(sidebar_inner, bg=BG_SIDEBAR, padx=26, pady=24)
        logo_frame.pack(fill="x")
        tk.Label(
            logo_frame, text="E Bank",
            font=(FONT_FAMILY, 20, "bold"), fg=BRAND_BLUE, bg=BG_SIDEBAR, anchor="w"
        ).pack(fill="x")

        # Navigation Canvas for pill-shaped items matching the screenshot
        self.nav_canvas = tk.Canvas(
            sidebar_inner, width=215, height=260,
            bg=BG_SIDEBAR, highlightthickness=0
        )
        self.nav_canvas.pack(fill="x", pady=(8, 0))

        # Divider line in sidebar as seen in screenshot
        tk.Frame(sidebar_inner, bg=BORDER_COLOR, height=1).pack(fill="x", padx=24, pady=16)

        # Bottom Logout / Switch Account button
        logout_frame = tk.Frame(sidebar_inner, bg=BG_SIDEBAR, padx=20, pady=20)
        logout_frame.pack(side="bottom", fill="x")
        tk.Button(
            logout_frame, text="⎋  Đăng xuất (Switch User)",
            font=(FONT_FAMILY, 9, "bold"),
            bg="#E2E8F0", fg=TEXT_DARK,
            activebackground="#CBD5E1", activeforeground=TEXT_DARK,
            relief="flat", bd=0, pady=8, cursor="hand2",
            command=self.show_auth
        ).pack(fill="x")

        # =====================================================================
        # 2. RIGHT MAIN AREA (Header + Active View Content)
        # =====================================================================
        main_area = tk.Frame(self.root_container, bg=BG_MAIN, padx=28, pady=18)
        main_area.grid(row=0, column=1, sticky="nsew")
        main_area.columnconfigure(0, weight=1)
        main_area.rowconfigure(1, weight=1)

        # --- TOP HEADER BAR ---
        header = tk.Frame(main_area, bg=BG_MAIN)
        header.grid(row=0, column=0, sticky="ew", pady=(0, 16))

        # Left: "Welcome, <user>"
        welcome_name = "Eda" if self.current_user.lower() == "eda" else self.current_user
        self.welcome_lbl = tk.Label(
            header, text=f"Welcome, {welcome_name}",
            font=(FONT_FAMILY, 21), fg=TEXT_DARK, bg=BG_MAIN
        )
        self.welcome_lbl.pack(side="left")

        # Right: Profile + Notification bell + Search pill
        profile_frame = tk.Frame(header, bg=BG_MAIN)
        profile_frame.pack(side="right")

        # Search Bar Pill (Canvas)
        search_canvas = tk.Canvas(profile_frame, width=265, height=40, bg=BG_MAIN, highlightthickness=0)
        search_canvas.pack(side="left", padx=(0, 14))
        create_rounded_rect(search_canvas, 2, 2, 263, 38, r=18, fill=SEARCH_BG, outline="")
        # Magnifying glass icon
        search_canvas.create_oval(16, 13, 26, 23, outline=TEXT_DARK, width=1.5)
        search_canvas.create_line(25, 22, 30, 27, fill=TEXT_DARK, width=1.5)

        self.search_entry = tk.Entry(
            search_canvas, textvariable=self.search_var,
            font=(FONT_FAMILY, 10), bg=SEARCH_BG, fg=TEXT_DARK,
            relief="flat", bd=0, insertbackground=TEXT_DARK
        )
        search_canvas.create_window(145, 20, window=self.search_entry, width=200, height=22)

        # Placeholder handling for Search
        self._search_placeholder = True
        self.search_entry.insert(0, "Search")
        self.search_entry.config(fg=TEXT_MUTED)

        def on_search_focus_in(e):
            if self._search_placeholder:
                self._search_placeholder = False
                self.search_entry.delete(0, "end")
                self.search_entry.config(fg=TEXT_DARK)

        def on_search_focus_out(e):
            if not self.search_entry.get().strip():
                self._search_placeholder = True
                self.search_entry.delete(0, "end")
                self.search_entry.insert(0, "Search")
                self.search_entry.config(fg=TEXT_MUTED)

        self.search_entry.bind("<FocusIn>", on_search_focus_in)
        self.search_entry.bind("<FocusOut>", on_search_focus_out)

        # Notification Bell Circle
        bell_canvas = tk.Canvas(profile_frame, width=40, height=40, bg=BG_MAIN, highlightthickness=0, cursor="hand2")
        bell_canvas.pack(side="left", padx=(0, 14))
        bell_canvas.create_oval(2, 2, 38, 38, fill=SEARCH_BG, outline="")
        bell_canvas.create_text(20, 20, text="🔔", font=(FONT_FAMILY, 11), fill=TEXT_DARK)
        bell_canvas.bind("<Button-1>", lambda e: self.navigate("transactions"))

        # User Profile Avatar + Full Name
        user_chip = tk.Frame(profile_frame, bg=BG_MAIN, cursor="hand2")
        user_chip.pack(side="left")

        av_c = tk.Canvas(user_chip, width=38, height=38, bg=BG_MAIN, highlightthickness=0)
        av_c.pack(side="left", padx=(0, 8))
        av_c.create_oval(2, 2, 36, 36, fill="#CBD5E1", outline="#94A3B8", width=1)
        # Stylish avatar silhouette / initial
        initials = self.current_user[:1].upper()
        av_c.create_oval(13, 9, 25, 21, fill="#334155", outline="")
        av_c.create_arc(7, 21, 31, 41, start=0, extent=180, fill="#475569", outline="")
        av_c.create_text(19, 15, text=initials, font=(FONT_FAMILY, 7, "bold"), fill="#FFFFFF")

        full_display = "Eda Tunca" if self.current_user.lower() == "eda" else self.current_user
        tk.Label(
            user_chip, text=full_display,
            font=(FONT_FAMILY, 9, "bold"), fg=TEXT_DARK, bg=BG_MAIN
        ).pack(side="left")

        # --- MAIN CONTENT STACK ---
        self.content_frame = tk.Frame(main_area, bg=BG_MAIN)
        self.content_frame.grid(row=1, column=0, sticky="nsew")
        self.content_frame.columnconfigure(0, weight=1)
        self.content_frame.rowconfigure(0, weight=1)

        # Instantiate the 3 views: Home, Transfer, Transactions
        self.views = {
            "home": HomeView(
                self.content_frame,
                current_user=self.current_user,
                on_navigate=self.navigate,
                search_var=self._get_clean_search_var()
            ),
            "transfer": TransferView(
                self.content_frame,
                current_user=self.current_user,
                on_data_changed=self._refresh_all_views,
                on_navigate=self.navigate
            ),
            "transactions": TransactionsView(
                self.content_frame,
                current_user=self.current_user,
                on_data_changed=self._refresh_all_views,
                search_var=self._get_clean_search_var()
            ),
        }

        for v in self.views.values():
            v.grid(row=0, column=0, sticky="nsew")

        self.navigate("home")

    def _get_clean_search_var(self):
        """Proxy StringVar that ignores placeholder 'Search'."""
        proxy = tk.StringVar(value="")
        self._clean_search_proxy = proxy
        return proxy

    def _on_search_changed(self):
        if not hasattr(self, "_clean_search_proxy"):
            return
        val = self.search_var.get()
        if getattr(self, "_search_placeholder", False) or val == "Search":
            self._clean_search_proxy.set("")
        else:
            self._clean_search_proxy.set(val)

        if hasattr(self, "views"):
            self.views["home"]._draw_transactions_card()
            self.views["transactions"].refresh_data()

    def _draw_sidebar_nav(self):
        c = self.nav_canvas
        c.delete("all")

        nav_items = [
            ("home", "Home", "⌂"),
            ("transfer", "Transfer", "⇄"),
            ("transactions", "Transactions", "☰"),
        ]

        y_start = 12
        item_h = 46
        gap = 8

        for idx, (key, label, icon_char) in enumerate(nav_items):
            y1 = y_start + idx * (item_h + gap)
            y2 = y1 + item_h
            is_active = (self.active_tab == key)
            tag = f"nav_{key}"

            if is_active:
                # Active pill shape matching screenshot (light lavender-blue pill rounded on right)
                create_rounded_rect(
                    c, -14, y1, 202, y2, r=22,
                    fill=SIDEBAR_ACTIVE_BG, outline="", tags=(tag,)
                )
                fg_color = PRIMARY_BLUE
                font_weight = "bold"
            else:
                create_rounded_rect(
                    c, -14, y1, 202, y2, r=22,
                    fill=BG_SIDEBAR, outline="", tags=(tag, f"bg_{key}")
                )
                fg_color = TEXT_DARK
                font_weight = "normal"

            # Draw custom crisp icon for each sidebar item
            ix, iy = 32, (y1 + y2) / 2
            if key == "home":
                # House icon
                c.create_polygon(
                    ix, iy - 7, ix - 8, iy, ix - 5, iy, ix - 5, iy + 7,
                    ix - 1, iy + 7, ix - 1, iy + 2, ix + 1, iy + 2, ix + 1, iy + 7,
                    ix + 5, iy + 7, ix + 5, iy, ix + 8, iy,
                    fill=fg_color, outline=fg_color, width=1, tags=(tag,)
                )
            elif key == "transfer":
                # Two horizontal transfer arrows ⇄
                c.create_line(ix - 7, iy - 3, ix + 6, iy - 3, fill=fg_color, width=1.8, tags=(tag,))
                c.create_polygon(ix + 3, iy - 6, ix + 8, iy - 3, ix + 3, iy, fill=fg_color, outline="", tags=(tag,))
                c.create_line(ix - 6, iy + 3, ix + 7, iy + 3, fill=fg_color, width=1.8, tags=(tag,))
                c.create_polygon(ix - 3, iy, ix - 8, iy + 3, ix - 3, iy + 6, fill=fg_color, outline="", tags=(tag,))
            elif key == "transactions":
                # Transactions icon (arrows + list lines)
                c.create_line(ix - 7, iy - 4, ix + 6, iy - 4, fill=fg_color, width=1.8, tags=(tag,))
                c.create_polygon(ix + 3, iy - 7, ix + 8, iy - 4, ix + 3, iy - 1, fill=fg_color, outline="", tags=(tag,))
                c.create_line(ix - 6, iy + 4, ix + 7, iy + 4, fill=fg_color, width=1.8, tags=(tag,))
                c.create_polygon(ix - 3, iy + 1, ix - 8, iy + 4, ix - 3, iy + 7, fill=fg_color, outline="", tags=(tag,))

            c.create_text(
                54, (y1 + y2) / 2,
                text=label,
                font=(FONT_FAMILY, 10, font_weight),
                fill=fg_color, anchor="w", tags=(tag,)
            )

            c.tag_bind(tag, "<Button-1>", lambda e, k=key: self.navigate(k))
            c.tag_bind(tag, "<Enter>", lambda e: c.config(cursor="hand2"))
            c.tag_bind(tag, "<Leave>", lambda e: c.config(cursor=""))

    def navigate(self, target: str):
        focus_dep = False
        if target == "deposit":
            target = "transfer"
            focus_dep = True

        self.active_tab = target
        self._draw_sidebar_nav()

        view = self.views.get(target)
        if view:
            view.refresh_data()
            view.tkraise()
            if focus_dep and hasattr(view, "focus_deposit"):
                view.focus_deposit()

    def _refresh_all_views(self):
        for v in self.views.values():
            v.refresh_data()


def run_app():
    app = EBankApp()
    app.mainloop()
