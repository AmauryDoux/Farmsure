import customtkinter as ctk
from farmsure.ui.theme import C
from farmsure.ui.widgets import SectionLabel

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

        logo = ctk.CTkFrame(self, fg_color="transparent")
        logo.pack(fill="x", padx=16, pady=(24, 32))
        ctk.CTkLabel(logo, text="🌾", font=ctk.CTkFont(size=30)).pack(side="left")
        ctk.CTkLabel(logo, text="FarmSure",
                     font=ctk.CTkFont(size=20, weight="bold"),
                     text_color=C["white"]).pack(side="left", padx=(8, 0))

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

        ctk.CTkFrame(self, fg_color=C["border"], height=1).pack(
            fill="x", padx=16, side="bottom", pady=(0, 8))
        ctk.CTkButton(
            self, text="  🚪  Sign Out", anchor="w",
            fg_color="transparent", hover_color="#3A1A1A",
            text_color=C["red"], font=ctk.CTkFont(size=14),
            height=44, corner_radius=8, command=on_logout,
        ).pack(fill="x", padx=10, side="bottom", pady=(0, 4))

        self._user_card = ctk.CTkFrame(self, fg_color=C["card"], corner_radius=10)
        self._user_card.pack(fill="x", padx=10, side="bottom", pady=(0, 6))
        ctk.CTkLabel(self._user_card, text="👤",
                     font=ctk.CTkFont(size=22), width=44).pack(
                         side="left", padx=(10, 0), pady=10)
        self._user_name_lbl = ctk.CTkLabel(self._user_card, text="",
                                            font=ctk.CTkFont(size=13, weight="bold"),
                                            text_color=C["white"], anchor="w")
        self._user_name_lbl.pack(side="left", padx=8, pady=10, fill="x", expand=True)

    def set_user(self, user):
        name = user.get("full_name", "Farmer")
        self._user_name_lbl.configure(text=name.split()[0] if name else "Farmer")

    def _nav(self, label):
        self.set_active(label)
        self._on_navigate(label)

    def set_active(self, label):
        if self._active:
            self._buttons[self._active].configure(
                fg_color="transparent", text_color=C["muted"])
        self._active = label
        self._buttons[label].configure(fg_color=C["green"], text_color=C["white"])
