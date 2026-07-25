# Results — 2026-07-25

Run of the procedure in `README.md` against `AIRULES.md` as of b06a83a, the
post-#335 file of 59 lines. Model `claude-sonnet-5`. 15 conversations, 10 turns
each, 150 replies, no errors. Reproduce with `python3 analyze.py`; the raw
output is in `results-output.txt`.

## The judge, before anything that rests on it

| check | result |
| --- | --- |
| repeat agreement on register across 3 passes | 150/156 texts unanimous |
| agreement with `claude-haiku-4-5` | 142/156 |
| hand-written controls classified correctly | 6/6 |

The controls include a Kansai reply written flat, with no exclamation and no
first person, and a mostly-standard reply carrying a single Kansai marker. Both
were classified correctly, so the judge is not keying on surface markers alone.
Agreement clears the 90% threshold fixed before the run.

## The failure reproduced

| cell | kansai | registers observed |
| --- | --- | --- |
| no block (control) | 0/30 | だ・である 17, ですます 13 |
| current `AIRULES.md` | 23/30 | 関西弁 23, ですます 5, だ・である 2 |
| register section only | 30/30 | 関西弁 30 |
| register section + 3 examples | 23/30 | 関西弁 23, ですます 4, だ・である 3 |
| register section − ですます ban | 27/30 | 関西弁 27, ですます 2, だ・である 1 |

Earlier rounds of this investigation reported that the failure never reproduced
outside claude.ai. That was an artifact of the probe design: every user turn was
written in plain form, which was chosen so that mirroring could not explain a
Kansai reply, and which also made mirroring unobservable. Adding turns written
in ですます reproduced it.

## The trigger

Failures do not scatter across turns. Within a cell they fall entirely inside
one conversation, and every failing conversation breaks at the same place.

| conversation | t1 plain | t2 plain | t3 ですます | t4 casual | t5 plain | t6 ですます | t7 casual | t8 plain | t9 ですます | t10 casual |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `AIRULES.md` rep3 | 関西 | 関西 | ですます | ですます | ですます | だである | ですます | だである | ですます | 関西 |
| 3 examples rep1 | 関西 | 関西 | ですます | ですます | だである | だである | ですます | だである | ですます | 関西 |
| − ですます ban rep2 | 関西 | 関西 | だである | 関西 | 関西 | ですます | 関西 | ですます | 関西 | 関西 |

Turn 3 is the first user turn written in ですます. All three conversations hold
the register through turns 1 and 2 and break at turn 3. None breaks before it.

Once broken, the register does not come back on its own: turns 5 and 8 are
written in plain form and stay in ですます or だ・である. The model follows its
own previous replies. Turn 10 recovers in two of the three, and is the one user
turn written in markedly casual Japanese.

By the style of the user's own turn:

| cell | plain | ですます | casual |
| --- | --- | --- | --- |
| current `AIRULES.md` | 10/12 | 6/9 | 7/9 |
| register section only | 12/12 | 9/9 | 9/9 |
| register section + 3 examples | 10/12 | 6/9 | 7/9 |
| register section − ですます ban | 11/12 | 7/9 | 9/9 |

## What the wording comparison does not show

Failures cluster by conversation, so the effective sample is 3 conversations per
cell, not 30 turns. One cell failed 0 of 3 and three cells failed 1 of 3. That
difference is not evidence at this sample size, and no ranking between wordings
is established here.

Round 1 of the investigation found the three-example wording strongest on Opus 5;
here it is indistinguishable from the full file. Neither result has the sample
size to contradict the other.

The trigger finding does not depend on this. Three independent conversations
broke at the same turn, and none broke earlier.

## First person

Zero violations across 150 replies. Occurrences of the specified set: うち 50,
plus ウチ and あたし. Two matches outside it were read and are not the
assistant's own first person — one `僕` and one `俺` inside a quoted remark
attributed to a code reviewer.

An earlier metric counted `自分` as a violation. It fired in every cell including
the control, because in technical prose `自分` means "one's own" (`自分のブランチ`,
`自分専用`) rather than referring to the speaker. It is excluded from the list.

## Energy

Descriptive only; the instruction it stands for (`テンション高めで明るく`) is
under-specified, and the figures are recorded rather than acted on.

| cell | judge call | exclamation and interjection markers per reply |
| --- | --- | --- |
| no block (control) | 0/30 | 0.1 |
| current `AIRULES.md` | 4/30 | 0.3 |
| register section only | 25/30 | 1.8 |
| register section + 3 examples | 19/30 | 1.0 |
| register section − ですます ban | 21/30 | 0.9 |

The register section on its own scores far above the same section inside the
full file, on both the judge's call and the marker count, which agree here.

## Limits

Sonnet 5, not the Opus 5 claude.ai serves. The wrapper claude.ai uses to deliver
"Instructions for Claude" is not published, so the placement is a reconstruction.
Three conversations per cell. Generation cost $2.80 at list price.
