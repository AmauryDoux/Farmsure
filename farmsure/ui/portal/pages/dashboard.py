import customtkinter as ctk
from farmsure.ui.theme import C, STATUS_COLOR
from farmsure.ui.widgets import Card, Heading, StatCard
import farmsure.db as db


class DashboardPage(ctk.CTkScrollableFrame):
    def __init__(self, master):
        super().__init__(master, fg_color=C["bg"], corner_radius=0,
                         scrollbar_button_color=C["card2"])

    def refresh(self, user):
        for w in self.winfo_children():
            w.destroy()

        stats  = db.get_claim_stats(user["id"])
        claims = db.get_user_claims(user["id"])
        fname  = user.get("full_name", "Farmer").split()[0]

        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.pack(fill="x", padx=32, pady=(28, 4))
        Heading(hdr, f"Good day, {fname} 👋", size=26).pack(anchor="w")
        ctk.CTkLabel(hdr, text="Here's an overview of your farm insurance account.",
                     font=ctk.CTkFont(size=14), text_color=C["muted"]).pack(anchor="w", pady=(4, 0))

        grid = ctk.CTkFrame(self, fg_color="transparent")
        grid.pack(fill="x", padx=32, pady=(20, 0))
        grid.columnconfigure((0, 1, 2, 3), weight=1, uniform="stat")

        for col, (lbl, val, color) in enumerate([
            ("Total Claims", stats["total"] or 0,    C["blue"]),
            ("Pending",      stats["pending"] or 0,  C["amber"]),
            ("Approved",     stats["approved"] or 0, C["green"]),
            ("Rejected",     stats["rejected"] or 0, C["red"]),
        ]):
            StatCard(grid, lbl, val, color=color).grid(
                row=0, column=col, padx=6, pady=4, sticky="nsew")

        tc = Card(self)
        tc.configure(border_width=1, border_color=C["border"])
        tc.pack(fill="x", padx=32, pady=(14, 0))
        inner = ctk.CTkFrame(tc, fg_color="transparent")
        inner.pack(fill="x", padx=18, pady=14)
        ctk.CTkLabel(inner, text="Total Loss Claimed",
                     font=ctk.CTkFont(size=13), text_color=C["muted"]).pack(anchor="w")
        total_val = stats["total_claimed"] or 0
        ctk.CTkLabel(inner, text=f"${total_val:,.2f}",
                     font=ctk.CTkFont(size=28, weight="bold"),
                     text_color=C["green_light"]).pack(anchor="w")

        Heading(self, "Recent Claims", size=17).pack(anchor="w", padx=32, pady=(28, 10))

        if not claims:
            empty = Card(self)
            empty.pack(fill="x", padx=32, pady=4)
            ctk.CTkLabel(empty, text="No claims yet. Submit your first claim to get started.",
                         font=ctk.CTkFont(size=13), text_color=C["muted"]).pack(pady=28)
        else:
            for claim in claims[:5]:
                self._claim_row(claim)

    def _claim_row(self, claim):
        row = Card(self)
        row.configure(border_width=1, border_color=C["border"])
        row.pack(fill="x", padx=32, pady=4)

        inner = ctk.CTkFrame(row, fg_color="transparent")
        inner.pack(fill="x", padx=18, pady=12)
        inner.columnconfigure(1, weight=1)

        status = claim["status"]
        color  = STATUS_COLOR.get(status, C["muted"])

        ctk.CTkLabel(inner, text=claim["claim_number"],
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=C["white"]).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(inner, text=f"{claim['crop_type']}  ·  {claim['issue_type']}",
                     font=ctk.CTkFont(size=12), text_color=C["muted"]).grid(
                         row=1, column=0, sticky="w")

        ctk.CTkLabel(inner, text=f"  {status}  ",
                     font=ctk.CTkFont(size=12, weight="bold"),
                     fg_color=color, text_color=C["white"],
                     corner_radius=6).grid(row=0, column=2, rowspan=2, sticky="e", padx=(8, 0))

        ctk.CTkLabel(inner, text=f"${claim['estimated_loss']:,.2f}",
                     font=ctk.CTkFont(size=13),
                     text_color=C["muted"]).grid(row=0, column=1, sticky="e", padx=8)
        ctk.CTkLabel(inner, text=claim["incident_date"],
                     font=ctk.CTkFont(size=11),
                     text_color=C["muted"]).grid(row=1, column=1, sticky="e", padx=8)
