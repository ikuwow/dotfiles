# AIRULES.md register adherence

Measures whether the conversational register defined in `AIRULES.md` survives a
multi-turn chat, under conditions approximating claude.ai. Tracked in
ikuwow/dotfiles#334.

The question behind it: the register holds in Claude Code and does not hold on
claude.ai, where the same file is pasted into "Instructions for Claude".

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
- Register block placed in a `<user_preferences>` section appended to the system
  prompt, the name the published prompt itself uses for that slot
- Conversations continued with `--resume`, so the model sees a real history

Varied: the wording of the register block, five cells including a control that
supplies no block at all. The control is what makes the rest interpretable — if
it does not come back in standard Japanese, the probe cannot detect the failure
being investigated.

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
inside a single call. Hand-written texts with known labels — including a
Kansai reply with no exclamation or first person, and a mostly-standard reply
carrying one Kansai marker — are judged in the same pass, so discrimination is
measured on this run rather than assumed.

| axis | how it is read |
| --- | --- |
| register | primary result; majority of the repeat judgements |
| tameguchi | primary result |
| first person | violations, counted as occurrences outside the specified set. Japanese drops subjects freely, so presence per turn measures opportunity rather than compliance |
| energy | descriptive only. Reported as the judge's call next to a count of surface markers, and not used to decide anything |

The energy axis stands for an instruction that is itself under-specified
(`テンション高めで明るく`). It is recorded because it is in the rules, not
because the number means much.

## Running it

```sh
python3 fetch_system_prompt.py   # rewrites claude-ai-system-prompt.txt
python3 run.py                   # writes replies.jsonl
python3 judge.py                 # writes judgements.jsonl
python3 analyze.py               # prints the reported figures
```

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
| `config.py` | every fixed input: model, probes, wordings, repetitions |
| `fetch_system_prompt.py` | fetches and unescapes the published claude.ai prompt |
| `run.py` | generates replies |
| `judge.py` | scores replies and controls, repeatedly and cross-model |
| `analyze.py` | aggregates into the reported figures |
| `controls.jsonl` | hand-written texts with known labels |
| `claude-ai-system-prompt.txt` | the prompt the recorded run used |
| `replies.jsonl`, `judgements.jsonl` | recorded run output |
| `RESULTS.md` | what the recorded run found |
