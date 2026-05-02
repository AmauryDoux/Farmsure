"""
Test generator agent — reads farmsure/db source files and writes
tests/test_generated.py using claude-haiku-4-5.

Fixes applied vs original:
- Streams the response to prevent truncation on large outputs
- Strips markdown code fences before saving (Claude sometimes wraps output)
- Stronger system prompt reinforcing raw Python output rules
"""

import os
import re
import anthropic
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

SYSTEM = """\
You are a Python testing expert. Your sole task is to output pytest test code.

CRITICAL RULES — follow exactly or the output is unusable:
1. Output raw Python source code ONLY. No markdown. No prose. No explanations.
2. Do NOT wrap the code in triple-backtick fences (```python ... ```).
   The first character of your response must be a valid Python token (import, #, or a class/def keyword).
3. Every class and function must be fully closed. Never leave a block, string, or
   expression incomplete at the end of the file.
4. Do not redefine the `clean_tables` fixture — it already exists in conftest.py
   and runs automatically (autouse=True).
5. Patch targets must match import paths. If get_connection is used in
   farmsure.db.users, patch it as farmsure.db.users.get_connection.
6. Suffix mock-based test class names with Mocked (e.g. TestUserLoginMocked)
   to avoid collisions with integration tests in tests/db/.
"""

PROMPT_TEMPLATE = """\
Generate comprehensive pytest tests for the following farmsure DB module source files.

Use unittest.mock.patch and MagicMock for unit tests (no real DB connection needed).
The conftest.py already handles test DB setup — do not duplicate it.

Source files:
{code_dump}

Output raw Python test code now:"""


def scan_files(directory: str = "farmsure/db") -> dict[str, str]:
    files = {}
    for path in Path(directory).rglob("*.py"):
        if "__pycache__" not in str(path):
            files[str(path)] = path.read_text()
    return files


def strip_fences(code: str) -> str:
    """Remove any markdown code fences the model may have added."""
    code = re.sub(r"^```[a-zA-Z]*\n?", "", code.strip())
    code = re.sub(r"\n?```$", "", code.strip())
    return code.strip()


def generate_tests(files: dict[str, str]) -> str:
    code_dump = "\n\n".join(
        f"# FILE: {name}\n{content}" for name, content in files.items()
    )

    print("Sending code to Claude (streaming)...")

    with client.messages.stream(
        model="claude-haiku-4-5",
        max_tokens=4096,
        system=SYSTEM,
        messages=[{"role": "user", "content": PROMPT_TEMPLATE.format(code_dump=code_dump)}],
    ) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)
        message = stream.get_final_message()

    print()  # newline after streamed output

    raw = next(block.text for block in message.content if block.type == "text")
    return strip_fences(raw)


def save_tests(test_code: str) -> None:
    output = Path("tests/test_generated.py")
    output.write_text(test_code + "\n")
    print(f"Saved to {output}")


def main() -> None:
    print("Scanning farmsure/db ...")
    files = scan_files()
    print(f"Found {len(files)} file(s): {list(files.keys())}")

    test_code = generate_tests(files)
    save_tests(test_code)

    print("\nRun tests with:")
    print("  pytest tests/test_generated.py -v")


if __name__ == "__main__":
    main()
