---
name: fund-filecoin
description: Get FIL (for gas) and USDFC (for storage) into an Ethereum-style wallet on Filecoin mainnet so the user can pay for Filecoin Onchain Cloud (FOC) storage — e.g. filecoin-pin, the Synapse SDK, FilCDN, or anything built on Filecoin Pay / Warm Storage. Tool-agnostic: uses cast (Foundry), web swaps/bridges, or aggregator APIs. Use when a user is blocked on "needs FIL", "needs USDFC", "fund my Filecoin wallet", "swap to USDFC", "insufficient balance for storage", or setting up payments for any FOC tool.
allowed-tools: Bash, Read, Glob, Grep, Edit, Write, WebFetch
metadata:
  short-description: Acquire FIL + USDFC on Filecoin mainnet to unblock Onchain Cloud storage
---

# Fund a wallet with FIL + USDFC for Filecoin Onchain Cloud

Filecoin Onchain Cloud (FOC) storage tools — [filecoin-pin](https://docs.filecoin.io/builder-cookbook/filecoin-pin/filecoin-pin-cli), the [Synapse SDK](https://docs.filecoin.cloud), FilCDN, and anything else on [Filecoin Pay](https://github.com/FilOzone/filecoin-pay) — all need the same two tokens in an **Ethereum-style (`0x…`) wallet on Filecoin mainnet** (chain `314`):

- **FIL** — Filecoin's native gas token. Pays transaction fees for every on-chain action (deposits, approvals, swaps).
- **USDFC** — a FIL-backed, overcollateralized USD stablecoin ([Secured Finance](https://usdfc.secured.finance)). This is what storage is actually *priced and paid* in, via Filecoin Pay.

This skill walks an agent through getting both into the user's wallet, then handing off to the FOC tool's own deposit step. It is **tool-agnostic** — it does not depend on any one CLI. Use `cast` (Foundry) for on-chain reads/writes, and either web UIs or aggregator APIs for swaps and bridges.

> **Mainnet only.** This skill funds Filecoin **mainnet** (chain `314`) — real value. It does not cover calibration testnet.

> The single most important insight: **cross-chain USDFC liquidity is thin.** Never try to bridge straight to USDFC from another chain. Instead, get **FIL onto Filecoin first**, then **swap a portion of that FIL to USDFC *on Filecoin*** (deep Sushi liquidity). Every reliable path below follows this shape.

## What "done" looks like

The wallet holds, on Filecoin mainnet:

- Enough **FIL** for gas (a little goes a long way — ~0.05–0.1 FIL covers many transactions), **plus**
- Enough **USDFC** for the intended storage. The on-chain storage floor (FWSS minimum deposit) is ~0.16–0.24 USDFC, but FOC tools want a real runway — a **first deposit of ~10 USDFC** is the documented starting point for filecoin-pin. FWSS requires a 30-day prepayment buffer.

After acquisition, the tokens still need to be **deposited into Filecoin Pay** (and Warm Storage approved) before storage works — see [step 5](#5-hand-off-deposit-into-filecoin-pay). Acquisition alone does not pay for storage.

## Steps

Don't guess addresses or URLs — use the [Reference](#reference) values exactly. Confirm anything irreversible (sends, swaps, bridges, mints) with the user before broadcasting.

### 1. Identify or create the wallet, and check balances first

FOC tools, MetaMask, Sushi, and the FEVM all use the **`0x…` (Ethereum-style) address**. The same key also has an equivalent native `f410…` address; only reach for that if an exchange specifically needs the `f`-form.

- **Existing wallet:** get the `0x` address from the user (never the private key unless a step needs to sign — and then via env var, see [Safety](#safety)).
- **New wallet:** generate one with a vetted tool — **never hand-roll key generation**. `cast wallet new` (Foundry) is the default; it prints the address and private key. Save the key to `.env` (e.g. `PRIVATE_KEY=0x…`), `chmod 600 .env`, and add it to `.gitignore`.

**Always check current balances before acquiring anything** — the user may already have what they need, or partially. With `cast`:

```sh
FIL_RPC=https://api.node.glif.io/rpc/v1
USDFC=0x80B98d3aa09ffff255c3ba4A241111Ff1262F045

# FIL (native) balance, in FIL:
cast balance <0xADDRESS> --ether --rpc-url $FIL_RPC

# USDFC balance (18 decimals) — raw atomic units:
cast call $USDFC "balanceOf(address)(uint256)" <0xADDRESS> --rpc-url $FIL_RPC
```

Report what they have vs. what they need, and only do the steps that close the gap.

### 2. Get FIL onto Filecoin

#### 2a. Exchange withdrawal (simplest for real funds)

If the user has FIL on an exchange (Coinbase, Kraken, Binance, etc.), the cleanest path is to **withdraw FIL directly to their `0x` FEVM address**. Confirm the exchange supports the FEVM/`0x` address format; if it only supports native `f1…`/`f3…`, use the wallet's `f410…` form (the funds are spendable from the same key on FEVM). This avoids bridge fees and finality waits entirely.

#### 2b. Bridge from another chain (USDC/ETH/etc. → FIL)

If the user holds tokens on Ethereum, Base, Arbitrum, Optimism, BSC, Polygon, or Avalanche, bridge to **native FIL** on Filecoin. **Squid Router** (over Axelar) is effectively the only aggregator with Filecoin (chain 314) liquidity — LI.FI, deBridge, Stargate, etc. don't list it.

- **Easiest (recommended): the Squid web UI**, human-in-the-loop. Build a deeplink that preselects the route and have the user complete it in their wallet:
  `https://app.squidrouter.com/?chains=<SRC_CHAIN_ID>,314&tokens=<SRC_TOKEN_ADDR>,0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee`
  (`0xeee…eee` is the native-token sentinel — here it targets native FIL.)
- **Programmatic (with `cast`)**: fetch route calldata from the Squid API and broadcast it yourself. This is more involved (ERC-20 inputs need a Permit2 **and** a direct router approval, then poll for delivery). See [`references/programmatic-swaps.md`](references/programmatic-swaps.md) for the full recipe.

Timing: Squid's Axelar Express path often delivers in ~2 min, but large transfers can fall back to source-chain finality (Ethereum ~15 min). Don't assume it's stuck; track via the [axelarscan](https://axelarscan.io) link the route provides.

#### 2c. Tiny gas drip (gas only, not storage)

For *just enough FIL to pay gas* (e.g. the user already plans to get USDFC another way), the ChainSafe mainnet faucet drips a small amount: <https://forest-explorer.chainsafe.dev/faucet/mainnet>. Browser-only, Cloudflare-gated, rate-limited — have the user do it. Far too small to swap into meaningful USDFC.

### 3. Get USDFC

#### 3a. Swap FIL → USDFC on Filecoin (recommended)

Once the wallet has FIL on Filecoin (step 2), swap a portion to USDFC **on Filecoin** where liquidity is deep:

- **Easiest: SushiSwap on Filecoin**, human-in-the-loop. Deeplink, native FIL → USDFC:
  `https://www.sushi.com/filecoin/swap?token0=NATIVE&token1=0x80b98d3aa09ffff255c3ba4a241111ff1262f045`
  Have the user connect and swap. Leave enough FIL behind for gas — don't swap the whole balance.
- **Programmatic (with `cast`)**: same-chain FIL→USDFC via the Squid API (fromChain=314, toChain=314, native → USDFC) or any Filecoin DEX router, then `cast send` the returned calldata. See [`references/programmatic-swaps.md`](references/programmatic-swaps.md).

#### 3b. Mint USDFC against FIL collateral (advanced)

USDFC is a Liquity-style overcollateralized stablecoin: open a "Trove" by locking FIL and minting USDFC, keeping the collateral ratio ≥110%, at <https://usdfc.secured.finance>. Use this only if the user explicitly wants to *borrow* USDFC against FIL they intend to keep, rather than swap. It's a debt position with liquidation risk — for simply paying for storage, the swap (3a) is simpler and has no liquidation exposure.

> Do **not** suggest bridging to USDFC directly from another chain — liquidity is thin and routes are unreliable. Bridge to FIL (2b), then swap on Filecoin (3a).

### 4. Verify final balances

Re-run the `cast` balance checks from step 1 and confirm both tokens are present in sufficient amount for the intended use. State the numbers back to the user. If USDFC is below the storage floor (~0.16–0.24 USDFC) or below what the tool needs, get more before proceeding.

### 5. Hand off: deposit into Filecoin Pay

Holding USDFC in the wallet is **not** the same as having paid for storage. FOC tools require depositing USDFC into **Filecoin Pay** and approving the **Warm Storage** service to spend it. Most tools do this for you — defer to the tool the user is actually using:

- **filecoin-pin:** `filecoin-pin payments setup` (interactive: checks balances, shows pricing, deposits; ~10 USDFC is the documented first deposit). Then `filecoin-pin payments status` to confirm. Top up runway later with `filecoin-pin payments fund --days <n>` (only after a first upload) or `--amount <usdfc>`.
- **Synapse SDK:** the SDK sets USDFC deposits/allowances through Filecoin Pay and approves Warm Storage; `prepare()` / `--auto-fund` computes and submits the deposit+approval. Follow the SDK's own funding flow.
- **Other / raw:** the deposit is an ERC-20 `approve` of USDFC to Filecoin Pay, then a `deposit` (or `depositWithPermit`) into the Payments contract, plus a Warm Storage operator approval. If a tool doesn't wrap this, see [`references/programmatic-swaps.md`](references/programmatic-swaps.md) for the contract-level shape — but prefer the tool's built-in command.

This is where this skill ends and the storage tool's setup takes over. The user is now unblocked.

## Reference

### Network

| Network | Chain ID | RPC | Explorer |
|---------|----------|-----|----------|
| Filecoin mainnet | `314` | `https://api.node.glif.io/rpc/v1` | `https://filfox.info/en` / `https://beryx.io/fil/mainnet` |

### Token / contract addresses (mainnet, chain 314)

| Token / contract | Address |
|------------------|---------|
| USDFC | `0x80B98d3aa09ffff255c3ba4A241111Ff1262F045` |
| Native sentinel (FIL / gas token in aggregators) | `0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee` |
| Squid Router | `0xce16F69375520ab01377ce7B88f5BA8C48F8D666` |
| Permit2 (all EVM chains) | `0x000000000022D473030F116dDEE9F6B43aC78BA3` |

USDFC has **18 decimals**. For Filecoin Pay / Warm Storage addresses (needed only for raw deposits), read them from the Synapse SDK's `@filoz/synapse-core` chain config rather than hard-coding — they version with the protocol.

### Web UIs (human-in-the-loop)

| Action | URL pattern |
|--------|-------------|
| Swap FIL → USDFC on Filecoin | `https://www.sushi.com/filecoin/swap?token0=NATIVE&token1=0x80b98d3aa09ffff255c3ba4a241111ff1262f045` |
| Bridge any chain → native FIL | `https://app.squidrouter.com/?chains=<SRC_ID>,314&tokens=<SRC_TOKEN>,0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee` |
| Mint USDFC vs FIL collateral | `https://usdfc.secured.finance` |
| Tiny FIL gas drip (mainnet) | `https://forest-explorer.chainsafe.dev/faucet/mainnet` (browser, rate-limited) |

### `cast` quick reference

```sh
cast wallet new                                              # generate a fresh keypair
cast wallet address <PRIVATE_KEY>                            # address from a key
cast balance <ADDR> --ether --rpc-url <RPC>                  # FIL balance
cast call <USDFC> "balanceOf(address)(uint256)" <ADDR> --rpc-url <RPC>   # USDFC (raw, 18dp)
cast send <TO> --value <WEI> --private-key $PRIVATE_KEY --rpc-url <RPC>  # send native FIL
```

For programmatic swaps/bridges (aggregator API → calldata → `cast send`), Permit2/approval handling, and the raw Filecoin Pay deposit shape, see [`references/programmatic-swaps.md`](references/programmatic-swaps.md).

## Safety

- **Treat the private key like a password.** Never paste it into a website, commit it, print it back to the user, or store it in plaintext on a shared system. Read it from an env var (`PRIVATE_KEY` / `.env` with `chmod 600`, gitignored) only when a step must sign.
- **Generate keys only with vetted tools** (`cast wallet new`, or `openssl rand -hex 32` + `cast wallet address`). Never improvise key generation in a script.
- **Confirm every irreversible action** (sends, swaps, bridges, mints) — amount, token, destination — with the user before broadcasting. This is mainnet: bridges and swaps cost gas + fees and can't be undone.
- **Verify addresses against the Reference**, not from memory or model recall. A wrong token address silently sends to nowhere.
- **Default to web UIs for swaps/bridges** unless the user wants automation; the programmatic path has more failure modes (approvals, slippage, relayer timing). When automating, surface aggregator/axelarscan links so the user can track and recover stuck transfers.
- **Start small.** Test the path with a modest amount before moving large sums.
