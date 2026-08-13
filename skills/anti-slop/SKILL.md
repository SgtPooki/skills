---
name: anti-slop
description: >-
  Quality gate for iterative coding work that prevents "code slop" — the
  measurable degradation (god-functions, copy-paste duplication, branch piles)
  that coding agents accumulate when they repeatedly modify their own code.
  Use this skill whenever you are modifying or extending code that already
  exists — adding a feature, handling a new requirement, fixing a bug in a
  codebase, doing a second or later pass on code you wrote earlier in the
  session — and ALWAYS before declaring any non-trivial coding task done.
  Also use when the user mentions refactoring, tech debt, code quality,
  maintainability, "clean this up", or complains that code has gotten messy
  or bloated over time.
---

# Anti-Slop: check your work before deciding you're done

## Why this exists

Research on iterative coding (SlopCodeBench, arXiv:2603.24755) measured what
happens when coding agents repeatedly extend their own code across evolving
requirements. The results are sobering, and they describe *you*:

- Structural erosion (complexity concentrating in a few giant functions)
  increased in **77%** of agent trajectories; duplication/verbosity in **75%**.
- Agents accumulated this debt **5–6× faster** than human open-source
  developers, and produced code 2× more eroded and 2.3× more verbose.
- The failure mode is invisible to you in the moment: each individual edit
  looks locally reasonable ("just add one more branch here"), passes the
  tests, and *feels* done. The rot only shows up in the trajectory.
- Crucially: agents given quality-aware prompts wrote cleaner *initial* code
  but degraded at the same rate. **Good intentions do not work. Measurement
  does.** That is why this skill uses a script with hard gates, not vibes.

The two failure patterns to internalize:

1. **Branch-pile extension.** A new requirement arrives and you graft it onto
   the existing structure as another `if`/`elif`/flag inside an
   already-long function, because that is the minimal diff. Repeat five
   times and `main()` is 240 lines with CCN 69 (a real measured example).
2. **Copy-paste variation.** A new case resembles an existing one, so you
   duplicate the block and tweak it rather than extracting the shared logic.

## The workflow

### Step 1 — Baseline before you touch anything

Before your first edit to existing code, record where quality stands:

```bash
pip install lizard --break-system-packages   # once, if not installed
python <skill-path>/scripts/slopcheck.py baseline <project-dir>
```

This snapshots erosion, duplication, and dead-code counts so the gates can
catch you making things *worse*, not just punish you for pre-existing mess
(pre-existing offenders are grandfathered — but may not grow further). If you
are writing a brand-new project, run the baseline right after your first
working version.

Baseline is a **once-per-project** action: it refuses to overwrite an existing
baseline, because the baseline advances automatically every time a check
passes. If it says a baseline already exists, that is the correct state —
just proceed to your work and the check.

### Step 2 — At every new/changed requirement, decide: extend or restructure?

This is the moment agents get wrong. Before writing code for a new
requirement, answer explicitly (in a sentence or two of your reasoning):

- Does this requirement break an assumption baked into the current structure?
  (e.g., "there is only one language", "input is always a file", "there are
  two modes") If yes, **restructure first, then add** — retrofitting the
  assumption via flags and branches is how branch-piles form.
- Is this the second or third variant of something that already exists?
  If yes, **extract the shared shape first** (interface, dispatch table,
  strategy), then add the new variant as data/plug-in, not as a sibling copy.
- Only when the requirement genuinely fits the existing structure is a pure
  extension the right move.

Restructuring before adding feels slower. It is cheaper than the cascading
rewrite you will otherwise face two requirements from now — and unlike you,
the check in Step 3 will notice.

See `references/refactor-triggers.md` for the specific smells and the
decision rules, with before/after examples.

### Step 3 — Gate before declaring done (mandatory)

You are not done when the tests pass. You are done when the tests pass AND
the quality gate passes:

```bash
python <skill-path>/scripts/slopcheck.py check <project-dir>
```

The gates (defaults; see `references/metrics.md` for definitions and tuning):

- No function may **newly** exceed CCN 15.
- Grandfathered offenders (already over 15 at baseline) may not grow more
  than +2 CCN.
- Erosion (share of complexity mass, CCN×√NLOC, in CCN>10 functions) must
  not rise more than 2 points over baseline.
- Duplication (lines in structural clones) must not rise more than 0.5
  points over baseline.
- Dead code (unused imports/variables, redefinitions — via ruff/pyflakes)
  must not increase.

On PASS the baseline advances automatically (ratchet), so these tolerances
are per-iteration budgets, not cumulative slack.

If the check FAILS: refactor — extract helpers from the flagged functions,
unify the duplicated blocks, delete dead code — re-run your tests to confirm
behavior is unchanged, then re-run the check. Do not report the task as
complete, and do not present results to the user as final, while the gate is
failing.

Do NOT try to pass the gate by loosening it: flags looser than the defaults
are ignored by design (a human can permit them with SLOPCHECK_ALLOW_OVERRIDE=1),
and `baseline` will not let you re-baseline away accumulated damage. If a gate
genuinely cannot be met (e.g., a parser function that is irreducibly branchy),
say so explicitly in your final message with the number and the reason, and let
the human decide — rather than silently skipping or negotiating with the check.

### Step 4 — Self-review sweep (2 minutes, catches what metrics can't)

Metrics catch concentration and duplication; they miss waste. Skim your full
diff (not just the last edit) and check:

- Dead code: unused imports/variables/functions/parameters left behind by
  your own earlier iterations; commented-out code; obsolete branches for
  requirements that changed under you.
- Wasteful constructs: unnecessary intermediate variables, rebuilding a list
  where a filter would do, guards for impossible cases, wrapper functions
  that only forward arguments.
- Drift: docstrings/comments/names that describe what the code did two
  iterations ago, not what it does now.
- Would a fresh implementation of the *current* spec look materially simpler
  than what you have? If clearly yes, your structure has drifted — spend the
  time to converge it now, or (in unattended runs) flag the divergence to
  the user honestly.

## Quick reference

| When | Command |
|---|---|
| Start of session / first working version | `slopcheck.py baseline <dir>` |
| Curious mid-task | `slopcheck.py report <dir>` |
| Before saying "done" (mandatory) | `slopcheck.py check <dir>` |

Script supports ~20 languages via lizard (Python, JS/TS, Go, Rust, Java,
C/C++, C#, Ruby, PHP, Swift, Kotlin...). Clone detection is built in — no
extra dependency. Use `--json` for machine-readable output.

Details: `references/metrics.md` (what the numbers mean, thresholds, when to
override) · `references/refactor-triggers.md` (smells, extend-vs-restructure
decision rules, worked examples).
