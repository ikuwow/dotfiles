# PR Review Response

How to reply to and resolve PR review thread comments.
Scope: review-thread comments only. Top-level PR comments
(`gh pr comment`) are out of scope.

This is the interim rule-only form of #126. A future
script (`bin/gh-pr-thread-{reply,resolve}`) will absorb the bot check
and replace these instructions.

## Targeting policy

Reply to and resolve only bot threads. Never reply to or resolve a
thread that contains any human comment. For threads with human
involvement, summarize the content to the user and wait for an
explicit instruction.

A thread qualifies as a bot thread only when every comment in it has
`author.__typename == "Bot"`. A single human comment anywhere in the
thread flips it to the human path — including the common case where a
bot opens a thread and a human follows up.

Known bot logins for cross-reference: `github-actions`, `dependabot`,
`copilot-pull-request-reviewer`, `renovate`. GraphQL `author.login`
has no `[bot]` suffix even when the UI shows one. `__typename` is the
authoritative signal; the login list only confirms identity at a
glance. Some automated reviewers (e.g. `devin-ai-integration`) post
under regular user accounts and return `__typename == "User"` — those
go on the human path under this rule and require explicit user
authorization to reply or resolve.

Anything not classified as a bot thread is treated as human.

## Step 1: List review threads (read-only)

```bash
gh api graphql -f query='query($owner:String!,$repo:String!,$num:Int!){repository(owner:$owner,name:$repo){pullRequest(number:$num){reviewThreads(first:100){nodes{id isResolved isOutdated comments(first:100){nodes{id author{login __typename} body createdAt path line}}}}}}}' -f owner=<owner> -f repo=<repo> -F num=<number>
```

Filter to actionable threads: `isResolved == false` and
`isOutdated == false`. Classify each by walking every comment in the
thread, per the rule in the previous section.

## Step 2: Reply to a bot thread

Only after confirming every comment in the thread is a bot. Mutations
require manual approval every time — re-verify the thread at the
approval prompt.

```bash
gh api graphql -f query='mutation($threadId:ID!,$body:String!){addPullRequestReviewThreadReply(input:{pullRequestReviewThreadId:$threadId,body:$body}){comment{id url}}}' -f threadId=<thread id> -f body=<reply body>
```

## Step 3: Resolve a bot thread

After the reply lands, resolve the same thread:

```bash
gh api graphql -f query='mutation($threadId:ID!){resolveReviewThread(input:{threadId:$threadId}){thread{id isResolved}}}' -f threadId=<thread id>
```

## Human threads

Do not call `addPullRequestReviewThreadReply` or `resolveReviewThread`
for a human-authored thread. Surface the comment content to the user
with thread id, path, line, and body excerpt, then stop.

If the user explicitly asks to reply to a specific human thread,
present the draft reply text, wait for approval, then issue the
mutation in step 2. Resolution of a human thread stays with the user.

## Forbidden shortcuts

- Skipping the bot check before any mutation
- Treating a thread as a bot thread based only on its opening comment
  when a later human comment is present
- Using `gh pr comment` to work around the human-thread restriction
  (top-level comments are a different surface, not a substitute reply)

## References

- `addPullRequestReviewThreadReply`: https://docs.github.com/en/graphql/reference/mutations#addpullrequestreviewthreadreply
- `resolveReviewThread`: https://docs.github.com/en/graphql/reference/mutations#resolvereviewthread
- `PullRequestReviewThread` (fields used: `id`, `isResolved`, `isOutdated`, `comments`): https://docs.github.com/en/graphql/reference/objects#pullrequestreviewthread
- `Bot` vs `User` (`__typename` source): https://docs.github.com/en/graphql/reference/interfaces#actor
