import customtkinter as ctk
from farmsure.ui.modal import ask_confirm
from datetime import date, datetime
from farmsure.ui.theme import C, CROP_TYPES, ISSUE_TYPES
from farmsure.ui.widgets import Card, Heading, SectionLabel, FieldLabel, ModernEntry, PrimaryButton, GhostButton
import farmsure.db as db


class NewClaimPage(ctk.CTkScrollableFrame):
    def __init__(self, master, on_submitted):
        super().__init__(master, fg_color=C["bg"], corner_radius=0,
                         scrollbar_button_color=C["card2"])
        self._on_submitted = on_submitted
        self._user = None
        self._build()

    def _build(self):
        Heading(self, "Submit a New Claim", size=24).pack(anchor="w", padx=32, pady=(28, 4))
        ctk.CTkLabel(self, text="Complete all required fields to file a crop insurance claim.",
                     font=ctk.CTkFont(size=14), text_color=C["muted"]).pack(
                         anchor="w", padx=32, pady=(0, 24))

        card = Card(self)
        card.configure(border_width=1, border_color=C["border"])
        card.pack(fill="x", padx=32, pady=(0, 16))

        f = ctk.CTkFrame(card, fg_color="transparent")
        f.pack(fill="x", padx=28, pady=24)
        f.columnconfigure((0, 1), weight=1, uniform="col")

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

        SectionLabel(f, "Incident Details").grid(
            row=3, column=0, columnspan=2, sticky="w", pady=(0, 10))

        FieldLabel(f, "Date of Incident *").grid(row=4, column=0, sticky="w")
        self._date = ModernEntry(f, placeholder=str(date.today()))
        self._date.insert(0, str(date.today()))
        self._date.grid(row=5, column=0, sticky="ew", padx=(0, 10), pady=(4, 16))

        FieldLabel(f, "Affected Area (acres)").grid(row=4, column=1, sticky="w")
        self._acres = ModernEntry(f, placeholder="e.g. 45.5")
        self._acres.grid(row=5, column=1, sticky="ew", padx=(10, 0), pady=(4, 16))

        FieldLabel(f, "Estimated Financial Loss (USD) *").grid(
            row=6, column=0, columnspan=2, sticky="w")
        self._loss = ModernEntry(f, placeholder="e.g. 12500.00")
        self._loss.grid(row=7, column=0, columnspan=2, sticky="ew", pady=(4, 16))

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
        crop      = self._crop.get()
        issue     = self._issue.get()
        inc       = self._date.get().strip()
        desc      = self._desc.get("1.0", "end").strip()
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

        if not ask_confirm(
            self.winfo_toplevel(),
            "Submit Claim",
            f"Submit a {crop} claim for ${loss:,.2f}?\n\n"
            "Our team will review it within 3–5 business days.",
            icon="📋",
        ):
            return

        db.create_claim(self._user["id"], crop, issue, desc, inc, acres, loss)
        self._err.configure(text="")
        self._clear()
        self._on_submitted()
