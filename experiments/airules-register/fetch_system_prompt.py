"""Fetch the published claude.ai system prompt and write the Opus 5 section.

The docs page wraps each prompt in MDX <Accordion> components, indents the body
by four spaces, and escapes markdown-significant characters. Undo all three so
the result can be passed to --system-prompt-file unchanged.

The committed copy of the output is what the recorded runs used; re-running this
against a later revision of the page will produce a different file.
"""

import re
import sys
import urllib.request

SOURCE = "https://platform.claude.com/docs/en/release-notes/system-prompts.md"
DST = "claude-ai-system-prompt.txt"

START_HEADING = "## Claude Opus 5"
NEXT_HEADING = "## Claude Fable 5"


def main() -> None:
    # The docs host rejects urllib's default User-Agent with a 403.
    request = urllib.request.Request(SOURCE, headers={"User-Agent": "curl/8"})
    with urllib.request.urlopen(request, timeout=60) as response:
        lines = response.read().decode("utf-8").splitlines()

    try:
        start = lines.index(START_HEADING)
        end = lines.index(NEXT_HEADING)
    except ValueError:
        sys.exit(f"headings not found in {SOURCE}; the page layout changed")

    body = [
        ln
        for ln in lines[start + 1 : end]
        if not re.match(r"\s*</?(AccordionGroup|Accordion)\b", ln)
    ]
    body = [ln[4:] if ln.startswith("    ") else ln for ln in body]

    text = "\n".join(body).strip()
    text = re.sub(r"\\([<>_&#*`\[\]])", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\((https?://[^)]+)\)", r"\1", text)

    with open(DST, "w", encoding="utf-8") as f:
        f.write(text + "\n")

    print(f"wrote {DST}: {len(text)} chars")


if __name__ == "__main__":
    main()
