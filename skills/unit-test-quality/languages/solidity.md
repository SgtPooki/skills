# Solidity override

Load for `*.t.sol` (Foundry) and Hardhat test files targeting contracts. The unit tier is a local EVM with no fork.

## Sharpened signals

- **N1.** `vm.createSelectFork` or any RPC URL in a test that is not in an explicit integration or fork tier. Reading `.env` for a private key.
- **N2 and N3.** `vm.warp` and `vm.roll` are the injected clock and are the target, not a finding; they trip N2 only when used as a blind wait rather than to reach a specific state. `block.timestamp` or `block.prevrandao` arithmetic in the test with no `vm.warp` first.
- **N4.** State from one test leaking into another. Foundry snapshots state per test; Hardhat needs `loadFixture` or a fresh deploy in `beforeEach`.
- **N5.** The strongest assertion is `assertTrue(success)` on a low-level call, or a transaction that "does not revert". Target: `assertEq` on storage or balances, `vm.expectEmit` for events, `vm.expectRevert(Selector.selector)` with the specific error.
- **N7.** `vm.mockCall` on the contract under test, or replacing it with a stub that returns the asserted value. `vm.mockCall` on a dependency contract is a legitimate boundary double.
- **N8.** A test whose only check is `vm.expectCall` with no assertion on resulting state, balance, or event.
- **N9.** Fuzz tests (`function testFuzz_...(uint256 x)`) are the sanctioned parameterization. `vm.assume` that narrows the input to a single value is a finding; the fuzz then tests nothing.
- **N10.** Tests renamed to drop the `test` prefix so the runner skips them.
- **A2.** For any state-changing call, assert the storage or balance change, the emitted event, and the revert path for unauthorized or invalid input. Value-bearing contracts get an invariant or property test for the accounting relationship that must hold.
- **A4.** Boundaries specific to this domain: zero amount, `type(uint256).max`, exact-boundary timestamps at epoch or deadline edges, empty arrays, the caller that lacks the role.

## Exemptions

- Deploying the full contract graph in `setUp` is normal and does not trip A3 by itself; A3 fires when an asserted value depends on a constructor argument the test never names.
- Gas snapshots are not assertions; a test that only updates `.gas-snapshot` is N5.
