"""Run `/pr-selfcheck` against the fixed PR N times and record each run.

Appends to runs.jsonl as each run completes and skips runs already recorded,
so a round interrupted by a rate limit or a killed process restarts with the
same command and redoes only what is missing.

Runs are sequential, never concurrent. The check's own steps write to the
shared repository: `git fetch origin pull/<n>/head` moves FETCH_HEAD, which
concurrent runs would race on, and step 3 reads through that ref.

The working tree must be clean before a round starts. One of the runs recorded
in ikuwow/dotfiles#369 declined to read a file after judging the tree's
uncommitted changes to belong to another session, so uncommitted state is an
input to the detector and not a neutral background.

Each run gets its own session id, which is also where Claude Code writes the
transcripts. The final report comes back on the parent's stream, but the parent
only carries the forked subagent's answer; what the subagent actually read is
in its own transcript under <session-id>/subagents/, and that trace is what
separates a run that gathered the evidence and judged differently from one that
never gathered it.
"""

import json
import os
import shutil
import subprocess
import sys
import time

import config


def repo_state():
    def git(*args):
        return subprocess.run(["git", *args], cwd=config.REPO_ROOT,
                              capture_output=True, text=True, check=True).stdout.strip()
    return {"head": git("rev-parse", "HEAD"),
            "branch": git("rev-parse", "--abbrev-ref", "HEAD"),
            "dirty": git("status", "--porcelain")}


def completed_runs():
    if not os.path.exists(config.RECORD_FILE):
        return set()
    with open(config.RECORD_FILE) as f:
        return {json.loads(line)["run"] for line in f if line.strip()}


def collect_transcripts(session_id, index):
    """Copy the parent and subagent transcripts out of ~/.claude/projects.

    They are copied rather than read in place because Claude Code prunes that
    directory, and a round's analysis has to stay reproducible from the
    committed files alone.
    """
    session_dir = os.path.join(config.PROJECTS_DIR, session_id)
    copied = []
    parent = os.path.join(config.PROJECTS_DIR, session_id + ".jsonl")
    if os.path.exists(parent):
        dest = os.path.join(config.RUNS_DIR, "run-%02d.session.jsonl" % index)
        shutil.copy(parent, dest)
        copied.append(os.path.basename(dest))
    agents_dir = os.path.join(session_dir, "subagents")
    if os.path.isdir(agents_dir):
        for n, name in enumerate(sorted(f for f in os.listdir(agents_dir)
                                        if f.endswith(".jsonl"))):
            dest = os.path.join(config.RUNS_DIR, "run-%02d.agent%d.jsonl" % (index, n))
            shutil.copy(os.path.join(agents_dir, name), dest)
            copied.append(os.path.basename(dest))
    return copied


def one_run(index):
    session_id = config.SESSION_UUID % index
    stream_path = os.path.join(config.RUNS_DIR, "run-%02d.stream.jsonl" % index)
    started = time.time()
    with open(stream_path, "w") as out:
        try:
            proc = subprocess.run(
                ["claude", "-p", "/pr-selfcheck %d" % config.PR,
                 "--output-format", "stream-json", "--verbose",
                 "--session-id", session_id],
                cwd=config.REPO_ROOT, stdout=out, stderr=subprocess.PIPE,
                text=True, timeout=config.TIMEOUT_SEC)
            outcome, returncode, stderr = "completed", proc.returncode, proc.stderr
        except subprocess.TimeoutExpired:
            # Recorded as an outcome rather than raised. One run in
            # ikuwow/dotfiles#369 terminated on a 600s stall with no output,
            # so a stall is a result the round has to be able to report.
            outcome, returncode, stderr = "timeout", None, ""
    elapsed = time.time() - started

    result = {}
    with open(stream_path) as f:
        for line in f:
            event = json.loads(line)
            if event.get("type") == "result":
                result = event
    text = ""
    with open(stream_path) as f:
        for line in f:
            event = json.loads(line)
            if event.get("type") == "assistant":
                for block in event["message"].get("content") or []:
                    if block.get("type") == "text":
                        text = block["text"]

    return {"run": index,
            "session_id": session_id,
            "outcome": outcome,
            "returncode": returncode,
            "stderr": stderr[-2000:],
            "elapsed_sec": round(elapsed, 1),
            "cost_usd": result.get("total_cost_usd"),
            "report": text,
            "transcripts": collect_transcripts(session_id, index)}


def main():
    os.makedirs(config.RUNS_DIR, exist_ok=True)
    state = repo_state()
    if state["dirty"]:
        sys.exit("working tree is dirty; commit or stash before a round:\n"
                 + state["dirty"])
    done = completed_runs()
    for index in range(1, config.RUNS + 1):
        if index in done:
            print("run %02d already recorded" % index)
            continue
        print("run %02d ..." % index, flush=True)
        record = one_run(index)
        record["repo"] = state
        with open(config.RECORD_FILE, "a") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
        print("  %s in %ss, $%s" % (record["outcome"], record["elapsed_sec"],
                                    record["cost_usd"]), flush=True)


if __name__ == "__main__":
    main()
