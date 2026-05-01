import customtkinter as ctk
from farmsure.ui.theme import C
from farmsure.ui.widgets import Heading, FieldLabel, ModernEntry, PrimaryButton
import farmsure.db as db


class RegisterPage(ctk.CTkFrame):
    def __init__(self, master, on_register, on_go_login):
        super().__init__(master, fg_color=C["bg"], corner_radius=0)
        self._on_register = on_register

        left = ctk.CTkFrame(self, fg_color=C["green_dark"], corner_radius=0, width=340)
        left.pack(side="left", fill="y")
        left.pack_propagate(False)

        ctk.CTkLabel(left, text="🌿", font=ctk.CTkFont(size=72)).pack(pady=(90, 8))
        ctk.CTkLabel(left, text="FarmSure",
                     font=ctk.CTkFont(size=34, weight="bold"),
                     text_color=C["white"]).pack()
        ctk.CTkLabel(left, text="Crop Insurance Portal",
                     font=ctk.CTkFont(size=15), text_color="#A5D6A7").pack(pady=(4, 0))
        ctk.CTkLabel(left, text="Join thousands of farmers\nalready protected.",
                     font=ctk.CTkFont(size=13), text_color="#81C784",
                     justify="center", wraplength=240).pack(pady=(40, 0))

        right = ctk.CTkScrollableFrame(self, fg_color=C["bg"], corner_radius=0,
                                       scrollbar_button_color=C["card2"])
        right.pack(side="right", fill="both", expand=True)

        form = ctk.CTkFrame(right, fg_color="transparent")
        form.pack(expand=True, padx=60, pady=40)

        Heading(form, "Create account", size=26).pack(anchor="w", pady=(0, 4))
        ctk.CTkLabel(form, text="All fields marked with * are required",
                     font=ctk.CTkFont(size=13), text_color=C["muted"]).pack(anchor="w", pady=(0, 24))

        def field(label, placeholder, show=""):
            FieldLabel(form, label).pack(anchor="w")
            e = ModernEntry(form, placeholder=placeholder, width=380, show=show)
            e.pack(pady=(4, 14))
            return e

        self._name     = field("Full Name *",        "Jane Smith")
        self._email    = field("Email Address *",    "jane@farm.com")
        self._phone    = field("Phone Number",       "+1 (555) 000-0000")
        self._farm     = field("Farm Name",          "Green Acres Farm")
        self._location = field("Farm Location",      "County, State")
        self._pw       = field("Password *",         "Min. 8 characters", show="•")
        self._pw2      = field("Confirm Password *", "Repeat password",   show="•")

        self._err = ctk.CTkLabel(form, text="", text_color=C["red"],
                                 font=ctk.CTkFont(size=12), wraplength=380)
        self._err.pack(pady=(0, 8))

        PrimaryButton(form, "Create Account", command=self._submit, width=380).pack()

        row = ctk.CTkFrame(form, fg_color="transparent")
        row.pack(pady=(16, 0))
        ctk.CTkLabel(row, text="Already have an account?",
                     font=ctk.CTkFont(size=13), text_color=C["muted"]).pack(side="left")
        ctk.CTkButton(row, text=" Sign in", fg_color="transparent",
                      hover_color=C["bg"], text_color=C["green"],
                      font=ctk.CTkFont(size=13, weight="bold"),
                      command=on_go_login).pack(side="left")

    def _submit(self):
        name  = self._name.get().strip()
        email = self._email.get().strip()
        phone = self._phone.get().strip()
        farm  = self._farm.get().strip()
        loc   = self._location.get().strip()
        pw    = self._pw.get()
        pw2   = self._pw2.get()

        if not name or not email or not pw:
            self._err.configure(text="Please fill in all required fields.")
            return
        if pw != pw2:
            self._err.configure(text="Passwords do not match.")
            return
        if len(pw) < 8:
            self._err.configure(text="Password must be at least 8 characters.")
            return

        uid, err = db.register_user(name, email, pw, farm, loc, phone)
        if err:
            self._err.configure(text=err)
        else:
            self._err.configure(text="")
            user, _ = db.login_user(email, pw)
            self._on_register(user)

    def clear(self):
        for w in [self._name, self._email, self._phone, self._farm,
                  self._location, self._pw, self._pw2]:
            w.delete(0, "end")
        self._err.configure(text="")
