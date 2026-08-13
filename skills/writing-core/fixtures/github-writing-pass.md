## What changed

Pinned the clock in the retry tests. The flaky failures came from real time
leaking into the backoff assertions; `FakeClock` removes the race.

## How to verify

Run `npm test retry` twenty times; before this change it failed roughly one
run in five, after it none. CI runs the loop in the `flake-check` job.

## Notes / risks

None. Test-only change; no runtime code touched.
