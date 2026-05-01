import customtkinter as ctk
from farmsure.ui.theme import C, STATUS_COLOR, STATUS_ACTIONS
from farmsure.ui.widgets import Card, Heading
import farmsure.db as db


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

        self._section_label("Farmer Information")
        fc = Card(self)
        fc.configure(border_width=1, border_color=C["border"])
        fc.pack(fill="x", padx=32, pady=(0, 16))
        fi = ctk.CTkFrame(fc, fg_color="transparent")
        fi.pack(fill="x", padx=20, pady=16)
        fi.columnconfigure((0, 1), weight=1, uniform="c")
        self._field_pair(fi, 0, "Farmer", claim.get("full_name", "—"),
                                 "Farm",   claim.get("farm_name", "—"))
        self._field_pair(fi, 1, "Location", claim.get("location", "—"),
                                 "Phone",    claim.get("phone", "—"))
        self._field(fi, 2, 0, "Email", claim.get("user_email", "—"), colspan=2)

        self._section_label("Claim Details")
        dc = Card(self)
        dc.configure(border_width=1, border_color=C["border"])
        dc.pack(fill="x", padx=32, pady=(0, 16))
        di = ctk.CTkFrame(dc, fg_color="transparent")
        di.pack(fill="x", padx=20, pady=16)
        di.columnconfigure((0, 1), weight=1, uniform="c")
        self._field_pair(di, 0, "Crop Type",  claim["crop_type"],
                                 "Issue Type", claim["issue_type"])
        acres = f"{claim['affected_acres']:,.1f} acres" if claim.get("affected_acres") else "—"
        self._field_pair(di, 1, "Incident Date", claim["incident_date"][:10],
                                 "Affected Area", acres)
        self._field(di, 2, 0, "Estimated Loss",
                    f"${claim['estimated_loss']:,.2f}", colspan=2, value_color=C["green_light"])

        self._section_label("Description")
        desc_card = Card(self)
        desc_card.configure(border_width=1, border_color=C["border"])
        desc_card.pack(fill="x", padx=32, pady=(0, 16))
        ctk.CTkLabel(desc_card, text=claim["description"],
                     font=ctk.CTkFont(size=13), text_color=C["text"],
                     wraplength=600, justify="left", anchor="w").pack(
                         fill="x", padx=20, pady=16)

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
