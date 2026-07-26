# Results

## Round 2 — 2026-07-26: which brightness wording reaches the reply

Seven cells, 21 conversations, 210 replies, no errors, $38.95 at list price.
Model `claude-sonnet-5`. Every cell carrying an instruction carries the whole of
`AIRULES.md`, as of 7830a08 and pinned as `round2/airules-input.md`, with the
wording edited into its tone section. Raw output in `round2/results-output.txt`.

### The judge, before anything that rests on it

| check | result |
| --- | --- |
| repeat agreement on register across 3 passes | 214/220 texts unanimous |
| repeat agreement on energy across 3 passes | 208/220 texts unanimous |
| agreement with `claude-haiku-4-5` on register | 202/220 |
| agreement with `claude-haiku-4-5` on energy | 190/220 |
| hand-written controls classified correctly | 10/10 register, 10/10 energy, 10/10 empathy |

Both repeat-agreement figures clear the thresholds in `config`. Energy is the
axis this round decides on, and cross-model agreement is looser there (86%)
than on register (92%), so differences of one or two replies between cells are
not differences.

The rubric was revised twice, both times against the control gate and both
times before a single reply existed. The first version scored the
exclamation-mark report at 3 of 3 despite the rubric already saying it should
cap at 1, so the cap was rewritten to key on spoken-versus-written vocabulary.
The second scored a 相槌 opener as empathy, overlapping the delivery axis it is
supposed to be independent of, so the two were separated explicitly. Nothing
was changed after the replies were generated.

### Neither candidate works alone

| cell | energy high | mean level | markers/reply |
| --- | --- | --- | --- |
| no block (control) | 2/30 | 1.00 | 0.2 |
| current `AIRULES.md` | 1/30 | 1.01 | 0.2 |
| + `テンション高めで明るく、サバサバしている` | 1/30 | 1.03 | 0.2 |
| + delivery bullets | 4/30 | 1.13 | 0.3 |
| + three bright examples | 2/30 | 1.07 | 0.3 |
| + both | 14/30 | 1.50 | 1.2 |
| + both + the guard | 12/30 | 1.44 | 0.9 |

Stating brightness as delivery scores 4 of 30 on its own. Replacing the single
example with three bright ones scores 2 of 30. The no-instruction control
scores 2 of 30. Put the two together and the figure is 14 of 30, on the judge's
call and on the marker count alike — 1.2 markers per reply against 0.2 to 0.3
in every cell that does not carry both.

The adjective wording that was removed in e53a3d8 scores 1 of 30, against the
control's 2 of 30: indistinguishable from supplying no instruction at all. It is
the closest cell to round 1's full-file cell and its 6 of 30, though not the
same one — round 1's file also carried the 感嘆・相槌 and persona bullets
e53a3d8 removed, and scored them on a coarser rubric.

So brightness is not a matter of finding the right sentence. A description of
the delivery and an example of it each fail on their own and work together,
which is the one result here that a differently-worded single bullet would not
have produced.

### Brightness lands on the conversational turns only

| cell | plain | desumasu | casual |
| --- | --- | --- | --- |
| no block (control) | 0/12 | 0/9 | 2/9 |
| current `AIRULES.md` | 0/12 | 0/9 | 1/9 |
| + the adjective bullet | 0/12 | 0/9 | 1/9 |
| + delivery bullets | 1/12 | 0/9 | 3/9 |
| + three bright examples | 0/12 | 0/9 | 2/9 |
| + both | 5/12 | 3/9 | 6/9 |
| + both + the guard | 2/12 | 3/9 | 7/9 |

The control row is the one to read the losing candidates against: 2 of 9 on the
casual turns is what supplying no instruction produces, so the examples cell
matches it exactly and the delivery cell is one reply above it.

Seven of the ten turns ask a technical question, and in every cell the answers
to them stay flat after the first sentence: a bright opener, then workmanlike
Kansai prose. Nothing moved that, and nothing was meant to — an explanation of
what squash merge costs has no cheerful version. The aggregate above is
therefore diluted by seven turns no wording is trying to move, and the casual
column is where the instruction is doing its work.

### The winning cell buys some of it with praise and invented experience

| cell | empathy padding, all | plain turns | casual turns |
| --- | --- | --- | --- |
| no block (control) | 7/30 | 0/12 | 7/9 |
| current `AIRULES.md` | 5/30 | 0/12 | 5/9 |
| + the adjective bullet | 6/30 | 0/12 | 6/9 |
| + delivery bullets | 7/30 | 1/12 | 6/9 |
| + three bright examples | 8/30 | 0/12 | 8/9 |
| + both | 14/30 | 5/12 | 9/9 |
| + both + the guard | 8/30 | 2/12 | 6/9 |

Empathy on the casual turns is not padding: two of those three turns ask the
assistant how it feels, so answering is the task. The plain column is where an
invented rapport shows, and the cell carrying both candidates goes from 0-1 of
12 to 5 of 12 there. Reading them: `ウチの経験則だと` on a question about
rebase, `お、ええとこ突いてきたな!`, `良い着眼点やで`. The first is a claim to
experience the assistant does not have; the other two are the praise
`過度な称賛・テンプレ的な感謝や謝罪は避ける` already forbids, in a file that
was carrying that bullet in every one of these cells.

Adding one line to the tone section — `明るさは話し方で出す。相手への称賛や自分
の体験談で出さない` — roughly halves it, 14 of 30 to 8 of 30 and 5 of 12 to 2 of
12, while brightness on the casual turns holds at 7 of 9 against 6 of 9. The
aggregate energy falls from 14 to 12, and all of that fall is on the technical
turns where brightness was not wanted.

At three conversations per cell, 14 against 12 is not a difference; re-judging
the identical texts moved several cells by one. What the run supports is that
the guard did not cost the brightness where it was wanted, and that it cut the
padding roughly in half.

### What shipped

The tone section of `AIRULES.md` gains the two delivery bullets, the guard, and
the three examples in place of the one, verbatim as the cell that was measured.

### Register and first person, unchanged

Every cell carrying an instruction is 30/30 on Kansai and on ため口, at every
turn index and under every user-turn style; the control is 0/30. Adding five
lines about tone moved neither.

First person: no violations. In the cells carrying an instruction there is one
match outside the specified set, `俺` in `3-delivery`, and it is quoted
hypothetical speech attributed to a code reviewer (`「俺ならこう書く」レベルの指
摘`) on the turn that asks about nitpicking review comments — the same
construction round 1 found. The control's two occurrences of `僕` are genuine
self-reference, which is what a cell carrying no first-person instruction is
expected to produce.

The three bright examples do not contain `ウチ`, where the example they replaced
did. The first-person bullet is unchanged and compliance did not move, so this
is recorded rather than acted on.

### Limits

Three conversations per cell, which is enough for the gap between 1 of 30 and
14 of 30 and not enough for the gap between 14 and 12. Sonnet 5 against the
Opus 5 section of the published prompt, and a reconstructed placement, as in
round 1 — so this ranks wordings against each other and does not predict what
claude.ai will do with any of them.

The bright examples were written against the probe set: two of the three answer
turns 1, 5 and 8. Demonstrating the delivery on the material at hand is what an
example is for, but it also means those three turns are closer to being handed
an answer in the three cells that carry them. Candidate B scoring 2 of 30 alone
bounds what that overlap can be worth.

## Round 1 — 2026-07-25: does the register survive

Run of the procedure in `README.md` against `AIRULES.md` as of b06a83a, the
post-#335 file of 59 lines. Model `claude-sonnet-5`. 15 conversations, 10 turns
each, 150 replies, no errors. Raw output in `round1/results-output.txt`; the
cell definitions are in `config.py` as of a28e795, which added the harness.

### The judge, before anything that rests on it

| check | result |
| --- | --- |
| repeat agreement on register across 3 passes | 151/156 texts unanimous |
| agreement with `claude-haiku-4-5` | 142/156 |
| hand-written controls classified correctly | 6/6 |

The controls include a Kansai reply written flat, with no exclamation and no
first person, and a mostly-standard reply carrying a single Kansai marker. Both
were classified correctly, so the judge is not keying on surface markers alone.
Agreement clears the threshold in `config.AGREEMENT_THRESHOLD`.

### The register holds everywhere

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

### An earlier version of this run said the opposite

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

### Energy

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

### First person

Zero violations across 150 replies. Occurrences of the specified set: 83, all
`うち`; `ウチ`, `あたし` and `あーし` do not appear. The count is a raw substring
match, so it includes non-pronoun uses such as `もうちょい` and `知らんうちに`.

Five matches outside the set were read. All five are quoted hypothetical speech
attributed to a code reviewer (`「私ならこう書く」`, `「俺やったらこう書くけど」`,
`「僕やったらこう書くけど」`), all on turn 7, which asks how it feels to receive
nitpicking review comments. None is the assistant referring to itself.

### Limits

Sonnet 5, given the Opus 5 section of the published prompt, which is what
claude.ai serves — the model and the system prompt come from different tiers.
The wrapper claude.ai uses to deliver "Instructions for Claude" is not
published, so the placement is a reconstruction. Three conversations per cell.
Generation cost $18.84 at list price, most of it the 21K-token system prompt
resent on every turn.
