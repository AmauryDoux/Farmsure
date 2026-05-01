import customtkinter as ctk
from farmsure.ui.theme import C
from farmsure.ui.widgets import Heading, ModernEntry, PrimaryButton
import farmsure.db as db


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

        ctk.CTkLabel(form, text="Email address",
                     font=ctk.CTkFont(size=13), text_color=C["muted"]).pack(anchor="w")
        self._email = ModernEntry(form, placeholder="agent@farmsure.com", width=340)
        self._email.pack(pady=(4, 16))

        ctk.CTkLabel(form, text="Password",
                     font=ctk.CTkFont(size=13), text_color=C["muted"]).pack(anchor="w")
        self._pw = ModernEntry(form, placeholder="••••••••", show="•", width=340)
        self._pw.pack(pady=(4, 24))

        self._err = ctk.CTkLabel(form, text="", text_color=C["red"],
                                 font=ctk.CTkFont(size=12))
        self._err.pack(pady=(0, 8))

        PrimaryButton(form, "Sign In", command=self._submit, width=340).pack()

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
