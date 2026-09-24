# Go override

Load for `*_test.go`.

## Sharpened signals

- **N1.** Real URLs or `net.Dial` in a test. `httptest.NewServer` is in-process and does not trip N1. `os.WriteFile` outside `t.TempDir()` does.
- **N2.** `time.Sleep` to wait for a goroutine or channel. Target: wait on the channel, a `sync.WaitGroup`, or an injected clock. `context.WithTimeout` used as the assertion is a finding.
- **N3.** `time.Now()` inside the code under test with no injected clock or `func() time.Time` field. Iterating a `map` and asserting order.
- **N4.** `t.Parallel()` combined with writes to package-level variables. Tests that share a package-level fixture built in `TestMain` and mutate it.
- **N5.** `assert.NoError(t, err)` or `require.NoError(t, err)` as the only assertion on a function that returns a value. `_ = result`.
- **N8.** The only check is that a mock's method was invoked (gomock `EXPECT()` with no assertion on the returned value or resulting state).
- **N9.** Table-driven tests are the idiom and are exempt: `for _, tc := range cases { t.Run(tc.name, func(t *testing.T) { ... }) }` where `cases` is a literal slice of inputs and expected outputs. The loop becomes a finding when the expected value is computed inside it, or when the body branches on `tc` fields to choose which assertion to run.
- **N10.** `t.Skip()` without a linked issue. Build tags that exclude the test from the default `go test ./...`.
- **A1.** Subtest names are the behavior names: `t.Run("returns ErrNotFound when the id is unknown", ...)`, not `t.Run("case 3", ...)`.

## Exemptions

- `testing.Short()` guards around slow cases are acceptable when the slow case is an integration test living in the same package; the unit case must still run.
- `require` (fail-fast) versus `assert` (continue) is a style choice, not a rule.
