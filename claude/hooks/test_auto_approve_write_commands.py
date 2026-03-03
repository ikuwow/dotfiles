#!/usr/bin/env python3
"""Tests for auto-approve-write-commands.py."""
import json
import subprocess
import sys
import unittest
from pathlib import Path

SCRIPT = Path(__file__).parent / "auto-approve-write-commands.py"
ALLOW_RESPONSE = {
    "hookSpecificOutput": {
        "hookEventName": "PermissionRequest",
        "decision": {"behavior": "allow"},
    }
}


def run_hook(payload: dict) -> str:
    result = subprocess.run(
        [sys.executable, SCRIPT],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


class TestAutoApproveWriteCommands(unittest.TestCase):
    def _assert_approved(self, command: str) -> None:
        payload = {"tool_name": "Bash", "tool_input": {"command": command}}
        output = run_hook(payload)
        self.assertEqual(json.loads(output), ALLOW_RESPONSE, f"Expected approval for: {command}")

    def _assert_not_approved(self, command: str) -> None:
        payload = {"tool_name": "Bash", "tool_input": {"command": command}}
        output = run_hook(payload)
        self.assertEqual(output, "", f"Expected no output for: {command}")

    # --- approved patterns ---

    def test_git_commit_simple(self):
        self._assert_approved('git commit -m "fix bug"')

    def test_git_commit_heredoc(self):
        self._assert_approved('git commit -m "$(cat <<\'EOF\'\nmessage\nEOF\n)"')

    def test_git_commit_multiple_m_with_empty(self):
        self._assert_approved('git commit -m "Subject" -m "" -m "Co-authored-by: X <x@example.com>"')

    def test_gh_pr_create_simple(self):
        self._assert_approved('gh pr create --draft --title "feat" --body "body"')

    def test_gh_pr_create_multiline_body(self):
        self._assert_approved('gh pr create --title "t" --body "$(cat <<\'EOF\'\nline1\nline2\nEOF\n)"')

    # --- not approved patterns ---

    def test_git_push(self):
        self._assert_not_approved("git push origin main")

    def test_git_rebase(self):
        self._assert_not_approved("git rebase main")

    def test_gh_pr_edit(self):
        self._assert_not_approved('gh pr edit 123 --title "new title"')

    def test_non_bash_tool(self):
        payload = {"tool_name": "Edit", "tool_input": {"file_path": "test.py"}}
        self.assertEqual(run_hook(payload), "")

    def test_invalid_json(self):
        result = subprocess.run(
            [sys.executable, SCRIPT],
            input="invalid json",
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.stdout.strip(), "")
        self.assertEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
