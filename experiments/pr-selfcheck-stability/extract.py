"""Turn each recorded run into a findings list and an evidence-route row.

Two things come out of a run and they answer different questions.

The report answers what the run concluded. It is parsed structurally against
the output format the skill prescribes, so a run that departed from that format
is visible as a parse failure rather than being silently read as "no findings".

The subagent transcript answers what the run looked at. Every signal below is
decided on the content a tool call returned, not on the command that was
issued: `ls ikuwowfiles/ | grep pr-guidelines` names the record without
returning a line of it, and counting that as having consulted the record would
erase the distinction the round exists to measure.
"""

import json
import os
import re

import config

# A phrase unique to each source, used to decide from a tool result whether the
# run actually had that source's content in hand.
MARKERS = {
    "read_body": "Where a reformat can change a rule",
    "read_diff": "diff --git a/claude/skills/git-workflow/pr-guidelines.md",
    "read_guidelines": "A body is ready when it holds all five properties",
    "read_record": "new in commit 1",
}

HEADING = re.compile(r"^###\s+(Fix|Note|Unverifiable|Property walk|Verdict)\s*$", re.M)
ITEM = re.compile(r"^-\s*\[([^\]]+)\]\s*(.+)$")


def sections(report):
    """Split a report on its `###` headings, keeping only the prescribed ones."""
    out, marks = {}, list(HEADING.finditer(report))
    for n, mark in enumerate(marks):
        end = marks[n + 1].start() if n + 1 < len(marks) else len(report)
        out[mark.group(1)] = report[mark.end():end].strip()
    return out


def parse_report(report):
    found = sections(report)
    missing = [name for name in ("Fix", "Note", "Unverifiable", "Property walk", "Verdict")
               if name not in found]
    findings = []
    for severity in config.SEVERITIES:
        body = found.get(severity, "")
        if body.strip().lower().startswith("none"):
            continue
        for line in body.splitlines():
            match = ITEM.match(line.strip())
            if match:
                findings.append({"severity": severity,
                                 "property": match.group(1).strip(),
                                 "text": match.group(2).strip()})
            elif line.strip().startswith("- "):
                # An item that carries no property tag still states a finding;
                # dropping it would understate the run.
                findings.append({"severity": severity, "property": None,
                                 "text": line.strip()[2:].strip()})
    walk = {}
    for line in found.get("Property walk", "").splitlines():
        match = re.match(r"^-\s*([A-Za-z]+)\s*:\s*(.+)$", line.strip())
        if match:
            walk[match.group(1)] = match.group(2).strip()
    verdict = found.get("Verdict", "").strip().splitlines()
    return {"findings": findings,
            "walk": walk,
            "verdict": verdict[0].strip() if verdict else None,
            "malformed": missing or sorted(walk) != sorted(config.PROPERTIES)}


def transcript_signals(paths):
    """Read the subagent transcripts for what the run had in hand."""
    calls, results, errors = [], [], 0
    for path in paths:
        with open(path) as f:
            for line in f:
                if not line.strip():
                    continue
                content = (json.loads(line).get("message") or {}).get("content")
                if not isinstance(content, list):
                    continue
                for block in content:
                    if block.get("type") == "tool_use":
                        argument = (block["input"].get("command")
                                    or block["input"].get("file_path")
                                    or block["input"].get("pattern")
                                    or block["input"].get("url") or "")
                        calls.append({"tool": block["name"], "arg": str(argument)})
                    elif block.get("type") == "tool_result":
                        payload = block.get("content")
                        if isinstance(payload, list):
                            payload = " ".join(part.get("text", "") for part in payload)
                        results.append(str(payload or ""))
                        if block.get("is_error"):
                            errors += 1
    joined = "\n".join(results)
    signals = {name: (marker in joined) for name, marker in MARKERS.items()}
    signals["named_record"] = any(
        os.path.basename(config.EVIDENCE_RECORD).split(".")[0] in call["arg"]
        for call in calls)
    signals["fetched_head"] = any("git fetch origin pull/" in call["arg"] for call in calls)
    signals["tool_calls"] = len(calls)
    signals["tool_errors"] = errors
    return signals, calls


def main():
    with open(config.RECORD_FILE) as f:
        records = [json.loads(line) for line in f if line.strip()]
    rows = []
    for record in records:
        parsed = parse_report(record["report"])
        agents = [os.path.join(config.RUNS_DIR, name)
                  for name in record["transcripts"] if ".agent" in name]
        signals, calls = transcript_signals(agents)
        rows.append({"run": record["run"],
                     "outcome": record["outcome"],
                     "elapsed_sec": record["elapsed_sec"],
                     "cost_usd": record["cost_usd"],
                     "verdict": parsed["verdict"],
                     "malformed": parsed["malformed"],
                     "findings": parsed["findings"],
                     "walk": parsed["walk"],
                     "signals": signals,
                     "calls": calls})
    with open(config.FINDINGS_FILE, "w") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    print("wrote %d rows to %s" % (len(rows), config.FINDINGS_FILE))


if __name__ == "__main__":
    main()
