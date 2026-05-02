"""
Local smoke-test for the PR review script.
Runs a Claude review against a real git diff and prints the result.
No GitHub token or PR number needed.

Usage:
    python agents/test_review.py                      # diff of last commit
    python agents/test_review.py <base_sha> <head_sha>  # custom range
"""

import re
import subprocess
import sys
import anthropic
from dotenv import load_dotenv

load_dotenv()

SYSTEM_PROMPT = """\
You are an expert code reviewer. Your job is to review pull request diffs and
provide concise, actionable feedback.

Focus on:
1. **Bugs & correctness** — logic errors, edge cases, off-by-one, null handling
2. **Security** — injection vulnerabilities, exposed secrets, unsafe operations
3. **Performance** — inefficient algorithms, N+1 queries, memory leaks
4. **Code quality** — readability, naming, duplication, dead code
5. **Tests** — missing coverage for new behaviour or bug fixes

Format your response as Markdown. Be constructive and specific.
"""

MAX_DIFF_CHARS = 80_000


def get_diff(base: str, head: str) -> str:
    result = subprocess.run(
        ["git", "diff", f"{base}...{head}"],
        capture_output=True, text=True, check=True,
    )
    return result.stdout


def get_last_commit_diff() -> str:
    result = subprocess.run(
        ["git", "diff", "HEAD~1...HEAD"],
        capture_output=True, text=True, check=True,
    )
    return result.stdout


def review(diff: str) -> str:
    if len(diff) > MAX_DIFF_CHARS:
        diff = diff[:MAX_DIFF_CHARS] + "\n\n[… diff truncated …]"

    client = anthropic.Anthropic()
    print("Calling Claude Haiku 4.5 ...\n")

    with client.messages.stream(
        model="claude-haiku-4-5",
        max_tokens=2048,
        system=[{"type": "text", "text": SYSTEM_PROMPT,
                 "cache_control": {"type": "ephemeral"}}],
        messages=[{"role": "user", "content":
                   f"Please review this diff:\n\n```diff\n{diff}\n```"}],
    ) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)
        message = stream.get_final_message()

    print(f"\n\n---\nTokens — input: {message.usage.input_tokens} "
          f"(cached: {message.usage.cache_read_input_tokens}) "
          f"output: {message.usage.output_tokens}")
    return next(b.text for b in message.content if b.type == "text")


def main() -> None:
    if len(sys.argv) == 3:
        diff = get_diff(sys.argv[1], sys.argv[2])
    else:
        print("Using diff of last commit (HEAD~1...HEAD)\n")
        diff = get_last_commit_diff()

    if not diff.strip():
        print("No diff found — commit something first, or pass two SHAs.")
        return

    review(diff)


if __name__ == "__main__":
    main()
