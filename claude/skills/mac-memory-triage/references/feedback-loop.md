# Memory Snapshot Feedback Loop (design notes)

## Problem

One-shot triage misses sluggish episodes; time-series capture is needed to correlate heavy moments with culprits. During this session's sampling, swap I/O deltas were near zero — evidence the machine thrashes episodically rather than continuously, so a single snapshot at investigation time can miss the actual heavy window.

## Option A — snapshot logger

A small script in `bin/` (e.g. `memsnapshot`) appending one JSONL line per run: timestamp, pressure level, free percentage, swap used, compressor pages, top-10 processes by MEM+CMPRS. Run via a launchd agent every N minutes. Keep the script under 100 lines per this repo's shell-script rules.

## Option B — event-driven capture

launchd may support memory-pressure event triggers. This is unverified; verify against `launchd.plist(5)` before building anything on this assumption.

## Option C — analysis loop

Feed the accumulated JSONL to a Claude session running the mac-memory-triage skill to diff against the baseline and name culprits. Optionally a `/loop` or scheduled routine that reads the latest snapshot and alerts on warn or critical pressure levels.

## Recommended first increment

Option A with manual analysis and no alerting.

## Constraints

- All snapshot commands are read-only
- Write logs outside the repo (e.g. under `~/ikuwowfiles/`, globally gitignored)
