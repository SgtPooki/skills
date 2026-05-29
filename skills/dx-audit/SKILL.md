---
name: dx-audit
description: Audit developer experience (DX/UX) of a library or tool across four surfaces — CLI, programmatic library/API, server/service, and GitHub Action — using measurable checks, clean consumer fixtures, and remediation-oriented scoring. Use when asked to audit DX, usability, onboarding, docs, examples, error handling, API ergonomics, or automation surfaces of a package you maintain.
allowed-tools: Bash, Read, Glob, Grep, Edit, Write, WebFetch
metadata:
  short-description: Measurable DX/UX audit across CLI, API, service, and Action surfaces
---

# DX Audit

Audit a repository for developer-facing DX/UX problems across up to four surfaces and produce a scored, evidence-backed remediation plan.

1. **CLI**
2. **Programmatic library/API**
3. **Server/service**
4. **GitHub Action**

Primary goals: minimize time to first success, minimize time to first output, cut cognitive load and task distance, improve machine discoverability, harden structured errors and observability — and report fixes with evidence, impact, and effort.

## When to invoke

- `/dx-audit` (no args) — auto-detect surfaces in the current repo and audit all detected ones.
- `/dx-audit cli|api|service|action [...]` — audit only the named surfaces.
- `/dx-audit <repo-path>` — audit a checkout elsewhere.
- Any request to "audit DX", "review usability/onboarding", "check API ergonomics", "is this package easy to consume", etc.

If the user names a focus (e.g. "prioritize onboarding friction and machine-readable output"), weight findings toward it but still score every detected surface.

## Audit tiers

Pick a tier up front and state it in the report — it determines which metrics are real vs `n/a`.

- **Static tier** (default for a quick pass): docs + source + contract inspection, plus any *cheap* live probe that needs no credentials or network mutation (`--help`, `--version`, parse-error exit codes, stream separation, `tsc` on examples). Do **not** populate metrics that require a run — TTFS, task success rate, error rate, startup time stay `n/a`. Don't print an `n/a`-riddled metrics table pretending to be a fixture run.
- **Fixture tier** (when credentials + time allow, or the user asks): everything in static, plus clean-room runs that produce real TTFS / TTFO / success-rate / example-reliability numbers — install the published tarball into a throwaway consumer, start the server and hit it, run the action via `act` or a real workflow.

Default to static unless the user says "full audit" or supplies credentials. Always name the tier in the report summary.

### Credentials for the fixture tier

Many real audits need a funded test identity. Before declaring a check un-runnable, look for one:

- Check the repo for a `.env` / `.env.example` / test-fixture key, and prefer a **testnet** (e.g. Filecoin **calibration**, Sepolia, a sandbox tenant) so runs cost nothing and mutate nothing real.
- Pass the secret explicitly rather than relying on ambient state, e.g. `source .env && filecoin-pin add file.txt --private-key "$PRIVATE_KEY_MAIN" --network calibration`.
- Never commit, echo, or write a private key into an artifact. Reference it by env-var name only in evidence.
- If no safe credential exists, stay in the static tier for that check and mark its run-dependent metrics `n/a` with a one-line reason.

## Workflow

Run these phases in order. Detail for each lives in `references/` — load the relevant file when you reach that phase.

### 1. Inventory — classify surfaces

Detect which surfaces exist. Signals:

| Surface | Detect via |
|---|---|
| CLI | `bin` field in `package.json`, shebang entrypoints, `commander`/`yargs`/`oclif`/`clap`/`cobra` deps, `cmd/` dirs |
| library/API | published package (`package.json`/`pyproject.toml`/`Cargo.toml`/`go.mod`), exported entry points, `exports` map, `.d.ts` |
| server/service | `openapi.*`, `.proto`, GraphQL schema, server entry (`listen(`, framework deps), `Dockerfile`, `docker-compose` |
| GitHub Action | `action.yml`/`action.yaml`, `.github/workflows` |

Mark each surface **present / absent / uncertain**. Derive the top 3–5 representative user tasks per present surface from README, docs, examples, and metadata. List assumptions explicitly.

### 2. Prepare fixtures

Test the **published artifact**, not the monorepo source — DX bugs hide in the gap between them.

- Library/API: `npm pack` (or equivalent) → install the tarball into a fresh throwaway consumer project → run the documented quickstart there.
- CLI: invoke the built/installed binary, not `src/`.
- Service: start via the documented command or `docker compose`; or connect to a provided base URL.
- Action: build a minimal fixture workflow.
- Always create **negative-path** fixtures too (invalid input, auth failure, transient failure/retry).
- Record exact commands, env vars, and timestamps as you go — they become the evidence trail.

See `references/harness.md` for ready-to-adapt command sequences.

### 3. Audit each detected surface

Walk the checklist for each present surface in `references/checklists.md`. For every check, capture: pass/fail, the evidence (command + output excerpt), and a 0/1/3/5 score. Measure the metrics defined in `references/metrics-and-scoring.md` (TTFS, TTFO, success rate, error rate, example reliability, discoverability, intervention rate).

Golden-path checks confirm the documented happy path works from a clean state. Negative-path checks confirm failures are understandable, structured, and safe.

### 4. Score

- Score each check **0/1/3/5** — those are the only legal values (see rubric in `references/metrics-and-scoring.md`). There is no 2 or 4; round to the nearest of 1 (partial) or 3 (acceptable).
- Use **`na`** for a check that is genuinely absent **or explicitly out of the maintainer's declared scope** — an `na` check is excluded and its weight renormalized away, so scoped-out work is never penalized. A whole absent surface is `na` too. **Guard against `na`-washing:** only mark `na` when the repo states the limit (e.g. "this Action targets Calibration only", "Node-only library"). A gap the maintainer *wants* but hasn't built is a low score, not `na`.
- Don't eyeball the rollup. Write the per-check scores into a `checks.json` and run the scorer:
  ```bash
  node <skill>/scripts/score.mjs checks.json --out "$OUT_DIR/scorecard.json"
  ```
  It computes category → surface → overall deterministically with the documented weights and the `na` renormalization. Input shape and category keys are documented at the top of `score.mjs` and in `references/metrics-and-scoring.md`.
- Attach evidence to every check scoring below 5.

### 5. Report

**Write artifacts outside the audited repo** so the audit never pollutes the target's working tree. Default `OUT_DIR` to a temp dir keyed by repo name, e.g. `OUT_DIR="${TMPDIR:-/tmp}/dx-audit/<repo-name>"`; `mkdir -p` it and report the path. Only write inside the repo if the user explicitly asks (and then under a path their `.gitignore` already covers).

Produce the artifacts below using the templates in `references/report-template.md`:

- `$OUT_DIR/report.md` — human-readable: summary (incl. **audit tier**), top findings, scorecard, per-surface detail, quick wins, high-impact fixes.
- `$OUT_DIR/scorecard.json` — machine-readable scores + metrics + findings (produced by `scripts/score.mjs`; schema in `references/metrics-and-scoring.md`).
- `$OUT_DIR/remediation-plan.md` — prioritized fixes.
- `$OUT_DIR/checks.json` — the per-check scores fed to the scorer (keep as the audit's reproducible input).

Each finding below score 3 must: explain the broken user journey, cite exact evidence, propose the smallest viable fix first then a hardening follow-up, and estimate impact (high/medium/low) and effort (small/medium/large). Prefer fixes that improve multiple surfaces at once.

Remediation priority order:
1. Unblock first success.
2. Make failures understandable.
3. Make automation safe and machine-readable.
4. Reduce task distance and doc gaps.
5. Improve observability and advanced scenarios.

## Reference files

- `references/checklists.md` — the prioritized P0/P1/P2 check tables for all four surfaces, with pass / excellent / failure criteria.
- `references/metrics-and-scoring.md` — metric definitions and targets, the discoverability formula, the 0/1/3/5 rubric, surface/category weights, score interpretation bands, and the `scorecard.json` schema.
- `references/report-template.md` — report skeleton plus a filled example, and per-surface test-case templates.
- `references/harness.md` — copy-adapt command harness for fixtures and a CI rollout pattern (fail on regression, not legacy debt).
- `scripts/score.mjs` — deterministic scorer: reads a `checks.json` of per-check 0/1/3/5/`na` scores, emits `scorecard.json` (category → surface → overall) with `na` renormalization. Run with `node`, no dependencies.

## Notes on thresholds

Numeric targets (TTFS budgets, ≥80% structured-output coverage, etc.) are **recommended operational defaults** synthesized from DevEx/API-usability literature and official CLI/HTTP/Action guidance — not universal law. If the repo documents a different support matrix, latency budget, or ergonomics tradeoff, honor that instead and note the deviation. For async protocols (WebSocket, MQTT, message queues), extend the server/service checklist with protocol-specific checks rather than forcing the HTTP rubric.
