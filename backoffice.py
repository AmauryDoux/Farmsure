"""
FarmSure – Insurance Back-Office
Desktop app for claims agents to review and action farmer claims.
"""

import customtkinter as ctk
from tkinter import messagebox
import database as db

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

# What action buttons to show per current status
STATUS_ACTIONS = {
    "Pending":      [("Start Review", C["blue"],  "#2A6BC9", "Under Review")],
    "Under Review": [("Approve",      C["green"], C["green_dark"], "Approved"),
                     ("Reject",       C["red"],   "#CC3030",       "Rejected")],
    "Approved":     [("Reopen",       C["blue"],  "#2A6BC9", "Under Review")],
    "Rejected":     [("Reopen",       C["blue"],  "#2A6BC9", "Under Review")],
}

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")


# ── Shared widgets ────────────────────────────────────────────────────────────

class Card(ctk.CTkFrame):
    def __init__(self, master, **kw):
        kw.setdefault("fg_color", C["card"])
        kw.setdefault("corner_radius", 12)
        super().__init__(master, **kw)


class Heading(ctk.CTkLabel):
    def __init__(self, master, text, size=20, **kw):
        kw.setdefault("font", ctk.CTkFont(size=size, weight="bold"))
        kw.setdefault("text_color", C["white"])
        super().__init__(master, text=text, **kw)


def _bind_tree(widget, event, callback):
    widget.bind(event, callback)
    for child in widget.winfo_children():
        _bind_tree(child, event, callback)


# ── Login page ────────────────────────────────────────────────────────────────

class LoginPage(ctk.CTkFrame):
    def __init__(self, master, on_login):
        super().__init__(master, fg_color=C["bg"], corner_radius=0)
        self._on_login = on_login

        left = ctk.CTkFrame(self, fg_color="#1A3020", corner_radius=0, width=340)
        left.pack(side="left", fill="y")
        left.pack_propagate(False)

        ctk.CTkLabel(left, text="🏛️", font=ctk.CTkFont(size=64)).pack(pady=(90, 8))
        ctk.CTkLabel(left, text="FarmSure",
                     font=ctk.CTkFont(size=34, weight="bold"),
                     text_color=C["white"]).pack()
        ctk.CTkLabel(left, text="Claims Back-Office",
                     font=ctk.CTkFont(size=15), text_color="#A5D6A7").pack(pady=(4, 0))
        ctk.CTkLabel(left, text="Authorized agents only.",
                     font=ctk.CTkFont(size=12), text_color="#81C784",
                     justify="center").pack(pady=(40, 0))

        right = ctk.CTkFrame(self, fg_color=C["bg"], corner_radius=0)
        right.pack(side="right", fill="both", expand=True)

        form = ctk.CTkFrame(right, fg_color="transparent", width=340)
        form.place(relx=0.5, rely=0.5, anchor="center")

        Heading(form, "Agent Sign In", size=26).pack(anchor="w", pady=(0, 4))
        ctk.CTkLabel(form, text="Sign in to manage and action claims",
                     font=ctk.CTkFont(size=14), text_color=C["muted"]).pack(anchor="w", pady=(0, 28))

        def entry(placeholder, show=""):
            ctk.CTkLabel(form, text=placeholder.split("@")[0].replace("agent", "Email address").replace("••", "Password"),
                         font=ctk.CTkFont(size=13), text_color=C["muted"]).pack(anchor="w")
            e = ctk.CTkEntry(form, placeholder_text=placeholder, show=show,
                             fg_color=C["card2"], border_color=C["border"],
                             text_color=C["text"], placeholder_text_color=C["muted"],
                             height=42, corner_radius=8, font=ctk.CTkFont(size=14), width=340)
            e.pack(pady=(4, 16))
            return e

        ctk.CTkLabel(form, text="Email address",
                     font=ctk.CTkFont(size=13), text_color=C["muted"]).pack(anchor="w")
        self._email = ctk.CTkEntry(form, placeholder_text="agent@farmsure.com",
                                   fg_color=C["card2"], border_color=C["border"],
                                   text_color=C["text"], placeholder_text_color=C["muted"],
                                   height=42, corner_radius=8, font=ctk.CTkFont(size=14), width=340)
        self._email.pack(pady=(4, 16))

        ctk.CTkLabel(form, text="Password",
                     font=ctk.CTkFont(size=13), text_color=C["muted"]).pack(anchor="w")
        self._pw = ctk.CTkEntry(form, placeholder_text="••••••••", show="•",
                                fg_color=C["card2"], border_color=C["border"],
                                text_color=C["text"], placeholder_text_color=C["muted"],
                                height=42, corner_radius=8, font=ctk.CTkFont(size=14), width=340)
        self._pw.pack(pady=(4, 24))

        self._err = ctk.CTkLabel(form, text="", text_color=C["red"], font=ctk.CTkFont(size=12))
        self._err.pack(pady=(0, 8))

        ctk.CTkButton(form, text="Sign In", command=self._submit,
                      fg_color=C["green"], hover_color=C["green_dark"],
                      text_color=C["white"], height=44, corner_radius=10,
                      font=ctk.CTkFont(size=14, weight="bold"), width=340).pack()

        self._pw.bind("<Return>", lambda e: self._submit())
        self._email.bind("<Return>", lambda e: self._pw.focus())

    def _submit(self):
        email = self._email.get().strip()
        pw    = self._pw.get()
        if not email or not pw:
            self._err.configure(text="Please fill in all fields.")
            return
        admin, err = db.login_admin(email, pw)
        if err:
            self._err.configure(text=err)
        else:
            self._err.configure(text="")
            self._on_login(admin)


# ── Claim row (left panel) ────────────────────────────────────────────────────

class ClaimRow(ctk.CTkFrame):
    def __init__(self, master, claim, on_select, **kw):
        kw.setdefault("fg_color", C["card"])
        kw.setdefault("corner_radius", 8)
        super().__init__(master, **kw)
        self.configure(border_width=1, border_color=C["border"])
        self._claim = claim
        self._on_select = on_select
        self._build()
        _bind_tree(self, "<Button-1>", lambda e: self._on_select(self._claim))

    def _build(self):
        inner = ctk.CTkFrame(self, fg_color="transparent")
        inner.pack(fill="x", padx=12, pady=9)

        top = ctk.CTkFrame(inner, fg_color="transparent")
        top.pack(fill="x")

        ctk.CTkLabel(top, text=self._claim["claim_number"],
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=C["white"]).pack(side="left")

        status = self._claim["status"]
        ctk.CTkLabel(top, text=f"  {status}  ",
                     font=ctk.CTkFont(size=10, weight="bold"),
                     fg_color=STATUS_COLOR.get(status, C["muted"]),
                     text_color=C["white"], corner_radius=5).pack(side="right")

        ctk.CTkLabel(inner, text=self._claim.get("full_name", "—"),
                     font=ctk.CTkFont(size=12), text_color=C["text"]).pack(anchor="w", pady=(3, 0))

        ctk.CTkLabel(inner,
                     text=f"{self._claim['crop_type']}  ·  {self._claim['issue_type']}",
                     font=ctk.CTkFont(size=11), text_color=C["muted"]).pack(anchor="w")

        ctk.CTkLabel(inner,
                     text=f"${self._claim['estimated_loss']:,.2f}  ·  {self._claim['incident_date'][:10]}",
                     font=ctk.CTkFont(size=11), text_color=C["muted"]).pack(anchor="w", pady=(2, 0))

    def set_selected(self, on: bool):
        if on:
            self.configure(fg_color=C["card2"], border_color=C["green"])
        else:
            self.configure(fg_color=C["card"], border_color=C["border"])


# ── Claims list panel (left) ──────────────────────────────────────────────────

class ClaimsListPanel(ctk.CTkFrame):
    def __init__(self, master, on_select, **kw):
        kw.setdefault("fg_color", C["sidebar"])
        kw.setdefault("corner_radius", 0)
        super().__init__(master, **kw)
        self.pack_propagate(False)
        self._on_select = on_select
        self._active_filter = "All"
        self._rows: list[ClaimRow] = []
        self._selected_id = None
        self._filter_btns: dict[str, ctk.CTkButton] = {}
        self._count_lbl = None
        self._build()

    def _build(self):
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.pack(fill="x", padx=16, pady=(20, 8))

        title_row = ctk.CTkFrame(hdr, fg_color="transparent")
        title_row.pack(fill="x")
        Heading(title_row, "Claims Queue", size=17).pack(side="left")
        self._count_lbl = ctk.CTkLabel(title_row, text="",
                                        font=ctk.CTkFont(size=12),
                                        text_color=C["muted"])
        self._count_lbl.pack(side="right")

        # Two rows of filter buttons to fit all statuses
        row1 = ctk.CTkFrame(self, fg_color="transparent")
        row1.pack(fill="x", padx=12, pady=(0, 3))
        row2 = ctk.CTkFrame(self, fg_color="transparent")
        row2.pack(fill="x", padx=12, pady=(0, 8))

        filters_r1 = ["All", "Pending"]
        filters_r2 = ["Under Review", "Approved", "Rejected"]

        for status, container in [(s, row1) for s in filters_r1] + [(s, row2) for s in filters_r2]:
            btn = ctk.CTkButton(
                container, text=status,
                fg_color=C["green"] if status == "All" else C["card2"],
                hover_color=C["green_dark"] if status == "All" else C["card"],
                text_color=C["white"], height=26, corner_radius=6,
                font=ctk.CTkFont(size=11),
                command=lambda s=status: self._set_filter(s),
            )
            btn.pack(side="left", padx=(0, 4))
            self._filter_btns[status] = btn

        ctk.CTkFrame(self, fg_color=C["border"], height=1).pack(fill="x", padx=12)

        self._scroll = ctk.CTkScrollableFrame(self, fg_color="transparent",
                                               scrollbar_button_color=C["card2"])
        self._scroll.pack(fill="both", expand=True, padx=8, pady=8)

    def _set_filter(self, status):
        self._active_filter = status
        for s, btn in self._filter_btns.items():
            active = s == status
            btn.configure(
                fg_color=C["green"] if active else C["card2"],
                hover_color=C["green_dark"] if active else C["card"],
            )
        self.refresh()

    def refresh(self, keep_selection=False):
        sel = self._selected_id if keep_selection else None
        for w in self._scroll.winfo_children():
            w.destroy()
        self._rows.clear()

        claims = db.get_all_claims(self._active_filter)
        self._count_lbl.configure(text=f"{len(claims)} claims")

        if not claims:
            ctk.CTkLabel(self._scroll, text="No claims found.",
                         font=ctk.CTkFont(size=13), text_color=C["muted"]).pack(pady=40)
            return

        for claim in claims:
            row = ClaimRow(self._scroll, claim, on_select=self._select)
            row.pack(fill="x", pady=3)
            self._rows.append(row)
            if sel and claim["id"] == sel:
                row.set_selected(True)

    def _select(self, claim):
        self._selected_id = claim["id"]
        for row in self._rows:
            row.set_selected(row._claim["id"] == claim["id"])
        self._on_select(claim)


# ── Claim detail panel (right) ────────────────────────────────────────────────

class ClaimDetailPanel(ctk.CTkScrollableFrame):
    def __init__(self, master, on_status_changed, **kw):
        kw.setdefault("fg_color", C["bg"])
        kw.setdefault("corner_radius", 0)
        kw.setdefault("scrollbar_button_color", C["card2"])
        super().__init__(master, **kw)
        self._on_status_changed = on_status_changed
        self._claim = None
        self._show_empty()

    def _show_empty(self):
        self._clear()
        ctk.CTkLabel(self, text="← Select a claim from the queue to review it",
                     font=ctk.CTkFont(size=15), text_color=C["muted"]).pack(pady=200)

    def _clear(self):
        for w in self.winfo_children():
            w.destroy()

    def load(self, claim):
        self._claim = claim
        self._clear()
        self._build()

    def _build(self):
        claim  = self._claim
        status = claim["status"]
        color  = STATUS_COLOR.get(status, C["muted"])

        # ── Header ──
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.pack(fill="x", padx=32, pady=(28, 0))

        top = ctk.CTkFrame(hdr, fg_color="transparent")
        top.pack(fill="x")
        Heading(top, claim["claim_number"], size=22).pack(side="left")
        ctk.CTkLabel(top, text=f"  {status}  ",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     fg_color=color, text_color=C["white"],
                     corner_radius=7).pack(side="right")

        ctk.CTkLabel(hdr, text=f"Submitted {claim['created_at'][:10]}",
                     font=ctk.CTkFont(size=12), text_color=C["muted"]).pack(anchor="w", pady=(4, 0))

        # ── Farmer info ──
        self._section_label("Farmer Information")
        fc = Card(self)
        fc.configure(border_width=1, border_color=C["border"])
        fc.pack(fill="x", padx=32, pady=(0, 16))

        fi = ctk.CTkFrame(fc, fg_color="transparent")
        fi.pack(fill="x", padx=20, pady=16)
        fi.columnconfigure((0, 1), weight=1, uniform="c")

        self._field_pair(fi, 0,
                         "Farmer",   claim.get("full_name", "—"),
                         "Farm",     claim.get("farm_name", "—"))
        self._field_pair(fi, 1,
                         "Location", claim.get("location", "—"),
                         "Phone",    claim.get("phone", "—"))
        self._field(fi, 2, 0, "Email", claim.get("user_email", "—"), colspan=2)

        # ── Claim details ──
        self._section_label("Claim Details")
        dc = Card(self)
        dc.configure(border_width=1, border_color=C["border"])
        dc.pack(fill="x", padx=32, pady=(0, 16))

        di = ctk.CTkFrame(dc, fg_color="transparent")
        di.pack(fill="x", padx=20, pady=16)
        di.columnconfigure((0, 1), weight=1, uniform="c")

        self._field_pair(di, 0,
                         "Crop Type",     claim["crop_type"],
                         "Issue Type",    claim["issue_type"])
        acres = f"{claim['affected_acres']:,.1f} acres" if claim.get("affected_acres") else "—"
        self._field_pair(di, 1,
                         "Incident Date", claim["incident_date"][:10],
                         "Affected Area", acres)
        self._field(di, 2, 0, "Estimated Loss",
                    f"${claim['estimated_loss']:,.2f}",
                    colspan=2, value_color=C["green_light"])

        # ── Description ──
        self._section_label("Description")
        desc_card = Card(self)
        desc_card.configure(border_width=1, border_color=C["border"])
        desc_card.pack(fill="x", padx=32, pady=(0, 16))
        ctk.CTkLabel(desc_card, text=claim["description"],
                     font=ctk.CTkFont(size=13), text_color=C["text"],
                     wraplength=600, justify="left", anchor="w").pack(
                         fill="x", padx=20, pady=16)

        # ── Actions ──
        self._section_label("Update Status")
        ac = Card(self)
        ac.configure(border_width=1, border_color=C["border"])
        ac.pack(fill="x", padx=32, pady=(0, 32))

        btn_row = ctk.CTkFrame(ac, fg_color="transparent")
        btn_row.pack(fill="x", padx=20, pady=16)

        actions = STATUS_ACTIONS.get(status, [])
        for label, fg, hover, new_status in actions:
            ctk.CTkButton(
                btn_row, text=label,
                fg_color=fg, hover_color=hover,
                text_color=C["white"], height=42, corner_radius=8,
                font=ctk.CTkFont(size=13, weight="bold"), width=150,
                command=lambda ns=new_status: self._set_status(ns),
            ).pack(side="left", padx=(0, 10))

        if not actions:
            ctk.CTkLabel(btn_row, text="No further actions available.",
                         font=ctk.CTkFont(size=13), text_color=C["muted"]).pack(anchor="w")

    def _section_label(self, text):
        ctk.CTkLabel(self, text=text.upper(),
                     font=ctk.CTkFont(size=11), text_color=C["muted"]).pack(
                         anchor="w", padx=32, pady=(16, 6))

    def _field(self, parent, row, col, label, value, colspan=1, value_color=None):
        f = ctk.CTkFrame(parent, fg_color="transparent")
        f.grid(row=row, column=col, columnspan=colspan, sticky="w",
               padx=(0, 16), pady=(0, 14))
        ctk.CTkLabel(f, text=label,
                     font=ctk.CTkFont(size=11), text_color=C["muted"]).pack(anchor="w")
        ctk.CTkLabel(f, text=value,
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=value_color or C["white"]).pack(anchor="w")

    def _field_pair(self, parent, row, label0, val0, label1, val1):
        self._field(parent, row, 0, label0, val0)
        self._field(parent, row, 1, label1, val1)

    def _set_status(self, new_status):
        if not self._claim:
            return
        db.update_claim_status(self._claim["id"], new_status)
        self._claim["status"] = new_status
        self._on_status_changed(self._claim)
        self.load(self._claim)


# ── Top bar ───────────────────────────────────────────────────────────────────

class TopBar(ctk.CTkFrame):
    def __init__(self, master, admin, on_logout, **kw):
        kw.setdefault("fg_color", C["sidebar"])
        kw.setdefault("corner_radius", 0)
        kw.setdefault("height", 56)
        super().__init__(master, **kw)
        self.pack_propagate(False)

        ctk.CTkLabel(self, text="🌾  FarmSure Back-Office",
                     font=ctk.CTkFont(size=16, weight="bold"),
                     text_color=C["white"]).pack(side="left", padx=20)

        ctk.CTkButton(self, text="Sign Out", command=on_logout,
                      fg_color="transparent", hover_color="#3A1A1A",
                      text_color=C["red"], height=32, corner_radius=6,
                      font=ctk.CTkFont(size=13), width=90).pack(side="right", padx=16)

        ctk.CTkFrame(self, fg_color=C["border"], width=1).pack(
            side="right", fill="y", pady=12)

        ctk.CTkLabel(self, text=f"👤  {admin.get('full_name', 'Agent')}",
                     font=ctk.CTkFont(size=13), text_color=C["muted"]).pack(
                         side="right", padx=16)


# ── Main view (post-login) ────────────────────────────────────────────────────

class MainView(ctk.CTkFrame):
    def __init__(self, master, admin, on_logout):
        super().__init__(master, fg_color=C["bg"], corner_radius=0)

        TopBar(self, admin, on_logout).pack(fill="x")
        ctk.CTkFrame(self, fg_color=C["border"], height=1).pack(fill="x")

        body = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
        body.pack(fill="both", expand=True)

        self._list = ClaimsListPanel(body, on_select=self._on_select, width=370)
        self._list.pack(side="left", fill="y")

        ctk.CTkFrame(body, fg_color=C["border"], width=1).pack(side="left", fill="y")

        self._detail = ClaimDetailPanel(body, on_status_changed=self._on_status_changed)
        self._detail.pack(side="right", fill="both", expand=True)

        self._list.refresh()

    def _on_select(self, claim):
        self._detail.load(claim)

    def _on_status_changed(self, _claim):
        self._list.refresh(keep_selection=True)


# ── Application ───────────────────────────────────────────────────────────────

class BackOfficeApp:
    def __init__(self):
        db.init_db()
        db.init_admin_db()

        self.root = ctk.CTk()
        self.root.title("FarmSure – Claims Back-Office")
        self.root.geometry("1240x800")
        self.root.minsize(980, 640)
        self.root.configure(fg_color=C["bg"])

        self._admin = None
        self._main: MainView | None = None

        self._login = LoginPage(self.root, on_login=self._on_login)
        self._login.pack(fill="both", expand=True)

    def _on_login(self, admin):
        self._admin = admin
        self._login.pack_forget()
        self._main = MainView(self.root, admin, on_logout=self._on_logout)
        self._main.pack(fill="both", expand=True)

    def _on_logout(self):
        if self._main:
            self._main.destroy()
            self._main = None
        self._admin = None
        self._login.pack(fill="both", expand=True)

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    BackOfficeApp().run()
