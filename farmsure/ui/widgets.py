import customtkinter as ctk
from farmsure.ui.theme import C


def _bind_tree(widget, event, callback):
    widget.bind(event, callback)
    for child in widget.winfo_children():
        _bind_tree(child, event, callback)


class Card(ctk.CTkFrame):
    def __init__(self, master, **kw):
        kw.setdefault("fg_color", C["card"])
        kw.setdefault("corner_radius", 12)
        super().__init__(master, **kw)


class Heading(ctk.CTkLabel):
    def __init__(self, master, text, size=22, **kw):
        kw.setdefault("font", ctk.CTkFont(size=size, weight="bold"))
        kw.setdefault("text_color", C["white"])
        super().__init__(master, text=text, **kw)


class SectionLabel(ctk.CTkLabel):
    def __init__(self, master, text, **kw):
        kw.setdefault("font", ctk.CTkFont(size=11, weight="normal"))
        kw.setdefault("text_color", C["muted"])
        super().__init__(master, text=text.upper(), **kw)


class FieldLabel(ctk.CTkLabel):
    def __init__(self, master, text, **kw):
        kw.setdefault("font", ctk.CTkFont(size=13))
        kw.setdefault("text_color", C["muted"])
        super().__init__(master, text=text, **kw)


class ModernEntry(ctk.CTkEntry):
    def __init__(self, master, placeholder="", **kw):
        kw.setdefault("fg_color", C["card2"])
        kw.setdefault("border_color", C["border"])
        kw.setdefault("text_color", C["text"])
        kw.setdefault("placeholder_text_color", C["muted"])
        kw.setdefault("height", 42)
        kw.setdefault("corner_radius", 8)
        kw.setdefault("font", ctk.CTkFont(size=14))
        super().__init__(master, placeholder_text=placeholder, **kw)


class PrimaryButton(ctk.CTkButton):
    def __init__(self, master, text, command=None, **kw):
        kw.setdefault("fg_color", C["green"])
        kw.setdefault("hover_color", C["green_dark"])
        kw.setdefault("text_color", C["white"])
        kw.setdefault("height", 44)
        kw.setdefault("corner_radius", 10)
        kw.setdefault("font", ctk.CTkFont(size=14, weight="bold"))
        super().__init__(master, text=text, command=command, **kw)


class GhostButton(ctk.CTkButton):
    def __init__(self, master, text, command=None, **kw):
        kw.setdefault("fg_color", "transparent")
        kw.setdefault("hover_color", C["card2"])
        kw.setdefault("text_color", C["muted"])
        kw.setdefault("height", 40)
        kw.setdefault("corner_radius", 8)
        kw.setdefault("font", ctk.CTkFont(size=13))
        super().__init__(master, text=text, command=command, **kw)


class StatCard(Card):
    def __init__(self, master, label, value, color=None, **kw):
        super().__init__(master, **kw)
        color = color or C["green"]
        self.configure(border_width=1, border_color=C["border"])
        ctk.CTkLabel(self, text=label, font=ctk.CTkFont(size=12),
                     text_color=C["muted"]).pack(anchor="w", padx=18, pady=(16, 2))
        ctk.CTkLabel(self, text=str(value), font=ctk.CTkFont(size=30, weight="bold"),
                     text_color=color).pack(anchor="w", padx=18, pady=(0, 16))
