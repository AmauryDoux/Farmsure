"""
AI PR reviewer — fetches the diff, asks Claude Haiku to review it,
and posts the result as a comment on the pull request.
"""

import json
import os
import subprocess
import sys
import urllib.request

import anthropic

# ── Prompt ────────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """\
You are an expert code reviewer. Your job is to review pull request diffs and
provide concise, actionable feedback.

Focus on:
1. **Bugs & correctness** — logic errors, edge cases, off-by-one, null handling
2. **Security** — injection vulnerabilities, exposed secrets, unsafe operations
3. **Performance** — inefficient algorithms, N+1 queries, memory leaks
4. **Code quality** — readability, naming, duplication, dead code
5. **Tests** — missing coverage for new behaviour or bug fixes

Format your response as Markdown. Reference specific file names and line ranges
when relevant. Be constructive and specific. If the change looks good, say so
briefly — not every PR needs extensive feedback.
"""

# Truncate diffs that would blow the 200K context window of Haiku 4.5.
MAX_DIFF_CHARS = 80_000


# ── Diff ──────────────────────────────────────────────────────────────────────

def get_diff() -> str:
    base = os.environ["BASE_SHA"]
    head = os.environ["HEAD_SHA"]
    result = subprocess.run(
        ["git", "diff", f"{base}...{head}"],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout


# ── GitHub comment ────────────────────────────────────────────────────────────

def post_comment(body: str) -> None:
    token  = os.environ["GITHUB_TOKEN"]
    repo   = os.environ["REPO"]
    pr_num = os.environ["PR_NUMBER"]

    url  = f"https://api.github.com/repos/{repo}/issues/{pr_num}/comments"
    data = json.dumps({"body": body}).encode()

    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Authorization",        f"Bearer {token}")
    req.add_header("Content-Type",         "application/json")
    req.add_header("Accept",               "application/vnd.github+json")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")

    with urllib.request.urlopen(req) as resp:
        if resp.status not in (200, 201):
            print(f"Failed to post comment: HTTP {resp.status}", file=sys.stderr)
            sys.exit(1)


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    diff = get_diff().strip()

    if not diff:
        print("Empty diff — nothing to review.")
        return

    if len(diff) > MAX_DIFF_CHARS:
        diff = diff[:MAX_DIFF_CHARS] + "\n\n[… diff truncated due to size …]"

    client = anthropic.Anthropic()

    # Stream the response so the action doesn't time out on large diffs.
    # The system prompt is marked for caching — subsequent runs on the same
    # runner pay only the cache-read rate for that token block.
    with client.messages.stream(
        model="claude-haiku-4-5",
        max_tokens=2048,
        system=[
            {
                "type": "text",
                "text": SYSTEM_PROMPT,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=[
            {
                "role": "user",
                "content": (
                    "Please review the following pull request diff:\n\n"
                    f"```diff\n{diff}\n```"
                ),
            }
        ],
    ) as stream:
        message = stream.get_final_message()

    review_text = next(
        block.text for block in message.content if block.type == "text"
    )

    comment = (
        "## 🤖 AI Code Review\n\n"
        f"{review_text}\n\n"
        "---\n"
        f"*Reviewed by [Claude Haiku 4.5](https://www.anthropic.com) — "
        f"`{message.usage.input_tokens}` input / "
        f"`{message.usage.output_tokens}` output tokens*"
    )

    post_comment(comment)
    print("Review posted successfully.")


if __name__ == "__main__":
    main()
