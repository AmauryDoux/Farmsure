import customtkinter as ctk
from farmsure.ui.theme import C
from farmsure.ui.backoffice.pages import LoginPage, ClaimsListPanel, ClaimDetailPanel
import farmsure.db as db


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

        ctk.CTkFrame(self, fg_color=C["border"], width=1).pack(side="right", fill="y", pady=12)

        ctk.CTkLabel(self, text=f"👤  {admin.get('full_name', 'Agent')}",
                     font=ctk.CTkFont(size=13), text_color=C["muted"]).pack(
                         side="right", padx=16)


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
