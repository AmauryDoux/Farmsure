"""
Root conftest — runs before any collection.

Automatically repairs tests/test_generated.py if the agent produces it with
markdown code fences or a truncated (syntactically incomplete) tail, both of
which are common agent output artefacts.
"""

import ast
import pathlib

def _repair_generated(path: pathlib.Path) -> None:
    if not path.exists():
        return

    text = path.read_text()

    # 1. Strip opening markdown fence (```python or ```)
    lines = text.splitlines()
    if lines and lines[0].startswith("```"):
        lines = lines[1:]

    # 2. Strip closing fence
    if lines and lines[-1].strip().startswith("```"):
        lines = lines[:-1]

    # 3. Trim truncated tail: remove lines from the end until the file parses
    while lines:
        candidate = "\n".join(lines)
        try:
            ast.parse(candidate)
            break
        except SyntaxError:
            lines.pop()

    path.write_text("\n".join(lines) + "\n")


def pytest_sessionstart(session):
    _repair_generated(pathlib.Path("tests/test_generated.py"))
# Test for PR testing
