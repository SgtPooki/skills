---
name: dep-verify
description: >-
  Full pre-merge audit of a dependency-update PR (Dependabot, Renovate, or a
  manual version bump) in ANY ecosystem — npm/pnpm/yarn, GitHub Actions,
  Docker, Go, Python, Rust, etc. Verifies the PR author is the real bot,
  checks release age against supply-chain cooldown windows, reads every
  intermediate changelog, diffs the published artifact for malicious or
  breaking changes, validates provenance/signatures, reviews the lockfile
  diff, maps the blast radius in the codebase, runs build/typecheck/tests,
  and produces a MERGE / MERGE WITH CAUTION / HOLD / REJECT verdict report.
  Use this whenever the user points at a dependency-update PR, asks "should I
  merge this dependabot/renovate PR", asks to review/verify/vet a package
  bump or version update, or asks whether an update has breaking changes or
  is safe. It never merges — it only reports.
---

# dep-verify: pre-merge audit for dependency updates

Verify a dependency-update PR on two independent axes, then report a verdict:

1. **Compatibility** — will this break the code? (Semver is declared intent,
   not a guarantee: roughly a third of releases ship breaking changes, many in
   minors/patches.)
2. **Supply-chain integrity** — is the published artifact what the maintainer
   meant to publish, and is it benign? (Every major npm attack of 2018–2025 —
   event-stream, ua-parser-js, chalk/debug, Shai-Hulud — was delivered as an
   ordinary-looking version bump. The artifact can differ from the git repo.)

A green CI run answers neither question by itself. Run **every phase below on
every PR** — do not skip phases because the update "looks small"; patch
releases are precisely where compromised versions ship, because reviewers
skim them.

**This skill never merges, approves, or comments on the PR.** The deliverable
is the verdict report (Phase 8). The human merges.

## Inputs

Accept any of: a PR URL, `owner/repo#123`, a branch name, or "the dependabot
PRs on <repo>". If given a repo with multiple open update PRs, list them
(`gh pr list --author app/dependabot`, also `app/renovate`), ask which to
audit — or audit each in turn if asked to handle all of them.

Work from a local clone when possible (clone or fetch the repo, check out the
PR branch: `gh pr checkout <n>` or `git fetch origin pull/<n>/head`). Many
checks need the real lockfile diff and a runnable tree. If the code cannot be
run locally (missing toolchain, private services), still do every static
phase and say clearly in the report which dynamic checks you could not run.

Detect the ecosystem from the manifest files the PR touches, then read
`references/ecosystems.md` for the ecosystem-specific commands used in
Phases 3–7. Read `references/supply-chain.md` before Phase 4 for the red-flag
taxonomy and attack patterns. A grouped PR (multiple packages) gets the full
audit **per package**; report per-package findings and one overall verdict
(the worst package sets the verdict).

## Phase 1 — Authenticate the PR itself

Fake-Dependabot attacks are real: in 2023, attackers used stolen tokens to
push commits with the forged author string `dependabot[bot]` to hundreds of
repos, adding secret-exfiltrating workflows. Author names in git are
arbitrary metadata, so verify the account, not the name:

- `gh pr view <n> --json author,title,headRefName` — the author must be the
  bot **app** account (`is_bot: true`; Dependabot's app account, not a user
  account that merely has "dependabot" in its name). Same idea for
  `renovate[bot]`.
- Commits must show **Verified** (GitHub-signed):
  `gh api repos/<o>/<r>/commits/<sha> --jq .commit.verification.verified`
- `gh pr diff <n> --name-only` — a real bot PR touches only manifest +
  lockfile (+ pinned-SHA comment lines in workflows). Any touched workflow,
  script, or source file that isn't a manifest is an immediate **REJECT**
  finding pending explanation. Also treat a force-push that rewrote the
  branch *after* checks passed as suspicious.

## Phase 2 — Classify the update

Record, per package: ecosystem; old → new version; direct or transitive;
production or development dependency; semver jump (treat a 0.x **minor** as a
major); whether the PR is grouped; whether it is a **security update** (fixes
a known CVE — this matters for the cooldown tradeoff in Phase 4).

This classification does not reduce the audit — it calibrates how much
weight findings carry in the verdict (a failing type-check matters more for a
prod dep; a brand-new release matters more for anything with install scripts).

## Phase 3 — What changed (compatibility)

- **Read release notes/changelogs for every intermediate version**, not just
  the newest — breaking changes accumulate across skipped versions. For a
  major, find the migration/upgrade guide (`MIGRATION.md`, `UPGRADING.md`,
  docs site).
- **Diff the published artifact**, not just the git repo, using the
  ecosystem's mechanism (e.g. `npm diff` — see `references/ecosystems.md`).
  The registry artifact is what actually runs; xz and chalk both shipped
  payloads absent from the repo.
- **Compare packaging metadata** old vs new: peer/companion dependency
  ranges, minimum runtime version (`engines`, `python_requires`, `go`
  directive…), entry points/exports maps, module format (ESM/CJS), type
  definitions, and — critically — **install/lifecycle scripts**. These break
  builds (or ship malware) without being "API changes".
- **No changelog?** That plus a nontrivial artifact diff is itself a finding.
  Reconstruct what changed from the tag compare and the artifact diff; never
  write "no changelog available" and move on.

## Phase 4 — Supply-chain integrity

Read `references/supply-chain.md`, then check:

- **Release age (cooldown).** Get the publish timestamp. Malicious releases
  are usually detected and pulled within hours-to-days; in 8 of 10 studied
  attacks the exploitation window was under a week, which is why Dependabot
  now defaults to a 3-day cooldown. A release **< 3 days old** ⇒ at best
  MERGE WITH CAUTION ("wait N more days"), unless it is a security fix —
  then weigh CVE severity against the freshness risk and say so explicitly.
- **Provenance / signatures.** Verify registry signatures and provenance
  attestations where the ecosystem supports them; confirm the recorded
  commit exists as the upstream tag. A **provenance regression** (previous
  versions attested, this one doesn't) is a strong red flag.
- **Publisher continuity.** Same maintainer/account as prior releases? Recent
  ownership transfer, a first publish in years, or a publishing burst across
  unrelated packages from one account are the event-stream/Shai-Hulud
  patterns.
- **Artifact red flags** (from the Phase 3 diff): new/changed install
  scripts; new dependencies (especially young, low-download ones); new
  binaries or high-entropy/obfuscated blobs; new network, subprocess, env,
  or filesystem-crawling code in a package that never needed it.
- **Known advisories/malware feeds** for the exact new version (`npm audit`,
  `osv-scanner`, GitHub Advisory DB — OSV includes the OpenSSF
  malicious-packages feed, so it catches known-malicious versions, not just
  CVEs).

## Phase 5 — Lockfile diff review

Reviewers skip lockfiles because they're machine-generated — which is exactly
why lockfile injection works. In the PR's lockfile diff, verify:

- **Scope**: only the expected package(s) and their legitimately re-resolved
  transitives changed. Unexplained mass churn or entries *removed* ⇒ finding.
- **Source URLs**: every changed entry resolves to the expected registry over
  HTTPS — never a random repo, gist, or unknown host, and never a different
  package name than the key.
- **Integrity hashes**: present and strong (e.g. sha512) for every changed
  entry; a changed hash for an *unchanged* version, or a hash-algorithm
  downgrade, is a red flag.
- **New transitives**: list what the bump newly pulls in; each is new attack
  and compatibility surface — give notable ones a quick Phase-4-style look.

## Phase 6 — Blast radius in this codebase

Findings only matter where the code is exposed to them:

- Direct vs transitive path: why is this package in the tree
  (`npm explain` / `pnpm why` / `go mod why` / equivalent)?
- Find every usage site: grep imports **including deep/subpath imports**
  (those are what exports-map changes break) and config-file references.
- Map **the APIs this codebase actually uses** against **the APIs that
  changed**. A huge changelog touching nothing you call is low risk; a
  one-line changelog rewriting the function in your request path is high
  risk. Name the specific files/functions affected in the report.
- If nothing imports it, say so — the right "review" may be removing the
  dependency instead of updating it.

## Phase 7 — Build and test against the PR branch

On the PR branch, with the lockfile installed **exactly as committed**
(frozen/ci-style install — this also enforces integrity hashes; disable
install scripts during audit installs where the tooling allows):

1. Install → build → type-check → lint → **full test suite** (ecosystem
   commands in `references/ecosystems.md`).
2. Check hosted CI status too (`gh pr checks <n>`) — but note that Dependabot
   workflows run with read-only tokens and without repo secrets, so a red
   integration job may be a token/secret quirk rather than a real failure;
   investigate before counting it either way.
3. Ask the coverage question explicitly: **do the tests actually exercise the
   code paths that use this dependency?** (Check the Phase 6 usage sites
   against test files/coverage.) If not, green tests prove little — run or
   propose a targeted smoke test of the affected feature, and say in the
   report what remains unverified.
4. Where relevant, check secondary regressions: bundle-size delta for
   frontend deps, image-size for Docker, startup time for CLIs.

## Phase 8 — Verdict report

Produce the report in the exact structure in
`references/report-template.md`. Verdict semantics:

- **MERGE** — every phase clean; evidence cited.
- **MERGE WITH CAUTION** — findings exist but are bounded and named (e.g.
  release is 2 days old: "safe to merge after <date>"; or coverage gap with
  a specific smoke test to run first). Always state the exact condition.
- **HOLD** — a compatibility problem to fix first (breaking API used in N
  places, failing tests, peer conflict) with the concrete fix or migration
  steps.
- **REJECT** — supply-chain red flags (unverifiable author, artifact/repo
  divergence, malicious-looking diff, lockfile tampering). Recommend pinning
  the previous version and, if warranted, reporting upstream.

Never soften a supply-chain finding into "caution" — anything in the REJECT
category stays REJECT until a human resolves it. When evidence is
incomplete (couldn't run tests, no changelog, no provenance support in the
ecosystem), the report must say what was **not** verified rather than
letting silence imply safety — an audit that quietly skipped a check is
worse than no audit, because it manufactures false confidence.
