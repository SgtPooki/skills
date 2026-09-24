# unit-test-quality

A skill that validates the quality of unit tests. Point an agent at a PR, a diff, or a test file and it returns a verdict with findings keyed to rule IDs.

## Layout

```
skills/unit-test-quality/
  SKILL.md          # the rules and the review procedure; this is what the agent loads
  research.md       # evidence behind every rule, with quotes, effect sizes, and a bibliography
  languages/
    typescript.md   # sharpened signals and exemptions for Vitest
    go.md           # table-driven tests, t.Parallel, httptest
    solidity.md     # Foundry/Hardhat: vm.warp, expectRevert, fork tiers
```

## Rule tiers

| Tier | Count | Effect of a hit |
|---|---|---|
| NEVER (N1 to N12) | 12 | Blocking. Verdict is `FAIL`. |
| ALWAYS (A1 to A9) | 9 | Required change. |
| Process for AI-authored tests (P1 to P4) | 4 | Required change when the tests were generated. |
| Contested (C1 to C7) | 7 | Warning only. |

Every rule in `SKILL.md` has a matching section in `research.md` with the sources behind it, an evidence grade (E1 quantitative to E4 single opinion), and a tag saying whether the rule is unchanged since before 2023, amplified by evidence about LLM-written tests, or new to the agent era.

## Adding a language

Create `languages/<language>.md`. It may add signals, sharpen a core rule's detection for that ecosystem, or list exemptions. It cannot remove a core rule. Keep the core rule IDs so findings stay comparable across languages.

## Challenging a rule

Open a PR against `research.md` with the counter-evidence. Rules the evidence does not support are already listed in its section 5; a rule moves tiers when the evidence for it changes, not when it is inconvenient.
