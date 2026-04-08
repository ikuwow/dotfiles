# gh api graphql Convention

When making read-only GraphQL API calls via `gh`, always use this format:

```bash
gh api graphql -f query='query { ... }'
```

Or the shorthand form (implicit query):

```bash
gh api graphql -f query='{ ... }'
```

Rules:

- Always use `-f` (not `--field`, `-F`, or `--raw-field`) for the query
  argument
- Always single-quote the query value
- Pass variables as separate `-f` or `-F` arguments:
  `gh api graphql -f query='query($owner: String!) { ... }' -f owner='octocat'`
- Mutations use the normal format and will require manual approval (this
  is intentional)

This convention enables the `approve_safe_commands.py` hook to auto-approve
read-only GraphQL queries while keeping mutations gated behind confirmation.
