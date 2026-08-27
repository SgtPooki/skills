---
name: review-pr
description: >-
  Full review of a pull request: runs code-standards-review in gate mode as
  the standards engine, adds a Spec axis (does the diff implement what the
  originating issue/spec asked — missing requirements, scope creep,
  implemented-but-wrong), and on request delivers findings as a PENDING
  GitHub review with inline comments the user publishes manually. Use when
  the user asks to review a PR, review a teammate's changes, or wants
  review findings posted to GitHub as a draft. For a standards check
  without a PR or spec (local diff, greenfield, self-check), use
  code-standards-review directly.
---

# Review a pull request

Layer on top of `code-standards-review`: that skill owns the standards
sweep, severity model, and report contract; this skill adds what reviewing
a PR specifically requires — the spec axis and draft delivery to GitHub.
Emit one integrated report with one verdict.

## Workflow

### 1. Pin the PR

Resolve the PR (number, URL, or current branch's PR). Gather metadata,
diff, changed files, and check status — reads via `gitcrawl gh` when on
PATH, plain `gh` otherwise. Note the author and their stated intent from
the PR body: reviewing a teammate's PR, phrase findings for a human
audience; reviewing your own or the user's, be blunt.

Completion criterion: PR number, head/base, diff, and check status in hand.

### 2. Standards axis

Invoke `code-standards-review` in **gate mode** against the PR. Its
workflow (authority discovery, precedence, ten dimensions, evidence rules,
report contract) applies unchanged. Do not re-derive any of it here.

### 3. Spec axis

Find the originating spec, in order:

1. Issue/ticket references in the PR body and commit messages
   (`#123`, `Closes #45`, tracker URLs) — fetch them.
2. A path the user supplied.
3. A spec/design doc under `docs/`, `specs/`, or notes matching the branch
   or feature name.
4. Ask the user. If they say there is none, record the axis as
   `n/a — no spec` and move on.

With a spec in hand, compare it to the diff and report, quoting the spec
line for each finding:

- **Missing**: a requirement the spec asks for that the diff omits or only
  partially implements — `should-fix`, or `blocker` when the PR claims to
  close the issue.
- **Wrong**: a requirement that looks implemented but whose behavior
  contradicts the spec — `blocker`.
- **Scope creep**: behavior in the diff nobody asked for — severity by
  consequence (usually `suggestion`; `should-fix` when it touches public
  contracts or security surface).

### 4. Integrate and report

One report in the gate shape from `references/report-contract.md` (in the
code-standards-review skill), with **Spec conformance** as an added
dimension row. Spec findings feed the same severity→verdict rules; the
verdict stays computed, never asserted. Cross-axis duplicates (one root
cause visible from both axes) collapse into one finding with the primary
dimension named.

### 5. Deliver as a pending GitHub review (only when asked)

Default output is the report in the conversation. When the user wants the
findings on the PR, create a **pending** review they publish themselves:

```bash
jq -n --slurpfile f findings.json '{body: $summary, comments: [...]}' | \
gh api repos/{owner}/{repo}/pulls/{n}/reviews --input -
```

- **Omit the `event` field** — that is what makes GitHub hold the review
  as PENDING, visible only to its author, editable in the "Finish your
  review" UI. Never pass `event` and never call the submit endpoint: the
  user publishes or discards.
- Each inline comment needs `path`, `line`, `side: "RIGHT"` (or
  `start_line` for ranges) anchored to a line in the diff. GitHub rejects
  comments outside diff hunks — validate against the hunks first; anything
  unanchorable goes in the review `body` instead, noted as such.
- GitHub allows one pending review per user per PR. If one already exists,
  stop and tell the user — do not delete it.
- Review body: the verdict line plus the summary; inline comments: one per
  finding, severity-labelled, with the actionable fix. Real `gh` for this
  write, authenticated as the user.
