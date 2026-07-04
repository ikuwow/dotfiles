# PR Reaction

How to react to PR events surfaced by `bin/pr-monitor` (event line spec
lives in `git-workflow.md` Phase 5). Covers all reaction surfaces:
review-thread comments, top-level PR comments, and PR-review summaries.
Also covers thread reply/resolve mechanics.

All calls go through the `agynio/gh-pr-review` extension and REST
`/pulls/<n>/comments`, both permission-friendly under the existing
allowlist — no step requires an approval prompt.

## Targeting policy

Reply to and resolve only bot threads. Never reply to or resolve a
thread that contains any human comment. For threads with human
involvement, summarize the content to the user and wait for an
explicit instruction.

A thread qualifies as a bot thread only when every comment in it has
`user.type == "Bot"` (REST) — equivalent to GraphQL
`author.__typename == "Bot"`. A single human comment anywhere in the
thread flips it to the human path — including the common case where a
bot opens a thread and a human follows up.

Known bot logins for cross-reference: `github-actions`, `dependabot`,
`copilot-pull-request-reviewer`, `renovate`. `user.login` has no
`[bot]` suffix even when the UI shows one. `user.type` is the
authoritative signal; the login list only confirms identity at a
glance. Some automated reviewers (e.g. `devin-ai-integration`) post
under regular user accounts and return `user.type == "User"` — those
go on the human path and require explicit user authorization to reply
or resolve.

Anything not classified as a bot thread is treated as human. The same
Bot/User distinction applies to `NEW_TOP_COMMENT` and `NEW_REVIEW`
events for whether to reply autonomously.

## Step 1: List and classify (read-only)

Two calls, joined on comment node id: the extension gives the thread
structure and resolution state, and REST gives `user.type` for the
bot check.

```bash
gh pr-review review view -R <owner>/<repo> <number> \
  --unresolved --not_outdated --include-comment-node-id
```

```bash
gh api /repos/<owner>/<repo>/pulls/<number>/comments \
  --jq '.[] | {node_id, user_login: .user.login, user_type: .user.type}'
```

Join on `comment_node_id` (extension) == `node_id` (REST). Classify
each thread by walking every comment per the previous section. The
extension's `--unresolved --not_outdated` flags filter server-side, so
no local `is_resolved` / `is_outdated` check is needed.

## Step 2: React by content, not event type

`NEW_COMMENT` is pre-filtered by the monitor to unresolved,
non-outdated threads; `NEW_TOP_COMMENT` is not, so classify it by
content.

- Clear fix request (`CHANGES_REQUESTED`, a `NEW_COMMENT`, a
  `NEW_TOP_COMMENT`, or a `NEW_REVIEW` asking for a change — from a
  human or an automated reviewer like Devin or Copilot): modify code
  and push, subject to Phase 5's pre-push checks and the Step 5 cap
  below. For a `NEW_COMMENT`, if the re-fetched thread is now
  `is_resolved` or `is_outdated`, it was handled in the interim —
  skip it. For a `NEW_REVIEW`, re-fetch the review body to classify
  intent.
- Question, nit, or ambiguous intent: reply and do not push. Pick the
  reply channel by event type so context stays intact:
  - `NEW_COMMENT` (review thread comment): reply inside the thread
    with `gh pr-review comments reply --thread-id <id> --body <text>
    -R <owner>/<repo> <number>`. Bot threads only per the targeting
    policy; human threads require explicit user authorization.
  - `NEW_TOP_COMMENT` / `NEW_REVIEW`: no thread to attach to; post a
    top-level PR comment with `gh pr comment <number> --body <text>`.
- `READY_FOR_REVIEW`: the user took the PR out of draft; no action,
  just register that review activity is now expected.
- Informational (`APPROVED`, or CI still `PENDING` / `IN_PROGRESS` /
  `QUEUED`): no action; surface it to the user on the next turn.

Event-specific notes:

- `STATE: MERGED` / `CLOSED` is terminal — handled in `git-workflow.md`
  Phase 5 exit conditions, not here.
- `NEW_TOP_COMMENT` carries only the author tag and login; re-fetch
  the body from the `comments` field before classifying.
- `CI_FAILURE`: get the `databaseId` from `gh run list` (check names
  don't always map 1:1 to run names), inspect with `gh run view
  --log-failed <databaseId>`, then fix and push.

## Step 3: Resolve threads

Applies to `NEW_COMMENT` only — top-level comments and review summary
bodies are not threads. Only bot-authored threads are resolved
autonomously per the targeting policy; human threads stay with the
user.

- After a fix push that addresses a `NEW_COMMENT`, resolve the
  originating thread so subsequent monitor passes skip it and reviewers
  see the discussion state.
- After a reply that closes a question / nit / ambiguous-intent
  comment (e.g., explaining an intentional decision), resolve the
  thread.
- Leave the thread open when waiting for the reviewer's follow-up.
- Get the thread id from Step 1's `review view` output (`thread_id`
  field), then run
  `gh pr-review threads resolve --thread-id <thread-id> -R <owner>/<repo> <number>`.

## Step 4: Human threads and human review reactions

Do not run `gh pr-review comments reply` or `gh pr-review threads
resolve` on a human-authored thread. Surface the comment content to
the user with thread id, path, line, and body excerpt, then stop.

Same discipline for `NEW_TOP_COMMENT` / `NEW_REVIEW` authored by a
human: do not auto-reply via `gh pr comment` unless the user asks.

If the user explicitly asks to reply to a specific human thread or
comment, present the draft reply text, wait for approval, then run the
command. Resolution of a human thread stays with the user.

## Step 5: Cap for autonomous fix pushes

Stop pushing autonomous fixes after 3 fix commits for this PR in this
session. Beyond that, switch to reply-only mode and notify the user
that the PR appears to need human attention. This prevents runaway
loops when an automated reviewer keeps re-requesting changes on each
push.

## Forbidden shortcuts

- Skipping the bot check before any mutation
- Treating a thread as a bot thread based only on its opening comment
  when a later human comment is present
- Using `gh pr comment` to work around the human-thread restriction
  (top-level comments are a different surface, not a substitute reply)

## References

- `agynio/gh-pr-review` extension: https://github.com/agynio/gh-pr-review
- REST `/pulls/{n}/comments` (source of `user.type`): https://docs.github.com/en/rest/pulls/comments#list-review-comments-on-a-pull-request
- `Bot` vs `User` semantics (GraphQL equivalent): https://docs.github.com/en/graphql/reference/interfaces#actor
