"""
Theme tests are pure-data checks — no Tk window needed.
Import only the data constants, not the module-level CTK calls.
"""
import pytest


def _load_theme():
    """Import theme constants without triggering CTK initialisation."""
    import importlib, sys, unittest.mock as mock

    # Stub out customtkinter so no display is required
    ctk_stub = mock.MagicMock()
    with mock.patch.dict(sys.modules, {"customtkinter": ctk_stub}):
        import farmsure.ui.theme as theme
        return theme


class TestPalette:
    REQUIRED_KEYS = [
        "bg", "sidebar", "card", "card2", "border",
        "green", "green_dark", "green_light",
        "amber", "blue", "red",
        "text", "muted", "white",
    ]

    def test_all_required_keys_present(self):
        theme = _load_theme()
        for key in self.REQUIRED_KEYS:
            assert key in theme.C, f"Missing palette key: {key}"

    def test_all_values_are_hex_colours(self):
        theme = _load_theme()
        for key, value in theme.C.items():
            assert isinstance(value, str), f"C[{key!r}] is not a string"
            assert value.startswith("#"), f"C[{key!r}] = {value!r} is not a hex colour"
            assert len(value) in (4, 7), f"C[{key!r}] = {value!r} has unexpected length"


class TestStatusColor:
    STATUSES = ["Pending", "Under Review", "Approved", "Rejected"]

    def test_all_statuses_mapped(self):
        theme = _load_theme()
        for status in self.STATUSES:
            assert status in theme.STATUS_COLOR, f"Missing STATUS_COLOR entry: {status}"

    def test_values_reference_palette(self):
        theme = _load_theme()
        palette_values = set(theme.C.values())
        for status, colour in theme.STATUS_COLOR.items():
            assert colour in palette_values, (
                f"STATUS_COLOR[{status!r}] = {colour!r} is not in the palette"
            )


class TestStatusActions:
    STATUSES = ["Pending", "Under Review", "Approved", "Rejected"]

    def test_all_statuses_have_actions(self):
        theme = _load_theme()
        for status in self.STATUSES:
            assert status in theme.STATUS_ACTIONS, f"Missing STATUS_ACTIONS entry: {status}"

    def test_each_action_is_a_four_tuple(self):
        theme = _load_theme()
        for status, actions in theme.STATUS_ACTIONS.items():
            assert isinstance(actions, list), f"STATUS_ACTIONS[{status!r}] is not a list"
            for action in actions:
                assert len(action) == 4, (
                    f"STATUS_ACTIONS[{status!r}] action {action!r} must be a 4-tuple "
                    "(label, fg_color, hover_color, new_status)"
                )

    def test_target_statuses_are_valid(self):
        theme = _load_theme()
        valid = set(self.STATUSES)
        for status, actions in theme.STATUS_ACTIONS.items():
            for _label, _fg, _hover, new_status in actions:
                assert new_status in valid, (
                    f"STATUS_ACTIONS[{status!r}] targets invalid status {new_status!r}"
                )


class TestCropAndIssueTypes:
    def test_crop_types_not_empty(self):
        theme = _load_theme()
        assert len(theme.CROP_TYPES) > 0

    def test_issue_types_not_empty(self):
        theme = _load_theme()
        assert len(theme.ISSUE_TYPES) > 0

    def test_crop_types_are_strings(self):
        theme = _load_theme()
        assert all(isinstance(c, str) for c in theme.CROP_TYPES)

    def test_issue_types_are_strings(self):
        theme = _load_theme()
        assert all(isinstance(i, str) for i in theme.ISSUE_TYPES)

    def test_no_duplicate_crop_types(self):
        theme = _load_theme()
        assert len(theme.CROP_TYPES) == len(set(theme.CROP_TYPES))

    def test_no_duplicate_issue_types(self):
        theme = _load_theme()
        assert len(theme.ISSUE_TYPES) == len(set(theme.ISSUE_TYPES))
