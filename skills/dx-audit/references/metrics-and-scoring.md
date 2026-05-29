# Metrics and scoring model

## Core metrics

| Metric | Definition | Formula | Default target | Notes |
|---|---|---|---|---|
| TTFS | Time to first success | `median(t_success − t_start)` across primary tasks | CLI ≤ 5m; API ≤ 15m; service ≤ 20m; action ≤ 10m | "Success" = first end-to-end task completes as documented |
| TTFO | Time to first output | `median(t_first_meaningful_feedback − t_invocation_start)` | CLI local < 0.1s; networked CLI shows feedback before request; action shows first meaningful log in first executable step; service reaches health in documented startup budget | Visible feedback, not task completion |
| Task success rate | Representative tasks completed without intervention | `successful_tasks / total_tasks` | ≥ 0.85 | Use a fixed task matrix |
| Error rate | Failed attempts per task attempt | `failed_attempts / total_attempts` | ≤ 0.20 | Count retries caused by confusing UX |
| Example reliability | Doc examples that execute successfully | `passing_examples / executable_examples` | ≥ 0.95 | Examples should be smoke-tested |
| Discoverability score | How easy it is to find + use the right capability | see formula below | ≥ 80/100 | Especially for API and service |
| Time-to-onboard | Time to complete top 3 tasks with no external help | `p75(sum(task_times_1..3))` | ≤ 45m | Holistic onboarding signal |
| Intervention rate | Tasks needing source reading, maintainer help, or undocumented steps | `tasks_needing_intervention / total_tasks` | ≤ 0.10 | Very strong DX signal |
| Change failure rate | Released changes causing a failure needing remediation | `failed_changes / total_changes` | team-specific; trend down | DORA-style delivery metric |
| Mean time to recovery | Avg recovery time after a release-caused failure | `sum(recovery_durations) / incidents` | team-specific; trend down | Matters for service + action |

## Discoverability formula

```text
DiscoverabilityScore =
    0.25 * EntryPointClarity      # is there one obvious starting point?
  + 0.25 * TaskDistance           # avg inverse hops to solve top tasks
  + 0.20 * ExampleCoverage        # runnable examples for common tasks + failures
  + 0.15 * Searchability          # findable with natural words from docs/help
  + 0.15 * MachineDiscoverability # --json, OpenAPI, introspection, types, outputs, metadata
```

Each component scored 0–100.

## Scoring rubric

Score each check **0 / 1 / 3 / 5** — these are the only legal values (no 2 or 4). The scorer rejects anything else.

| Score | Meaning |
|---|---|
| 0 | Missing, broken, or actively harmful |
| 1 | Partial, inconsistent, or undocumented |
| 3 | Acceptable default; works for most users |
| 5 | Strong, tested, low-friction |
| `na` | Genuinely absent, or explicitly out of the maintainer's **declared** scope |

### When to use `na` (and when not to)

`na` excludes a check and renormalizes the remaining weights at its level — so it never raises or lowers the score, it just removes the slot. Use it only when the repo *states* the boundary:

- ✅ Action README says "educational demo, Calibration testnet only" → its cross-network / production-platform checks are `na`.
- ✅ Library declares "Node-only" → browser-runtime checks are `na`.
- ❌ A capability the maintainer wants but hasn't built → that's a **0 or 1**, not `na`. Marking unbuilt-but-desired work `na` is score-washing.

A whole absent surface is `na`; the scorer renormalizes surface weights across the present surfaces.

## Weights

Surface weights (default overall score):

| Surface | Weight |
|---|---:|
| CLI | 25 |
| Programmatic library/API | 30 |
| Server/service | 30 |
| GitHub Action | 15 |

Category weights inside each surface:

| Category | Weight |
|---|---:|
| Onboarding and discoverability | 25% |
| Correctness and safety | 25% |
| Error handling and observability | 20% |
| Machine actionability and automation | 20% |
| Documentation and examples | 10% |

## Calculation

```text
CheckScoreNormalized = CheckScore / 5
CategoryScore        = weighted average of normalized checks in that category
SurfaceScore         = Σ(CategoryScore * CategoryWeight)
OverallScore         = Σ(SurfaceScore * SurfaceWeight)
# If a surface is absent, mark N/A and renormalize remaining surface weights.
```

## Interpretation

| Overall score | Interpretation |
|---|---|
| 90–100 | Outstanding DX/UX |
| 75–89 | Strong, with targeted friction |
| 60–74 | Acceptable, but notable DX debt |
| 40–59 | Poor; onboarding/support costs likely elevated |
| <40 | Critical; interface redesign or major remediation warranted |

## Scoring with `scripts/score.mjs`

Don't roll up by hand. Record per-check scores in a `checks.json`, then:

```bash
node <skill>/scripts/score.mjs checks.json --out "$OUT_DIR/scorecard.json"   # also prints a table
node <skill>/scripts/score.mjs checks.json --quiet                            # JSON to stdout only
```

`checks.json` input shape — group checks by surface and by **canonical category key** (`onboarding`, `correctness`, `errors`, `automation`, `docs`); unknown category keys are warned and ignored:

```json
{
  "repo": "name",
  "commit": "sha",
  "surfaces": {
    "cli": { "categories": {
      "onboarding":  [ { "check": "help", "score": 3, "priority": "P0" } ],
      "correctness": [ { "check": "exit_codes", "score": 1 } ],
      "errors":      [ { "check": "streams", "score": 5 } ],
      "automation":  [ { "check": "scriptable_json", "score": 0 } ],
      "docs":        [ { "check": "examples", "score": 3 } ]
    } },
    "server_service": "na"
  }
}
```

Each check is equally weighted inside its category; categories use the weights above; surfaces use the surface weights above. `na` (per-check or whole-surface) is excluded and renormalized. The scorer maps each surface score to a status (`pass` ≥75 / `warn` ≥60 / `fail` <60) and a rating band, and computes `overall_score`. Keep `checks.json` in `$OUT_DIR` as the reproducible audit input.

## scorecard.json schema

```json
{
  "repo": "string",
  "timestamp": "ISO-8601",
  "surfaces": {
    "cli":            { "score": 0, "status": "pass|warn|fail|na", "metrics": {}, "findings": [] },
    "library_api":    { "score": 0, "status": "pass|warn|fail|na", "metrics": {}, "findings": [] },
    "server_service": { "score": 0, "status": "pass|warn|fail|na", "metrics": {}, "findings": [] },
    "github_action":  { "score": 0, "status": "pass|warn|fail|na", "metrics": {}, "findings": [] }
  },
  "overall_score": 0,
  "top_risks": [],
  "quick_wins": [],
  "assumptions": [],
  "commands_run": []
}
```

Each entry in a surface's `findings` array should carry: `check`, `priority`, `score`, `evidence` (command + output excerpt), `fix` (smallest viable first), `hardening` (follow-up), `impact` (high/medium/low), `effort` (small/medium/large).
