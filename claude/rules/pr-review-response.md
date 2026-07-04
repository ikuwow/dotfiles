# PR Review Response

How to reply to and resolve PR review thread comments.
Scope: review-thread comments only. Top-level PR comments
(`gh pr comment`) are out of scope.

This is the interim rule-only form of #126. All calls go through the
`agynio/gh-pr-review` extension and the REST `/pulls/<n>/comments`
endpoint, both permission-friendly under the existing allowlist, so no
step requires an approval prompt.

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
go on the human path under this rule and require explicit user
authorization to reply or resolve.

Anything not classified as a bot thread is treated as human.

## Step 1: List review threads (read-only)

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

## Step 2: Reply to a bot thread

Only after confirming every comment in the thread is a bot. The
extension performs the mutation without an approval prompt, so the
bot check in Step 1 is the sole gate — do not skip it.

```bash
gh pr-review comments reply --thread-id <thread id> --body <reply body> -R <owner>/<repo> <number>
```

## Step 3: Resolve a bot thread

After the reply lands, resolve the same thread:

```bash
gh pr-review threads resolve --thread-id <thread id> -R <owner>/<repo> <number>
```

## Human threads

Do not run `gh pr-review comments reply` or `gh pr-review threads
resolve` on a human-authored thread. Surface the comment content to
the user with thread id, path, line, and body excerpt, then stop.

If the user explicitly asks to reply to a specific human thread,
present the draft reply text, wait for approval, then run the reply
command in Step 2. Resolution of a human thread stays with the user.

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
