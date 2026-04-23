#!/usr/bin/env python3
"""PreCompact hook: back up the transcript JSONL before compaction."""

import json
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path


def main():
    try:
        input_data = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)

    transcript_path = input_data.get("transcript_path", "")
    if not transcript_path or not os.path.exists(transcript_path):
        sys.exit(0)

    session_id = input_data.get("session_id", "unknown")
    trigger = input_data.get("trigger", "unknown")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Back up the transcript JSONL
    backup_dir = Path.home() / ".claude" / "transcript-backups"
    backup_dir.mkdir(parents=True, exist_ok=True)

    backup_name = f"{session_id}_pre_compact_{trigger}_{timestamp}.jsonl"
    backup_path = backup_dir / backup_name
    shutil.copy2(transcript_path, backup_path)

    # Record the backup path in the project's memory directory
    transcript_p = Path(transcript_path)
    # transcript_path is like ~/.claude/projects/<project>/<session>.jsonl
    project_dir = transcript_p.parent
    memory_dir = project_dir / "memory"
    if memory_dir.is_dir():
        snapshot_path = memory_dir / "compact-snapshot.md"
        snapshot_path.write_text(
            f"# Pre-compact transcript backup\n\n"
            f"- Timestamp: {timestamp}\n"
            f"- Trigger: {trigger}\n"
            f"- Backup: {backup_path}\n"
        )

    print(f"Transcript backed up to {backup_path}")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        # Never block compaction
        sys.exit(0)
