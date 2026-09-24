# TypeScript and JavaScript override

Load for `*.test.ts`, `*.spec.ts`, `*.test.js`, `*.spec.js`, and anything under `__tests__/`. Assumes Vitest; adapt matcher names for Mocha, Node test runner, or others.

## Sharpened signals

- **N2.** Every `expect` on a promise is awaited: `await expect(p).rejects.toThrow(...)`, never a bare `expect(p).rejects`. Async tests use `async` functions, not `done` callbacks. Timers are faked with `vi.useFakeTimers()` and advanced explicitly.
- **N4.** When a file uses `spyOn` or module mocks (`vi.mock`), they are restored between tests: `vi.restoreAllMocks()` in `afterEach`, or `restoreMocks: true` in config. Local `vi.fn()` stubs created inside a test have nothing to restore and are exempt. `vi.restoreAllMocks()` restores only `vi.spyOn` spies (Vitest 3 and later); a `mockReturnValue` set on a `vi.fn` declared in `vi.mock` needs `mockReset()` in `afterEach` or `mockReturnValueOnce`. Shared files under `os.tmpdir()` are a finding. These two are the only order-dependence mechanisms with evidence in JavaScript (Hashemi 2022; JS-TOD 2025).
- **N5.** Weak matchers to flag when they are the strongest assertion: `toBeDefined`, `toBeTruthy`, `toBeFalsy`, `not.toThrow`, `toBeInstanceOf`, `expect.anything()`, `expect.any(Object)`, and argumentless `toThrow()` or `rejects.toThrow()` when the error type or message is known. `toMatchSnapshot` on an object larger than a screen with no targeted assertion beside it is a finding.
- **N7.** `vi.mock('./thing-under-test')` on the module that exports the system under test. `vi.spyOn(sut, 'method')` where `method` is what the test claims to verify.
- **N8.** The only assertions are `toHaveBeenCalled`, `toHaveBeenCalledWith`, `toHaveBeenCalledTimes`, or `mock.calls` inspection.
- **N9.** `test.each` and `it.each` with a literal table are the sanctioned parameterization. A `for` over a literal array inside one `it` is exempt but reports as C3, since `it.each` would name the failing row. A loop wrapping `it(...)` with computed expectations is not exempt.
- **N10.** `it.only`, `describe.only`, `it.skip`, `xit`, `xdescribe`, `it.todo` left behind. `--passWithNoTests` or `passWithNoTests: true` added in the same PR.
- **A7.** `vi.mock('ethers')`, `vi.mock('axios')`, `vi.mock('@filoz/synapse-sdk')` without a project-owned wrapper is a warning, not a block; wrapping every SDK is not always worth it.
- **A7.** Doubles are typed against the interface they replace: `vi.fn<RateSource['getRate']>()` or an object literal with `satisfies RateSource`. An untyped `vi.fn()` returns `any` and lets the test pass on a shape the real dependency would never return. Warn.

## Exemptions

- `beforeEach` that only constructs the system under test with fresh fakes is not a General Fixture; A3 fires when the asserted value comes from a default inside that setup.
- `msw` or a hermetic in-process HTTP mock does not trip N1; a real `localhost` server started in setup does.
