# Before creating a PR or an issue

These steps run before the body of a new PR or issue is written, and
before an `implementer` subagent that will open a PR is dispatched.
Each step reads the target repository (step 1 also the source), which
differs from the working directory whenever the PR or issue goes to
another repository, and the target's own `CLAUDE.md` is then not
loaded.

## 1. Resolve the target and its visibility

- Take `owner/repo` from `-R` / `--repo`, otherwise from the working
  directory, and read the visibility of both the target and the
  repository the content comes from:
  `gh repo view [<owner>/<repo>] --json nameWithOwner,visibility`
- When the target's visibility is wider than the source's (`PRIVATE`
  to `INTERNAL` or `PUBLIC`, `INTERNAL` to `PUBLIC`) and the body will
  carry anything from the source, stop and confirm with the user before
  writing
  - Anything from the source includes its `owner/repo`, its issue and
    PR numbers, and code, comments, or rule text quoted from it
  - Everyone the target's visibility admits can read the content from
    the moment it is created, and removing it later does not undo what
    was already read

## 2. Read the target's rules

- Read `CONTRIBUTING.md` at the target's root, in `.github/`, or in
  `docs/`, and when the target is not the working directory's
  repository, also `CLAUDE.md` and `AGENTS.md` at its root
  - Follow what they state about language, title format, labels, and
    linking, over the defaults in this skill
- For an issue, also read `.github/ISSUE_TEMPLATE/config.yml`
  - `blank_issues_enabled: false` means every issue starts from one of
    the templates
  - `contact_links` names a channel outside issues, such as
    Discussions, and when the request fits one, ask the user whether to
    use it instead
- When the target has no `CONTRIBUTING.md` or `config.yml` of its own,
  read the one in the owner's public `.github` repository, which GitHub
  serves as the default (see step 3)
- In a repository other than the working directory, read a local clone
  when `ghq list -p -e <owner>/<repo>` finds one, after
  `git -C <clone> fetch origin`, through
  `git -C <clone> show origin/HEAD:<path>`, since the clone's working
  tree may be stale or on another branch
  - Without a clone, or when `origin/HEAD` does not resolve in it, read
    `gh api repos/<owner>/<repo>/contents/<path> -H 'Accept: application/vnd.github.raw'`

## 3. Find the template

Match file names case-insensitively in each place below.

- PR: `pull_request_template.md` at the root, in `docs/`, or in
  `.github/`, and the files in a `PULL_REQUEST_TEMPLATE/` directory in
  any of those three
- Issue: the `.md` and `.yml` files in `.github/ISSUE_TEMPLATE/` other
  than `config.yml`, taking the one whose purpose matches the issue
- When the target has none of its own, look in the same places in the
  owner's public `.github` repository, which GitHub serves as the
  default
  ([default community health files](https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/creating-a-default-community-health-file))
- An issue form (`.yml`) cannot be filled through `--body-file`, so its
  field labels become the body's section headings, with every field the
  form marks required filled
- When no template exists, name the paths searched in the message to
  the user, so the absence can be checked

## 4. Search for duplicates

- Search the target's issues and PRs, open and closed:
  `gh search issues --repo <owner>/<repo> --include-prs <keywords>`
  - Leave `--state` unset, so a closed issue declined earlier surfaces
    too
  - Run at least two keyword sets, such as the component's name and
    the error text or symptom
- A duplicate of an issue is another issue or a PR covering the same
  problem or request
- A duplicate of a PR is another PR making the same change, and the
  issue the PR addresses is its parent rather than a duplicate
- When a duplicate turns up, stop before creating and ask the user to
  choose: comment on the existing one, create a new one linked to it,
  or drop it
- Report the queries run and the number of hits for each
