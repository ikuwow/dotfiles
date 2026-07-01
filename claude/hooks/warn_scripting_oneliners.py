#!/usr/bin/env python3
"""Warn on Bash one-liners that invoke arbitrary-code scripting tools.

Detects ``awk``, ``sed``, ``perl -e`` / ``-E``, ``python -c``,
``python3 -c``, and ``ruby -e`` in Bash commands. On the first occurrence per session
per rule, denies the tool call with a suggestion to prefer purpose-
built commands (tr, cut, head, tail, sort, uniq, grep, jq, ...). On
subsequent occurrences of the same rule in the same session, the
command is allowed through so the assistant can proceed after
confirming the special tool is actually needed.

Session state is tracked in ``~/.claude/state/scripting_warned_<session_id>.json``.
Set ``ENABLE_SCRIPTING_WARNING=0`` to disable.

Spec: https://docs.anthropic.com/en/docs/claude-code/hooks
"""
import json
import os
import random
import re
import sys
from datetime import datetime

# Split on &&, ||, ;, newline, or single | (pipe) outside quotes.
# `\|\|` is tried before `\|` so `||` is not consumed as two `|`.
_SEPARATOR_RE = re.compile(r"&&|\|\||;|\n|\|")

_STATE_DIR = os.path.expanduser("~/.claude/state")
_STATE_PREFIX = "scripting_warned_"

_ALTERNATIVES = (
    "  tr        : 文字置換・削除\n"
    "  cut       : カラム抽出\n"
    "  head/tail : 行数指定抽出\n"
    "  sort/uniq : ソート・重複処理\n"
    "  grep/rg   : パターンマッチ\n"
    "  jq        : JSON処理\n"
    "  yq        : YAML/TOML処理"
)

_RULE_LABELS = {
    "awk_oneliner": "awk",
    "sed_oneliner": "sed",
    "perl_oneliner": "perl -e",
    "python_oneliner": "python -c",
    "ruby_oneliner": "ruby -e",
}


def _split_outside_quotes(command: str) -> list[str]:
    """Split command by shell separators, ignoring separators inside quotes.

    >>> _split_outside_quotes("cat file | awk '{print $1}'")
    ['cat file ', " awk '{print $1}'"]
    >>> _split_outside_quotes("echo 'awk hi | sed'")
    ["echo 'awk hi | sed'"]
    >>> _split_outside_quotes("a && b || c ; d")
    ['a ', ' b ', ' c ', ' d']
    >>> _split_outside_quotes("a\\nawk x")
    ['a', 'awk x']
    >>> _split_outside_quotes('echo "pipe | inside double"')
    ['echo "pipe | inside double"']
    """
    segments = []
    current = []
    in_single = False
    in_double = False
    i = 0
    while i < len(command):
        ch = command[i]

        if ch == "\\" and in_double and i + 1 < len(command):
            current.append(ch)
            current.append(command[i + 1])
            i += 2
            continue

        if ch == "'" and not in_double:
            in_single = not in_single
            current.append(ch)
            i += 1
            continue
        if ch == '"' and not in_single:
            in_double = not in_double
            current.append(ch)
            i += 1
            continue

        if not in_single and not in_double:
            match = _SEPARATOR_RE.match(command, i)
            if match:
                segments.append("".join(current))
                current = []
                i = match.end()
                continue

        current.append(ch)
        i += 1

    segments.append("".join(current))
    return segments


def detect_rules(command: str) -> list[str]:
    """Return rule names for scripting tools invoked at segment head.

    Detects each pattern only when it appears at the start of a shell
    segment (after splitting on &&, ||, ;, newline, or |). Segment-head
    matching prevents false positives from the tool name appearing as
    an argument (e.g. ``echo hello awk``).

    Detected — segment-head:
    >>> detect_rules("awk '{print $1}' file")
    ['awk_oneliner']
    >>> detect_rules("sed -i 's/a/b/' file")
    ['sed_oneliner']

    Detected — after a pipe, ``&&``, ``||``, ``;``, or newline:
    >>> detect_rules("cat f | awk '{print $2}'")
    ['awk_oneliner']
    >>> detect_rules("ls | sed 's/x/y/'")
    ['sed_oneliner']
    >>> detect_rules("mkdir d && awk '{print}' f")
    ['awk_oneliner']
    >>> detect_rules("false || sed s/a/b/ f")
    ['sed_oneliner']
    >>> detect_rules("ls ; awk NR==1 f")
    ['awk_oneliner']
    >>> detect_rules("mkdir d\\nawk '{print}' f")
    ['awk_oneliner']

    Detected — perl/python/ruby require -e / -E / -c:
    >>> detect_rules("perl -e 'print 1'")
    ['perl_oneliner']
    >>> detect_rules("perl -E 'say 1'")
    ['perl_oneliner']
    >>> detect_rules("python -c 'print(1)'")
    ['python_oneliner']
    >>> detect_rules("python3 -c 'print(1)'")
    ['python_oneliner']
    >>> detect_rules("ruby -e 'p 1'")
    ['ruby_oneliner']

    Multiple rules in one command — reported in order:
    >>> detect_rules("awk '{print $1}' f | sed 's/a/b/'")
    ['awk_oneliner', 'sed_oneliner']

    NOT detected — inside single quotes:
    >>> detect_rules("echo 'awk not here'")
    []
    >>> detect_rules("git commit -m 'refactor sed logic'")
    []

    NOT detected — as an argument, not segment head:
    >>> detect_rules("echo hello awk")
    []
    >>> detect_rules("ls awk_output/")
    []

    NOT detected — perl/python/ruby without -e / -c:
    >>> detect_rules("perl script.pl")
    []
    >>> detect_rules("python script.py --awk sed")
    []
    >>> detect_rules("ruby app.rb")
    []

    NOT detected — substring / hyphenated names:
    >>> detect_rules("git awk-branch")
    []
    >>> detect_rules("awkward --help")
    []
    >>> detect_rules("sedimentary process")
    []
    """
    rules = []
    for seg in _split_outside_quotes(command):
        seg = seg.strip()
        if not seg:
            continue

        if re.match(r"awk(\s|$)", seg):
            rules.append("awk_oneliner")
            continue
        if re.match(r"sed(\s|$)", seg):
            rules.append("sed_oneliner")
            continue
        if re.match(r"perl(\s|$)", seg) and re.search(r"(^|\s)-[eE](\s|$)", seg):
            rules.append("perl_oneliner")
            continue
        if re.match(r"python3?(\s|$)", seg) and re.search(r"(^|\s)-c(\s|$)", seg):
            rules.append("python_oneliner")
            continue
        if re.match(r"ruby(\s|$)", seg) and re.search(r"(^|\s)-e(\s|$)", seg):
            rules.append("ruby_oneliner")
            continue
    return rules


def _state_path(session_id: str) -> str:
    return os.path.join(_STATE_DIR, f"{_STATE_PREFIX}{session_id}.json")


def _load_state(session_id: str) -> set:
    try:
        with open(_state_path(session_id)) as f:
            return set(json.load(f))
    except (OSError, ValueError):
        return set()


def _save_state(session_id: str, shown: set) -> None:
    try:
        os.makedirs(_STATE_DIR, exist_ok=True)
        with open(_state_path(session_id), "w") as f:
            json.dump(sorted(shown), f)
    except OSError:
        pass


def _cleanup_old_state() -> None:
    try:
        if not os.path.isdir(_STATE_DIR):
            return
        cutoff = datetime.now().timestamp() - 30 * 24 * 60 * 60
        for name in os.listdir(_STATE_DIR):
            if not name.startswith(_STATE_PREFIX) or not name.endswith(".json"):
                continue
            path = os.path.join(_STATE_DIR, name)
            try:
                if os.path.getmtime(path) < cutoff:
                    os.remove(path)
            except OSError:
                pass
    except OSError:
        pass


def _build_message(rule_name: str) -> str:
    label = _RULE_LABELS.get(rule_name, rule_name)
    return (
        f"'{label}' を検出した。用途特化のコマンドで代替できないか検討してほしい：\n"
        f"{_ALTERNATIVES}\n\n"
        "これらで表現困難な場合（複雑な条件分岐、フィールド演算、"
        "複数行にまたがる状態管理等）は、同じコマンドをそのまま再実行して。"
        "このセッション内では2回目以降は通る。"
    )


def main() -> None:
    if os.environ.get("ENABLE_SCRIPTING_WARNING", "1") == "0":
        sys.exit(0)

    if random.random() < 0.1:
        _cleanup_old_state()

    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)

    if data.get("tool_name", "") != "Bash":
        sys.exit(0)

    command = data.get("tool_input", {}).get("command", "")
    if not command:
        sys.exit(0)

    detected = detect_rules(command)
    if not detected:
        sys.exit(0)

    session_id = data.get("session_id", "default")
    shown = _load_state(session_id)

    for rule in detected:
        if rule in shown:
            continue
        shown.add(rule)
        _save_state(session_id, shown)
        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": _build_message(rule),
            },
        }))
        sys.exit(0)

    sys.exit(0)


if __name__ == "__main__":
    main()
