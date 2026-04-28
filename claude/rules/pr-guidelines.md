# PR Guidelines

Quality criteria for pull requests. Follow these when writing a PR body
and when reviewing your own PR.

## Writing Style

- Summarize the change at a high level. Do not mirror the diff line-by-line.
- Keep bullet points few and meaningful. Each bullet should convey a
  distinct decision or outcome, not an individual code change.
- Focus on what changes from the user's or system's perspective — behavior
  changes, new capabilities, removed limitations, etc. — rather than
  listing implementation details (resources added, files touched).
- Anything a reviewer can see by reading the diff does not need to be
  restated in the body. Focus on context the diff cannot convey: why the
  change was made, trade-offs considered, and things to watch out for.

### Essence-first principle

A PR body is not a complete record of the change — it is a summary that
helps a reviewer make a decision. Over-writing buries the signal, and
duplicating context that lives elsewhere causes the two copies to drift
apart over time. Compose the body around the following established
principles.

#### Why over what

The diff already shows *what* changed. The body concentrates on *why*
the change is needed and the shape of the decision (the approach taken
vs. approaches rejected, what was deliberately left out of scope).

References:
- Chris Beams, *How to Write a Git Commit Message*: <https://cbea.ms/git-commit/>
- Linux kernel, *Documentation/process/submitting-patches.rst*

#### Single source of truth (DRY)

If the design rationale, background, or requirements already live
elsewhere (issue, design doc, ADR, prior PR, official spec), do not
duplicate the content into the PR body. Replace it with a one-line
summary plus a link. Duplication creates a sync cost; whichever copy
is updated next will leave the other stale.

Example:
- ✗ "Legal flagged session token storage on YYYY-MM-DD because… (paragraph
  retelling the history)"
- ✓ "Compliance-driven change. Background: <issue #456>"

#### Inverted pyramid

Place the most important information first (the point of the change and
the major design decisions). A reviewer reading only the first few lines
should be able to tell what kind of PR this is and where to focus.

#### Information hiding (Parnas)

Surface only the information a reviewer needs to approve or reject the
PR. Implementation details and the raw log of how the decision was
reached should be hidden, or moved behind a link.

#### Filter before writing

Run each sentence and section through these filters before keeping it.
Drop anything that fails:

1. Is this a restatement of facts the diff already shows?
2. Is this content that already lives elsewhere (issue, design doc,
   prior PR, official spec)?
   → If yes, replace with one line + link.
3. Does the reviewer need this to approve or reject the PR?
4. Am I describing verification that CI already performs automatically?

## PR Body Checklist

When writing a PR body, cover every applicable item:

1. Purpose and motivation
   - State what changed and why (bug, feature, tech debt, compliance, etc.).
   - A reviewer should understand the intent from the body alone.

2. Scope
   - Clearly describe the boundary of the change.
   - Call out anything intentionally left out of scope.

3. Sources and references
   - Provide official documentation URLs or other authoritative sources
     that justify configuration values, tool choices, or version selections.
   - Especially important for dotfiles / infrastructure changes where
     "why this value" matters.

4. Issue linking
   - Do NOT use auto-close keywords (`Closes`, `Fixes`, `Resolves`).

5. Verification
   - Describe only what was actually verified under "confirmed" items.
   - Do not claim verification that was not performed.
   - When the change affects environments that CI cannot replicate
     (e.g., Claude Code web, external services), include manual test
     steps the reviewer can follow to verify in the real environment
     before merging.

## Review Criteria

Used by `/pr-selfcheck` to evaluate a PR after creation.

1. Reviewer-facing information
   - Can a reviewer understand the purpose, what changed, and the impact
     from the PR body alone?
   - Is the scope of the change clear?

2. Sources and references
   - Are official documentation URLs or other authoritative sources provided
     to justify configuration values, tool choices, or version selections?

3. Intent and rationale
   - Does the PR explain not just what changed but why?
   - Is the motivation stated?

4. Link validity
   - Do all URLs in the PR body resolve to the expected content?
   - Do anchor links point to the correct section?

5. Title / body / diff consistency
   - Does the PR title accurately reflect the change?
   - Is there any contradiction between the body description and the
     actual diff?

6. Diff coverage
   - Does the PR body account for all files and changes in the diff?
   - Are there unexplained changes?

7. Conciseness (Essence-first principle)
   - Does the body follow the Essence-first principle in *Writing Style*
     (why over what, single source of truth, inverted pyramid,
     information hiding)?
   - Is the body a high-level summary rather than a line-by-line restatement
     of the diff?
   - Are bullet points few and meaningful, each conveying a distinct point?
   - Is content that lives in another document (issue, design doc, prior
     PR, official spec) replaced with a one-line summary + link rather
     than duplicated?

8. Verification completeness
   - Is every changed code path covered by CI, manual test steps in the
     PR body, or another verification mechanism?
   - Are there paths that only run in a specific target environment
     (e.g., Claude Code web, external services) without a stated plan
     to verify them?
