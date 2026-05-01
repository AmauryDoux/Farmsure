import customtkinter as ctk
from farmsure.ui.theme import C
from farmsure.ui.widgets import Heading, FieldLabel, ModernEntry, PrimaryButton
import farmsure.db as db


class LoginPage(ctk.CTkFrame):
    def __init__(self, master, on_login, on_go_register):
        super().__init__(master, fg_color=C["bg"], corner_radius=0)
        self._on_login = on_login

        left = ctk.CTkFrame(self, fg_color=C["green"], corner_radius=0, width=340)
        left.pack(side="left", fill="y")
        left.pack_propagate(False)

        ctk.CTkLabel(left, text="🌾", font=ctk.CTkFont(size=72)).pack(pady=(90, 8))
        ctk.CTkLabel(left, text="FarmSure",
                     font=ctk.CTkFont(size=34, weight="bold"),
                     text_color=C["white"]).pack()
        ctk.CTkLabel(left, text="Crop Insurance Portal",
                     font=ctk.CTkFont(size=15), text_color="#C8E6C9").pack(pady=(4, 0))
        ctk.CTkLabel(left, text="Protecting farmers,\none harvest at a time.",
                     font=ctk.CTkFont(size=13), text_color="#A5D6A7",
                     justify="center", wraplength=240).pack(pady=(40, 0))

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
