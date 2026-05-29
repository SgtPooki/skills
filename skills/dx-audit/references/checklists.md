# Surface audit checklists

Priorities: **P0** = blocks or seriously harms first success; **P1** = significant friction; **P2** = polish. Score each check 0/1/3/5 (see `metrics-and-scoring.md`). Thresholds are recommended operational defaults — defer to repo-documented policy when it exists.

## CLI

Synthesized from the Command Line Interface Guidelines (CLIG); ripgrep is a positive doc-richness exemplar.

| Priority | Check | Pass criteria | Excellent criteria | Failure example |
|---|---|---|---|---|
| P0 | Help and entry behavior | `tool --help`, `tool -h`, and `tool subcmd --help` all work; missing required args show concise guidance, not a stack trace | Also supports `tool help`; help opens with 1–2 runnable examples and a docs/support link | Bare command hangs, crashes, or prints raw parser internals |
| P0 | Exit codes | Success returns `0`; ≥4 common failure modes map to stable, documented non-zero codes | Error codes listed in docs and covered by tests | Every failure returns `1` with no distinction |
| P0 | Standard streams | Primary + machine-readable output on `stdout`; logs and errors on `stderr` | Sampled commands preserve pipe behavior under redirection tests | JSON mixed with log lines on `stdout` |
| P0 | Scriptable output | List/inspect/report commands support `--json`; rich-table commands offer a line-safe `--plain` | ≥80% of state-reporting commands have structured output + schema examples | Human formatting breaks piping to `jq`/`grep` |
| P0 | Non-interactive safety | Mutating/destructive commands support non-interactive args; dangerous ops require TTY confirmation or explicit `--force` in non-TTY | Also `--dry-run` for all destructive/bulk ops | CI blocks on a prompt, or deletes without confirmation |
| P1 | TTY-aware behavior | Prompts only when `stdin` is a TTY; file commands support `-` for stdin/stdout | Color/progress/prompt adapt cleanly to TTY vs non-TTY | Prompt appears inside a pipe or redirect |
| P1 | Responsiveness and progress | First feedback `<100ms` for local commands, or before a network request; tasks >2s show progress | ETA/animated progress for long tasks; configurable timeouts | Appears frozen for seconds, then fails |
| P1 | Error quality | ≥90% of sampled errors explain what failed, why, and the corrective next action | Unexpected failures have a debug mode + bug-report path | `Error: EACCES` with no guidance |
| P2 | Flag consistency | Standard meanings preserved for `-h/--help`, `--version`, `-q/--quiet`, `--json`, `--dry-run` | Common aliases consistent across subcommands | `-h` means "host" on one subcommand, "help" elsewhere |
| P2 | Discoverability extras | Complex CLIs document shell completions, config locations, examples, FAQs | Completion install is one documented command | Advanced commands discoverable only by reading source |

## Programmatic library / API

Grounded in API-usability research (learnability, examples, mental-model fit, discoverability, error prevention, method placement, parameter structure, typing-as-documentation). TS/JS checks shown; map to equivalent typed-surface checks in other languages.

| Priority | Check | Pass criteria | Excellent criteria | Failure example |
|---|---|---|---|---|
| P0 | Clean install + first-use | Fresh consumer fixture installs the **published** artifact and completes the documented quickstart with no undocumented prerequisites | TTFS ≤ 15 min for the primary task; examples run in CI | README works only from monorepo source, not the published package |
| P0 | Public surface typing | TS/JS: declarations exist, public exports resolve, consumer fixtures type-check under supported module-resolution modes | Public API fully typed; examples compile under Node and bundler targets | Runtime exports exist but types or `exports` map are broken |
| P0 | Quickstart and examples | One copy/paste quickstart, one common-task example, one error-handling example, one advanced scenario per top-level surface | Examples are runnable smoke tests in CI | Docs show signatures but no realistic usage |
| P0 | Error model | Public errors are structured + documented; invalid input, auth failures, transient failures, retries are distinguishable | Typed error classes/codes are stable and shown in examples | Consumers must parse free-text messages to branch logic |
| P1 | Discoverability and naming | Top 10 tasks completable from docs/autocomplete within ≤3 lookup hops, no source reading | Task-to-symbol distance avg ≤2 hops; discoverability ≥80 | Users must guess terminology or grep source for the entry point |
| P1 | Parameter ergonomics | No public call needs >3 required positional params; no >2 consecutive same-type scalar params without an options object | Options objects/builders for complex calls; consistent param order | Function takes 6 positional strings/booleans |
| P1 | Mental-model fit | Core methods live on the objects/modules users expect; architecture-heavy patterns mitigated with aliases/factories/docs | Most common task starts from one obvious entry object/module | Functionality present but hidden behind a non-obvious factory |
| P1 | Conceptual docs | Point-of-entry docs explain concepts, object relationships, lifecycle, design intent — not just signatures | Includes migration and architecture diagrams | API reference exists but no overview of how pieces fit |
| P2 | Backward compat + migration | Versioning policy exists; deprecations marked; breaking changes have migration docs | Automated deprecation warnings or codemods | Silent break in a minor release |
| P2 | Cross-runtime clarity | Supported runtimes, module systems, browsers, polyfill needs are explicit | Matrix-tested support table published | Claims broad compatibility but works in one environment only |

## Server / service

Based on OpenAPI, RFC 9457 (problem details), RFC 9110 (status semantics), Kubernetes probes, gRPC health/status, GraphQL introspection/errors, OpenTelemetry semantics; GitHub and Stripe as real-world rate-limit/idempotency exemplars.

| Priority | Check | Pass criteria | Excellent criteria | Failure example |
|---|---|---|---|---|
| P0 | Machine-readable contract | HTTP publishes OpenAPI; GraphQL supports introspection in appropriate envs; gRPC publishes proto/health | Contract linked from landing docs and validated in CI | Users must reverse-engineer routes |
| P0 | Status / protocol correctness | Endpoints use correct HTTP/gRPC status semantics; `201` includes `Location`; `204` has no body | ≥95% protocol-conformance on sampled endpoints | `200 OK` for creation, validation failure, and server error alike |
| P0 | Structured errors | HTTP errors use `application/problem+json` or documented equivalent; GraphQL/gRPC expose codes/details; all errors carry correlation/request ID | 100% of negative-path tests have stable machine-readable codes + actionable detail | HTML error page or raw stack trace to API clients |
| P0 | Retry and idempotency | Critical writes are idempotent or accept idempotency keys; transient failures document retry/backoff; `Retry-After` used appropriately | Rate-limit headers / quota info exposed and documented | Client cannot safely retry a POST after timeout |
| P1 | Health, readiness, startup | Health endpoint or gRPC health service exists; readiness distinct from liveness when backend deps matter | Startup probe/readiness docs + sample deploy config | Single "ping" returns healthy while dependencies are down |
| P1 | Auth and permission clarity | Auth methods, required scopes/claims, least-privilege examples, common auth errors documented | Sandbox/test credentials or a no-cost local path | 401/403 with no hint which scope is missing |
| P1 | Observability | Logs/metrics/traces use consistent names; include route/method/result and correlation IDs | OpenTelemetry semantic conventions or equivalent | Failures uncorrelatable across logs and traces |
| P1 | Pagination and rate limits | Collection endpoints document pagination model, defaults, caps, rate-limit behavior | Generated examples show pagination + backoff handling | List endpoint silently truncates results |
| P2 | Versioning and deprecation | API versioning policy explicit; deprecations have sunset guidance | Changelog + compatibility timeline machine-readable | Breaking changes land without migration notice |
| P2 | Onboarding path | One "hello world" and one authenticated request completable end-to-end from docs | TTFS ≤ 20 min including auth setup | First request needs hidden config or support intervention |

## GitHub Action

Grounded in GitHub's metadata, workflow-command, logging, and authoring docs; `actions/checkout` and `docker/build-push-action` as scenario-rich exemplars. Note: outputs are capped at **1 MB per job / 50 MB per workflow run**, and JS actions for all hosted runners should be pure JavaScript (no external binaries).

| Priority | Check | Pass criteria | Excellent criteria | Failure example |
|---|---|---|---|---|
| P0 | Metadata completeness | `action.yml` exists; `name` + `description` present; inputs/outputs declared and described; runtime explicit | Input defaults, deprecations, output semantics precise and tested | Action exists but only README describes inputs |
| P0 | README completeness | Covers what it does, required/optional inputs + outputs, secrets, env vars, permissions, ≥1 working example workflow | Multiple scenario examples + troubleshooting section | Marketplace page exists but invocation is unclear |
| P0 | Failure semantics | Invalid inputs fail with actionable messages; failure path emits targeted error annotations or grouped logs | Negative-path tests verify exact failure messaging | Exits non-zero with no context |
| P1 | Runtime/platform compatibility | JS/composite actions claiming hosted-runner support are tested on Ubuntu, Windows, macOS; Docker-action platform limits stated | Support matrix + runner minimum versions documented | Claims "cross-platform" but silently Bash/Linux-only |
| P1 | Inputs and validation | Required inputs validated in code, not just metadata; lowercase input IDs; safe defaults | Inputs include examples + edge-case docs | `required: true` set but missing input yields a cryptic runtime failure |
| P1 | Logs and annotations | Uses `::group::`, `::notice::`, `::warning::`, `::error::`, optional `::debug::`, secret masking | Compact on success, rich on failure | Long runs dump unstructured logs and leak secrets |
| P1 | Permissions and security | Minimum `GITHUB_TOKEN` permissions documented; warns about untrusted input where relevant | Example workflows include `permissions:` blocks | Implicitly assumes broad token scopes |
| P2 | Output contract | Outputs stable, documented, size-safe; consumable without scraping logs | Output examples verified in a sample workflow | Users must parse job logs to get values |
| P2 | Testability | Local lint + smoke workflows exist; example workflow runnable with minimal setup | Local `act` path + remote workflow smoke tests | Only maintainers can validate releases |
| P2 | Marketplace polish | Branding configured; examples easy to browse | "Common scenarios" section comparable to top public actions | Bare, hard-to-scan listing |
