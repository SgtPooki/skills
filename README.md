# skills

Reusable AI agent skills for Claude Code, Cursor, Codex, and other agents.

## Install

```bash
npx skills add SgtPooki/skills
```

This installs all skills via [vercel-labs/skills](https://github.com/vercel-labs/skills). Cursor, Codex, and other universal agents get skills automatically. Claude Code and other agents can be selected during install.

For non-interactive installs:

```bash
npx skills add SgtPooki/skills --yes
```

For global install (available in all projects):

```bash
npx skills add SgtPooki/skills -y -g
```

## Available skills

### peer-review

Cross-agent review for specs, plans, code changes, pull requests, and design decisions using Cursor, Codex, and Claude CLI agents.

```
/peer-review cursor Review this spec for completeness
/peer-review codex What's wrong with this API design?
/peer-review claude Review this PR for edge cases
/peer-review Review this spec          # sends to all available agents
```

Keeps the reviewer different from the authoring agent — if Claude wrote the work, it reviews with Cursor or Codex, and vice versa.

### beads

Layer [beads](https://github.com/steveyegge/beads) (`bd`) on top of GitHub Issues to give multiple agents (Claude, Codex, Cursor, Gemini) a local, atomic, conflict-free task queue. GitHub Issues stays canonical for specs and `fixes #N` commit closure; beads handles claim races, PR-review lifecycle, and worktree discipline.

```
/beads                  # show ready work + protocol reminder
/beads init             # bootstrap beads in a new repo (install, init, GH sync, hooks)
/beads claim <id>       # atomic claim + create isolated worktree
/beads ship             # walk through the PR-review lifecycle
/beads protocol         # print the full agent protocol
```

Enforces a shared multi-agent workflow: set `BEADS_ACTOR` per agent, work each implementation bead in a dedicated `git worktree`, never force-release a stale claim without audit, never put a bead ID as a commit closure reference (`fixes #N` stays canonical).

### fund-filecoin

Unblock anyone who needs **FIL + USDFC** on Filecoin **mainnet** to pay for Filecoin Onchain Cloud (FOC) storage — filecoin-pin, the Synapse SDK, FilCDN, or anything on Filecoin Pay. A tool-agnostic, human-in-the-loop walkthrough an agent can follow to get both tokens into a wallet, using `cast` (Foundry), web swaps/bridges, or aggregator APIs.

```
"I need USDFC to use filecoin-pin"
"fund my Filecoin wallet"
"swap my USDC to FIL and USDFC"
"insufficient balance for storage"
```

Checks existing balances first, then routes to the right path: exchange withdrawal, or the reliable cross-chain shape — **bridge to native FIL (Squid), then swap FIL→USDFC *on* Filecoin (Sushi)** — and hands off to the tool's own Filecoin Pay deposit step. Programmatic `cast` + aggregator-API recipes (with Permit2 handling and recovery from stuck bridges) live in `references/`.

### dx-audit

Audit the developer experience of a library or tool you maintain across four surfaces — CLI, programmatic library/API, server/service, and GitHub Action — with measurable checks, clean consumer fixtures, and remediation-oriented scoring.

```
/dx-audit                       # auto-detect surfaces, audit all
/dx-audit cli api               # audit only the named surfaces
/dx-audit ../some-other-repo    # audit a checkout elsewhere
```

Runs in a **static tier** (docs + source + cheap live probes) by default, or a **fixture tier** (clean-room runs of the published artifact against a testnet) for real TTFS/success/error metrics. Tests the **published artifact** (not monorepo source) to catch DX bugs that hide in the gap between them. Writes a scored `report.md`, deterministic `scorecard.json` (via `scripts/score.mjs`), and a prioritized `remediation-plan.md` to a temp dir (`$TMPDIR/dx-audit/<repo>`), never polluting the audited repo. Detailed P0/P1/P2 checklists, metrics, the 0/1/3/5 rubric with `na`-for-scope handling, report templates, and a CI rollout harness live in `references/`.
