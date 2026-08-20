"""Group the findings from every run into the distinct defects they name.

Agreement across runs is only countable once "the same finding" is decided,
and two runs never phrase one the same way. A judge does that grouping.

The judge is itself a model, so it carries the variance the round is measuring.
Three independent passes run over the same input, and two findings are treated
as one defect when at least two of the three passes group them together. The
transitive closure of that majority relation is the reported grouping, and the
per-pass disagreement is reported alongside it so a grouping that only held in
one pass cannot pass as settled.

The judge sees findings stripped of their run index, so it cannot group by
which run said what.
"""

import json
import subprocess

import config

PASSES = 3

PROMPT = """You are grouping findings produced by repeated runs of one PR review checklist over one unchanged pull request.

Each finding below has an id. Two findings belong to the same group when they name the same defect in the pull request, however differently they are worded. Two findings that name different defects belong to different groups, even when they share a property tag or a severity. A finding that names no defect in the pull request belongs to its own group.

Return JSON and nothing else, in this shape:

{"groups": [{"label": "<one clause naming the defect>", "ids": [<id>, ...], "unaccounted_hunk": <true|false>}]}

Every id below appears in exactly one group. Set "unaccounted_hunk" to true only when the group's defect is that some part of the diff is not named, accounted for, or explained by the PR body.

Findings:

%s
"""


def claude_json(prompt):
    proc = subprocess.run(
        ["claude", "-p", "--safe-mode", "--tools", "", "--model", config.JUDGE_MODEL,
         prompt],
        capture_output=True, text=True, check=True)
    text = proc.stdout.strip()
    start, end = text.find("{"), text.rfind("}")
    if start < 0 or end < 0:
        raise ValueError("judge returned no JSON object:\n" + text[:2000])
    return json.loads(text[start:end + 1])


def load_findings():
    items = []
    with open(config.FINDINGS_FILE) as f:
        for line in f:
            row = json.loads(line)
            for finding in row["findings"]:
                items.append({"id": len(items),
                              "run": row["run"],
                              "severity": finding["severity"],
                              "property": finding["property"],
                              "text": finding["text"]})
    return items


def render(items):
    return "\n".join(
        "%d. [%s / %s] %s" % (item["id"], item["severity"], item["property"], item["text"])
        for item in items)


def merge(items, passes):
    """Union findings that at least two passes put in the same group."""
    together = {}
    for result in passes:
        for group in result["groups"]:
            ids = sorted(group["ids"])
            for a in range(len(ids)):
                for b in range(a + 1, len(ids)):
                    together[(ids[a], ids[b])] = together.get((ids[a], ids[b]), 0) + 1

    parent = {item["id"]: item["id"] for item in items}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for (a, b), count in together.items():
        if count * 2 > len(passes) and find(a) != find(b):
            parent[find(a)] = find(b)

    groups = {}
    for item in items:
        groups.setdefault(find(item["id"]), []).append(item["id"])

    labels, flags = {}, {}
    for result in passes:
        for group in result["groups"]:
            for member in group["ids"]:
                labels.setdefault(member, []).append(group.get("label", ""))
                flags.setdefault(member, []).append(bool(group.get("unaccounted_hunk")))

    out = []
    for ids in groups.values():
        votes = [flag for member in ids for flag in flags.get(member, [])]
        splits = sum(1 for (a, b), count in together.items()
                     if a in ids and b in ids and count < len(passes))
        out.append({"label": labels.get(ids[0], [""])[0],
                    "ids": sorted(ids),
                    "runs": sorted({item["run"] for item in items if item["id"] in ids}),
                    "unaccounted_hunk": sum(votes) * 2 > len(votes),
                    "pairs_not_unanimous": splits})
    return sorted(out, key=lambda group: (-len(group["runs"]), group["label"]))


def main():
    items = load_findings()
    if not items:
        raise SystemExit("no findings to group; every run reported none")
    prompt = PROMPT % render(items)
    passes = [claude_json(prompt) for _ in range(PASSES)]
    groups = merge(items, passes)
    with open(config.CLUSTERS_FILE, "w") as f:
        json.dump({"items": items, "passes": passes, "groups": groups}, f,
                  ensure_ascii=False, indent=2)
    print("%d findings from %d runs grouped into %d defects"
          % (len(items), len({item["run"] for item in items}), len(groups)))


if __name__ == "__main__":
    main()
