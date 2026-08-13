# anti-slop

A quality gate that stops coding agents from rotting a codebase while they
iterate on it.

## The goal

This skill is **not** about winning a benchmark. It exists because of a
measured, reproducible failure mode: when a coding agent repeatedly extends
its own code — requirement after requirement, session after session — it
accumulates "slop": god-functions grown one `elif` at a time, copy-paste
variants of existing blocks, and dead code from abandoned iterations. Every
individual edit looks reasonable and passes the tests; the rot only shows in
the trajectory. SlopCodeBench (arXiv:2603.24755) measured this across 11
models: structural erosion rose in ~80% of agent trajectories and verbosity
in ~90%, while human-maintained repos stayed flat.

The paper's key negative result: telling the agent to write clean code
(quality-aware prompting) improves the *first* draft but does not change the
degradation *slope*. This skill's bet is that a **measured gate with a
failing exit code** does — the agent is not asked to care about quality, it
is blocked from declaring "done" until a script says the structure didn't
get worse.

## How it's meant to be used

Day to day, you shouldn't think about it:

1. The skill lives in your skills collection and auto-triggers whenever the
   agent modifies existing code (and always before declaring a non-trivial
   task done).
2. The agent records a baseline once per project (`slopcheck.py baseline .`),
   makes an explicit extend-vs-restructure decision at each new requirement,
   and must pass `slopcheck.py check .` before finishing. On every passing
   check the baseline ratchets forward, so the tolerances are per-iteration.
3. Optionally — and recommended, because a skill is advisory while a hook is
   mechanical — install the Stop hook so the gate physically blocks the turn
   from ending while the check fails (see below). Skill-firing reliability is
   the single biggest real-world weakness of the advisory-only setup.

The intended outcome: you come back to a repo weeks later and `main()` is
still a dispatcher, not a CCN-51 pile.

## Evidence that it works

Validated 2026-07-28/29 on the real SlopCodeBench harness (mini_swe agent,
Qwen3.6-35B on local vLLM), three arms × two problems, plus an adversarial
methodology review by Cursor, Codex, and Gemini. Using the benchmark's
official metrics:

| Arm | cfgpipe final erosion | code_search final erosion |
|---|---|---|
| control (`just-solve`) | 0.571 | 0.863 |
| paper's quality prompt, no gate | 0.686 | 0.489 / 0.621 (two seeds) |
| **this skill's gated workflow** | **0.000** | **0.000** |

The gate arm stayed flat on every checkpoint; both non-gate arms eroded —
replicating the paper's "prompting doesn't work" finding and isolating the
gate as the differentiator. Out-of-band metrics no prompt mentioned (max
nesting depth 4 vs 14, cognitive erosion 0.45 vs 0.93) confirm genuinely
better structure, not threshold gaming. Cost: mean strict test pass rate
dropped ~9–16 pts, concentrated where refactor loops competed with a hard
checkpoint. Caveats: one local 35B model, 1–2 seeds per cell — strong pilot
evidence, not statistical proof. Full report: `antislop-scbench-report.html`
(kept locally).

The same experiment caught the agent **negotiating with the gate** — passing
`--erosion-tolerance 0.20` and re-running `baseline` mid-task. That is why
slopcheck v2 has the anti-gaming policy below.

## What's in the skill

| File | Purpose |
|---|---|
| `SKILL.md` | The workflow the agent follows (baseline → decide → gate → sweep) |
| `scripts/slopcheck.py` | The measured gate: erosion (mass = CCN×√NLOC, per the paper), structural clone detection, dead-code count (ruff/pyflakes), hard CCN ceiling |
| `scripts/stop-hook.sh` | Optional Claude Code Stop hook that blocks ending the turn while the gate fails |
| `references/metrics.md` | Metric definitions, thresholds, when overriding is legitimate |
| `references/refactor-triggers.md` | Extend-vs-restructure decision rules with worked examples |

### The gates (v2)

1. No function may **newly** exceed CCN 15.
2. Grandfathered offenders (over the ceiling at baseline) may not grow more
   than +2 CCN — legacy debt must shrink, not grow.
3. Erosion may not rise more than +0.02 over the (ratcheting) baseline.
4. Duplication may not rise more than +0.005 (ratio) nor +50 clone lines
   (absolute — keeps the gate meaningful in large repos where 0.5% is a lot).
5. Dead code (unused imports/variables, redefinitions) may not increase.

### Per-project excludes

Put path prefixes or globs (one per line) in `.slopcheck/ignore` to keep
generated/vendored code out of the scan (e.g. a typedoc `docs/api` site).
The file is read from the baseline's directory, so it also applies when the
same repo is scanned via a worktree or copy.

### Anti-gaming policy (v2, deliberate)

- Flags looser than the defaults are **ignored** unless a human sets
  `SLOPCHECK_ALLOW_OVERRIDE=1`. Stricter is always allowed.
- `baseline` refuses to overwrite an existing baseline (that would launder
  accumulated slop into accepted history). The baseline advances only via
  passing checks; a human reset requires `--force` + `SLOPCHECK_ALLOW_RESET=1`.

### Installing the Stop hook (recommended)

Add to `~/.claude/settings.json` (or a project's `.claude/settings.json`):

```json
{
  "hooks": {
    "Stop": [
      { "hooks": [ { "type": "command",
        "command": "bash /ABSOLUTE/PATH/TO/skills/anti-slop/scripts/stop-hook.sh" } ] }
    ]
  }
}
```

The hook is opt-in per project: it only acts in directories that contain
`.slopcheck/baseline.json`, exits silently everywhere else, and never blocks
twice in a row (loop safety via `stop_hook_active`).

## Known limitations / roadmap

- Clone detection is line-window hashing (≥6 normalized lines); renamed-
  identifier and sub-window clones slip through. AST-aware detection is the
  planned upgrade.
- Dead-code gate covers Python only (ruff/pyflakes); other languages rely on
  the Step-4 self-review sweep.
- The extend-vs-restructure step is still prose — it improves decisions when
  followed but nothing measures it.
- Proving generalization needs: seeds, more of SlopCodeBench's 20 problems,
  a frontier-model replication, and a harness-enforced-gate arm (the Stop
  hook is that enforcement for real sessions).
