import customtkinter as ctk
from farmsure.ui.theme import C, STATUS_COLOR
from farmsure.ui.widgets import Heading, _bind_tree
import farmsure.db as db


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

        row1 = ctk.CTkFrame(self, fg_color="transparent")
        row1.pack(fill="x", padx=12, pady=(0, 3))
        row2 = ctk.CTkFrame(self, fg_color="transparent")
        row2.pack(fill="x", padx=12, pady=(0, 8))

        for status, container in (
            [(s, row1) for s in ["All", "Pending"]] +
            [(s, row2) for s in ["Under Review", "Approved", "Rejected"]]
        ):
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
