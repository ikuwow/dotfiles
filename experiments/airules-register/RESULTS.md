# Results — 2026-07-25

Run of the procedure in `README.md` against `AIRULES.md` as of b06a83a, the
post-#335 file of 59 lines. Model `claude-sonnet-5`. 15 conversations, 10 turns
each, 150 replies, no errors. Reproduce with `python3 analyze.py`; the raw
output is in `results-output.txt`.

## The judge, before anything that rests on it

| check | result |
| --- | --- |
| repeat agreement on register across 3 passes | 151/156 texts unanimous |
| agreement with `claude-haiku-4-5` | 142/156 |
| hand-written controls classified correctly | 6/6 |

The controls include a Kansai reply written flat, with no exclamation and no
first person, and a mostly-standard reply carrying a single Kansai marker. Both
were classified correctly, so the judge is not keying on surface markers alone.
Agreement clears the threshold in `config.AGREEMENT_THRESHOLD`.

## The register holds everywhere

| cell | kansai | tameguchi | registers observed |
| --- | --- | --- | --- |
| no block (control) | 0/30 | 17/30 | だ・である 17, ですます 13 |
| current `AIRULES.md` | 30/30 | 30/30 | 関西弁 30 |
| register section only | 30/30 | 30/30 | 関西弁 30 |
| register section + 3 examples | 30/30 | 30/30 | 関西弁 30 |
| register section − ですます ban | 30/30 | 30/30 | 関西弁 30 |

By the style of the user's own turn, and by turn index, every cell carrying an
instruction is 12/12, 9/9, 9/9 and 3/3 at every one of the ten turns. The
control is 0 everywhere. Neither a user turn written in ですます nor ten turns of
accumulated history moves any of them.

The failure reported from claude.ai — replies arriving in ですます or だ・である —
therefore still does not reproduce here, under the closest condition this
harness can construct.

## An earlier version of this run said the opposite

A previous run of this harness found the register breaking at turn 3, the first
user turn written in ですます, in three of fifteen conversations. That result was
an artifact and has been discarded.

That runner continued each conversation with `claude -p --resume`, and a resumed
session does not carry the `--system-prompt-file` given on the first invocation.
Verified directly: a system prompt demanding a fixed token in every reply is
obeyed on turn 1 and ignored on the resumed turn 2, twice out of two. So that run
measured a register instruction present only on the opening turn, and what it
found was that an instruction which is no longer present loses to the user's own
register on the third turn — a true statement about a condition nobody is in.

The current runner drives all ten turns through one process over stream-json.
`smoke_test.py` re-checks the property on demand.

Two smaller faults in that runner are also fixed: `main()` raised a `TypeError`
after every conversation had already been generated, and the documented
resume-by-skip was never called, so a restart duplicated instead of resuming.
The restart path has since been exercised — a run that lost one cell to a stale
error row skipped the 12 recorded conversations and regenerated only the 3
missing ones.

## Energy

The one axis where the cells differ.

| cell | judge call | exclamation and interjection markers per reply |
| --- | --- | --- |
| no block (control) | 3/30 | 0.3 |
| current `AIRULES.md` | 6/30 | 0.5 |
| register section only | 28/30 | 1.6 |
| register section + 3 examples | 30/30 | 1.4 |
| register section − ですます ban | 30/30 | 2.3 |

The same eight bullets score 28-30 of 30 on their own and 6 of 30 inside the
59-line file, on both the judge's call and the independent marker count. The
register survives that burial and the tone does not.

The instruction this axis stands for (`テンション高めで明るく`) is
under-specified, and the judge is applying its own reading of it. The figures
are recorded rather than acted on. What survives that caveat is the gap between
6/30 and 28/30, which is larger than the axis's vagueness can account for and
appears in the marker count as well.

## First person

Zero violations across 150 replies. Occurrences of the specified set: 83, all
`うち`; `ウチ`, `あたし` and `あーし` do not appear. The count is a raw substring
match, so it includes non-pronoun uses such as `もうちょい` and `知らんうちに`.

Five matches outside the set were read. All five are quoted hypothetical speech
attributed to a code reviewer (`「私ならこう書く」`, `「俺やったらこう書くけど」`,
`「僕やったらこう書くけど」`), all on turn 7, which asks how it feels to receive
nitpicking review comments. None is the assistant referring to itself.

## Limits

Sonnet 5, given the Opus 5 section of the published prompt, which is what
claude.ai serves — the model and the system prompt come from different tiers.
The wrapper claude.ai uses to deliver "Instructions for Claude" is not
published, so the placement is a reconstruction. Three conversations per cell.
Generation cost $18.84 at list price, most of it the 21K-token system prompt
resent on every turn.
