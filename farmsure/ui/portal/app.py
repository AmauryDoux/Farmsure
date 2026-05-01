import customtkinter as ctk
from farmsure.ui.theme import C
from farmsure.ui.portal.sidebar import Sidebar
from farmsure.ui.portal.pages import (
    LoginPage, RegisterPage, DashboardPage, NewClaimPage, MyClaimsPage, ProfilePage,
)
import farmsure.db as db


class FarmerInsuranceApp:
    def __init__(self):
        db.init_db()
        self._user = None

        self.root = ctk.CTk()
        self.root.title("FarmSure – Crop Insurance Portal")
        self.root.geometry("1100x720")
        self.root.minsize(900, 600)
        self.root.configure(fg_color=C["bg"])

        self._login_page    = LoginPage(self.root, self._on_login, self._show_register)
        self._register_page = RegisterPage(self.root, self._on_login, self._show_login)
        self._login_page.pack(fill="both", expand=True)

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
        self._pages = {
            "Dashboard": DashboardPage(self._content),
            "New Claim": NewClaimPage(self._content, on_submitted=self._after_claim),
            "My Claims": MyClaimsPage(self._content),
            "Profile":   ProfilePage(self._content, on_updated=self._on_profile_updated),
        }

    def _navigate(self, label):
        if self._active_page:
            self._active_page.pack_forget()
        page = self._pages[label]

        if label in ("Dashboard", "My Claims", "Profile"):
            page.refresh(self._user)
        elif label == "New Claim":
            page.set_user(self._user)

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
        for w in [self._login_page, self._register_page]:
            try:
                w.pack_forget()
            except Exception:
                pass
        if self._pages:
            for p in self._pages.values():
                p.destroy()
        self._build_pages()
        self._pages["New Claim"].set_user(user)
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
