# Technical Reference Doc Scoping

## Applies to

Reference documentation for operating or managing a directory, module,
or service. Specifically:

- README.md
- Operational / runbook docs
- Per-host or per-module operations notes

## Does not apply to

Documents where rationale and discussion are part of the value:

- PR description / commit message
- Issue / discussion / chat
- ADR / design doc

## Rule

Before writing the body, articulate the file's management scope in one
sentence. Scope = the range of information needed to operate what this
file directly manages (the playbook, code, config in this directory).

Information outside that scope does not belong in the body. Common
out-of-scope material:

- Internal behavior or resolution algorithms of dependencies (external
  tools, OS, services)
- Configuration or operations of other directories or systems
- Design rationale (why A and not B) -- that goes in the PR description
  or ADR
- Detailed examples of individual workloads using this thing

When out-of-scope material must be touched, summarize in one line plus
a link to the primary source. Do not paste the mechanism explanation
into the body.

This applies from the very first draft. Do not write verbose first and
trim only after a reviewer or user asks.
