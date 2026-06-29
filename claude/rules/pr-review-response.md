# PR Review Comment Response

How to react to PR review comments (line / threaded comments tied to specific
diff hunks), separate from top-level PR comments.

The hard rule: never reply to or resolve a thread whose first author is human.
Summarize the content to the user in the conversation and stop. The user
decides.

For bot threads (`__typename == "Bot"` or login in the known list inside
`bin/gh-pr-thread-bot-guard.sh`), follow the procedure below.

## Procedure

1. List threads:
   `gh-pr-review-threads <owner/repo> <pr-number>`
2. Filter to threads where `isResolved == false` and `isOutdated == false`.
   Resolved or outdated threads are already handled or no longer applicable.
3. For each remaining thread:
   - If the first comment author is human, stop. Summarize and surface to the
     user. Do not call reply / resolve scripts.
   - If the first comment author is a bot:
     - Decide whether the comment is actionable (fix needed) or
       discussion / nit / question.
     - For actionable comments: implement the fix in code first, push, then
       reply with a one-line acknowledgment via
       `gh-pr-thread-reply <owner/repo> <pr-number> <thread-id> '<body>'`.
     - For discussion / nit: reply explaining the position (accept or
       decline with reason).
     - After replying, resolve the thread:
       `gh-pr-thread-resolve <owner/repo> <pr-number> <thread-id>`.

## Prohibited

- Calling `gh api graphql` directly to reply or resolve threads.
  Always go through the wrapper scripts so the bot guard fires.
- Bypassing the bot guard, including for "obviously safe" human threads.
- Resolving without replying (the thread record loses the reasoning).

## When the bot guard refuses

The wrapper exits with a non-zero status and a stderr message identifying
the author login and `__typename`. Surface that message to the user and
stop. Do not retry against a different thread ID hoping to slip through.
