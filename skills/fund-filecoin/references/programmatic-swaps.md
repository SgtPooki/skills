# Programmatic swaps, bridges & deposits with `cast`

Load this when the user wants to **automate** acquiring FIL/USDFC (no browser), or when a storage tool doesn't wrap the Filecoin Pay deposit. For most users the web UIs in `SKILL.md` are simpler and safer — reach for these recipes only when scripting is the explicit goal.

All of these follow the same shape: **get calldata from an aggregator API, then broadcast it with `cast send`.** You are not hand-crafting swap math — the aggregator returns a ready transaction. Your job is approvals, signing, and waiting.

Prerequisites: Foundry (`cast`), the signer's key in `$PRIVATE_KEY`, `jq`, and `curl`. Addresses, RPCs, and chain IDs come from the `SKILL.md` Reference tables.

---

## 1. Bridge another chain → native FIL (Squid API)

Squid (over Axelar) is the only aggregator with Filecoin (314) liquidity. Bridge to **native FIL** (sentinel `0xeee…eee`), then swap to USDFC on Filecoin (§2). Don't bridge to USDFC directly.

### 1.1 Request a route

```sh
SRC_CHAIN=42161            # e.g. Arbitrum; see chain IDs below
SRC_TOKEN=0xaf88d065e77c8cC2239327C5EDb3A432268e5831   # e.g. USDC on Arbitrum (or 0xeee…eee for native)
AMOUNT=10000000           # in SRC_TOKEN atomic units (USDC = 6 decimals → 10 USDC)
SIGNER=0xYourAddress      # must equal the FIL recipient (see note)

curl -s -X POST https://v2.api.squidrouter.com/v2/route \
  -H 'Content-Type: application/json' \
  -H 'x-integrator-id: squid-swap-widget' \
  -d "{
    \"fromAddress\": \"$SIGNER\",
    \"fromChain\": \"$SRC_CHAIN\",
    \"fromToken\": \"$SRC_TOKEN\",
    \"fromAmount\": \"$AMOUNT\",
    \"toChain\": \"314\",
    \"toToken\": \"0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee\",
    \"toAddress\": \"$SIGNER\",
    \"slippage\": 1
  }" > route.json

jq '.route.estimate | {fromAmountUSD, toAmountUSD, toAmount, estimatedRouteDuration}' route.json
TARGET=$(jq -r '.route.transactionRequest.target' route.json)
DATA=$(jq -r '.route.transactionRequest.data' route.json)
VALUE=$(jq -r '.route.transactionRequest.value' route.json)
```

`x-integrator-id: squid-swap-widget` is the public widget identity — no registration needed. If you run many quotes from one address and hit `Too many quote requests`, set your own integrator ID. **The recipient (`toAddress`) must equal `$SIGNER`** if you intend to swap FIL→USDFC on Filecoin afterward — the on-Filecoin swap is signed by the same key, so the FIL has to land in that wallet.

### 1.2 Approve the router (ERC-20 inputs only)

Native-token inputs (`fromToken` = `0xeee…eee`) skip this. For ERC-20 inputs, Squid's router pulls funds **either** via a plain `transferFrom` **or** via Uniswap **Permit2** depending on the route — so authorize **both** to avoid an opaque on-chain revert (`AllowanceExpired` / `TransferFailed`):

```sh
PERMIT2=0x000000000022D473030F116dDEE9F6B43aC78BA3
SRC_RPC=<rpc for SRC_CHAIN>
MAX=$(cast max-uint)

# (a) direct allowance: token → router
cast send $SRC_TOKEN "approve(address,uint256)" $TARGET $MAX \
  --private-key $PRIVATE_KEY --rpc-url $SRC_RPC

# (b) Permit2 path: token → Permit2, then Permit2 authorizes the router
cast send $SRC_TOKEN "approve(address,uint256)" $PERMIT2 $MAX \
  --private-key $PRIVATE_KEY --rpc-url $SRC_RPC
# Permit2.approve(token, spender=router, amount=uint160 max, expiration=uint48 far-future)
cast send $PERMIT2 "approve(address,address,uint160,uint48)" \
  $SRC_TOKEN $TARGET 1461501637330902918203684832716283019655932542975 281474976710655 \
  --private-key $PRIVATE_KEY --rpc-url $SRC_RPC
```

Read existing allowances first and skip if already set, to save gas.

### 1.3 Execute and wait

```sh
TX=$(cast send $TARGET $DATA --value $VALUE \
  --private-key $PRIVATE_KEY --rpc-url $SRC_RPC --json | jq -r '.transactionHash')
echo "source tx: $TX  → track: https://axelarscan.io/gmp/$TX"

# Poll Squid until terminal. success / partial_success = good; refund / needs_gas = failed.
REQ_ID=$(jq -r '.route.params.requestId // empty' route.json)
while :; do
  ST=$(curl -s "https://v2.api.squidrouter.com/v2/status?transactionId=$TX&fromChainId=$SRC_CHAIN&toChainId=314${REQ_ID:+&requestId=$REQ_ID}" \
        -H 'x-integrator-id: squid-swap-widget' | jq -r '.squidTransactionStatus // "ongoing"')
  echo "status: $ST"
  case "$ST" in success|partial_success) break;; refund|needs_gas|not_found) echo "FAILED: $ST"; break;; esac
  sleep 10
done
```

The destination FIL balance can lag the `success` flag by a few seconds — re-check with `cast balance` before the next step.

**Source chain IDs:** Ethereum `1`, Optimism `10`, BSC `56`, Polygon `137`, Base `8453`, Arbitrum `42161`, Avalanche `43114`.

---

## 2. Swap FIL → USDFC on Filecoin (same-chain)

Once native FIL is on Filecoin, swap a portion to USDFC. Same Squid pattern, but `fromChain` and `toChain` are both `314` and there's no bridge wait. **Leave enough FIL behind for gas** (this swap's gas + the later Filecoin Pay deposit).

```sh
FIL_RPC=https://api.node.glif.io/rpc/v1
SWAP_IN=<wei of FIL to swap>      # e.g. 90% of balance; keep the rest for gas
SIGNER=0xYourAddress

curl -s -X POST https://v2.api.squidrouter.com/v2/route \
  -H 'Content-Type: application/json' -H 'x-integrator-id: squid-swap-widget' \
  -d "{
    \"fromAddress\": \"$SIGNER\",
    \"fromChain\": \"314\",
    \"fromToken\": \"0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee\",
    \"fromAmount\": \"$SWAP_IN\",
    \"toChain\": \"314\",
    \"toToken\": \"0x80B98d3aa09ffff255c3ba4A241111Ff1262F045\",
    \"toAddress\": \"$SIGNER\",
    \"slippage\": 1
  }" > swap.json

TARGET=$(jq -r '.route.transactionRequest.target' swap.json)
DATA=$(jq -r '.route.transactionRequest.data' swap.json)
VALUE=$(jq -r '.route.transactionRequest.value' swap.json)   # = SWAP_IN for native input
cast send $TARGET $DATA --value $VALUE --private-key $PRIVATE_KEY --rpc-url $FIL_RPC
```

Native input → no token approval needed. Confirm the USDFC landed: `cast call <USDFC> "balanceOf(address)(uint256)" $SIGNER --rpc-url $FIL_RPC`.

Any Filecoin DEX with a routed API works too (the SushiSwap router on Filecoin, etc.) — the pattern is identical: fetch calldata, `cast send`. Squid is convenient because §1 and §2 share one API.

---

## 3. Raw deposit into Filecoin Pay (only if your tool doesn't wrap it)

Prefer the storage tool's own command (`filecoin-pin payments setup`, Synapse SDK `prepare()`/`--auto-fund`). Drop to this only when integrating against Filecoin Pay directly.

Conceptually three on-chain steps, signed on Filecoin (chain 314):

1. **Approve** USDFC to the Filecoin Pay (Payments) contract: `USDFC.approve(payments, amount)` — or skip with a one-shot `depositWithPermit` (EIP-2612 signature + deposit in a single tx).
2. **Deposit** USDFC into your Payments account: `Payments.deposit(token=USDFC, to=you, amount)` (exact signature varies by version).
3. **Approve the Warm Storage operator** so the storage service can draw from your deposit: an operator-approval call on Payments (first-time only; later deposits skip it).

Pull the **Payments** and **Warm Storage** addresses and the exact ABIs from the `@filoz/synapse-core` chain config (its `chains.ts` carries `filecoinPayV1` and `filecoinWarmStorageService` addresses per chain ID) rather than hard-coding — they version with the protocol. Then encode with `cast calldata` / `cast send`. Re-check `Payments.accounts(...)` / the tool's `payments status` to confirm the deposit and runway.

---

## Failure modes & recovery

| Symptom | Cause | Fix |
|---------|-------|-----|
| `AllowanceExpired` / `TransferFailed` on bridge execute | router approval missing | do **both** approvals in §1.2 (direct ERC-20 **and** Permit2) |
| `Too many quote requests for this address` | shared Squid integrator rate limit | back off and retry, or set your own `x-integrator-id` |
| Bridge `status` stuck on `ongoing` for many minutes | Axelar source-finality wait (large transfer) | keep polling; track on `https://axelarscan.io/gmp/<tx>` — it usually still lands |
| `status` = `refund` / `needs_gas` | route failed / underfunded destination gas | funds refund on source; check axelarscan, re-quote a larger amount |
| Swap reverts on Filecoin for "insufficient funds" | swapped too much FIL, none left for gas | leave a FIL buffer; swap a smaller portion |
| USDFC below storage floor after swap | bridged/swapped too little | floor is ~0.16–0.24 USDFC; bridge/swap a larger amount |
