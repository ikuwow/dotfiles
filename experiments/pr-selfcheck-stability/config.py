"""Fixed inputs for the pr-selfcheck run-to-run agreement experiment.

Everything a run depends on lives here, so changing the design is a diff
against one file rather than an edit scattered across the scripts.

The target is a merged PR. Its body, its diff and its head commit are frozen,
so every run of the check sees byte-identical input and any difference between
runs comes from the checker. An open PR cannot serve here: a body edited
between runs makes disagreement uninterpretable, and two of the runs recorded
in ikuwow/dotfiles#369 reported the body changing between their own fetches.

`/pr-selfcheck` is invoked exactly as a session invokes it -- the slash
command, no model or effort override, no permission-mode override, under this
repository's own settings. The skill's frontmatter (`model: sonnet`,
`effort: medium`, `context: fork`, `agent: general-purpose`) is what decides
how the check runs, and overriding any of it from the harness would measure a
detector that is not the deployed one.
"""

import os

REPO = "ikuwow/dotfiles"
PR = 367

RUNS = 10
TIMEOUT_SEC = 900

DATA_DIR = "round1"
RUNS_DIR = os.path.join(DATA_DIR, "runs")
RECORD_FILE = os.path.join(DATA_DIR, "runs.jsonl")
FINDINGS_FILE = os.path.join(DATA_DIR, "findings.jsonl")
CLUSTERS_FILE = os.path.join(DATA_DIR, "clusters.json")

# Session ids are derived from the run index so an interrupted round restarts
# without renaming anything, and so a recorded run can be traced back to the
# transcript Claude Code wrote under ~/.claude/projects.
SESSION_UUID = "5e1fc4ec-0000-4000-8000-%012d"

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROJECTS_DIR = os.path.expanduser("~/.claude/projects/" + REPO_ROOT.replace("/", "-"))

JUDGE_MODEL = "claude-sonnet-5"

# Reading this record is the evidence route that separated the one run in
# ikuwow/dotfiles#369 that reported the unaccounted hunk from the two that did
# not. It is gitignored, so it exists only in this working tree; a run from a
# fresh clone cannot take this route at all.
EVIDENCE_RECORD = "ikuwowfiles/pr-guidelines-reformat-check.md"

# The five properties `pr-guidelines.md` defines, in the order it states them.
# The output format requires one Property walk line per property, so a run
# missing one of these produced a malformed report.
PROPERTIES = ["Decidable", "Grounded", "Necessary", "Scoped", "Conformant"]

SEVERITIES = ["Fix", "Note", "Unverifiable"]
