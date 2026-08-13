# Research Basis

This reference records the standards behind `code-standards-review`. Treat it
as a source-backed menu, not a rigid checklist. Repo-specific rules and local
conventions still decide the review unless they conflict with security,
correctness, data-loss, or public compatibility.

## Source Map

| Area | Source | Why include it |
|---|---|---|
| Review mechanics | [Google Engineering Practices: What to look for in a code review](https://google.github.io/eng-practices/review/reviewer/looking-for.html) | First-party engineering guide covering design, functionality, complexity, tests, naming, comments, style, and docs. Useful because it frames review around overall codebase health instead of perfection. |
| Modularity | [Parnas, "On the Criteria To Be Used in Decomposing Systems into Modules"](https://dl.acm.org/doi/10.1145/361598.361623) and accessible [PDF copy](https://prl.khoury.northeastern.edu/img/p-tr-1971.pdf) | Canonical basis for information hiding: decompose around design decisions likely to change, not just execution steps. Included over generic "small files" advice because it gives a reasoned criterion for boundaries. |
| Architecture boundaries | [Alistair Cockburn, Hexagonal Architecture](https://alistair.cockburn.us/hexagonal-architecture) | Original ports-and-adapters source. Included as a boundary lens: keep application logic insulated from UI/database/external devices through ports and adapters. |
| Domain modeling | [Eric Evans, Domain-Driven Design Reference](https://www.domainlanguage.com/wp-content/uploads/2016/05/DDD_Reference_2015-03.pdf) and [Martin Fowler, Bounded Context](https://martinfowler.com/bliki/BoundedContext.html) | Evans defines domain, model, ubiquitous language, and bounded context; Fowler explains explicit interrelationships between contexts. Included because domain terminology and ownership are reviewable standards. |
| SOLID | [Robert C. Martin, Design Principles and Design Patterns](https://www.fil.univ-lille.fr/~routier/enseignement/licence/coo/cours/Principles_and_Patterns.pdf), [Principles of OOD](https://butunclebob.com/ArticleS.UncleBob.PrinciplesOfOod), and [Liskov/Wing behavioral subtyping](https://www.cs.cmu.edu/~wing/publications/LiskovWing94.pdf) | Useful as change-cost heuristics for responsibilities, extension points, substitutability, interface size, and dependency direction. Included as heuristics, not as acronym-driven blockers. |
| DRY | Andy Hunt and Dave Thomas, [*The Pragmatic Programmer*](https://pragprog.com/titles/tpp20/the-pragmatic-programmer-20th-anniversary-edition/) (Topic 9: DRY) | Included as "every piece of knowledge must have a single, unambiguous, authoritative representation", not "no repeated lines". Competes with local clarity and decoupling, so violations need a concrete change-cost consequence. |
| Testing strategy | [Google Testing Blog: Just Say No to More End-to-End Tests](https://testing.googleblog.com/2015/04/just-say-no-to-more-end-to-end-tests.html) and [Android testing strategies](https://developer.android.com/training/testing/fundamentals/strategies) | Both support a pyramid-shaped strategy: many small fast tests, fewer broader tests. Included because changed behavior should be covered at the cheapest reliable level. |
| Security | [NIST SSDF](https://csrc.nist.gov/projects/ssdf), [OWASP ASVS](https://owasp.org/www-project-application-security-verification-standard/), [OWASP Secure Code Review Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Secure_Code_Review_Cheat_Sheet.html), [SEI CERT Coding Standards](https://cmu-sei.github.io/secure-coding-standards/) | NIST gives lifecycle practices, ASVS gives verifiable application security requirements, OWASP code review covers human review of flaws tools miss, and CERT covers language-level secure coding. Included because security can override local convention. |
| Observability/runtime | [OpenTelemetry Documentation](https://opentelemetry.io/docs/), [OpenTelemetry homepage](https://opentelemetry.io/), and [Twelve-Factor App](https://12factor.net/) / [Logs](https://12factor.net/logs) | OTel standardizes traces, metrics, and logs; Twelve-Factor treats logs as event streams and config/backing services as deploy-time concerns. Included for reviewing new runtime paths and operator diagnosability. |
| API contracts | [OpenAPI Specification](https://swagger.io/specification/v3.2/) and [OpenAPI Initiative](https://www.openapis.org/) | OpenAPI formally describes HTTP API surface and semantics. Included because public contracts should be explicit and diffable where applicable. |
| Versioning | [Semantic Versioning 2.0.0](https://semver.org/) | SemVer requires a declared public API and maps incompatible, compatible feature, and compatible fix changes to major/minor/patch. Included for compatibility review, but only applies where the project declares or implies a public API. |
| Commit/change signaling | [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) | Provides machine-readable change intent and ties breaking-change notation to SemVer. Included as a DX/release automation convention only when the repo uses it. |
| UX/accessibility | [W3C WCAG 2.2](https://www.w3.org/TR/WCAG22/) and [WAI WCAG overview](https://www.w3.org/WAI/standards-guidelines/wcag/) | WCAG defines testable success criteria around perceivable, operable, understandable, and robust content. Included because user-facing UI changes can fail even when code is clean. |
| Module depth | John Ousterhout, *A Philosophy of Software Design* (2018) | Deep modules (small interface, large hidden functionality) vs shallow pass-throughs; complexity as change amplification, cognitive load, unknown unknowns. Included because "many small files" is a junior proxy the review should not reward. |
| Error design | Joe Duffy, ["The Error Model"](https://joeduffyblog.com/2016/02/07/the-error-model/) (Midori, 2016); Alexis King, ["Parse, Don't Validate"](https://lexi-lambda.github.io/blog/2019/11/05/parse-don-t-validate/) (2019); Ousterhout ch. 10 | Expected failures vs bugs are different designs; the best handling removes the error from the interface or makes illegal states unrepresentable. Included because error handling is interface design, not catch-block convention. |
| Wrong abstraction | Sandi Metz, ["The Wrong Abstraction"](https://sandimetz.com/blog/2016/1/20/the-wrong-abstraction) (2016) | Duplication is far cheaper than the wrong abstraction; deduplicate what is the same by necessity, not coincidence. Included to give the DRY competing-option teeth. |
| Test trustworthiness | Google Testing Blog: ["Change-Detector Tests Considered Harmful"](https://testing.googleblog.com/2015/01/testing-on-toilet-change-detector-tests.html) (2015), DAMP-over-DRY guidance; Mäntylä & Lassenius, "What Types of Defects Are Really Discovered in Code Reviews?" (IEEE TSE 2009) | A trustworthy suite fails only on real defects and survives refactors. ~75% of review findings are evolvability, not functional bugs — so tests carry correctness, and tests themselves need review. |
| Rollout safety | Martin Fowler, [ParallelChange / expand-contract](https://martinfowler.com/bliki/ParallelChange.html); Google SRE Workbook (canarying); *Accelerate* (Forsgren, Humble, Kim, 2018) | A correct end-state with an unsafe transition is a defect: backward compatibility with the deployed version, rollback including interim data, flags/canaries. Included because senior reviewers review the rollout as part of the diff. |
| Review process research | Bacchelli & Bird, "Expectations, Outcomes, and Challenges of Modern Code Review" (ICSE 2013); Bosu, Greiler & Bird, "Characteristics of Useful Code Reviews" (MSR 2015); SmartBear/Cisco study (Cohen, 2006); Sadowski et al., "Modern Code Review: A Case Study at Google" (ICSE-SEIP 2018) | Review's comparative advantage is design and knowledge transfer, not bug-finding; effectiveness collapses past ~400 changed lines; reviewer familiarity roughly doubles useful-comment density. Grounds the oversized-diff finding and the noise philosophy. |
| Agent maintainability | [agents.md](https://agents.md); Stripe, ["Minions"](https://stripe.dev/blog/minions-stripes-one-shot-end-to-end-coding-agents); *Building Evolutionary Architectures* (Ford, Parsons, Kua, 2017) on fitness functions | Agents are permanent new contributors: greppable unique names, context-window-sized modules, machine-checkable invariants over prose rules, concise accurate agent docs, deterministic fast tests as the agent's feedback loop. |

## Core Review Principles

### Repo Fit Beats Generic Purity

Google's review guide asks whether a change integrates well with the rest of
the system and improves overall code health. For this skill, that means local
docs, tooling, and adjacent patterns are evidence; generic principles are only
lenses. A review should not create churn by asking one diff to abandon the
project's established architecture.

Use a generic principle as a finding only when it predicts a concrete
consequence in this codebase: future changes must touch multiple independent
owners, a public contract becomes ambiguous, tests cannot isolate behavior, or
security/operability weakens.

### Modularity Is About Hidden Decisions

Parnas argues that modularization improves flexibility and comprehensibility
when modules hide design decisions likely to change. Prefer findings about
leaked decisions over findings about file size alone:

- database/vendor concepts leaking into domain objects;
- callers reaching into another module's internal state;
- shared utilities that centralize unrelated reasons to change;
- interfaces exposing methods clients do not need.

Competing option: organize solely by processing step or layer. That can be
simple for small systems, but it often scatters one volatile decision across
many modules. The review should ask what decision the changed module hides.

### Boundaries Need Contracts

Hexagonal architecture and DDD both support the same reviewable idea: code
outside a boundary should communicate through explicit ports, adapters,
commands, queries, events, schemas, or public APIs. Do not require hexagonal
ceremony everywhere. Do flag a change that bypasses an existing boundary or
imports another bounded context's internals.

Competing option: direct calls for simplicity. Accept direct calls when the
repo's local pattern uses them and the dependency is stable. Escalate when the
direct call crosses ownership, domain language, persistence, network, or public
contract boundaries.

### Domain Language Owns Meaning

Evans defines ubiquitous language as language structured around the domain
model within a bounded context. Review for term ownership:

- business invariants belong in the owning domain/module;
- vendor/API/database terms should be translated at the edge;
- the same word should not mean different things inside one context;
- different contexts may use different models if the boundary is explicit.

Competing option: reuse external DTOs everywhere. That is convenient, but it
couples business meaning to vendor shape and makes later replacement harder.

### SOLID And DRY Are Consequence Heuristics

SOLID is useful for spotting change-cost risks: multiple reasons to change,
extension by repeated edits, broken substitutability, oversized interfaces, and
dependencies pointing toward volatile details. DRY is about duplicated
knowledge, not repeated syntax.

Do not write findings like "violates SOLID" or "not DRY". Write the consequence:
"adding another storage provider will require editing this switch and three
callers" or "the same authorization rule now has two authoritative homes".

Competing option: premature abstraction. Prefer local duplication when the
duplicated code is likely to diverge, when the abstraction would be speculative,
or when the repo intentionally keeps variants separate.

### Modules Should Be Deep

Ousterhout's refinement of Parnas: a module's cost is its interface, its
benefit is what it hides. Review for depth, not size:

- shallow pass-through wrappers and one-class-per-step decompositions add
  names without hiding knowledge — do not reward them as "modular";
- splitting a coherent 100-line function into ten fragments can raise
  cognitive load; the metric is what a caller must know, not line count;
- complexity pulled downward (module absorbs the edge cases) beats
  complexity pushed up (flags, optional params, "callers must remember to").

Competing option: many small single-responsibility units. Accept when each
unit genuinely hides a separate volatile decision; flag when the same
knowledge leaks across all of them.

### Errors Are Interface Design

The best error handling removes the failure from the interface (define
errors out of existence), makes illegal states unrepresentable
(parse-don't-validate at I/O edges), and separates expected domain outcomes
from programmer bugs — bugs fail loudly, they are not caught-logged-continued.
Review the error taxonomy of a changed interface like any other contract.

Competing option: defensive catch-everything. Accept at true process
boundaries (request handlers, job runners); flag when it swallows bugs or
forces every caller to repeat recovery logic.

### The Data Model Outranks the Code

Schema, wire-format, and public-type mistakes carry their whole history with
them; they are 10–100× costlier to fix than code mistakes, and Hyrum's Law
freezes observable behavior once consumers exist. Review weight should skew
toward migrations, cardinality, lifecycle, and boundary types — a mediocre
algorithm on a crisp model refactors cleanly; the reverse does not.

### Rollout Safety Is Part of the Diff

A change is not just its end state: is the migration expand/contract
compatible with the currently deployed version, can it be flagged, canaried,
and rolled back — including data written in the interim, and what happens if
it stops halfway? Review the transition, not only the destination.

Competing option: "we deploy atomically". Accept for single-instance tools
with no persistent state; flag whenever data, multiple versions in flight,
or external consumers exist.

### Tests Should Cover Changed Behavior Cheaply — and Be Trustworthy

Google and Android testing guidance both favor many small, fast tests with
fewer broad tests. For review:

- changed domain rules need tests that fail when the rule is wrong;
- public APIs need contract or integration coverage;
- UI/user flows need appropriate interaction coverage;
- bug fixes should include regression tests when practical;
- untested vital behavior can be a blocker.

Review tests as the specification, not as coverage. The staff-level
questions: would this test fail if the feature were broken, or does it only
assert that mocks were called? Does it pin behavior callers rely on, or
implementation details that make the next refactor bleed (change-detector
tests)? Are failure paths tested? A flaky or over-mocked test is a finding —
it raises future change cost while providing no signal, and it poisons the
feedback loop humans and agents use to know they are done.

Competing option: only end-to-end coverage. Accept it for thin integration
changes where unit seams would be artificial, but flag it when failures become
slow, flaky, or hard to diagnose.

### Security Overrides Style

NIST SSDF, OWASP ASVS, OWASP secure code review, and CERT all treat security as
an engineering practice, not a post-hoc style issue. A local convention does not
excuse new injection risk, broken authorization, secret exposure, unsafe
deserialization, weak crypto, supply-chain weakening, or insecure defaults.

Use security findings only when the changed code creates or worsens a plausible
attack or misuse path. Name the path.

### Observability Is Part Of Runtime Correctness

OpenTelemetry standardizes telemetry signals; Twelve-Factor treats logs as
event streams. New runtime paths, background jobs, retries, queues, external
calls, and failure modes should be diagnosable through the repo's existing
observability style.

Competing option: avoid noisy logs/metrics. Accept silence for pure computation
or already-wrapped paths. Flag gaps when operators would not know a new path is
failing, retrying, dropping data, or violating an SLO.

### Public Contracts Need Compatibility Analysis

SemVer only works when a public API is declared. OpenAPI exists so HTTP API
surfaces and semantics can be described. For review:

- identify public APIs, CLIs, schemas, config, events, database migrations, and
  exported packages;
- check whether the change is backward compatible;
- require migration, deprecation, versioning, or release-note updates for
  breaking changes.

Competing option: "internal only". Accept it when the repo truly has no external
consumers. Escalate when downstream users, generated clients, persisted data, or
automation could break.

### UX, Accessibility, And DX Are Standards Too

WCAG gives testable accessibility criteria for user-facing web content. DX
standards are usually repo-specific: clear CLI flags, useful errors, docs, fast
feedback, and predictable setup. Review these only when the diff changes a user
or developer surface.

Competing option: defer polish. Accept deferral for hidden/internal changes.
Flag when users lose keyboard access, screen-reader semantics, error recovery,
or developers lose a documented workflow.

### Maintainers Include Agents

Agents are permanent new contributors: every onboarding affordance now pays
out on every task, not once per hire. Review for what breaks their (and new
humans') navigation and feedback loops:

- greppable, unique names — magic string construction and reused generic
  identifiers are invisible to search, the primary navigation tool;
- a change should be understandable from the file plus its colocated test,
  without holding four other files in mind;
- expectations encoded as machine-checkable invariants (lint rules,
  architecture tests, schema checks) rather than added prose in agent docs;
- `AGENTS.md`/`CLAUDE.md`/README accuracy: a diff that invalidates
  documented commands or layout without updating them is a finding;
- deterministic fast tests are the shared sensory organ — flakiness reads
  as broken code to an agent and trains humans to ignore red.

### Review Process Is a Quality Variable

Defect-detection effectiveness collapses beyond roughly 400 changed lines
per review session, and reviewer familiarity with the files roughly doubles
useful-comment density. Review's measured comparative advantage is design
and knowledge transfer (~75% of findings are evolvability), with correctness
delegated to tests and rollout controls. For this skill: an oversized,
unsplittable diff is itself reportable (a should-fix on review readiness),
and correctness demands flow into test-trustworthiness findings rather than
line-by-line bug hunts.

## Output Contract Rationale

Design choices behind the report contract:

- verdict first, so local gates can parse the result;
- a summary table, so silence does not imply compliance;
- findings with evidence, consequence, and fix;
- repo convention override, to prevent noisy generic advice;
- strict caps and a tradeoff section, to keep subjective issues out of PR
  comments;
- three verdict levels rather than a binary gate: `PASS WITH CONCERNS`
  preserves the binary merge decision (`FAIL` blocks) while still surfacing
  non-blocking review feedback for humans.
