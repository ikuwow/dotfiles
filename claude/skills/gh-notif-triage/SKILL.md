---
name: gh-notif-triage
description: Triage GitHub notifications and mark noise as done. TRIGGER when the user invokes /gh-notif-triage. Accepts optional arguments `all` (include already-read), `auto` (full-auto without approval).
model: sonnet
effort: medium
---

# GitHub Notification Triage

Read the GitHub notification inbox, classify each thread by `reason` plus
content, mark noise as "done" (remove from inbox), and keep
action-relevant items visible.

## Arguments

`$ARGUMENTS` is a space-separated list:

- (none) — semi-automatic, unread-only. Default.
- `all` — include already-read notifications.
- `auto` — full-auto. Skip the approval step before deletion.

## Steps

1. Fetch notifications:

   ```
   gh api '/notifications?all=false&per_page=50'
   ```

   When the `all` argument is present, switch to `all=true`.

2. Classify each thread per the rule table below.

3. Print a table showing each `done` candidate with:
   - thread id
   - reason
   - repository
   - subject title
   - human-clickable URL (see "URL handling")

4. If `auto` is in the arguments, skip to step 5.
   Otherwise wait for the user to approve / reject / refine before
   deleting.

5. For each approved `done` candidate, mark it done:

   ```
   gh api -X DELETE /notifications/threads/<thread_id>
   ```

6. Print the list of done threads in-conversation. Do not write a log
   file — the kept categories (`review_requested` / `mention` /
   `assign`) are retrievable from other GitHub views.

## Rule table

Default behavior per `reason`. Edit this table in place when the user's
preferences change.

| reason           | default          | rationale                                                |
| ---------------- | ---------------- | -------------------------------------------------------- |
| ci_activity      | done             | CI / check-suite result, visible on the PR itself        |
| subscribed       | done             | subscription update, no direct action requested          |
| state_change     | done             | close / merge notice, low involvement                    |
| review_requested | keep             | review request, kept by default                          |
| mention          | keep             | named explicitly, likely actionable                      |
| assign           | keep             | assigned, actionable                                     |
| author           | keep (read body) | own PR; read title / state before deciding               |
| security_alert   | keep             | always kept (safety default)                             |

For `author`, briefly inspect title and state before classifying. A
self-authored merge notice can flip to `done`; an active review on
one of the user's PRs stays `keep`.

## URL handling

`subject.url` from the API is an `api.github.com` URL. Convert to a
human-clickable link before displaying:

- `api.github.com/repos` → `github.com`
- `/pulls/` → `/pull/`

`CheckSuite` notifications have a null `subject.url`. Fall back to
`repository.html_url`.

## Prohibited

- `PATCH /notifications/threads/<id>` ("mark as read"). It leaves the
  item in the inbox and does not serve the goal of this skill.
- `DELETE /notifications/threads/<id>/subscription` ("unsubscribe"). A
  different endpoint and a different action — never confuse with done.

## References

- GitHub REST notifications: https://docs.github.com/en/rest/activity/notifications
- Issue: ikuwow/dotfiles#186
