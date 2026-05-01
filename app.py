"""
Farmers Insurance – desktop application
Built with CustomTkinter for a modern dark-theme UI.
"""

import customtkinter as ctk
from tkinter import messagebox
import database as db
from datetime import date, datetime

# ── Palette ──────────────────────────────────────────────────────────────────
C = {
    "bg":          "#161618",
    "sidebar":     "#1C1C1E",
    "card":        "#2C2C2E",
    "card2":       "#3A3A3C",
    "border":      "#3A3A3C",
    "green":       "#34A853",
    "green_dark":  "#1E7E34",
    "green_light": "#81C784",
    "amber":       "#FFA726",
    "blue":        "#4A9EFF",
    "red":         "#FF5252",
    "text":        "#F5F5F5",
    "muted":       "#8E8E93",
    "white":       "#FFFFFF",
}

STATUS_COLOR = {
    "Pending":      C["amber"],
    "Under Review": C["blue"],
    "Approved":     C["green"],
    "Rejected":     C["red"],
}

CROP_TYPES = [
    "Wheat", "Corn / Maize", "Rice", "Soybeans", "Cotton",
    "Vegetables", "Fruits / Orchards", "Hay / Forage", "Other",
]

ISSUE_TYPES = [
    "Drought / Lack of Water", "Flood / Excess Water", "Frost / Freeze Damage",
    "Storm / Hail Damage", "Pest Infestation", "Disease / Blight",
    "Poor Germination", "Soil Contamination", "Wildfire Damage", "Other",
]

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")


# ── Reusable widgets ──────────────────────────────────────────────────────────

class Card(ctk.CTkFrame):
    def __init__(self, master, **kw):
        kw.setdefault("fg_color", C["card"])
        kw.setdefault("corner_radius", 14)
        super().__init__(master, **kw)


class SectionLabel(ctk.CTkLabel):
    def __init__(self, master, text, **kw):
        kw.setdefault("font", ctk.CTkFont(size=11, weight="normal"))
        kw.setdefault("text_color", C["muted"])
        super().__init__(master, text=text.upper(), **kw)


class Heading(ctk.CTkLabel):
    def __init__(self, master, text, size=22, **kw):
        kw.setdefault("font", ctk.CTkFont(size=size, weight="bold"))
        kw.setdefault("text_color", C["white"])
        super().__init__(master, text=text, **kw)


class FieldLabel(ctk.CTkLabel):
    def __init__(self, master, text, **kw):
        kw.setdefault("font", ctk.CTkFont(size=13))
        kw.setdefault("text_color", C["muted"])
        super().__init__(master, text=text, **kw)


class ModernEntry(ctk.CTkEntry):
    def __init__(self, master, placeholder="", **kw):
        kw.setdefault("fg_color", C["card2"])
        kw.setdefault("border_color", C["border"])
        kw.setdefault("text_color", C["text"])
        kw.setdefault("placeholder_text_color", C["muted"])
        kw.setdefault("height", 42)
        kw.setdefault("corner_radius", 8)
        kw.setdefault("font", ctk.CTkFont(size=14))
        super().__init__(master, placeholder_text=placeholder, **kw)


class PrimaryButton(ctk.CTkButton):
    def __init__(self, master, text, command=None, **kw):
        kw.setdefault("fg_color", C["green"])
        kw.setdefault("hover_color", C["green_dark"])
        kw.setdefault("text_color", C["white"])
        kw.setdefault("height", 44)
        kw.setdefault("corner_radius", 10)
        kw.setdefault("font", ctk.CTkFont(size=14, weight="bold"))
        super().__init__(master, text=text, command=command, **kw)


class GhostButton(ctk.CTkButton):
    def __init__(self, master, text, command=None, **kw):
        kw.setdefault("fg_color", "transparent")
        kw.setdefault("hover_color", C["card2"])
        kw.setdefault("text_color", C["muted"])
        kw.setdefault("height", 40)
        kw.setdefault("corner_radius", 8)
        kw.setdefault("font", ctk.CTkFont(size=13))
        super().__init__(master, text=text, command=command, **kw)


class StatCard(Card):
    def __init__(self, master, label, value, color=None, **kw):
        super().__init__(master, **kw)
        color = color or C["green"]
        self.configure(border_width=1, border_color=C["border"])
        ctk.CTkLabel(self, text=label, font=ctk.CTkFont(size=12),
                     text_color=C["muted"]).pack(anchor="w", padx=18, pady=(16, 2))
        ctk.CTkLabel(self, text=str(value), font=ctk.CTkFont(size=30, weight="bold"),
                     text_color=color).pack(anchor="w", padx=18, pady=(0, 16))


# ── Login / Register pages ────────────────────────────────────────────────────

class LoginPage(ctk.CTkFrame):
    def __init__(self, master, on_login, on_go_register):
        super().__init__(master, fg_color=C["bg"], corner_radius=0)
        self._on_login = on_login

        # ── left panel ──
        left = ctk.CTkFrame(self, fg_color=C["green"], corner_radius=0, width=340)
        left.pack(side="left", fill="y")
        left.pack_propagate(False)

        ctk.CTkLabel(left, text="🌾", font=ctk.CTkFont(size=72)).pack(pady=(90, 8))
        ctk.CTkLabel(left, text="FarmSure",
                     font=ctk.CTkFont(size=34, weight="bold"),
                     text_color=C["white"]).pack()
        ctk.CTkLabel(left, text="Crop Insurance Portal",
                     font=ctk.CTkFont(size=15),
                     text_color="#C8E6C9").pack(pady=(4, 0))

        ctk.CTkLabel(left, text="Protecting farmers,\none harvest at a time.",
                     font=ctk.CTkFont(size=13), text_color="#A5D6A7",
                     justify="center", wraplength=240).pack(pady=(40, 0))

        # ── right panel ──
        right = ctk.CTkFrame(self, fg_color=C["bg"], corner_radius=0)
        right.pack(side="right", fill="both", expand=True)

        form = ctk.CTkFrame(right, fg_color="transparent")
        form.place(relx=0.5, rely=0.5, anchor="center")
        form.configure(width=340)

        Heading(form, "Welcome back", size=26).pack(anchor="w", pady=(0, 4))
        ctk.CTkLabel(form, text="Sign in to your account",
                     font=ctk.CTkFont(size=14), text_color=C["muted"]).pack(anchor="w", pady=(0, 28))

        FieldLabel(form, "Email address").pack(anchor="w")
        self._email = ModernEntry(form, placeholder="you@example.com", width=340)
        self._email.pack(pady=(4, 14))

        FieldLabel(form, "Password").pack(anchor="w")
        self._pw = ModernEntry(form, placeholder="••••••••", show="•", width=340)
        self._pw.pack(pady=(4, 24))

        self._err = ctk.CTkLabel(form, text="", text_color=C["red"],
                                 font=ctk.CTkFont(size=12))
        self._err.pack(pady=(0, 8))

        PrimaryButton(form, "Sign In", command=self._submit, width=340).pack()

        row = ctk.CTkFrame(form, fg_color="transparent")
        row.pack(pady=(16, 0))
        ctk.CTkLabel(row, text="New to FarmSure?",
                     font=ctk.CTkFont(size=13), text_color=C["muted"]).pack(side="left")
        ctk.CTkButton(row, text=" Create account", fg_color="transparent",
                      hover_color=C["bg"], text_color=C["green"],
                      font=ctk.CTkFont(size=13, weight="bold"),
                      command=on_go_register).pack(side="left")

        # bind Enter key
        self._pw.bind("<Return>", lambda e: self._submit())
        self._email.bind("<Return>", lambda e: self._pw.focus())

    def _submit(self):
        email = self._email.get().strip()
        password = self._pw.get()
        if not email or not password:
            self._err.configure(text="Please fill in all fields.")
            return
        user, err = db.login_user(email, password)
        if err:
            self._err.configure(text=err)
        else:
            self._err.configure(text="")
            self._on_login(user)

    def clear(self):
        self._email.delete(0, "end")
        self._pw.delete(0, "end")
        self._err.configure(text="")


class RegisterPage(ctk.CTkFrame):
    def __init__(self, master, on_register, on_go_login):
        super().__init__(master, fg_color=C["bg"], corner_radius=0)

        # ── left panel ──
        left = ctk.CTkFrame(self, fg_color=C["green_dark"], corner_radius=0, width=340)
        left.pack(side="left", fill="y")
        left.pack_propagate(False)

        ctk.CTkLabel(left, text="🌿", font=ctk.CTkFont(size=72)).pack(pady=(90, 8))
        ctk.CTkLabel(left, text="FarmSure",
                     font=ctk.CTkFont(size=34, weight="bold"),
                     text_color=C["white"]).pack()
        ctk.CTkLabel(left, text="Crop Insurance Portal",
                     font=ctk.CTkFont(size=15),
                     text_color="#A5D6A7").pack(pady=(4, 0))
        ctk.CTkLabel(left, text="Join thousands of farmers\nalready protected.",
                     font=ctk.CTkFont(size=13), text_color="#81C784",
                     justify="center", wraplength=240).pack(pady=(40, 0))

        # ── right panel ──
        right = ctk.CTkScrollableFrame(self, fg_color=C["bg"], corner_radius=0,
                                       scrollbar_button_color=C["card2"])
        right.pack(side="right", fill="both", expand=True)

        form = ctk.CTkFrame(right, fg_color="transparent")
        form.pack(expand=True, padx=60, pady=40)

        Heading(form, "Create account", size=26).pack(anchor="w", pady=(0, 4))
        ctk.CTkLabel(form, text="All fields marked with * are required",
                     font=ctk.CTkFont(size=13), text_color=C["muted"]).pack(anchor="w", pady=(0, 24))

        def field(label, placeholder, show=""):
            FieldLabel(form, label).pack(anchor="w")
            e = ModernEntry(form, placeholder=placeholder, width=380, show=show)
            e.pack(pady=(4, 14))
            return e

        self._name     = field("Full Name *",        "Jane Smith")
        self._email    = field("Email Address *",    "jane@farm.com")
        self._phone    = field("Phone Number",       "+1 (555) 000-0000")
        self._farm     = field("Farm Name",          "Green Acres Farm")
        self._location = field("Farm Location",      "County, State")
        self._pw       = field("Password *",         "Min. 8 characters", show="•")
        self._pw2      = field("Confirm Password *", "Repeat password",   show="•")

        self._err = ctk.CTkLabel(form, text="", text_color=C["red"],
                                 font=ctk.CTkFont(size=12), wraplength=380)
        self._err.pack(pady=(0, 8))

        PrimaryButton(form, "Create Account", command=self._submit, width=380).pack()

        row = ctk.CTkFrame(form, fg_color="transparent")
        row.pack(pady=(16, 0))
        ctk.CTkLabel(row, text="Already have an account?",
                     font=ctk.CTkFont(size=13), text_color=C["muted"]).pack(side="left")
        ctk.CTkButton(row, text=" Sign in", fg_color="transparent",
                      hover_color=C["bg"], text_color=C["green"],
                      font=ctk.CTkFont(size=13, weight="bold"),
                      command=on_go_login).pack(side="left")

        self._on_register = on_register

    def _submit(self):
        name  = self._name.get().strip()
        email = self._email.get().strip()
        phone = self._phone.get().strip()
        farm  = self._farm.get().strip()
        loc   = self._location.get().strip()
        pw    = self._pw.get()
        pw2   = self._pw2.get()

        if not name or not email or not pw:
            self._err.configure(text="Please fill in all required fields.")
            return
        if pw != pw2:
            self._err.configure(text="Passwords do not match.")
            return
        if len(pw) < 8:
            self._err.configure(text="Password must be at least 8 characters.")
            return

        uid, err = db.register_user(name, email, pw, farm, loc, phone)
        if err:
            self._err.configure(text=err)
        else:
            self._err.configure(text="")
            user, _ = db.login_user(email, pw)
            self._on_register(user)

    def clear(self):
        for w in [self._name, self._email, self._phone, self._farm,
                  self._location, self._pw, self._pw2]:
            w.delete(0, "end")
        self._err.configure(text="")


# ── Sidebar ───────────────────────────────────────────────────────────────────

NAV_ITEMS = [
    ("🏠", "Dashboard"),
    ("📋", "New Claim"),
    ("📁", "My Claims"),
    ("👤", "Profile"),
]


class Sidebar(ctk.CTkFrame):
    def __init__(self, master, on_navigate, on_logout):
        super().__init__(master, fg_color=C["sidebar"], corner_radius=0, width=220)
        self.pack_propagate(False)
        self._on_navigate = on_navigate
        self._buttons = {}
        self._active = None

        # logo
        logo = ctk.CTkFrame(self, fg_color="transparent")
        logo.pack(fill="x", padx=16, pady=(24, 32))
        ctk.CTkLabel(logo, text="🌾", font=ctk.CTkFont(size=30)).pack(side="left")
        ctk.CTkLabel(logo, text="FarmSure",
                     font=ctk.CTkFont(size=20, weight="bold"),
                     text_color=C["white"]).pack(side="left", padx=(8, 0))

        # nav
        SectionLabel(self, "Navigation").pack(anchor="w", padx=20, pady=(0, 8))
        for icon, label in NAV_ITEMS:
            btn = ctk.CTkButton(
                self, text=f"  {icon}  {label}", anchor="w",
                fg_color="transparent", hover_color=C["card"],
                text_color=C["muted"], font=ctk.CTkFont(size=14),
                height=44, corner_radius=8,
                command=lambda l=label: self._nav(l),
            )
            btn.pack(fill="x", padx=10, pady=2)
            self._buttons[label] = btn

        # bottom
        ctk.CTkFrame(self, fg_color=C["border"], height=1).pack(
            fill="x", padx=16, side="bottom", pady=(0, 8))
        ctk.CTkButton(
            self, text="  🚪  Sign Out", anchor="w",
            fg_color="transparent", hover_color="#3A1A1A",
            text_color=C["red"], font=ctk.CTkFont(size=14),
            height=44, corner_radius=8, command=on_logout,
        ).pack(fill="x", padx=10, side="bottom", pady=(0, 4))

        # user pill  (populated via set_user)
        self._user_card = ctk.CTkFrame(self, fg_color=C["card"], corner_radius=10)
        self._user_card.pack(fill="x", padx=10, side="bottom", pady=(0, 6))
        self._user_icon = ctk.CTkLabel(self._user_card, text="👤",
                                       font=ctk.CTkFont(size=22), width=44)
        self._user_icon.pack(side="left", padx=(10, 0), pady=10)
        self._user_name_lbl = ctk.CTkLabel(self._user_card, text="",
                                            font=ctk.CTkFont(size=13, weight="bold"),
                                            text_color=C["white"], anchor="w")
        self._user_name_lbl.pack(side="left", padx=8, pady=10, fill="x", expand=True)

    def set_user(self, user):
        name = user.get("full_name", "Farmer")
        short = name.split()[0] if name else "Farmer"
        self._user_name_lbl.configure(text=short)

    def _nav(self, label):
        self.set_active(label)
        self._on_navigate(label)

    def set_active(self, label):
        if self._active:
            self._buttons[self._active].configure(
                fg_color="transparent", text_color=C["muted"])
        self._active = label
        self._buttons[label].configure(
            fg_color=C["green"], text_color=C["white"])


# ── Dashboard page ────────────────────────────────────────────────────────────

class DashboardPage(ctk.CTkScrollableFrame):
    def __init__(self, master):
        super().__init__(master, fg_color=C["bg"], corner_radius=0,
                         scrollbar_button_color=C["card2"])

    def refresh(self, user):
        for w in self.winfo_children():
            w.destroy()

        stats = db.get_claim_stats(user["id"])
        claims = db.get_user_claims(user["id"])
        fname = user.get("full_name", "Farmer").split()[0]

        # header
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.pack(fill="x", padx=32, pady=(28, 4))
        Heading(hdr, f"Good day, {fname} 👋", size=26).pack(anchor="w")
        ctk.CTkLabel(hdr, text=f"Here's an overview of your farm insurance account.",
                     font=ctk.CTkFont(size=14), text_color=C["muted"]).pack(anchor="w", pady=(4, 0))

        # stat cards
        grid = ctk.CTkFrame(self, fg_color="transparent")
        grid.pack(fill="x", padx=32, pady=(20, 0))
        grid.columnconfigure((0, 1, 2, 3), weight=1, uniform="stat")

        card_data = [
            ("Total Claims",  stats["total"] or 0,        C["blue"]),
            ("Pending",       stats["pending"] or 0,      C["amber"]),
            ("Approved",      stats["approved"] or 0,     C["green"]),
            ("Rejected",      stats["rejected"] or 0,     C["red"]),
        ]
        for col, (lbl, val, color) in enumerate(card_data):
            StatCard(grid, lbl, val, color=color).grid(
                row=0, column=col, padx=6, pady=4, sticky="nsew")

        # total claimed
        tc = Card(self)
        tc.configure(border_width=1, border_color=C["border"])
        tc.pack(fill="x", padx=32, pady=(14, 0))
        inner = ctk.CTkFrame(tc, fg_color="transparent")
        inner.pack(fill="x", padx=18, pady=14)
        ctk.CTkLabel(inner, text="Total Loss Claimed",
                     font=ctk.CTkFont(size=13), text_color=C["muted"]).pack(anchor="w")
        total_val = stats["total_claimed"] or 0
        ctk.CTkLabel(inner, text=f"${total_val:,.2f}",
                     font=ctk.CTkFont(size=28, weight="bold"),
                     text_color=C["green_light"]).pack(anchor="w")

        # recent claims
        Heading(self, "Recent Claims", size=17).pack(
            anchor="w", padx=32, pady=(28, 10))

        if not claims:
            empty = Card(self)
            empty.pack(fill="x", padx=32, pady=4)
            ctk.CTkLabel(empty, text="No claims yet. Submit your first claim to get started.",
                         font=ctk.CTkFont(size=13), text_color=C["muted"]).pack(pady=28)
        else:
            for claim in claims[:5]:
                self._claim_row(claim)

    def _claim_row(self, claim):
        row = Card(self)
        row.configure(border_width=1, border_color=C["border"])
        row.pack(fill="x", padx=32, pady=4)

        inner = ctk.CTkFrame(row, fg_color="transparent")
        inner.pack(fill="x", padx=18, pady=12)
        inner.columnconfigure(1, weight=1)

        status = claim["status"]
        color  = STATUS_COLOR.get(status, C["muted"])

        ctk.CTkLabel(inner, text=claim["claim_number"],
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=C["white"]).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(inner, text=f"{claim['crop_type']}  ·  {claim['issue_type']}",
                     font=ctk.CTkFont(size=12), text_color=C["muted"]).grid(
                         row=1, column=0, sticky="w")

        badge = ctk.CTkLabel(inner, text=f"  {status}  ",
                             font=ctk.CTkFont(size=12, weight="bold"),
                             fg_color=color, text_color=C["white"],
                             corner_radius=6)
        badge.grid(row=0, column=2, rowspan=2, sticky="e", padx=(8, 0))

        ctk.CTkLabel(inner, text=f"${claim['estimated_loss']:,.2f}",
                     font=ctk.CTkFont(size=13),
                     text_color=C["muted"]).grid(row=0, column=1, sticky="e", padx=8)
        ctk.CTkLabel(inner, text=claim["incident_date"],
                     font=ctk.CTkFont(size=11),
                     text_color=C["muted"]).grid(row=1, column=1, sticky="e", padx=8)


# ── New Claim page ────────────────────────────────────────────────────────────

class NewClaimPage(ctk.CTkScrollableFrame):
    def __init__(self, master, on_submitted):
        super().__init__(master, fg_color=C["bg"], corner_radius=0,
                         scrollbar_button_color=C["card2"])
        self._on_submitted = on_submitted
        self._user = None
        self._build()

    def _build(self):
        Heading(self, "Submit a New Claim", size=24).pack(
            anchor="w", padx=32, pady=(28, 4))
        ctk.CTkLabel(self, text="Complete all required fields to file a crop insurance claim.",
                     font=ctk.CTkFont(size=14), text_color=C["muted"]).pack(
                         anchor="w", padx=32, pady=(0, 24))

        card = Card(self)
        card.configure(border_width=1, border_color=C["border"])
        card.pack(fill="x", padx=32, pady=(0, 16))

        f = ctk.CTkFrame(card, fg_color="transparent")
        f.pack(fill="x", padx=28, pady=24)
        f.columnconfigure((0, 1), weight=1, uniform="col")

        # ── row 0: crop type + issue type ──
        SectionLabel(f, "Crop Information").grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))

        FieldLabel(f, "Crop Type *").grid(row=1, column=0, sticky="w")
        self._crop = ctk.CTkOptionMenu(
            f, values=CROP_TYPES,
            fg_color=C["card2"], button_color=C["green"],
            button_hover_color=C["green_dark"],
            text_color=C["text"], dropdown_fg_color=C["card"],
            font=ctk.CTkFont(size=13), height=42, corner_radius=8,
        )
        self._crop.grid(row=2, column=0, sticky="ew", padx=(0, 10), pady=(4, 16))

        FieldLabel(f, "Type of Issue *").grid(row=1, column=1, sticky="w")
        self._issue = ctk.CTkOptionMenu(
            f, values=ISSUE_TYPES,
            fg_color=C["card2"], button_color=C["green"],
            button_hover_color=C["green_dark"],
            text_color=C["text"], dropdown_fg_color=C["card"],
            font=ctk.CTkFont(size=13), height=42, corner_radius=8,
        )
        self._issue.grid(row=2, column=1, sticky="ew", padx=(10, 0), pady=(4, 16))

        # ── row 1: incident date + affected acres ──
        SectionLabel(f, "Incident Details").grid(
            row=3, column=0, columnspan=2, sticky="w", pady=(0, 10))

        FieldLabel(f, "Date of Incident *").grid(row=4, column=0, sticky="w")
        self._date = ModernEntry(f, placeholder=str(date.today()))
        self._date.insert(0, str(date.today()))
        self._date.grid(row=5, column=0, sticky="ew", padx=(0, 10), pady=(4, 16))

        FieldLabel(f, "Affected Area (acres)").grid(row=4, column=1, sticky="w")
        self._acres = ModernEntry(f, placeholder="e.g. 45.5")
        self._acres.grid(row=5, column=1, sticky="ew", padx=(10, 0), pady=(4, 16))

        # ── estimated loss ──
        FieldLabel(f, "Estimated Financial Loss (USD) *").grid(
            row=6, column=0, columnspan=2, sticky="w")
        self._loss = ModernEntry(f, placeholder="e.g. 12500.00")
        self._loss.grid(row=7, column=0, columnspan=2, sticky="ew", pady=(4, 16))

        # ── description ──
        SectionLabel(f, "Description").grid(
            row=8, column=0, columnspan=2, sticky="w", pady=(0, 10))
        FieldLabel(f, "Describe the crop damage in detail *").grid(
            row=9, column=0, columnspan=2, sticky="w")
        self._desc = ctk.CTkTextbox(
            f, height=120, fg_color=C["card2"], border_color=C["border"],
            border_width=1, text_color=C["text"], corner_radius=8,
            font=ctk.CTkFont(size=13),
        )
        self._desc.grid(row=10, column=0, columnspan=2, sticky="ew", pady=(4, 0))

        # ── notice ──
        notice = ctk.CTkFrame(f, fg_color="#1A2A1A", corner_radius=8,
                              border_width=1, border_color="#2E5C2E")
        notice.grid(row=11, column=0, columnspan=2, sticky="ew", pady=(20, 0))
        ctk.CTkLabel(notice,
                     text="ℹ️  Once submitted your claim will be reviewed within 3–5 business days. "
                          "You'll be able to track its status in My Claims.",
                     text_color=C["green_light"], font=ctk.CTkFont(size=12),
                     wraplength=700, justify="left").pack(padx=16, pady=12)

        self._err = ctk.CTkLabel(self, text="", text_color=C["red"],
                                 font=ctk.CTkFont(size=13))
        self._err.pack(anchor="w", padx=32, pady=(12, 0))

        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.pack(anchor="w", padx=32, pady=(8, 32))
        PrimaryButton(btn_row, "  Submit Claim  ", command=self._submit).pack(side="left")
        GhostButton(btn_row, "  Clear Form  ", command=self._clear).pack(side="left", padx=(12, 0))

    def set_user(self, user):
        self._user = user

    def _clear(self):
        self._date.delete(0, "end")
        self._date.insert(0, str(date.today()))
        self._acres.delete(0, "end")
        self._loss.delete(0, "end")
        self._desc.delete("1.0", "end")
        self._err.configure(text="")
        self._crop.set(CROP_TYPES[0])
        self._issue.set(ISSUE_TYPES[0])

    def _submit(self):
        if not self._user:
            return
        crop  = self._crop.get()
        issue = self._issue.get()
        inc   = self._date.get().strip()
        desc  = self._desc.get("1.0", "end").strip()
        acres_str = self._acres.get().strip()
        loss_str  = self._loss.get().strip()

        if not inc or not desc or not loss_str:
            self._err.configure(text="Please fill in all required fields.")
            return
        try:
            loss = float(loss_str.replace(",", ""))
        except ValueError:
            self._err.configure(text="Estimated loss must be a valid number.")
            return
        try:
            acres = float(acres_str.replace(",", "")) if acres_str else None
        except ValueError:
            self._err.configure(text="Affected acres must be a valid number.")
            return
        if loss <= 0:
            self._err.configure(text="Estimated loss must be greater than zero.")
            return

        try:
            datetime.strptime(inc, "%Y-%m-%d")
        except ValueError:
            self._err.configure(text="Date must be in YYYY-MM-DD format.")
            return

        claim_number = db.create_claim(
            self._user["id"], crop, issue, desc, inc, acres, loss)
        self._err.configure(text="")
        self._clear()
        messagebox.showinfo(
            "Claim Submitted",
            f"Your claim {claim_number} has been submitted successfully!\n\n"
            "Our team will review it within 3–5 business days.",
        )
        self._on_submitted()


# ── My Claims page ────────────────────────────────────────────────────────────

class MyClaimsPage(ctk.CTkScrollableFrame):
    def __init__(self, master):
        super().__init__(master, fg_color=C["bg"], corner_radius=0,
                         scrollbar_button_color=C["card2"])

    def refresh(self, user):
        for w in self.winfo_children():
            w.destroy()

        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.pack(fill="x", padx=32, pady=(28, 20))
        Heading(hdr, "My Claims", size=24).pack(anchor="w")
        ctk.CTkLabel(hdr, text="Track the status of all your submitted claims below.",
                     font=ctk.CTkFont(size=14), text_color=C["muted"]).pack(anchor="w", pady=(4, 0))

        claims = db.get_user_claims(user["id"])
        if not claims:
            empty = Card(self)
            empty.configure(border_width=1, border_color=C["border"])
            empty.pack(fill="x", padx=32)
            ctk.CTkLabel(empty, text="🌾\n\nYou haven't submitted any claims yet.\nUse 'New Claim' to get started.",
                         font=ctk.CTkFont(size=14), text_color=C["muted"],
                         justify="center").pack(pady=40)
            return

        # header row
        hrow = ctk.CTkFrame(self, fg_color="transparent")
        hrow.pack(fill="x", padx=32)
        for col, (label, w) in enumerate([
            ("Claim #", 140), ("Crop", 150), ("Issue", 190), ("Date", 110),
            ("Loss (USD)", 110), ("Status", 110),
        ]):
            ctk.CTkLabel(hrow, text=label, font=ctk.CTkFont(size=11, weight="bold"),
                         text_color=C["muted"], width=w, anchor="w").pack(side="left", padx=4)

        ctk.CTkFrame(self, fg_color=C["border"], height=1).pack(
            fill="x", padx=32, pady=6)

        for claim in claims:
            row = Card(self)
            row.configure(border_width=1, border_color=C["border"],
                          fg_color=C["card"])
            row.pack(fill="x", padx=32, pady=3)

            inner = ctk.CTkFrame(row, fg_color="transparent")
            inner.pack(fill="x", padx=12, pady=10)

            status = claim["status"]
            color  = STATUS_COLOR.get(status, C["muted"])
            cols = [
                (claim["claim_number"], C["white"], 140),
                (claim["crop_type"],    C["muted"], 150),
                (claim["issue_type"],   C["muted"], 190),
                (claim["incident_date"],C["muted"], 110),
                (f"${claim['estimated_loss']:,.2f}", C["green_light"], 110),
            ]
            for text, color_t, width in cols:
                ctk.CTkLabel(inner, text=text, font=ctk.CTkFont(size=13),
                             text_color=color_t, width=width, anchor="w").pack(
                                 side="left", padx=4)

            ctk.CTkLabel(inner, text=f"  {status}  ",
                         font=ctk.CTkFont(size=12, weight="bold"),
                         fg_color=color, text_color=C["white"],
                         corner_radius=6, width=100).pack(side="left", padx=4)


# ── Profile page ──────────────────────────────────────────────────────────────

class ProfilePage(ctk.CTkScrollableFrame):
    def __init__(self, master, on_updated):
        super().__init__(master, fg_color=C["bg"], corner_radius=0,
                         scrollbar_button_color=C["card2"])
        self._on_updated = on_updated
        self._user = None

    def refresh(self, user):
        self._user = user
        for w in self.winfo_children():
            w.destroy()
        self._build()

    def _build(self):
        user = self._user
        Heading(self, "My Profile", size=24).pack(anchor="w", padx=32, pady=(28, 4))
        ctk.CTkLabel(self, text="Update your account information below.",
                     font=ctk.CTkFont(size=14), text_color=C["muted"]).pack(
                         anchor="w", padx=32, pady=(0, 24))

        # avatar card
        av = Card(self)
        av.configure(border_width=1, border_color=C["border"])
        av.pack(fill="x", padx=32, pady=(0, 16))
        inner = ctk.CTkFrame(av, fg_color="transparent")
        inner.pack(padx=24, pady=20, anchor="w")

        circle = ctk.CTkLabel(inner, text=user["full_name"][0].upper(),
                              font=ctk.CTkFont(size=32, weight="bold"),
                              fg_color=C["green"], text_color=C["white"],
                              width=72, height=72, corner_radius=36)
        circle.pack(side="left")

        info = ctk.CTkFrame(inner, fg_color="transparent")
        info.pack(side="left", padx=20)
        ctk.CTkLabel(info, text=user["full_name"],
                     font=ctk.CTkFont(size=18, weight="bold"),
                     text_color=C["white"]).pack(anchor="w")
        ctk.CTkLabel(info, text=user["email"],
                     font=ctk.CTkFont(size=13), text_color=C["muted"]).pack(anchor="w")
        since = user.get("created_at", "")[:10]
        ctk.CTkLabel(info, text=f"Member since {since}",
                     font=ctk.CTkFont(size=12), text_color=C["muted"]).pack(anchor="w")

        # edit form
        ecard = Card(self)
        ecard.configure(border_width=1, border_color=C["border"])
        ecard.pack(fill="x", padx=32, pady=(0, 24))

        f = ctk.CTkFrame(ecard, fg_color="transparent")
        f.pack(fill="x", padx=28, pady=24)
        f.columnconfigure((0, 1), weight=1, uniform="col")

        SectionLabel(f, "Personal Information").grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 12))

        def entry_pair(row, label0, val0, label1, val1):
            FieldLabel(f, label0).grid(row=row, column=0, sticky="w")
            FieldLabel(f, label1).grid(row=row, column=1, sticky="w")
            e0 = ModernEntry(f)
            e0.insert(0, val0 or "")
            e0.grid(row=row+1, column=0, sticky="ew", padx=(0, 10), pady=(4, 14))
            e1 = ModernEntry(f)
            e1.insert(0, val1 or "")
            e1.grid(row=row+1, column=1, sticky="ew", padx=(10, 0), pady=(4, 14))
            return e0, e1

        self._name_e, self._farm_e = entry_pair(
            1, "Full Name *", user["full_name"], "Farm Name", user.get("farm_name", ""))
        self._loc_e, self._phone_e = entry_pair(
            3, "Farm Location", user.get("location", ""), "Phone Number", user.get("phone", ""))

        self._err = ctk.CTkLabel(f, text="", text_color=C["red"],
                                 font=ctk.CTkFont(size=12))
        self._err.grid(row=5, column=0, columnspan=2, sticky="w")

        PrimaryButton(f, "  Save Changes  ", command=self._save).grid(
            row=6, column=0, columnspan=2, sticky="w", pady=(8, 0))

    def _save(self):
        name  = self._name_e.get().strip()
        farm  = self._farm_e.get().strip()
        loc   = self._loc_e.get().strip()
        phone = self._phone_e.get().strip()
        if not name:
            self._err.configure(text="Full name is required.")
            return
        db.update_user(self._user["id"], name, farm, loc, phone)
        self._user = db.get_user(self._user["id"])
        self._err.configure(text="")
        messagebox.showinfo("Profile Updated", "Your profile has been updated successfully.")
        self._on_updated(self._user)


# ── Main application ──────────────────────────────────────────────────────────

class FarmerInsuranceApp:
    def __init__(self):
        db.init_db()
        self._user = None

        self.root = ctk.CTk()
        self.root.title("FarmSure – Crop Insurance Portal")
        self.root.geometry("1100x720")
        self.root.minsize(900, 600)
        self.root.configure(fg_color=C["bg"])

        # ── auth layer ──
        self._login_page    = LoginPage(self.root, self._on_login, self._show_register)
        self._register_page = RegisterPage(self.root, self._on_login, self._show_login)
        self._login_page.pack(fill="both", expand=True)

        # ── main layer (sidebar + content) ──
        self._main_frame = ctk.CTkFrame(self.root, fg_color=C["bg"], corner_radius=0)
        self._sidebar = Sidebar(self._main_frame,
                                on_navigate=self._navigate,
                                on_logout=self._logout)
        self._sidebar.pack(side="left", fill="y")

        self._content = ctk.CTkFrame(self._main_frame, fg_color=C["bg"], corner_radius=0)
        self._content.pack(side="right", fill="both", expand=True)

        self._pages: dict[str, ctk.CTkFrame] = {}
        self._active_page = None

    def _build_pages(self):
        dash    = DashboardPage(self._content)
        claim   = NewClaimPage(self._content, on_submitted=self._after_claim)
        claims  = MyClaimsPage(self._content)
        profile = ProfilePage(self._content, on_updated=self._on_profile_updated)
        self._pages = {
            "Dashboard": dash,
            "New Claim": claim,
            "My Claims": claims,
            "Profile":   profile,
        }

    def _navigate(self, label):
        if self._active_page:
            self._active_page.pack_forget()
        page = self._pages[label]

        if label == "Dashboard":
            page.refresh(self._user)
        elif label == "My Claims":
            page.refresh(self._user)
        elif label == "New Claim":
            page.set_user(self._user)
        elif label == "Profile":
            page.refresh(self._user)

        page.pack(fill="both", expand=True)
        self._active_page = page

    def _after_claim(self):
        self._sidebar.set_active("My Claims")
        self._navigate("My Claims")

    def _on_profile_updated(self, updated_user):
        self._user = updated_user
        self._sidebar.set_user(updated_user)

    def _show_register(self):
        self._login_page.pack_forget()
        self._register_page.pack(fill="both", expand=True)

    def _show_login(self):
        self._register_page.pack_forget()
        self._login_page.clear()
        self._login_page.pack(fill="both", expand=True)

    def _on_login(self, user):
        self._user = user
        # hide auth layer
        for w in [self._login_page, self._register_page]:
            try:
                w.pack_forget()
            except Exception:
                pass
        # build pages fresh for this user
        if self._pages:
            for p in self._pages.values():
                p.destroy()
        self._build_pages()
        self._pages["New Claim"].set_user(user)
        # show main layout
        self._main_frame.pack(fill="both", expand=True)
        self._sidebar.set_user(user)
        self._sidebar.set_active("Dashboard")
        self._navigate("Dashboard")

    def _logout(self):
        self._user = None
        self._main_frame.pack_forget()
        self._login_page.clear()
        self._login_page.pack(fill="both", expand=True)

    def run(self):
        self.root.mainloop()
