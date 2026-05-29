# Report template and test-case templates

## report.md template

```markdown
# DX Audit Report

## Summary
- Repository:
- Commit:
- Date:
- Surfaces audited:
- Overall score:
- Rating:
- Assumptions:

## Top findings
| Severity | Surface | Finding | Evidence | Recommended fix | Impact | Effort |
|---|---|---|---|---|---|---|

## Scorecard
| Surface | Score | Rating | TTFS | TTFO | Success rate | Error rate | Discoverability |
|---|---:|---|---:|---:|---:|---:|---:|

## Surface details

### CLI
- Strengths:
- Weaknesses:
- Failed checks:
- Commands run:

### Programmatic library/API
- Strengths:
- Weaknesses:
- Failed checks:
- Commands run:

### Server/service
- Strengths:
- Weaknesses:
- Failed checks:
- Commands run:

### GitHub Action
- Strengths:
- Weaknesses:
- Failed checks:
- Commands run:

## Quick wins
| Priority | Fix | Why it matters | Expected score lift |

## High-impact fixes
| Priority | Fix | Why it matters | Dependencies | Expected score lift |

## Evidence files
- scorecard.json
- evidence.json
- task-timings.json
```

## Filled example

```markdown
# DX Audit Report

## Summary
- Repository: acme-tools
- Commit: 1a2b3c4
- Date: 2026-05-29
- Surfaces audited: CLI, library/API, server/service, GitHub Action
- Overall score: 72
- Rating: Acceptable, but notable DX debt
- Assumptions: Local Docker available; published package tested from npm tarball fixture

## Top findings
| Severity | Surface | Finding | Evidence | Recommended fix | Impact | Effort |
|---|---|---|---|---|---|---|
| Critical | Server/service | Error responses unstructured and inconsistent | 400 returns plain text, 500 returns HTML, no request ID | Adopt RFC 9457 problem details + correlation IDs | High | Medium |
| High | CLI | `list` has no `--json` and mixes logs with data | `stdout` contains table + warnings | Add `--json`; move warnings to `stderr` | High | Small |
| High | Library/API | Quickstart omits a required env var; examples untested | Quickstart fails in clean fixture | Add env var to quickstart; run examples in CI | High | Small |
| Medium | GitHub Action | README omits permissions + failure-path behavior | Example workflow missing `permissions:` block | Document minimum permissions; add failure example | Medium | Small |

## Scorecard
| Surface | Score | Rating | TTFS | TTFO | Success rate | Error rate | Discoverability |
|---|---:|---|---:|---:|---:|---:|---:|
| CLI | 68 | Warn | 4m12s | 42ms | 0.83 | 0.22 | 71 |
| Programmatic library/API | 79 | Good | 11m08s | 3.4s | 0.89 | 0.14 | 77 |
| Server/service | 63 | Warn | 16m34s | 1.1s | 0.78 | 0.27 | 74 |
| GitHub Action | 76 | Good | 7m50s | 18s | 0.86 | 0.17 | 73 |

## Quick wins
| Priority | Fix | Why it matters | Expected score lift |
|---|---|---|---:|
| P0 | Add RFC 9457 error envelope with request ID | Makes all client failures actionable + parseable | +8 |
| P0 | Add `--json` to state/reporting CLI commands | Unblocks automation + support tooling | +6 |
| P0 | Run docs examples in CI | Prevents onboarding regressions | +5 |
| P1 | Add Action README permissions + failure examples | Reduces workflow setup confusion | +3 |
```

## Test-case templates

### CLI
```yaml
task_id: cli-basic-help
goal: discover command usage
command: "<cli> --help"
success_condition:
  - exit_code == 0
  - output contains description
  - output contains example
  - no stack trace
metrics: [ttfo_ms, help_length_lines]

task_id: cli-json-output
goal: consume output by automation
command: "<cli> list --json"
success_condition:
  - stdout is valid JSON
  - stderr contains no user logs on success
metrics: [parse_ok, fields_present]
```

### Library / API
```yaml
task_id: lib-quickstart
goal: complete first successful integration
steps:
  - create clean project
  - install published artifact
  - paste official quickstart
  - execute or type-check
success_condition:
  - exit_code == 0
  - expected output observed
metrics: [ttfs_seconds, undocumented_steps_count, type_errors]

task_id: lib-negative-validation
goal: inspect structured error behavior
steps:
  - call API/library with intentionally invalid input
success_condition:
  - stable error class/code
  - actionable message
metrics: [error_code_present, remediation_hint_present]
```

### Server / service
```yaml
task_id: server-health
goal: verify startup and readiness
steps:
  - start service
  - poll health endpoint or health RPC
success_condition:
  - healthy within startup budget
metrics: [startup_seconds, readiness_seconds]

task_id: server-problem-details
goal: verify structured errors
steps:
  - send invalid request
success_condition:
  - correct status
  - structured error format
  - request/correlation id present
metrics: [status_ok, machine_readable_error, human_actionable_detail]
```

### GitHub Action
```yaml
task_id: action-success
goal: run action in minimal workflow
steps:
  - create fixture workflow
  - execute locally or remotely
success_condition:
  - workflow/job succeeds
  - documented outputs available
metrics: [first_log_seconds, outputs_ok]

task_id: action-failure
goal: verify actionable failure path
steps:
  - omit required input or provide invalid input
success_condition:
  - failure is explicit
  - annotation/log explains fix
metrics: [annotation_present, masked_secrets_ok]
```
