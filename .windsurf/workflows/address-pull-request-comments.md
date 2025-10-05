---
auto_execution_mode: CASCADE_COMMANDS_AUTO_EXECUTION_UNSPECIFIED
description: How to address Github pull request comments
---
1. Assume that you are given a pull request link. If you are not, prompt the user to provide one.
2. Check out the PR branch: `gh pr checkout [id]`
If the user does not have the gh CLI, prompt them to fill it out.

3. Get comments on PR
```bash
gh api --paginate repos/[owner]/[repo]/pulls/[id]/comments | jq '.[] | {user: .user.login, body, path, line, original_line, created_at, in_reply_to_id, pull_request_review_id, commit_id}'
```

4. For EACH comment, do the following. Remember to address one comment at a time.
  4a. Print out the following: "(index). From [user] on [file]:[lines] — [body]"
  4b. Analyze the file and the line range.
  4c. If you don't understand the comment, do not make a change. Just ask me for clarification, or let me implement it myself.
  4d. If you think you can make the change, make the change BEFORE moving onto the next comment.

5. After all comments are processed, summarize what you did, and which comments need my attention.
