import customtkinter as ctk
from farmsure.ui.modal import ask_confirm
from farmsure.ui.theme import C
from farmsure.ui.widgets import Card, Heading, SectionLabel, FieldLabel, ModernEntry, PrimaryButton
import farmsure.db as db


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

        av = Card(self)
        av.configure(border_width=1, border_color=C["border"])
        av.pack(fill="x", padx=32, pady=(0, 16))
        inner = ctk.CTkFrame(av, fg_color="transparent")
        inner.pack(padx=24, pady=20, anchor="w")

        ctk.CTkLabel(inner, text=user["full_name"][0].upper(),
                     font=ctk.CTkFont(size=32, weight="bold"),
                     fg_color=C["green"], text_color=C["white"],
                     width=72, height=72, corner_radius=36).pack(side="left")

        info = ctk.CTkFrame(inner, fg_color="transparent")
        info.pack(side="left", padx=20)
        ctk.CTkLabel(info, text=user["full_name"],
                     font=ctk.CTkFont(size=18, weight="bold"),
                     text_color=C["white"]).pack(anchor="w")
        ctk.CTkLabel(info, text=user["email"],
                     font=ctk.CTkFont(size=13), text_color=C["muted"]).pack(anchor="w")
        ctk.CTkLabel(info, text=f"Member since {user.get('created_at', '')[:10]}",
                     font=ctk.CTkFont(size=12), text_color=C["muted"]).pack(anchor="w")

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

        self._name_e,  self._farm_e  = entry_pair(
            1, "Full Name *", user["full_name"], "Farm Name", user.get("farm_name", ""))
        self._loc_e,   self._phone_e = entry_pair(
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
        if not ask_confirm(
            self.winfo_toplevel(),
            "Save Changes",
            "Update your profile with these details?",
            icon="👤",
        ):
            return

        db.update_user(self._user["id"], name, farm, loc, phone)
        self._user = db.get_user(self._user["id"])
        self._err.configure(text="")
        self._on_updated(self._user)
