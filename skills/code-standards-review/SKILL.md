---
name: code-standards-review
description: >-
  Verdict-first standards review (PASS / PASS WITH CONCERNS / FAIL) of a code
  change — GitHub PR, branch, local diff, or pasted diff — against repo
  conventions first, then cross-cutting engineering standards. Use when the
  user asks for a standards review, PR review, pre-merge gate, or
  architecture audit — and after completing a non-trivial code change, as a
  quick-mode self-check that the change aligns with repo patterns and best
  practices. Also use when starting a new project or auditing a young repo's
  foundations (greenfield mode). Not for diagnosing why code fails
  (debugging) and not a dedicated defect hunt: it reviews changes, it does
  not fix them.
---

# Code Standards Review

Produce a verdict report for the change. Report only; do not approve, merge,
request changes, or post comments unless the user separately asks for that.

This is a standards review: does the change preserve the codebase's long-term
shape — conventions, boundaries, contracts, tests, maintainability, and
user/operator surfaces. It is not an exhaustive bug hunt, but a correctness
defect the diff introduces is always reportable when you find one while
applying the standards lenses.

One reviewer, one report. Consult specialist skill guidance when it is
directly relevant (`dep-verify` findings for a dependency bump, `anti-slop`
metrics already produced for this same diff), but produce a single integrated
review yourself. Do not dispatch the review to other skills or agents, and do
not re-run checks another skill already ran on the same diff — cite their
results as evidence.

## References

Read `references/report-contract.md` before writing the final report. It is
the required output contract, defines the two report modes, and owns the
canonical dimension list.

Read `references/research.md` when you need the source-backed rationale for a
standard, when two principles conflict, or when deciding whether a generic
best practice should become a finding.

Read `references/greenfield.md` when the target is a new or young project
rather than a diff — bootstrapping a repo or auditing its foundations. In
greenfield mode, skip the diff workflow: audit (or scaffold) the day-one
items it lists, then report gaps with the same severity model and report
shapes.

## Inputs

Accept any of:

- GitHub PR URL or number
- Branch, commit range, or "current branch vs main"
- Local staged, unstaged, or uncommitted changes
- Pasted diff or specific files

Prefer real repository state over pasted summaries. If a PR is named and `gh`
is available, use it for PR metadata, changed files, diff, checks, and author
context. If `gh` is unavailable or unauthenticated, continue from local git
state and say what could not be verified.

## Workflow

### 1. Pin the target, mode, and scope

Identify the exact diff being reviewed.

- PR: inspect `gh pr view`, `gh pr diff`, and `gh pr checks` when available.
- Branch: compare against the merge base with the likely base branch.
- Local work: review staged and unstaged changes; state which were included.
- Pasted diff: state that repository context may be incomplete.

Choose the report mode (shapes defined in `references/report-contract.md`),
with this precedence:

1. Explicit user wording wins ("quick check" → quick; "full review", "audit",
   "gate" → gate).
2. A PR, pre-merge, or release context → **gate**, regardless of diff size.
3. Otherwise (local work, pasted diffs, post-change self-checks) → **quick**,
   unless the change is large.

Scope hygiene — classify before reviewing:

- Generated files, lockfiles, snapshots, compiled/binary assets: review their
  source inputs and regeneration consistency, not their bodies.
- Vendored/third-party code: out of scope unless the diff edits it directly.
- Formatter-only or mechanical churn: sample it; do not apply design lenses.
- Renames/moves: detect with `git diff -M` (`--find-renames`) or PR rename
  metadata; review only modified hunks and updated import sites, not the
  moved content as greenfield code. Cite the new path.
- Deletions-only diffs are in scope: assess removed public surface under
  API & semver, orphaned tests/references/callers, and removed authz or
  telemetry; most modularity/domain dimensions are `n/a`.
- Huge diffs or monorepo-wide changes: prioritize public contracts and
  security-sensitive paths, sample repeated mechanical edits, and state what
  was not inspected. A diff far past reviewable size (~400 changed lines,
  excluding generated/mechanical churn) that could have been split is itself
  a `should-fix` on review readiness.

Completion criterion: the report can name the target, the mode, the files in
scope, and the files excluded with reasons.

### 2. Discover repo authority

Look for local sources before applying generic principles:

- agent/repo instructions: `AGENTS.md`, `CLAUDE.md`, `.cursorrules`,
  `.cursor/rules`, `.github/copilot-instructions.md`
- contribution standards: `CONTRIBUTING*`, `README*`, `docs/`, `CODEOWNERS`,
  `SECURITY.md`
- architecture and domain docs: `docs/architecture*`, ADR/RFC/spec folders
- build/test/lint authority: package manifests, task files, CI configs,
  formatter/linter configs, typecheck configs
- nearby exemplars: modules that solve the same kind of problem correctly

In monorepos, discover authority per changed package (nearest instructions
file, manifest, lint config, CI job); a package's own rules beat repo-root
rules for that package's files, and sibling-package conventions do not apply.

Use `rg` and file reads. Do not infer a mandatory convention from one example;
look for repeated patterns, docs, or tooling.

Quick mode narrows the search, never the authority: always read the nearest
instructions/conventions file (`README`, `AGENTS.md`/`CLAUDE.md`,
`CONTRIBUTING`) and any ADR or doc governing the changed area — documented
conventions bind every finding in both modes. What quick mode skips is only
the broad workspace sweep (exhaustive CI/config/doc trawling).

Completion criterion: authority sources (paths) and one to three adjacent
exemplars for the changed area are identified — listed in a gate report's
Scope/Evidence, cited from findings where they matter in a quick report.
Grounding rules for findings apply at step 6.

### 3. Apply precedence

Use this order:

1. Explicit user instruction for this review
2. Security, correctness, data-loss, and public API compatibility
3. Documented repo rules and automated tooling
4. Existing local conventions and adjacent patterns
5. Ecosystem idioms
6. Generic engineering principles

Repo conventions normally beat generic SOLID/DRY/modularity advice. Do not ask
a change to be more "principled" than the surrounding code unless the change
introduces a concrete failure mode, crosses a documented boundary, weakens
security, or breaks a public contract.

### 4. Review dimensions

Score the dimensions listed in `references/report-contract.md` (that table is
the canonical list). Use these lenses, matched one-to-one to its rows:

- **Repo conventions**: the authority and precedence work from steps 2–3.
- **Architecture boundaries**: dependency direction, ports/adapters,
  layer/context ownership, no internal cross-module reach-through.
- **Maintainability & modularity**: information hiding, module depth (small
  interface hiding real functionality — shallow pass-throughs are a smell,
  not a virtue), low coupling, change localization, error handling designed
  as part of the interface (expected outcomes vs bugs; illegal states
  unrepresentable).
- **Domain model**: bounded contexts, ubiquitous language, invariants in the
  owning model, vendor terms translated at edges. Weight schema/wire-format/
  public-type changes heaviest — data-model mistakes outlive code mistakes.
- **SOLID/DRY/change cost**: consequence-based use only. Flag change-cost and
  knowledge duplication, not acronym violations.
- **Tests & verification**: changed behavior and public contracts need
  meaningful tests at the cheapest reliable level — and trustworthy ones:
  a test that would not fail if the feature broke, asserts mocks over
  behavior, or flakes is a finding.
- **Security**: authn/authz, input validation, injection, secrets, unsafe
  defaults, dependency/supply-chain surface.
- **Observability**: new runtime paths need enough logs, metrics, traces, or
  errors for operators to diagnose failure.
- **API & semver compatibility**: public API changes need explicit
  compatibility analysis, versioning — and a safe transition: expand/
  contract migrations, rollback (including interim data), flag/canary
  ability where the repo deploys incrementally.
- **DX & UX/accessibility**: new user/developer surfaces need clear errors,
  docs, accessibility, and predictable workflows — for human and agent
  contributors both: greppable names, invariants encoded as checks rather
  than prose, and agent/README docs updated when the diff invalidates them.

Evaluate all ten dimensions in both modes — quick mode omits the table, not
the sweep; any `not assessed` dimension must surface in the quick scope note.
Use the result tokens exactly as `references/report-contract.md` defines
them. Silence is not compliance.

One root cause produces one finding; name its primary dimension in the
finding. Secondary dimensions it touches keep their own independently
assessed result.

Non-code diffs: docs-only changes make most code dimensions `n/a` (assess DX
clarity, and UX only for user-facing docs); infra/CI/manifest changes keep
security and observability in scope, with API/semver relevant only when
public schemas or CRDs change.

### 5. Verify when practical

Run checks mapped to the changed paths: targeted tests, lint, typecheck, or
build for the affected packages. If the full suite is slow, run the targeted
subset and record what was not run. For a PR, inspect hosted check status as
evidence — an in-scope failing check becomes a finding, with severity per the
contract's check-failure rules — but do not treat green CI as a substitute
for standards review.

Report a locally-run check failure as a finding only when you are confident
the failure comes from the reviewed change. A failure from environment setup,
missing dependencies, or a wrong command goes under `Not assessed`, not
`Findings`.

### 6. Write only evidence-backed findings

Use a finding only when all are true:

- the issue is introduced or worsened by the reviewed change;
- there is a concrete consequence;
- the finding cites `file:line` evidence in the diff (for deletions, cite the
  removal hunk as `old_path:line`; for renames, cite the new path; for an
  unverifiable required check, cite the check's source per the contract);
- the standard is grounded in repo authority, a public contract, security/API
  rules, or a source-backed generic principle;
- the fix is actionable.

This grounding applies to every finding at every severity, not only blockers.
If a concern is plausible but not provable, put it in `Tradeoffs` or drop it.
If two reasonable senior engineers could disagree and the consequence is not
concrete, do not make it a finding.

### 7. Emit the report

Use the structure for the chosen mode in `references/report-contract.md`.

Completion criterion: the contract's pre-emit self-check passes — every
finding severity and every `not assessed` dimension is accounted for in the
report, and the verdict follows mechanically from the severity rules.
