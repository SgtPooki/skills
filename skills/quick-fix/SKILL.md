---
name: quick-fix
description: Solve one issue with the smallest correct diff, loop it through unit-test-quality, code-standards-review, and ponytail-review until clean, then show it in plannotator-review. Local only.
disable-model-invocation: true
---

# Quick fix

Input: an issue number or URL. Output: an uncommitted diff that every review gate passes, opened in plannotator-review.

The working tree is the deliverable. Commits, pushes, branches, PRs, and issue comments wait until the user asks for them.

## Steps

1. **Pin the tree.** Run `git status --short` and record every modified or untracked file; those belong to the user, and plannotator-review shows untracked files in its diff. If any exist, ask the user whether to set them aside, and leave them in place until they answer. Done when the tree holds only files the fix will change, or the user has said how to handle the rest.

2. **Read the issue and trace the code.** Read the issue body, comments, and definition of done, plus any commits or PRs it cites. Trace the flow end to end and grep every caller of each function you will change. Done when you can state the root cause in one sentence and map each definition-of-done line to the code that must change.

3. **Fix at the root with the smallest diff.** Change the one place every caller routes through. Code, copy, and comments the fix does not require keep their original form, so the diff shows only the fix: agreed user-facing copy stays word for word, and code you wrap or move keeps its original expressions. New comments use plain words. Done when the diff covers every definition-of-done line and nothing else.

4. **Prove the tests go red.** Add or update a test for each definition-of-done line, and carry every existing assertion whose behavior still exists into the new shape. Run the new tests against the pre-fix source (`git show HEAD:<file>` into place, then restore the fix) and confirm they fail. Then break each new branch of the fix in turn and confirm a test fails. Run the package's tests, type-check, and non-writing lint. Done when every new test has a named mutation that turns it red and all checks pass.

5. **Gate loop.** Run unit-test-quality, code-standards-review in quick mode, and ponytail-review against the diff. Resolve every finding, warning, concern, and tradeoff, then run all three again, because a fix for one gate can trip another. Done when a full pass of all three has nothing left to resolve. A concern only the user can decide is listed for them and ends the loop.

6. **Show it.** Only after step 5 is done, run plannotator-review. Report the root cause, the fix, each test with the mutation it catches, the gate results, and any concerns for the user to decide. Give each returned annotation a verdict (Confirmed, Partly, Not a bug, Intended) with code evidence, and change code once the user agrees. After any change, run step 5 again before reopening plannotator-review.
