# PR Reaction

How to react to PR events emitted by `bin/pr-monitor`. Event line spec
lives in the git-workflow skill's `SKILL.md` Phase 5.

## Targeting policy

Reply / resolve threads and reply to top-level comments / reviews only
when the author is a bot. Never touch anything with a human author
autonomously — summarize to the user and wait for an explicit
instruction.

- Bot thread = every comment in it has REST `user.type == "Bot"`. Any
  single `User`-type comment flips the thread to the human path — a
  bot can open a thread that a human later joins.
- Bot `NEW_TOP_COMMENT` / `NEW_REVIEW` = event line tag is `[BOT]`
  (derived from GraphQL `author.__typename` in `bin/pr-monitor`; on
  conflict with any other signal, the tag wins).
- Author type is always taken from a live API response
  (`user.type` / `__typename`), never assumed from a login name. The
  same GitHub App can show a different login string per API — e.g.
  GraphQL `author.login` omits the `[bot]` suffix that REST
  `user.login` includes — so match on type, not on login text.

## Step 1: List and classify threads (read-only)

Run both, join on `comment_node_id` (extension) == `node_id` (REST):

```bash
gh pr-review review view -R <owner>/<repo> <number> \
  --unresolved --not_outdated --include-comment-node-id
```

```bash
gh api /repos/<owner>/<repo>/pulls/<number>/comments \
  --jq '.[] | {node_id, user_login: .user.login, user_type: .user.type}'
```

Walk every comment in each thread to classify per the targeting policy.

`NEW_TOP_COMMENT` / `NEW_REVIEW` skip this step — take the `[BOT|USER]`
tag directly from the event line.

## Step 2: React by content

Classify each event by content (`NEW_TOP_COMMENT` may include either
kind, `NEW_COMMENT` is pre-filtered to unresolved / non-outdated).

- Clear fix request (`CHANGES_REQUESTED`, or a `NEW_COMMENT` /
  `NEW_TOP_COMMENT` / `NEW_REVIEW` asking for a change): modify code
  and push, subject to Phase 5's pre-push checks and the Step 5 cap.
  For a `NEW_COMMENT` whose thread is now `is_resolved` / `is_outdated`
  on re-fetch, skip it. For a `NEW_REVIEW`, re-fetch the body first.
- Question / nit / ambiguous intent — reply, do not push. Bot author
  only; human author requires explicit user authorization.
  - `NEW_COMMENT` (thread): `gh pr-review comments reply --thread-id
    <id> --body <text> -R <owner>/<repo> <number>`.
  - `NEW_TOP_COMMENT` / `NEW_REVIEW` (top-level):
    `gh pr comment <number> --body <text>`.
- `READY_FOR_REVIEW`: no action; register that review activity is now
  expected.
- Informational (`APPROVED`, or CI `PENDING` / `IN_PROGRESS` /
  `QUEUED`): no action; surface to the user on the next turn.

`NEW_TOP_COMMENT` carries author + login only — re-fetch body from
the `comments` field before classifying.

## Step 3: Resolve threads

Bot-authored `NEW_COMMENT` threads only. Resolve after:

- A fix push addressing the thread.
- A reply closing a question / nit / ambiguous-intent comment.

Leave open while waiting for the reviewer's follow-up. Take the thread
id from Step 1's `thread_id` field:

```bash
gh pr-review threads resolve --thread-id <thread-id> -R <owner>/<repo> <number>
```

## Step 4: Human-authored events

Do not auto-reply or auto-resolve. Surface the content to the user
(thread id / path / line / body excerpt for threads; body excerpt for
top-level) and stop.

If the user explicitly asks to reply, draft the text, wait for
approval, then run the command. Resolution stays with the user.

## Step 5: Cap for autonomous fix pushes

Stop autonomous fix pushes after 3 fix commits for this PR in this
session. Switch to reply-only and notify the user.

## Forbidden shortcuts

- Skipping the bot check before any mutation.
- Treating a thread as a bot thread from its opening comment alone
  when later comments include a human.
- Posting a top-level `gh pr comment` in place of a review-thread
  reply to bypass the bot-check.
- Classifying an author from a remembered login string instead of a
  live `user.type` / `__typename` lookup.

## References

- `agynio/gh-pr-review` extension: https://github.com/agynio/gh-pr-review
