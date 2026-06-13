# shellcheck shell=bash
# Shared bot-author guard for gh-pr-thread-{reply,resolve}.
#
# A thread is bot-authored when the FIRST comment's author satisfies either:
#   - GraphQL __typename == "Bot"
#   - login appears in KNOWN_BOTS below (covers GitHub App accounts that
#     report __typename as "User", e.g. copilot-pull-request-reviewer)
#
# Source this file from a script; do not execute directly.

KNOWN_BOTS=(
  "github-actions[bot]"
  "dependabot[bot]"
  "renovate[bot]"
  "copilot-pull-request-reviewer[bot]"
  "copilot-pull-request-reviewer"
  "coderabbitai[bot]"
  "devin-ai-integration[bot]"
  "claude[bot]"
)

gh_pr_thread_assert_bot() {
  local repo="$1"
  local pr="$2"
  local thread_id="$3"

  # Thread IDs come from GitHub GraphQL and are opaque base64-style strings.
  # Reject anything outside that charset so the value cannot influence the jq
  # filter or the GraphQL variable binding.
  if ! [[ "$thread_id" =~ ^[A-Za-z0-9_=/+-]+$ ]]; then
    echo "Error: thread id contains unexpected characters: $thread_id" >&2
    exit 1
  fi

  # Direct node(id:) lookup avoids the 100-thread pagination cap of
  # reviewThreads(first:100) and removes the client-side jq filter on the
  # thread id (the previous lookup would silently fail on PRs with >100
  # threads and the id-in-jq form had a subtle quoting risk).
  local json
  # shellcheck disable=SC2016 # GraphQL query: $vars are query variables, not shell
  json="$(gh api graphql \
    -f tid="$thread_id" \
    -f query='query($tid:ID!){
      node(id:$tid){
        ... on PullRequestReviewThread {
          comments(first:1){ nodes{ author{ login __typename } } }
        }
      }
    }' \
    --jq '.data.node.comments.nodes[0].author')"

  if [ -z "$json" ] || [ "$json" = "null" ]; then
    echo "Error: thread $thread_id not found on $repo PR $pr" >&2
    exit 1
  fi

  local typename login
  typename="$(echo "$json" | jq -r '.__typename')"
  login="$(echo "$json" | jq -r '.login')"

  if [ "$typename" = "Bot" ]; then
    return 0
  fi

  local b
  for b in "${KNOWN_BOTS[@]}"; do
    if [ "$login" = "$b" ]; then
      return 0
    fi
  done

  echo "Error: thread $thread_id first author is not a bot (login=$login, __typename=$typename). Reply/resolve refused." >&2
  exit 1
}
