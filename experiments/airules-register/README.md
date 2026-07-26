# AIRULES.md register adherence

Measures whether the conversational register and tone defined in `AIRULES.md`
survive a multi-turn chat, under conditions approximating claude.ai. Tracked in
ikuwow/dotfiles#334.

Round 1 asked whether the register survives; it does, in every cell carrying an
instruction. What did not survive was the brightness of the delivery. Round 2
(ikuwow/dotfiles#337) varies only the brightness wording and asks which one
reaches the reply.

## What this can and cannot establish

The claude.ai request is approximated, not reproduced. The published system
prompt is public, but the wrapper that carries "Instructions for Claude" into
the request is not, so the placement used here is a plausible reconstruction.
Runs are on `claude-sonnet-5`; claude.ai serves Opus 5.

Consequently a result here transfers as a relative comparison between cells, not
as a statement about what claude.ai will do.

## Design

Fixed across every cell:

- Runner `claude -p --safe-mode --tools ""`, so no `CLAUDE.md`, skills, hooks or
  MCP servers reach the request and the tool definitions are absent
- System prompt replaced wholesale with the published claude.ai prompt
- The cell's block placed in a `<user_preferences>` section appended to the
  system prompt. The tag name comes from prose in the published prompt naming
  the product setting; no such tag appears in the prompt itself
- All ten turns driven through one process over stream-json, each sent after the
  previous turn's result event

The last point is load-bearing. `--resume` starts a new process and does not
carry the `--system-prompt-file` from the first invocation, so a conversation
built that way carries the register instruction on turn 1 only. Sending every
turn up front does not work either: messages that arrive while the model is
generating are merged into the turn in progress. `smoke_test.py` checks both
properties with a system prompt demanding a fixed token in every reply.

Varied: the brightness wording, six cells including a control that supplies no
block at all. The control is what makes the rest interpretable — if it does not
come back in standard Japanese, the probe cannot detect the failure being
investigated.

Every cell that carries an instruction carries the whole of `AIRULES.md` with
the wording edited into its tone section, which is the condition the file is
actually deployed under. Round 1 measured the tone bullets as a standalone
block as well, and the energy axis saturated at 28-30 of 30 there while the
same bullets scored 6 of 30 inside the file, so a standalone cell separates
nothing.

| cell | wording |
| --- | --- |
| `0-control` | no block at all |
| `1-airules-current` | the file unchanged |
| `2-adjective` | the `テンション高めで明るく、サバサバしている` bullet removed in e53a3d8 |
| `3-delivery` | brightness stated as delivery — 語勢, テンポ, 感嘆詞, 感嘆符 |
| `4-examples` | the single example replaced by three bright ones |
| `5-delivery-examples` | both candidates together |

The candidates ask for nothing to be added to the content of a reply. A wording
that produced brightness by inventing shared feeling or experience would be
buying it with fabrication, which the rest of the file forbids, so the judge
scores that separately as `empathy_padding`.

Ten turns per conversation, three repetitions per cell. Each turn is tagged with
how the user's own message is written:

| tag | what it is | why it is there |
| --- | --- | --- |
| `plain` | standard Japanese, plain form | register cue absent from the user's turn |
| `desumasu` | standard Japanese, polite form | mirroring pressure toward ですます |
| `casual` | opinion or small talk | leaves room for tone |

Earlier rounds used `plain` turns exclusively, which removed mirroring as an
explanation but also removed it as a measurable effect.

## Scoring

Every reply is judged three times by the primary judge and once by a second
model, so disagreement appears in the output instead of being averaged away
inside a single call. Hand-written texts with known labels are judged in the
same pass, so discrimination is measured on this run rather than assumed.

Repeat agreement below `config.AGREEMENT_THRESHOLD` on register, or
`config.ENERGY_AGREEMENT_THRESHOLD` on energy, is reported as a failure of the
measurement, and the figures under it are not to be interpreted.

| axis | how it is read |
| --- | --- |
| register | primary result; majority of the repeat judgements |
| tameguchi | primary result |
| energy | primary result for round 2. A 0-3 ordinal on the delivery, collapsed to a boolean at `config.ENERGY_HIGH_THRESHOLD`, reported next to its own mean and an independent count of surface markers |
| empathy padding | whether the reply added empathy, anecdote or praise to the content. Not a target; watched so that a wording is not credited for brightness it bought with fabrication |
| first person | raw substring occurrences, printed for reading. A match outside the specified set is a violation only once someone has read it in context; quoted speech attributed to another person is not one. Japanese drops subjects freely, so presence per turn would measure opportunity rather than compliance |

Round 1 reported energy as descriptive only, because the instruction it stood
for (`テンション高めで明るく`) was under-specified and the judge was applying
its own reading of it. Round 2 decides on that axis, so the axis is defined in
`config.JUDGE_RUBRIC` instead: brightness is a property of the delivery, and
the exclamation marks in a text are explicitly not the grounds for the score.

Four of the controls exist for that definition, and two of them exist to break
a judge that fails it — a report voice with an exclamation mark on every
sentence, and a reply full of empathy written flat. Both must come back low.
The controls are also the reason the marker regex in `config` was left
unchanged: a marker set edited to match a candidate's wording would score that
candidate on its own terms.

Because the energy figures are comparable only within a rubric, `2-adjective`
carries the exact wording round 1 measured at 6 of 30 and is the only cell that
connects the two rounds.

## Running it

```sh
python3 fetch_system_prompt.py         # rewrites claude-ai-system-prompt.txt
python3 judge.py --controls-only       # judges the hand-written texts only
python3 analyze.py --controls-only     # the gate: does the judge discriminate?
python3 smoke_test.py                  # two turns; checks the system prompt persists
python3 run.py                         # appends to replies.jsonl
python3 judge.py                       # writes judgements.jsonl
python3 analyze.py                     # prints the reported figures
```

Run the gate first. Generation costs tens of dollars and the controls cost
cents, so a rubric that cannot separate a bright reply from a loud one is worth
finding before the replies exist rather than after. Revising the rubric once
the replies are in hand is a different act, and the results are not
interpretable if it happens.

`run.py` appends per conversation and skips conversations already complete in
`replies.jsonl`, so an interrupted run is restarted with the same command, and
raising `config.REPETITIONS` adds repetitions without regenerating the recorded
ones. A conversation that failed is retried, and `judge.py` keys on
`(cell, rep, turn)` keeping the last, so the successful attempt is the one
analysed. To start over, delete the round's `replies.jsonl` first.

`fetch_system_prompt.py` overwrites the committed prompt with whatever the docs
page currently serves. The committed copy is the one the recorded results used;
re-fetching changes the input, so do it deliberately rather than as a habit.

`config.py` holds the model, probe set, wordings and repetition count. Changing
the design should be a diff against that file.

Authentication comes from whatever the local `claude` CLI is logged in with.
`--safe-mode` does not force API-key auth, so runs go through the same
credentials as an interactive session.

## Files

| file | contents |
| --- | --- |
| `config.py` | every fixed input: model, probes, wordings, repetitions, judge rubric, thresholds |
| `fetch_system_prompt.py` | fetches and unescapes the published claude.ai prompt |
| `run.py` | generates replies |
| `smoke_test.py` | two turns, checking the system prompt reaches both |
| `judge.py` | scores replies and controls, repeatedly and cross-model |
| `analyze.py` | aggregates into the reported figures |
| `controls.jsonl` | hand-written texts with known labels |
| `claude-ai-system-prompt.txt` | the prompt the recorded runs used |
| `round1/`, `round2/` | recorded output, one directory per round; `config.DATA_DIR` selects which one is written |
| `RESULTS.md` | what the recorded runs found |
