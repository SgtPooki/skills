# Greenfield: Project Startup Standards

Use this reference when the target is a new or young project rather than a
diff: bootstrapping a repo, or auditing an early repo's foundations. Findings
use the same severity model and report shapes as `report-contract.md`; a
missing day-one item is a finding, a deferred item present too early is a
tradeoff or finding (premature complexity).

Ordering principle: day one is for ratchets — standards that only hold if
they have held from commit 1 — and for things 10× more expensive to retrofit.
Everything else waits for its trigger. Sources: four-way independent research
convergence on DORA/Accelerate, Google eng-practices and SRE, Stripe
engineering, agents.md, Nygard ADRs, Ousterhout, Metz; see `research.md` for
the principle-level sources.

## Day-one non-negotiables

1. **README quickstart that CI executes.** Three commands max: setup, test,
   run. If CI runs the quickstart it cannot rot.
2. **One-command dev environment.** Pinned toolchain (`mise`/devcontainer/
   `.tool-versions`), `.env.example`, universal verbs (`make dev|check|test`
   or script equivalents). Setup friction is hours for humans and hard
   failure for agents.
3. **Formatter + linter + strict types, enforced in CI from commit 1.**
   Zero-config formatter; maximum strictness on day one — retrofitting
   strictness onto 50k lines is a quarter of work. Tooling is the real style
   guide; humans never litigate what machines enforce.
4. **CI runs exactly what developers run locally**, green-required to merge.
5. **Test harness with one fast, hermetic exemplar test.** No network, no
   real clock, colocated with the code. Day-one coverage is irrelevant; the
   copyable pattern is the point.
6. **`AGENTS.md` (mirrored/symlinked as `CLAUDE.md`).** ~100 lines max:
   commands, layout map ("where would X live"), the few rules a linter
   cannot enforce, pointer to the exemplar module. Concise beats
   encyclopedic — stale megadocs hurt agents more than no docs.
7. **Lockfile + dependency policy.** Committed lockfile, update automation
   with a cooldown window for non-security bumps, stated bias against
   trivial dependencies.
8. **Schema-first boundaries from the first boundary.** Migrations-as-code
   from the first table, OpenAPI/protobuf/JSON Schema from the first
   endpoint, parse-don't-validate types at every I/O edge. Data-model
   mistakes outlive code mistakes.
9. **Review norms as config.** `CODEOWNERS`, PR template with
   Purpose/Risk/Rollout/Test-evidence sections, branch protection, small-PR
   norm (review effectiveness collapses past ~400 changed lines).
10. **ADR habit: `docs/adr/0001-...` the day the first real decision lands.**
    ADRs are append-only; starting late means the most important decisions
    are the ones never recorded.
11. **Structured logging convention declared once**, used by the first real
    code path so every later path copies it.

## Set up when first needed (immediately when the trigger fires)

| Trigger | Artifact |
|---|---|
| First deploy | Feature flags, written rollback procedure, expand/contract migration rule in PR template |
| First production traffic | Runbook, dashboards, one leading-signal alert |
| First DB | Migration tool + expand/contract discipline |
| First external API consumer | Versioning/deprecation policy (Hyrum's Law starts running) + breaking-change CI check |
| Second similar component | Scaffold/golden-path generator, extracted from the first, not designed up front |
| First flaky test | Quarantine mechanism + zero-tolerance norm the same week — flakiness teaches everyone (and every agent) to ignore red |
| First repeated agent/human mistake | A lint rule or architecture test — never another paragraph of prose |
| Second package | Nested `AGENTS.md` + identical package skeleton |

## Deliberately deferred

- **Microservices / plugin architectures / generic platform layers** — wait
  for the third concrete variant; premature flexibility is coupling with
  extra ceremony, and service boundaries blind agents and debuggers alike.
- **Coverage thresholds** — early gates breed assertion-free tests; review
  test trustworthiness instead.
- **Comprehensive architecture docs** — ADRs + AGENTS.md + code; the big doc
  rots.
- **Vendor-abstraction layers "in case we switch"** — hide decisions *likely*
  to change (Parnas); vendor switches usually are not. An ADR recording the
  lock-in is the cheap insurance.
- **Monorepo build systems / heavy infra** — until the pain is real.
- **Custom style rules beyond stock formatter/linter** — stock configs are
  what every human and model already knows.

## Greenfield report

Audit mode: score the day-one list as the checklist (present / missing /
deferred-appropriately), findings for missing ratchets, tradeoffs for
judgment calls, and a prioritized next-actions list. Scaffold mode: create
the day-one artifacts, then emit the same report showing what was set up and
what was deliberately deferred with triggers.
