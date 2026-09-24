---
name: unit-test-quality
description: Use when reviewing, validating, or grading unit tests in a PR, a diff, or a test file. Judges whether existing or proposed unit tests are trustworthy, flags hard violations by rule ID, and applies extra checks when the tests were written by an AI agent. Not for writing tests, and not for integration or end-to-end tests.
---

# Unit test quality

Judge unit tests the way a skeptical reviewer would: could this test fail if the behavior broke, and would a reader trust it? Every finding cites a rule ID below. The evidence and sources behind each rule live in [research.md](research.md); read it when a rule is challenged, not on every run.

Scope is Feathers' definition: a test that touches a database, the network, or the filesystem, that cannot run alongside other tests, or that needs environment setup is not a unit test and is out of scope here (flag it under N1 and move on).

## Steps

1. **Collect the targets.** List every test file in scope (the diff, the PR, or the path given). For each, identify the system under test and its language. Load the matching override from `languages/` if one exists; it can add, sharpen, or exempt a core rule but never removes one.
2. **Read the code under test first.** Note its public API, its side-effect boundaries (network, storage, chain, clock), and, for a PR, the changed lines. You cannot judge an oracle without knowing what the code is supposed to do.
3. **Apply the NEVER rules to every test, then N11 to the implementation diff.** One hit is a blocking finding. A test may appear under several IDs; when rules overlap, cite the most specific one and mention the others in the same bullet. A skipped test is cited under N10 only; do not evaluate its other rules until it runs.
4. **Apply the ALWAYS rules to every test.** A miss is a required change.
5. **If the PR contains AI-authored tests, or you cannot tell, apply the process rules.**
6. **Apply the contested rules as warnings only.** Never block on them.
7. **Report.** Done when every test in scope has been checked against every rule and each finding names a rule ID, a `file:line`, and a concrete fix.

## Report format

- **Verdict:** `PASS`, `PASS WITH WARNINGS`, or `FAIL`. Any NEVER hit is `FAIL`.
- **Blocking:** one bullet per NEVER hit: rule ID, `file:line`, what the test does, the fix. N11 bullets cite the implementation file.
- **Required:** one bullet per ALWAYS miss, same shape. Process-rule misses state the evidence needed (a command and its output, a CI link, a red run) instead of a code fix.
- **Warnings:** contested-rule findings, marked optional.
- **Would fail if:** one line per test naming a mutation of the code under test that it would catch, or the words cannot fail, followed by the count of tests that cannot fail (see A6).

Assume the author is competent. Explain why, briefly, on the first occurrence of each rule; after that, cite the ID only.

## NEVER rules

Hard guardrails. The positive target follows each one. Signals locate a suspect; a finding blocks only when the target is violated. A signal whose target still holds (for example, a module-level variable that every test overwrites before reading) is a warning with the rule ID, not a block.

**N1. No network, database, real filesystem, or environment setup.** Target: in-process only, with fakes at the boundary.
Signals: HTTP or RPC clients, sockets, DB drivers, reads of files the test did not create, `process.env` reads beyond test-injected values, containers or servers started in setup, README steps before the unit suite. A per-test temp directory the test creates, fills, and removes is hermetic and is not N1; report it under A8 when a fake would be cheaper.

**N2. No sleeps or fixed delays as synchronization; no unawaited async.** Target: fake timers, or await an explicit signal.
Signals: `sleep`, `setTimeout` as a wait, `time.Sleep`, `await delay(n)`, retry loops on a clock, unawaited promises, `expect(p).resolves` without `await`, assertions inside callbacks that may never run.

**N3. No uncontrolled time, randomness, collection order, or float equality.** Target: injected clock and seed; sort before comparing; tolerance for floats.
Signals: `Date.now()`, `new Date()`, `time.Now()`, `block.timestamp` reaching the system under test, including through an injected clock that wraps the real one, whether or not the result is asserted. A pre-existing call the PR only moved is a warning, not a block; `Math.random()`, unseeded RNG, `uuid()`; array equality on a set, map, or unordered query; `==` on floats; timing windows tight enough to fail under load.

**N4. No order dependence or shared mutable state.** Target: every test passes alone, in random order, in parallel.
Signals: module-level or static state written by tests; singleton mutation without reset; a test reading what another wrote; numbered test names; shared fixtures mutated across tests; mocks not restored between tests; shared temp paths.

**N5. No assertion-free tests and no weak-only assertions.** Target: at least one assertion that pins a specific, spec-derived value or relationship.
Signals: zero `expect` or `assert` calls; the strongest assertion is `toBeDefined`, `toBeTruthy`, `not.toThrow`, `isinstance`, `len > 0`, `assert.NoError` on a function with output; a large snapshot as the only check; `expect(true).toBe(true)`.

**N6. No expected value derived from the code under test.** Target: literals or hand-derived values from the spec. When the copied value comes from a special case in production code, cite N11 instead.
Signals: `expect(f(x)).toEqual(f(x))`; expected computed by calling the same module or a private helper; an inline re-implementation of the same algorithm; expected values visibly pasted from a first run.

**N7. No mocking or spying on the system under test; no asserting that a stub returned what the test told it to return.** Target: the real unit runs, doubles only at its boundaries.
Signals: `vi.mock('./module-under-test')`, `spyOn(sut, ...)`, `vm.mockCall` on the contract under test, partial mocks of the claimed method; an asserted value that traces to a `mockReturnValue` or `thenReturn` in the same test.

**N8. No interaction-only assertions when an outcome is observable.** Target: assert the return value, state change, event, or error; verify a call only at a side-effect boundary where nothing else can be observed.
Signals: the only assertions are `toHaveBeenCalledWith`, `verify(...)`, `AssertCalled`, or call order; every argument of every call pinned when one matters.

**N9. No conditional logic, loops, or hand-rolled exception handling in a test body.** Target: straight-line code with literal inputs and outputs; table-driven cases where the table holds literals.
Signals: `if`, `switch`, `for`, `while`, ternaries, `try/catch`; expected values built by computation; empty or broad `catch`; Go `recover` without asserting the panic value. Exempt: iterating a literal table (`test.each`, `for _, tc := range cases`, `parametrize`, or a `for` over a literal array of cases inside one test); prefer the framework form so a red run names the row.

**N10. No skipping, disabling, commenting out, weakening, or deleting a test to reach green.** Target: fix the implementation; quarantine only with a linked issue.
Signals: `it.skip`, `xit`, `describe.skip`, `.only`, `t.Skip`, `@Disabled`, `#[ignore]`, `pytest.mark.skip` without an issue link; commented-out assertions; early `return`; in a diff: removed `expect` lines, `toEqual` loosened to `toBeDefined`, deleted test files, lower test count than base, `--passWithNoTests` added.
For a diff, list every removed assertion and name the removed production behavior that retires it. An assertion dropped while reshaping a test table, splitting a test, or merging tests, whose behavior still exists, is an N10 hit: carry it into the new shape.

**N11. No test special-casing in production code.** Target: a general implementation that the tests happen to exercise.
Signals in the implementation diff: literals matching test expected values; `if input == <fixture value>`; lookup tables keyed on test inputs; `NODE_ENV === 'test'`; `isTestMode`; setters added only for tests; `"pytest" in sys.modules`.

**N12. No testing private methods or reaching into internals.** Target: exercise the public API; if a private helper needs its own tests, it wants to be its own unit.
Signals: reflection into privates, `(obj as any).privateFn()`, `#private` bypass, tests named after private helpers, assertions on private fields.

## ALWAYS rules

**A1. One behavior per test, named by scenario and expected outcome.**
Signals of a miss: a second call to the system under test after an assertion; names like `testFoo`, `works`, `handles edge cases`, or the bare function name; "and" in a name; unrelated assertion groups separated by re-setup.

**A2. Assert a specific observable outcome through the public API.**
Return value, state, emitted event, revert, or error. Down-rank assertions on internal structure or call order.

**A3. Keep the fixture visible; DAMP over DRY for arrange and assert.**
Signals of a miss: an asserted value never set in the test or a clearly named inline helper; reliance on builder or `beforeEach` defaults; a fixture file whose contents decide the assertion but are not named in the test; helpers three levels deep before the input appears. Builders and factories for value objects are fine.

**A4. Cover boundaries and error paths for the behavior under test.**
Empty, null, zero, negative, max, off-by-one, malformed, out of order, and the thrown or rejected branch. A PR that adds a guard needs a test that trips it.

**A5. Tests in a PR exercise the changed lines.**
Map diff hunks to tests. A miss: tests that never call the changed function, cover none of the changed branches, or mock away the changed code.

**A6. Every test can fail.**
For each test, name the mutation of the code under test that would make it go red (return a constant, invert the condition, skip validation). If you cannot, the test is a finding. For a PR, prefer evidence of a red run before the implementation.

**A7. Real implementation first, then fake, then stub; mock only unmanaged out-of-process dependencies.**
Signals of a miss: a mock for a value object, pure function, or cheap in-process collaborator; every dependency mocked by default. Warn, not block, on `vi.mock` of a third-party package without a project-owned adapter.

**A8. Fast.**
A single test above roughly 100 ms without justification is a finding. Sleeps and I/O are already N2 and N1; A8 covers what remains, such as heavy per-test fixture construction or large loops.

**A9. Arrange, act, assert, with one act.**
Given-When-Then is the same shape. Interleaved setup, calls, and assertions; a second act nested inside an assertion argument; or many bare assertions where a failure would not say which condition broke, are a miss.

## Process rules for AI-authored tests

Apply when the PR says tests were generated, when the author is a bot, or when you cannot tell.

**P1. Evidence that tests ran, not a claim.** Require the command and captured output or a CI link. Cross-check the test count against the base branch.

**P2. Tests derived from the spec, not from the implementation in the same context.** A miss: implementation and tests authored together with no red-run evidence; test comments that paraphrase implementation internals rather than requirements. Recommend a separate session or agent for the tests.

**P3. Delta coverage and surviving mutants, never a coverage percentage.** A PR justified by "raises coverage to N%" is a finding. When a mutation tool is available (Stryker, cargo-mutants, mutmut, gambit for Solidity), report the surviving mutants on changed lines; when it is not, do A6 by hand.

**P4. Generated tests clear hard gates before human review.** Build, pass on repeated runs, and add coverage or kill a mutant. A test that adds no coverage and kills no mutant is a deletion candidate.

## Contested rules

Report as warnings. The literature disagrees; see research.md section 4.

- **C1.** Mocks of cheap in-process collaborators. Classical school flags it; London school does not. Warn.
- **C2.** Assertion count. Enforce one behavior (A1), never a count.
- **C3.** Repeated literal setup across tests. Fine. Warn only when bodies differ by one value and a parameterized case would be clearer.
- **C4.** Assertion Roulette by counting. Warn only for many unexplained assertions about different behaviors; a good name or comment is sufficient explanation.
- **C5.** Mutation score threshold. Surface a few survivors; never demand a number.
- **C6.** Test length. Soft signal only.
- **C7.** Property-based tests for pure functions. Encourage; review the property itself for tautologies like `x == x`.

## What this skill does not do

It does not write tests, and it does not judge integration or end-to-end suites. Rules that popular guidance repeats but the evidence does not support, such as one assert per test or any coverage percentage, are listed in research.md section 5 and are not applied.
