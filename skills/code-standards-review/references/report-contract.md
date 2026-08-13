# Report Contract

Keep evidence concrete: commands run, file paths, line references, PR
metadata, checked docs, and test output. In a gate report, every `⚠️`, `❌`,
and `not assessed` row must appear again under `Findings`, `Tradeoffs`, or
`Not assessed`. In a quick report, name `not assessed` dimensions in the
scope note.

## Modes

SKILL.md step 1 owns mode selection; the modes differ only in shape:

- **gate** — the full report below, including the summary table.
- **quick** — the verdict line, a one-line scope note (target, files
  reviewed, files excluded, and any `not assessed` dimensions), then
  `Findings`, `Tradeoffs`, and `Recommended next step` as needed. No summary
  table. Verdict and severity rules are identical in both modes.

## Gate report shape

```markdown
# Code standards review: <target>

**Verdict: PASS | PASS WITH CONCERNS | FAIL**
<One-sentence justification. For FAIL, name the blocker. For PASS WITH
CONCERNS, name the highest-value follow-up. For PASS, say why the reviewed
scope is clean.>

**Scope:** <mode, files reviewed, files excluded and why>

## Summary table

| Dimension | Result | Evidence |
|---|---|---|
| Repo conventions | ✅/⚠️/❌/n/a/not assessed | |
| Architecture boundaries | ✅/⚠️/❌/n/a/not assessed | |
| Maintainability & modularity | ✅/⚠️/❌/n/a/not assessed | |
| Domain model | ✅/⚠️/❌/n/a/not assessed | |
| SOLID/DRY/change cost | ✅/⚠️/❌/n/a/not assessed | |
| Tests & verification | ✅/⚠️/❌/n/a/not assessed | |
| Security | ✅/⚠️/❌/n/a/not assessed | |
| Observability | ✅/⚠️/❌/n/a/not assessed | |
| API & semver compatibility | ✅/⚠️/❌/n/a/not assessed | |
| DX & UX/accessibility | ✅/⚠️/❌/n/a/not assessed | |

## Findings
<Numbered findings, blocking first. Omit if none.>

## Tradeoffs
<Context-sensitive choices that are defensible or need human confirmation.
Omit if none.>

## Not assessed
<Checks or dimensions that could not be evaluated, why, and what would close
the gap. Omit only when every relevant dimension was assessed.>

## Recommended next step
<One concrete next action for the human or implementer. The skill itself does
not merge, approve, request changes, or comment on the PR.>
```

This table is the canonical dimension list; SKILL.md step 4's lenses match
its rows one-to-one.

## Result Values

Use exactly these five tokens:

- `✅`: assessed and acceptable for the reviewed diff. Suggestions against a
  dimension do not change its icon.
- `⚠️`: at least one `should-fix` finding on this dimension.
- `❌`: at least one `blocker` finding on this dimension.
- `n/a`: dimension does not apply to this diff. Use it for merely untouched
  dimensions — never `✅`.
- `not assessed`: dimension might apply, but available context or tooling did
  not allow a credible assessment.

Row icons are derived from finding severity: a `blocker` marks its primary
dimension `❌`, a `should-fix` marks it `⚠️`. Secondary dimensions touched by
the same root cause keep their own independently assessed token; their
Evidence cell may add "see Finding N". The verdict is computed from findings,
never from counting rows.

## Severity Model

Use consequence-based severity, not category-based severity.

- **blocker**: should stop merge. A concrete failure introduced by the diff,
  an exploitable or plausibly attackable security weakness, a data-loss risk,
  a public compatibility break without migration/versioning, a violated
  documented boundary, a missing test for vital changed behavior, or a breach
  of a documented repo rule the repo treats as mandatory.
- **should-fix**: clear maintainability, domain, test, DX, UX, observability,
  or security-hardening weakness with a concrete future-cost scenario. Does
  not fail the gate alone. A security or API concern without a concrete
  exploit, break, or data-loss consequence is `should-fix`, not `blocker`.
- **suggestion**: a non-blocking improvement where the better alternative is
  clear, with evidence; current code is defensible. (When the best path is
  genuinely ambiguous and needs human direction, it belongs in `Tradeoffs`,
  not here.)

Test gaps: a missing test for vital changed behavior (a domain rule, public
contract, or security-relevant path) is a `blocker`; other coverage gaps are
`should-fix`.

Check failures: a failing required check in scope is a `blocker` (usually
under Tests & verification); a failing optional or informational check is
`should-fix`. A repo-documented mandatory gate (required CI, mandatory
security scan) that could not be verified at all is also a `blocker` — cite
the check's source (CI config path, required-check name) instead of a diff
line. A failure caused by environment setup, missing dependencies, or a wrong
command goes under `Not assessed`, never `Findings`.

## Verdict Rules

The verdict is computed from findings — never asserted independently:

- **FAIL** ⟺ at least one `blocker` finding.
- **PASS WITH CONCERNS** ⟺ no blockers, and at least one `should-fix`
  finding, unresolved tradeoff, or `not assessed` on a dimension relevant to
  the diff.
- **PASS** ⟺ no findings above `suggestion`, no unresolved tradeoffs, and
  every relevant dimension is `✅` or `n/a`.

A tradeoff is **unresolved** unless its Recommendation is "accept" (backed by
evidence); accepted tradeoffs do not affect the verdict.

`not assessed` never produces FAIL by itself. The unverifiable-mandatory-gate
case is not an exception: it is an ordinary `blocker` finding (see Check
failures), so its dimension row becomes `❌` and FAIL follows from the normal
rules.

Pre-emit self-check, both modes: the verdict maps exactly to the emitted
findings, unresolved tradeoffs, and named `not assessed` dimensions — a PASS
alongside a `should-fix`, or a PASS WITH CONCERNS with nothing listed, is a
contract violation. Gate mode additionally: every `❌` row maps to a
`blocker` finding and every `⚠️` row to a `should-fix` finding, and vice
versa. A capped finding's one-line "+N more" title counts as a valid
referent.

## Finding Template

```markdown
1. **[blocker|should-fix] <short title>** — `<file>:<line>` (add "and N
   other sites" when instances are bundled)
   - **Symptom:** What the diff does.
   - **Standard:** Repo rule, exemplar, public contract, or source-backed
     principle that applies.
   - **Consequence:** What breaks, becomes unsafe, or becomes harder.
   - **Fix:** Concrete change to make.
```

Every `blocker` and `should-fix` finding must include all four fields; if any
field cannot be filled honestly, demote to `Tradeoffs` or drop it.
Suggestions may be a single line: `**[suggestion]** <claim> — <evidence>;
<fix>`.

## Noise Controls

- Report one finding per root cause. Bundle repeated instances.
- List every `blocker`, always. Cap `should-fix` findings at the five most
  important and suggestions at three, unless the user asks for exhaustive
  output; when capped, state "+N more" with one-line titles.
- Do not re-list individual diagnostics the repo's formatter/linter tooling
  already reports. A failing in-scope required check is still a finding —
  summarize the failure, don't enumerate its diagnostics. When lint could not
  be run, a convention issue with `file:line` evidence and repo authority is
  still reportable.
- Flag pre-existing debt only when the diff worsens it or relies on it in a
  new way.
- Generic principles become blockers only with repo authority, security
  impact, or public-contract impact behind them.

## Tradeoffs

Use `Tradeoffs` only for defensible choices that need human judgment — never
to restate a finding (a finding already carries its fix):

```markdown
| Item | Tension | Evidence | Recommendation |
|---|---|---|---|
| <choice> | <e.g. DRY vs decoupling> | `<file>:<line>` and precedent | <accept, document, or change> |
```

When repo convention conflicts with a generic principle, record the convention
and normally follow the repo. Escalate only if the convention creates a concrete
security, correctness, data-loss, or compatibility issue in this change.
