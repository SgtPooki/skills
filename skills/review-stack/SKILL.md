---
name: review-stack
description: Run the full review stack on code (reflect, anti-slop, code-standards-review or review-pr, anorth-review, unit-test-quality, ponytail-review) plus the writing stack on any prose, and merge the results into one report.
disable-model-invocation: true
---

# Review stack

Input: a PR number or URL, a branch, or nothing (the local diff). Output: one merged report. This skill routes to other skills; each one owns its own rules, so read and follow each skill rather than restating it here.

## Steps

1. **Pin the target and mode.** Name the exact diff: PR, branch against its merge base, or staged plus unstaged changes. Pick the mode:
   - **self**: code you or the user wrote in this session and have not yet sent for review. Edits are allowed.
   - **review**: someone else's change, or any PR. Report only; change no code.

   Done when the diff and mode are stated in one line.

2. **Reflect (self mode only).** Run `reflect` on the diff and apply its edits. Carry its unconfirmed product decisions into the report. Then run `anti-slop` against the result. Done when both have finished and the diff is final for this pass.

3. **Run the review lenses.** Run each against the same diff:
   - `review-pr` for a PR, `code-standards-review` otherwise (quick mode in self mode, gate mode in review mode). Its verdict is the report's verdict.
   - `anorth-review`, loading only the themes the diff matches. When it dispatches theme subagents, give them the strongest Claude model (`claude-fable-5-1`), never haiku or sonnet.
   - `unit-test-quality` when the diff touches tests.
   - `ponytail-review`, always last, so it sees what reflect settled on.

   Launch lenses in parallel subagents when the harness supports it. Done when every lens has returned a report.

4. **Check the prose.** Collect the prose the diff adds or changes (comments, docstrings, docs, README) and the prose this run will publish (PR description, review comments). Run `writing-core` with the matching scenario skill, then the prose sweep in `anti-slop`, then `my-voice` last. Done when every prose item has passed all three, or has a finding.

5. **Merge.** Deduplicate findings that point at the same location and cause, and tag each surviving finding with every lens that raised it. Resolve overlaps this way:
   - A test finding from both `anorth-review` and `unit-test-quality`: keep the unit-test-quality rule ID.
   - A `ponytail-review` cut that undoes a structure `reflect` chose on purpose: list it as a question for the user, not a fix.
   - A finding only one lens raised stays as that lens wrote it.

   Done when no two findings share a location and cause.

6. **Report.** Lead with the verdict and the diff reviewed. Then findings ranked most severe first, each with location, lens tags, and a fix. Then questions for the user: product decisions from reflect, design questions, and ponytail/reflect conflicts. End with ponytail's `net:` line. In self mode, list what reflect and anti-slop already changed. Commits, pushes, and GitHub comments wait until the user asks.
