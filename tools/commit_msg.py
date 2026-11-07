"""Git `commit-msg` hook: every commit message must start with `JAR-<number>: <description>`.

Git calls this with one argument: the path of a file holding the message being committed.
Exit code 0 lets the commit through; anything else aborts it.

Run by hand:  uv run python -m tools.commit_msg .git/COMMIT_EDITMSG
"""

import re
import sys
from collections.abc import Sequence
from pathlib import Path

# ^JAR-   literal project key        \d+   one or more digits
# :\s     a colon and one whitespace  \S    the description starts with a real character
JIRA_KEY_PATTERN = re.compile(r"^JAR-\d+: \S")

# Messages that git writes itself (merging a pull request, `git revert`) are allowed.
GIT_GENERATED_PREFIXES = ("Merge ", 'Revert "')

HELP = """\
Commit message rejected.

Every commit must start with the Jira key of the issue it belongs to:

    JAR-<number>: <description>

Example:  JAR-2: add pre-commit hooks
"""


def first_meaningful_line(text: str) -> str:
    """Return the first line that isn't blank or a git comment (lines starting with '#')."""
    for line in text.splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            return stripped
    return ""


def is_valid_message(message: str) -> bool:
    """True if the subject line follows the JARVIS commit convention."""
    subject = first_meaningful_line(message)
    if subject.startswith(GIT_GENERATED_PREFIXES):
        return True
    return JIRA_KEY_PATTERN.match(subject) is not None


def main(argv: Sequence[str]) -> int:
    if not argv:
        print("usage: commit_msg.py <path-to-commit-message-file>", file=sys.stderr)
        return 2
    message = Path(argv[0]).read_text(encoding="utf-8")
    if is_valid_message(message):
        return 0
    print(HELP, file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
