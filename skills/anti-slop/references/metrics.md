# Metrics: what slopcheck measures and why

Both metrics come from SlopCodeBench (arXiv:2603.24755), which found they
degrade in ~3 out of 4 agent coding trajectories while pass rates alone show
nothing wrong. They measure *structure*, independently of correctness.

## Structural erosion

**Definition:** the fraction of the codebase's total complexity mass that
lives in high-complexity functions.

```
mass(f)  = CCN(f) × √NLOC(f)         # the paper's formula: complexity dominates size
erosion  = Σ mass(f) for f with CCN > 10   ÷   Σ mass(f) for all f
```

(v1 of this script used `CCN + NLOC`; v2 matches the paper's `CC × sqrt(SLOC)`
so numbers are comparable with SlopCodeBench results. Baselines recorded by v1
are auto-upgraded on the first passing v2 check.)

**Intuition:** two codebases can have identical total complexity, but one
spreads it across thirty focused functions while the other concentrates it
in three god-functions. The second is eroded: every future change must be
threaded through those same overloaded functions, which is exactly how
agents end up doing cascading rewrites and giving up on structure.

**Reference points:** human open-source Python repos average ~0.34 erosion;
agent-written code in the study averaged ~0.70. If your check reports
erosion above ~0.5 and rising, you are on the agent-typical trajectory.

**CCN > 10** as the "high complexity" cutoff follows the long-standing
radon/McCabe convention. The hard per-function ceiling of **15** for *new*
offenders is deliberately forgiving — the point is to stop branch-piling
before a function reaches CCN 30+, where refactoring becomes genuinely
risky.

## Duplication (verbosity proxy)

**Definition:** the fraction of normalized source lines that appear in
duplicated blocks of ≥ 6 consecutive similar lines (string/number literals
and whitespace are normalized away, so "copy-paste then tweak the constant"
still counts).

The paper's full verbosity metric also includes 137 ast-grep rules for
wasteful Python constructs; slopcheck approximates it with the clone
component because clones are language-agnostic and are the dominant,
actionable signal. The Step-4 self-review sweep in SKILL.md covers the
rule-based patterns (dead code, unnecessary variables, redundant rebuilds)
manually.

**Reference points:** agent code in the study was 2.3× more verbose than
human baselines, and only 18 of 473 human repos exceeded the *median* agent
verbosity. Duplication rising checkpoint-over-checkpoint is the signature
of copy-paste variation instead of extraction.

## The gates and their tolerances

| Gate | Default | Rationale |
|---|---|---|
| New function over CCN | 15 | Catch branch-piles early, while extraction is still cheap. Pre-existing offenders are grandfathered so the skill is usable on messy legacy code. |
| Grandfathered growth | +2 CCN | A function already over the ceiling may not keep growing — validation runs showed a CCN-16 function can otherwise branch-pile to 50+ behind the grandfather clause. |
| Erosion delta vs baseline | +0.02 | The study measured agents adding ~0.026 erosion *per checkpoint* — this gate blocks exactly that per-iteration creep while tolerating measurement noise. The baseline ratchets forward on every passing check, so this is a true per-iteration budget. |
| Duplication delta vs baseline | +0.005 | Study agents added ~0.014 verbosity per checkpoint; 0.005 allows small legitimate repetition (test fixtures, boilerplate) but fails a pasted block. |
| Duplication absolute cap | +50 clone lines | Ratio tolerance scales with repo size (0.5% of a 25k-line repo would allow ~125 pasted lines per iteration, forever, because the baseline ratchets). The absolute cap keeps the gate meaningful in large codebases. |
| Dead code delta vs baseline | 0 | Unused imports/variables and redefinitions (ruff `F401,F811,F841`, or pyflakes) are the residue of abandoned iterations; they may be removed, never added. |

## When overriding is legitimate

Loosening any gate is a **human** decision: flags looser than the defaults are
ignored unless the environment variable `SLOPCHECK_ALLOW_OVERRIDE=1` is set.
(Validation runs on SlopCodeBench caught an agent quietly passing
`--erosion-tolerance 0.20` at the hardest checkpoint — that is exactly the
rationalization this policy exists to block.) If you believe an override is
warranted, state the case in your final message and let the human set the
variable. Legitimate cases a human may approve:

- **Irreducibly branchy code:** large `match`/dispatch over a wire protocol,
  opcode interpreter, exhaustive enum handling. CCN is high but each branch
  is trivial. Consider a dispatch table first; if that genuinely doesn't
  fit, `--max-ccn 25` with a stated reason is honest.
- **Generated or vendored code:** exclude it via `.slopcheck/ignore` — one
  glob or path prefix per line, matched against the scan-root-relative path
  (e.g. `docs/api` for a generated typedoc site). This is the one exclusion
  mechanism agents may use freely, since hiding generated code makes the
  metrics more honest, not less.
- **Test files with intentionally repetitive cases:** either accept a higher
  `--dup-tolerance` for the test directory or run the check on production
  code only. Do not let production-code duplication hide behind this excuse.

What is *not* legitimate: raising tolerances because the deadline is now, or
because "it still passes the tests". Passing tests is precisely the signal
the study showed to be blind to this failure mode.

## Interpreting a failing check

- **Erosion rose + one function flagged:** classic branch-pile. Extract each
  logical branch group into a named helper; the parent becomes a dispatcher.
- **Duplication rose, erosion flat:** copy-paste variant. Find the clone
  pairs (the report lists files), extract the shared function with the
  varying parts as parameters.
- **Both rose:** you likely retrofitted a requirement that broke a structural
  assumption. Revisit the extend-vs-restructure decision you skipped —
  see refactor-triggers.md.
- **Erosion high but flat since baseline:** pre-existing debt. Not your gate
  failure, but mention it to the user as observed tech debt.
