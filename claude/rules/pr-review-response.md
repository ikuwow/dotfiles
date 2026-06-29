# PR Review Response

How to reply to and resolve PR review thread comments.
Scope: review-thread comments only. Top-level PR comments
(`gh pr comment`) are out of scope.

This is the interim rule-only form of ikuwow/dotfiles#126. A future
script (`bin/gh-pr-thread-{reply,resolve}`) will absorb the bot check
and replace these instructions.

## Targeting policy

Reply to and resolve only bot comments. Never reply to or resolve a
human comment by mutation. For human comments, summarize the content
to the user and wait for an explicit instruction.

A thread's author is the author of the thread's first comment.

Bot author: GraphQL `author.__typename == "Bot"`. Known logins
include `github-actions`, `dependabot`, `copilot-pull-request-reviewer`,
`renovate`, `devin-ai-integration` (note: GraphQL `author.login` has no
`[bot]` suffix even when the UI shows one). `__typename` is the
authoritative signal; the login list is a sanity check.

Anything not classified as bot is treated as human.

## Step 1: List review threads (read-only)

Extend the `reviewThreads` query in `git-workflow.md` with
`author{login __typename}` on each comment node. Example:

```bash
gh api graphql -f query='query($owner:String!,$repo:String!,$num:Int!){repository(owner:$owner,name:$repo){pullRequest(number:$num){reviewThreads(first:100){nodes{id isResolved isOutdated comments(first:100){nodes{id author{login __typename} body path line}}}}}}}' -f owner=<owner> -f repo=<repo> -F num=<number>
```

Filter to actionable threads: `isResolved == false` and
`isOutdated == false`. Classify each by the first comment's
`author.__typename`.

## Step 2: Reply to a bot thread

Only after confirming the first comment is a bot. Mutation is
manually approved every time (`approve_gh_graphql_readonly.py` only
auto-approves read-only queries) — re-verify the author at the
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
- Using `gh pr comment` to work around the human-thread restriction
  (top-level comments are a different surface, not a substitute reply)
- Using `--field` / `-F` / `--raw-field` for the `query` argument
  (see `gh-graphql.md`)

## References

- `addPullRequestReviewThreadReply`: https://docs.github.com/en/graphql/reference/mutations#addpullrequestreviewthreadreply
- `resolveReviewThread`: https://docs.github.com/en/graphql/reference/mutations#resolvereviewthread
- `PullRequestReviewThread` (fields used: `id`, `isResolved`, `isOutdated`, `comments`): https://docs.github.com/en/graphql/reference/objects#pullrequestreviewthread
- `Bot` vs `User` (`__typename` source): https://docs.github.com/en/graphql/reference/interfaces#actor
