import customtkinter as ctk

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

C = {
    "bg":          "#161618",
    "sidebar":     "#1C1C1E",
    "card":        "#2C2C2E",
    "card2":       "#3A3A3C",
    "border":      "#3A3A3C",
    "green":       "#34A853",
    "green_dark":  "#1E7E34",
    "green_light": "#81C784",
    "amber":       "#FFA726",
    "blue":        "#4A9EFF",
    "red":         "#FF5252",
    "text":        "#F5F5F5",
    "muted":       "#8E8E93",
    "white":       "#FFFFFF",
}

STATUS_COLOR = {
    "Pending":      C["amber"],
    "Under Review": C["blue"],
    "Approved":     C["green"],
    "Rejected":     C["red"],
}

STATUS_ACTIONS = {
    "Pending":      [("Start Review", C["blue"],  "#2A6BC9",      "Under Review")],
    "Under Review": [("Approve",      C["green"], C["green_dark"], "Approved"),
                     ("Reject",       C["red"],   "#CC3030",       "Rejected")],
    "Approved":     [("Reopen",       C["blue"],  "#2A6BC9",      "Under Review")],
    "Rejected":     [("Reopen",       C["blue"],  "#2A6BC9",      "Under Review")],
}

CROP_TYPES = [
    "Wheat", "Corn / Maize", "Rice", "Soybeans", "Cotton",
    "Vegetables", "Fruits / Orchards", "Hay / Forage", "Other",
]

ISSUE_TYPES = [
    "Drought / Lack of Water", "Flood / Excess Water", "Frost / Freeze Damage",
    "Storm / Hail Damage", "Pest Infestation", "Disease / Blight",
    "Poor Germination", "Soil Contamination", "Wildfire Damage", "Other",
]
