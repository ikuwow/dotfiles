"""Run `/pr-selfcheck` against the round's PR N times and record each run.

Appends to runs.jsonl as each run completes and skips runs already recorded,
so a round interrupted by a rate limit or a killed process restarts with the
same command and redoes only what is missing.

Each run executes in its own clone of the repository. The check's step 3 runs
`git fetch origin pull/<n>/head` and reads through that ref, so runs sharing
one repository would race on FETCH_HEAD; a clone per run removes the shared
state and lets the round run several at a time. The clone's `origin` is
repointed at the real remote, because a clone taken from a local path would
otherwise resolve both `gh` and the PR ref against that path.

The clone carries the gitignored paths named in `config.MIRRORED_PATHS`. They
are part of what the check reads -- one route to the evidence in
ikuwow/dotfiles#369 was a gitignored record -- and a clone without them
measures a different detector.

The main working tree must be clean before a round starts, and stays clean
throughout. One of the runs recorded in #369 declined to read a file after
judging the tree's uncommitted changes to belong to another session, so
uncommitted state is an input to the detector and not a neutral background. A
round's own output would otherwise accumulate as untracked files, so the output
directory goes into .git/info/exclude for the duration and is committed
afterwards.

The main tree still decides which rules the check reads: `~/.claude/skills`
resolves into it, and every run recorded so far loaded `pr-guidelines.md`
through that path or through the tree's own. A round therefore measures
whatever the main tree has checked out, and the clones inherit it because they
are taken from that tree at that branch.

Each run gets its own session id, which is also where Claude Code writes the
transcripts. The final report comes back on the parent's stream, but the parent
only carries the forked subagent's answer; what the subagent actually read is
in its own transcript under <session-id>/subagents/, and that trace is what
separates a run that gathered the evidence and judged differently from one that
never gathered it.
"""

import glob
import json
import os
import shutil
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import config

_write_lock = threading.Lock()


def git(*args, cwd=None):
    return subprocess.run(["git", *args], cwd=cwd or config.REPO_ROOT,
                          capture_output=True, text=True, check=True).stdout.strip()


def repo_state():
    return {"head": git("rev-parse", "HEAD"),
            "branch": git("rev-parse", "--abbrev-ref", "HEAD"),
            "dirty": git("status", "--porcelain")}


def hide_output_dir():
    """Keep the round's own output out of `git status` while the round runs.

    Written to .git/info/exclude rather than to a tracked .gitignore: the
    exclusion is an artifact of collection, and the files it hides are meant to
    be committed once the round is over.
    """
    path = os.path.join(config.REPO_ROOT, ".git", "info", "exclude")
    entry = "experiments/pr-selfcheck-stability/" + config.DATA_DIR + "/"
    with open(path) as f:
        if entry in f.read().splitlines():
            return
    with open(path, "a") as f:
        f.write(entry + "\n")


def make_workspace(index, branch):
    """Clone the repository for one run and mirror the paths git does not carry."""
    path = os.path.join(config.WORKSPACE_ROOT, "run-%02d" % index)
    if os.path.exists(path):
        shutil.rmtree(path)
    os.makedirs(config.WORKSPACE_ROOT, exist_ok=True)
    git("clone", "--quiet", "--branch", branch, config.REPO_ROOT, path)
    git("remote", "set-url", "origin", config.REMOTE_URL, cwd=path)
    for relative in config.MIRRORED_PATHS:
        source = os.path.join(config.REPO_ROOT, relative)
        if not os.path.exists(source):
            continue
        destination = os.path.join(path, relative)
        if os.path.isdir(source):
            shutil.copytree(source, destination, dirs_exist_ok=True)
        else:
            shutil.copy(source, destination)
    return path


def completed_runs():
    """Runs already recorded, dropping ones that failed so they are retried.

    A timeout counts as recorded: a run that stalls is a result the round
    reports. A non-zero exit is not a result -- it means the run never reached
    the check -- so its record is removed and the run is taken again.
    """
    if not os.path.exists(config.RECORD_FILE):
        return set()
    with open(config.RECORD_FILE) as f:
        records = [json.loads(line) for line in f if line.strip()]
    kept = [record for record in records if record["outcome"] != "failed"]
    if len(kept) != len(records):
        with open(config.RECORD_FILE, "w") as f:
            for record in kept:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
    return {record["run"] for record in kept}


def collect_transcripts(session_id, index):
    """Copy the parent and subagent transcripts out of ~/.claude/projects.

    They are copied rather than read in place because Claude Code prunes that
    directory, and a round's analysis has to stay reproducible from the
    committed files alone.

    A run in a clone writes under the project directory named after the clone's
    path, so the session is located by searching for its id rather than by
    reconstructing the name Claude Code derives from a working directory.
    """
    copied = []
    for parent in glob.glob(os.path.join(config.PROJECTS_ROOT, "*",
                                         session_id + ".jsonl")):
        dest = os.path.join(config.RUNS_DIR, "run-%02d.session.jsonl" % index)
        shutil.copy(parent, dest)
        copied.append(os.path.basename(dest))
        agents_dir = os.path.join(os.path.dirname(parent), session_id, "subagents")
        if os.path.isdir(agents_dir):
            for n, name in enumerate(sorted(f for f in os.listdir(agents_dir)
                                            if f.endswith(".jsonl"))):
                dest = os.path.join(config.RUNS_DIR,
                                    "run-%02d.agent%d.jsonl" % (index, n))
                shutil.copy(os.path.join(agents_dir, name), dest)
                copied.append(os.path.basename(dest))
    return copied


def one_run(index, branch):
    session_id = config.SESSION_UUID % (config.SESSION_OFFSET + index)
    stream_path = os.path.join(config.RUNS_DIR, "run-%02d.stream.jsonl" % index)
    workspace = make_workspace(index, branch)
    started = time.time()
    with open(stream_path, "w") as out:
        try:
            proc = subprocess.run(
                ["claude", "-p", "/pr-selfcheck %d" % config.PR,
                 "--output-format", "stream-json", "--verbose",
                 "--session-id", session_id],
                cwd=workspace, stdout=out, stderr=subprocess.PIPE,
                text=True, timeout=config.TIMEOUT_SEC)
            # A non-zero exit is recorded as its own outcome. Reading it as a
            # completed run would enter the round as a run that reported
            # nothing, which is indistinguishable in the tables from a run that
            # looked and found nothing.
            outcome = "completed" if proc.returncode == 0 else "failed"
            returncode, stderr = proc.returncode, proc.stderr
        except subprocess.TimeoutExpired:
            # Recorded as an outcome rather than raised. One run in
            # ikuwow/dotfiles#369 terminated on a 600s stall with no output,
            # so a stall is a result the round has to be able to report.
            outcome, returncode, stderr = "timeout", None, ""
    elapsed = time.time() - started

    result, text = {}, ""
    with open(stream_path) as f:
        for line in f:
            event = json.loads(line)
            if event.get("type") == "result":
                result = event
            elif event.get("type") == "assistant":
                for block in event["message"].get("content") or []:
                    if block.get("type") == "text":
                        text = block["text"]

    # Transcripts are collected only for a run that reached the check. A run
    # that exited before starting has no transcript of its own, and the session
    # id it was refused may already name another round's, whose transcript
    # would then be copied in and read as this round's data.
    transcripts = collect_transcripts(session_id, index) if outcome != "failed" else []

    return {"run": index,
            "session_id": session_id,
            "workspace": workspace,
            "outcome": outcome,
            "returncode": returncode,
            "stderr": (stderr or "")[-2000:],
            "elapsed_sec": round(elapsed, 1),
            "cost_usd": result.get("total_cost_usd"),
            "report": text,
            "transcripts": transcripts}


def record(row, state):
    row["repo"] = state
    with _write_lock:
        with open(config.RECORD_FILE, "a") as f:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
        print("run %02d %s in %ss, $%s" % (row["run"], row["outcome"],
                                           row["elapsed_sec"], row["cost_usd"]),
              flush=True)


def main():
    os.makedirs(config.RUNS_DIR, exist_ok=True)
    hide_output_dir()
    state = repo_state()
    if state["dirty"]:
        sys.exit("working tree is dirty; commit or stash before a round:\n"
                 + state["dirty"])
    done = completed_runs()
    pending = [index for index in range(1, config.RUNS + 1) if index not in done]
    print("round %s, PR #%d, branch %s, %d run(s) pending, %d worker(s)"
          % (config.DATA_DIR, config.PR, state["branch"], len(pending),
             config.WORKERS), flush=True)
    with ThreadPoolExecutor(max_workers=config.WORKERS) as pool:
        futures = [pool.submit(one_run, index, state["branch"]) for index in pending]
        for future in as_completed(futures):
            record(future.result(), state)


if __name__ == "__main__":
    main()
