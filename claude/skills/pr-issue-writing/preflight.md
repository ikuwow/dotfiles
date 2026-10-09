# Before creating a PR or an issue

These steps run before the body of a new PR or issue is written, and
before an existing PR's placeholder body is replaced. Each step reads
the target repository, which differs from the working directory
whenever the PR or issue goes to another repository, and the target's
own `CLAUDE.md` is then not loaded.

## 1. Resolve the target and its visibility

- Take `owner/repo` from `-R` / `--repo`, otherwise from the working
  directory, and read its visibility:
  `gh repo view [<owner>/<repo>] --json nameWithOwner,visibility`
- When the target is `PUBLIC` and the content originates in a private
  or internal repository, stop and confirm with the user before
  writing
  - Content of that kind includes the source repository's `owner/repo`,
    its issue and PR numbers, and code or comments quoted from it
  - A public issue or PR notifies watchers by mail as it is created,
    and deleting it afterwards does not recall the mail

## 2. Read the target's rules

- Read `CLAUDE.md` and `AGENTS.md` at the target's root, and
  `CONTRIBUTING.md` at its root, in `.github/`, or in `docs/`
  - Follow what they state about language, title format, labels, and
    linking, over the defaults in this skill
- For an issue, also read `.github/ISSUE_TEMPLATE/config.yml`
  - `blank_issues_enabled: false` means every issue starts from one of
    the templates
  - `contact_links` names a channel outside issues, such as
    Discussions, and when the request fits one, ask the user whether to
    use it instead
- In a repository other than the working directory, read a local clone
  when `ghq list -p <owner>/<repo>` finds one, otherwise
  `gh api repos/<owner>/<repo>/contents/<path> -H 'Accept: application/vnd.github.raw'`

## 3. Find the template

- PR: `pull_request_template.md` at the root, in `docs/`, or in
  `.github/`, and the files in a `PULL_REQUEST_TEMPLATE/` directory in
  any of those three
- Issue: the `.md` and `.yml` files in `.github/ISSUE_TEMPLATE/`, taking
  the one whose purpose matches the issue
- When the target has none of its own, look in the same places in the
  owner's `.github` repository, which GitHub serves as the default
  ([default community health files](https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/creating-a-default-community-health-file))
- A Markdown template sets the body's sections and their order
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
- When a result covers the same problem or change, stop before
  creating and ask the user to choose: comment on the existing one,
  create a new one linked to it, or drop it
- Report the queries run and the number of hits for each
