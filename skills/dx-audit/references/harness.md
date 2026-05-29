# Command harness and CI rollout

Copy and adapt. The point of the harness is to test the **published artifact** under clean-room conditions, then preserve evidence. These commands are the **fixture tier** — they produce real TTFS/TTFO/success/error numbers. The static tier skips anything below that needs credentials or mutates state.

## Output dir (keep it out of the audited repo)

```bash
REPO_NAME="$(basename "$(git -C "$REPO" rev-parse --show-toplevel)")"
OUT_DIR="${TMPDIR:-/tmp}/dx-audit/${REPO_NAME}"
mkdir -p "$OUT_DIR"
```

Write `report.md`, `scorecard.json`, `remediation-plan.md`, `checks.json`, and any `evidence.json` / `task-timings.json` under `$OUT_DIR`. Never inside the target repo unless the user asks and the path is already gitignored.

## Credentials for fixture runs

Many CLIs/services need a funded identity. Find a safe one before declaring a check un-runnable, and prefer a **testnet** so runs are free and non-destructive:

```bash
# prefer a test key already in the repo, on a testnet
source "$REPO/.env"   # or .env.example / a documented test fixture
filecoin-pin add ./sample.txt --private-key "$PRIVATE_KEY_MAIN" --network calibration
```

Rules: reference secrets by env-var name only — never echo, commit, or write a key into an artifact. If no safe testnet credential exists, stay static for that check and mark its run-dependent metrics `n/a` with a reason.

## JS/TS library + CLI smoke harness

```bash
# clean install for CI-like conditions
npm ci

# package smoke test from the publishable artifact
npm pack
PKG_TGZ="$(ls -t *.tgz | head -n1)"
mkdir -p .tmp/consumer
cd .tmp/consumer
npm init -y >/dev/null 2>&1
npm install "../../${PKG_TGZ}"
# confirm the published entry point actually imports
node -e "import('<pkg-name>').then(() => console.log('import-ok')).catch(e => { console.error(e); process.exit(1); })"
cd ../..

# CLI smoke checks (built/installed binary, not src/)
node ./dist/cli.js --help
node ./dist/cli.js list --json | jq . >/dev/null && echo "json-ok"
```

For other ecosystems: `pip install dist/*.whl` into a fresh venv, `cargo package` + install, `go install ./...` from a clean module cache.

## Service smoke harness

```bash
docker compose up -d || true
# golden path
curl -fsS http://127.0.0.1:3000/healthz
# negative path — expect a structured error + request id, not HTML/stack trace
curl -i http://127.0.0.1:3000/nonexistent

# contract lint
spectral lint openapi.yaml
```

## GitHub Action harness

```bash
actionlint                                   # static lint
act -W .github/workflows/dx-audit.yml -j smoke || true   # local run

# remote verification when auth is available
gh workflow run dx-audit.yml
gh run view --log                            # preserve as evidence
```

## CI rollout pattern

Run on pull requests and manual dispatch, persist the scorecard artifacts, and **fail only on regression thresholds — never on legacy debt all at once**. Adoption stays realistic when the gate protects against backsliding rather than demanding instant perfection.

Good default gate — fail the build when **any** of:
- a new P0 regression appears, or
- overall score drops by more than 3 points vs the baseline branch, or
- example reliability drops below 95%.

This matches the DevEx evidence: target the highest-leverage friction, not vanity compliance numbers.

## Prioritized quick wins (highest ROI, usually improve multiple surfaces)

| Priority | Quick win | Why it is high impact |
|---|---|---|
| P0 | One **verified quickstart** per surface, run in CI | Stale/missing examples are a top API-learning obstacle; runnable examples are among the strongest usability aids |
| P0 | Standardize **structured errors** with actionable detail + correlation IDs | Cuts support burden; makes failures scriptable and debuggable |
| P0 | Add **machine-readable descriptions** — `--json`, OpenAPI, typed declarations, outputs metadata | Improves both human DX and tooling/automation |
| P0 | Fix **first-run discoverability** — top-level help, obvious entry points, permissions/auth docs, README examples | Shortens TTFS, lowers intervention rate |
| P1 | Add **health/readiness** + documented retry/idempotency behavior | Safer to integrate, easier to operate |
| P1 | **Action metadata + README completeness + permissions block** | Actions fail disproportionately from missing invocation context |
| P1 | Reduce **parameter friction** — replace long positional signatures with options objects/builders | Structural API decisions measurably influence error rates |
| P2 | Improve **logs and annotations** in Actions and CLI | Better feedback loops, especially on negative paths |

## Tooling reference

- `npm ci` — clean, reproducible installs for CI.
- `actionlint` — GitHub workflow/action static linting.
- `act` — run Actions locally.
- `gh workflow run` / `gh run view --log` — remote execution + downloadable evidence.
- `spectral lint` — OpenAPI linting (built-in OpenAPI ruleset).
- `jq` — validate/inspect `--json` CLI output.
