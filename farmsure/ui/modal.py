"""
Themed modal overlay.

Uses two overrideredirect windows:
  1. A semi-transparent backdrop so the app dims but stays visible underneath.
  2. The modal card itself — no OS chrome, fully custom.

Public API
----------
ask_confirm(master, title, message, icon) -> bool
show_info(master, title, message, icon)
"""

import customtkinter as ctk
from farmsure.ui.theme import C


class _ThemedModal:
    def __init__(
        self,
        root,
        title: str,
        message: str,
        icon: str,
        confirm: bool,
    ):
        self.result = False

        root.update_idletasks()
        rx = root.winfo_rootx()
        ry = root.winfo_rooty()
        rw = root.winfo_width()
        rh = root.winfo_height()

        # ── 1. Semi-transparent dimmed backdrop ───────────────────────────────
        self._backdrop = ctk.CTkToplevel(root)
        self._backdrop.overrideredirect(True)
        self._backdrop.configure(fg_color="#000000")
        self._backdrop.wm_attributes("-alpha", 0.45)
        self._backdrop.geometry(f"{rw}x{rh}+{rx}+{ry}")
        self._backdrop.lift()

        # ── 2. Modal card (no OS chrome) ──────────────────────────────────────
        self._win = ctk.CTkToplevel(root)
        self._win.overrideredirect(True)
        self._win.configure(fg_color=C["card"])

        # Border frame fills the window
        border = ctk.CTkFrame(
            self._win,
            fg_color=C["card"],
            border_width=1,
            border_color=C["border"],
            corner_radius=0,
        )
        border.pack(fill="both", expand=True)

        inner = ctk.CTkFrame(border, fg_color="transparent")
        inner.pack(padx=40, pady=36)

        # ── Icon badge ────────────────────────────────────────────────────────
        ctk.CTkLabel(
            inner,
            text=icon,
            font=ctk.CTkFont(size=24),
            fg_color=C["green"],
            text_color=C["white"],
            width=60, height=60,
            corner_radius=30,
        ).pack(pady=(0, 18))

        # ── Title ─────────────────────────────────────────────────────────────
        ctk.CTkLabel(
            inner,
            text=title,
            font=ctk.CTkFont(size=19, weight="bold"),
            text_color=C["white"],
        ).pack()

        # ── Divider ───────────────────────────────────────────────────────────
        ctk.CTkFrame(inner, fg_color=C["border"], height=1).pack(
            fill="x", pady=(14, 14)
        )

        # ── Message ───────────────────────────────────────────────────────────
        ctk.CTkLabel(
            inner,
            text=message,
            font=ctk.CTkFont(size=13),
            text_color=C["muted"],
            wraplength=280,
            justify="center",
        ).pack()

        # ── Buttons ───────────────────────────────────────────────────────────
        btn_row = ctk.CTkFrame(inner, fg_color="transparent")
        btn_row.pack(pady=(24, 0))

        if confirm:
            ctk.CTkButton(
                btn_row,
                text="Cancel",
                fg_color=C["card2"],
                hover_color=C["border"],
                text_color=C["muted"],
                font=ctk.CTkFont(size=13),
                height=40, corner_radius=8, width=120,
                command=self._cancel,
            ).pack(side="left", padx=(0, 10))

            ctk.CTkButton(
                btn_row,
                text="Confirm",
                fg_color=C["green"],
                hover_color=C["green_dark"],
                text_color=C["white"],
                font=ctk.CTkFont(size=13, weight="bold"),
                height=40, corner_radius=8, width=120,
                command=self._confirm,
            ).pack(side="left")
        else:
            ctk.CTkButton(
                btn_row,
                text="Got it",
                fg_color=C["green"],
                hover_color=C["green_dark"],
                text_color=C["white"],
                font=ctk.CTkFont(size=14, weight="bold"),
                height=40, corner_radius=8, width=200,
                command=self._ok,
            ).pack()

        # ── Position card centred over the root window ────────────────────────
        self._win.update_idletasks()
        cw = self._win.winfo_reqwidth()
        ch = self._win.winfo_reqheight()
        cx = rx + (rw - cw) // 2
        cy = ry + (rh - ch) // 2
        self._win.geometry(f"{cw}x{ch}+{cx}+{cy}")

        self._win.lift()
        self._win.grab_set()
        root.wait_window(self._win)

    # ── Button handlers ───────────────────────────────────────────────────────

    def _confirm(self):
        self.result = True
        self._close()

    def _cancel(self):
        self.result = False
        self._close()

    def _ok(self):
        self._close()

    def _close(self):
        self._win.grab_release()
        self._win.destroy()
        self._backdrop.destroy()


# ── Public helpers ────────────────────────────────────────────────────────────

def ask_confirm(
    master,
    title: str,
    message: str,
    icon: str = "?",
) -> bool:
    """Show a Confirm / Cancel modal. Returns True if the user confirms."""
    return _ThemedModal(master, title, message, icon, confirm=True).result


def show_info(
    master,
    title: str,
    message: str,
    icon: str = "✓",
) -> None:
    """Show an informational modal with a single Got it button."""
    _ThemedModal(master, title, message, icon, confirm=False)
