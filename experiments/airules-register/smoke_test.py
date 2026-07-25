"""Check that the runner's turn loop works and the system prompt persists.

Sends two turns through run.claude() with a system prompt demanding a fixed
token in every reply. Both replies must carry it: the first shows the system
prompt applied, the second shows it still applied on a later turn, which is the
property the whole experiment rests on and which --resume does not have.
"""

import config
import run

TOKEN = "ZZQQ7"
SYSTEM = f"Always end every single reply with the exact token {TOKEN} on its own line."
SYSTEM_PATH = "system-smoke-test.txt"


def main():
    with open(SYSTEM_PATH, "w", encoding="utf-8") as f:
        f.write(SYSTEM)

    original = config.PROBE_TURNS
    config.PROBE_TURNS = [("plain", "What is 2+2?"), ("plain", "And 3+3?")]
    try:
        replies, cost = run.claude(SYSTEM_PATH)
    finally:
        config.PROBE_TURNS = original

    for index, reply in enumerate(replies, start=1):
        mark = "ok" if TOKEN in reply else "MISSING TOKEN"
        print(f"turn {index}: {reply!r} — {mark}")

    if len(replies) != 2 or not all(TOKEN in r for r in replies):
        raise SystemExit("system prompt did not persist across turns")
    print(f"both turns carry the token; ${cost:.4f} at list price")


if __name__ == "__main__":
    main()
