import customtkinter as ctk
from farmsure.ui.theme import C, STATUS_COLOR
from farmsure.ui.widgets import Card, Heading
import farmsure.db as db


class MyClaimsPage(ctk.CTkScrollableFrame):
    def __init__(self, master):
        super().__init__(master, fg_color=C["bg"], corner_radius=0,
                         scrollbar_button_color=C["card2"])

    def refresh(self, user):
        for w in self.winfo_children():
            w.destroy()

        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.pack(fill="x", padx=32, pady=(28, 20))
        Heading(hdr, "My Claims", size=24).pack(anchor="w")
        ctk.CTkLabel(hdr, text="Track the status of all your submitted claims below.",
                     font=ctk.CTkFont(size=14), text_color=C["muted"]).pack(anchor="w", pady=(4, 0))

        claims = db.get_user_claims(user["id"])
        if not claims:
            empty = Card(self)
            empty.configure(border_width=1, border_color=C["border"])
            empty.pack(fill="x", padx=32)
            ctk.CTkLabel(empty,
                         text="🌾\n\nYou haven't submitted any claims yet.\nUse 'New Claim' to get started.",
                         font=ctk.CTkFont(size=14), text_color=C["muted"],
                         justify="center").pack(pady=40)
            return

        hrow = ctk.CTkFrame(self, fg_color="transparent")
        hrow.pack(fill="x", padx=32)
        for label, w in [("Claim #", 140), ("Crop", 150), ("Issue", 190),
                          ("Date", 110), ("Loss (USD)", 110), ("Status", 110)]:
            ctk.CTkLabel(hrow, text=label, font=ctk.CTkFont(size=11, weight="bold"),
                         text_color=C["muted"], width=w, anchor="w").pack(side="left", padx=4)

        ctk.CTkFrame(self, fg_color=C["border"], height=1).pack(fill="x", padx=32, pady=6)

        for claim in claims:
            row = Card(self)
            row.configure(border_width=1, border_color=C["border"])
            row.pack(fill="x", padx=32, pady=3)

            inner = ctk.CTkFrame(row, fg_color="transparent")
            inner.pack(fill="x", padx=12, pady=10)

            status = claim["status"]
            color  = STATUS_COLOR.get(status, C["muted"])

            for text, color_t, width in [
                (claim["claim_number"],             C["white"],       140),
                (claim["crop_type"],                C["muted"],       150),
                (claim["issue_type"],               C["muted"],       190),
                (claim["incident_date"],            C["muted"],       110),
                (f"${claim['estimated_loss']:,.2f}", C["green_light"], 110),
            ]:
                ctk.CTkLabel(inner, text=text, font=ctk.CTkFont(size=13),
                             text_color=color_t, width=width, anchor="w").pack(
                                 side="left", padx=4)

            ctk.CTkLabel(inner, text=f"  {status}  ",
                         font=ctk.CTkFont(size=12, weight="bold"),
                         fg_color=color, text_color=C["white"],
                         corner_radius=6, width=100).pack(side="left", padx=4)
