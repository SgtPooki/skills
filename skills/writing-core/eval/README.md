# Skill eval harness

`writingcheck.py --selftest` tests the linter. Nothing tested the skills. A
prose edit to a `SKILL.md` changes what agents write, and every existing check
passes identically before and after — green means "the checker still works",
not "the skill still works".

This harness closes that gap for the edits worth worrying about: changes to
`writing-core/SKILL.md`, which is loaded on every drafting task and inherited
by all five scenario skills.

## Run

```bash
python3 run.py                                    # HEAD vs working tree
python3 run.py --model gemma4:31b-q8              # different local model
python3 run.py --report-only                      # re-grade saved outputs
```

Needs `omp` and a local model server. Outputs land in `runs/` as
`<probe>.<arm>.md` and are overwritten each run; they are gitignored.

`--model` must be provider-qualified (`ollama/<name>`), and the runner refuses
anything that is not a local provider unless you pass `--allow-remote`. A bare
model name is not a pin: when omp cannot match it, it falls back to the
configured default provider, which here is a shared remote endpoint. A full
run is two generations per probe, which is not traffic to send somewhere by
accident.

Exit code is 1 when a mechanical regression fires, so this can gate a commit.

## Arms

`baseline` is `skills/writing-core/SKILL.md` as committed at HEAD; `candidate`
is the working tree. Scenario skills come from the working tree in both arms,
so the diff isolates the core edit. With nothing uncommitted the arms are
identical — a useful self-check that the harness is measuring what it claims.

## What it grades

The probe set exists to catch one specific failure: a rule scoped to one
scenario leaking into the others. So the probes are split. Four informative
artifacts (README, PR body, ADR, release note) assert BLUF *holds*; three
marketing artifacts (cold email, landing page, X thread) assert the
awareness-stage opening is *allowed*. An edit that helps one group at the
other's expense shows up as a row that moved.

Per output: `writingcheck.py` error count, word count, and one signal —
whether a BLUF probe opened with buildup, or whether a marketing probe led
with the product name in its hook.

## What it does not grade

Whether the prose is any good. The mechanical signals are proxies chosen
because they are cheap and hard to game, not because they are sufficient.
A passing table means "nothing obviously broke"; read the diffs:

```bash
for f in runs/*.baseline.md; do diff -u "$f" "${f%.baseline.md}.candidate.md"; done
```

Local models are also noisier than the models these skills actually run
under. Treat a single moved row as a prompt to look, not a verdict — rerun
before concluding anything from one sample.

## Adding probes

One JSON object per line in `probes/`:

```json
{"id": "readme", "scenario": "writing-docs", "bluf": true, "prompt": "..."}
{"id": "cold-email", "scenario": "writing-marketing", "bluf": false, "product": "widget-cli", "prompt": "..."}
```

`bluf` picks the signal to grade. `product` is required when `bluf` is false —
it is the string the hook must not lead with.
