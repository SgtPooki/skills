---
name: slide-deck-foc
description: Build a single self-contained HTML slide deck from notes or analysis, validate it (arithmetic, cross-slide consistency, claims-against-source, writing voice, structure), and publish it to Filecoin Onchain Cloud (FOC) via filecoin-pin so it is shareable as an inbrowser.link/ipfs URL. Use when asked to "build a slide deck", "make a deck", "turn this into slides", "consolidate this into a presentation", or "publish a deck to FOC / Filecoin / IPFS" and share a link.
allowed-tools: Bash, Read, Glob, Grep, Edit, Write
metadata:
  short-description: Build a one-file slide deck and publish it to Filecoin Onchain Cloud
---

# Slide deck to FOC

Turn notes, analysis, or learnings into a single self-contained HTML slide deck, validate every number and claim, and publish it to Filecoin Onchain Cloud so it can be shared as one link. The output is a `*.html` file that runs offline (no CDNs) and an `inbrowser.link/ipfs/<cid>` URL.

## Workflow

1. **Gather** the content: the audience, the thesis in one sentence, the key points, and every number/claim with its source.
2. **Build** the deck from `assets/template.html` (copy it, fill in slides, follow the rules below).
3. **Validate**: run `assets/validate.sh <deck.html>`, then do the content checks (recompute math, verify claims against source, check cross-slide consistency).
4. **Publish** to FOC with `filecoin-pin add`.
5. **Return** the `inbrowser.link/ipfs/<cid>` URL.

Do all four. A deck with a wrong number or a contradicted claim is worse than no deck.

---

## 1. Build

Start from `assets/template.html`. It is a complete, self-contained deck: inline CSS + JS, keyboard nav (arrows/space, F for fullscreen, Home/End), a progress bar, and a slide counter that reads `slides.length` so it stays correct as you add slides. No external resources, so it renders offline and from IPFS.

Each slide is one `<section class="slide">`. The first has `class="slide active"`. Components available (see the template): `kicker` + `h2` title, `p`, `.formula` blocks, tables with right-aligned `.num` monospace cells, `.card` in `.grid2`/`.grid3`, `.footnote`, and color classes `accent` / `good` / `warn` / `muted`.

### Content patterns that make a deck land

- **Lead each slide with the punchline**, then support it. The title says the conclusion.
- **Define key variables and terms on their own slide** before you use them. If a single ratio or metric drives the model, give it a slide: definition, formula, a worked example, and whether it is measured or assumed.
- **Show ranges and sensitivity, not point estimates.** Label things honestly: "illustrative", "list-price ceiling", "base case". One number presented as fact invites a takedown.
- **Add an Assumptions appendix slide** that lists every input and marks it given / assumed / placeholder (a color-coded table). This pre-empts "where did that number come from?".
- **Do not over-anchor on one data point.** If something is `n=1` (one example, one partner, one measurement), say so on the slide and show what happens if it is 10x off.
- **A closing call-to-action beats a summary.** Do not end on a slide that just repeats the body.

### Writing voice (check every line)

These are the tells that get a deck sent back. The validate script catches the mechanical ones; you own the rest.

- **No em-dashes or en-dashes** (`—`, `–`, `&mdash;`, `&ndash;`). Use a colon in labels ("Path A: ..."), a comma or parentheses in prose, a hyphen in numeric ranges ("$2-20M"). This is the single most common offense.
- **No AI-smell words**: comprehensive, robust, leverage(s), facilitate, ensure, furthermore, additionally, seamless, "it is worth noting", "in conclusion". Say the specific thing instead.
- **No business-speak, no emoji** in the deck.
- **Be specific.** Give the number, the date, the named example. Never "often", "recently", "a lot".
- **Do not fabricate specifics.** If you do not know a number, say so or omit it. A confident wrong number is worse than a hedge.

---

## 2. Validate

Run the mechanical checks, then the content checks. Fix everything before publishing.

```bash
bash <skill-dir>/assets/validate.sh <deck.html>
```

That covers: balanced `<section>` open/close, em/en-dashes, AI-smell words, emoji, and external resources (which would break offline/IPFS rendering).

Then do the checks a script cannot:

- **Recompute every number.** Use `node -e '...'` to recompute totals, percentages, and any derived figure. Do not take a number on faith just because it was in the source notes.
- **Check cross-slide consistency.** The same quantity must read the same on every slide. If slide 3 says one thing and slide 9 implies another, one of them is wrong. Grep for the recurring figures and reconcile.
- **Verify claims against the source, not memory.** If the deck states a figure, rate, limit, mechanism, or fact, confirm it in the authoritative source before asserting it: the paper, dataset, spec, official figures, or (for code) the constant in the contract or config. Use the current version of the source, not a cached or stale copy. Cite it in the notes. A number that "sounds right" is how wrong decks happen.
- **Label what you could not verify.** If a given number is unconfirmable from source, mark it as provided-but-unverified in the speaker notes rather than presenting it as fact.

Keep a companion `*-notes.md` with the assumptions, the per-figure math, and the source references. It travels with the deck and answers the hard questions.

---

## 3. Publish to FOC

Publish with `filecoin-pin` (the FOC client). It packs the file into a UnixFS CAR, stores it on Filecoin storage providers, commits on-chain, and verifies the content is retrievable. The result is permanent, paid storage with a link that stays live. Nothing to install beyond Node.js: `npx` fetches the CLI on demand.

### Prerequisites

- **Node.js** (provides `npx`). The CLI is run as `npx --yes filecoin-pin@latest ...`, no global install.
- **A Filecoin wallet** you control, as a private key.
- **Funds in that wallet:** real FIL (gas) plus USDFC (a Filecoin stablecoin, for storage). Storing a small HTML deck costs a tiny fraction of a USDFC.
- **First time only:** approve the payment contracts once with `npx --yes filecoin-pin@latest payments setup`. For wallet setup and funding, see the filecoin-pin docs: https://github.com/filecoin-project/filecoin-pin

### Credentials

Give the wallet key to the CLI through the `PRIVATE_KEY` environment variable; `filecoin-pin` reads it automatically. Keep it out of version control and never print it.

```bash
# set it for the current shell:
export PRIVATE_KEY=0xYOUR_PRIVATE_KEY

# or keep it in a gitignored .env (a line `PRIVATE_KEY=0x...`) and load it:
set -a; . ./.env; set +a
```

You do not need to echo the key to check it: `payments status` and `add` both print the wallet address they use, so you can confirm the right wallet without exposing the secret. (Session-key auth also works via `--wallet-address` + `--session-key`.)

### Confirm the wallet is funded (avoids a partial upload)

```bash
npx --yes filecoin-pin@latest payments status | tail -20
```

Look for runway / "Storage covered". If it is empty, fund the wallet, or add `--auto-fund` to the upload to deposit USDFC and maintain a 30-day runway.

### Publish

```bash
npx --yes filecoin-pin@latest add path/to/deck.html
```

Useful flags: `--copies <n>` (default 2), `--egress-provider none` (skip the FilBeam CDN if you do not need it), `--auto-fund`, `--provider-id <id>` (pin to a specific provider).

The run can take a few minutes (provider upload + on-chain confirmation + IPNI advertisement). For long runs, run it in the background and read the log. Wait for "IPNI provider records found" before sharing.

### The shareable URL

The output prints a **Root CID**. The share link is:

```
https://inbrowser.link/ipfs/<rootCID>
```

Gotchas worth knowing:

- A small single-block file gets a raw `bafkrei...` CID. That is fine; inbrowser.link sniffs content type and renders the HTML.
- The deck must be **fully self-contained** (no external CSS/JS/fonts/images). External resources will not load over IPFS. The validate script flags these.
- The **FilBeam CDN URL** that `add` also prints serves the CAR/piece bytes, not the rendered page. Always share the **inbrowser.link** URL for viewing.

---

## What makes this worth promoting

One command from "I have notes" to "here is a link anyone can open": a deck that is self-contained, honest about its assumptions, verified against source, and pinned to Filecoin so it cannot quietly disappear. The deck is the artifact; the link is the delivery; FOC is the durable store.
