---
name: beads
description: Use beads (bd) as a local agent execution queue for multi-agent parallel work. Handles atomic task claiming, PR-review lifecycle, and worktree discipline so multiple agents (Claude, Codex, Cursor, Gemini) can work the same repo without collisions. GitHub Issues stays canonical for specs and `fixes #N` commit closure. Use when saying "next task", "claim a task", "what should I work on", "bd ready", "find work", or when bootstrapping beads in a new repo.
allowed-tools: Bash, Read, Glob, Grep, Edit, Write
metadata:
  short-description: Atomic task queue for multi-agent repo work
---

# Beads

Layers [beads](https://github.com/steveyegge/beads) (`bd`) on top of GitHub Issues to give multiple agents (Claude, Codex, Cursor, Gemini) a local, atomic, conflict-free task queue. **GitHub Issues stays canonical** for specs and `fixes #N` commit closure; beads handles claim races, PR-review lifecycle, and subtask decomposition.

## When to invoke this skill

- `/beads` (no args) — show `bd ready` + a protocol reminder; the default entry point for "what should I work on next?"
- `/beads init` — bootstrap beads in the current repo (install CLI if missing, `bd init`, configure GH sync, install hooks, write a local copy of the protocol)
- `/beads claim <id>` — atomic claim + create an isolated worktree ready to work in
- `/beads ship` — walk through the PR-review lifecycle (create review bead, link deps, record audit)
- `/beads protocol` — print the full protocol (same content as below)

If the user asks for "next task" or similar without `/beads`, invoke `/beads` implicitly.

## Steps by mode

### `/beads` (default — show ready queue)

1. Verify bd is installed: `which bd` — if missing, tell user to run `/beads init` or install via `curl -fsSL https://raw.githubusercontent.com/steveyegge/beads/main/scripts/install.sh | bash` or `npm i -g @beads/bd`.
2. Verify repo is bd-initialized: check for `.beads/` directory — if missing, tell user to run `/beads init`.
3. Run `bd ready --limit 10` and present the output.
4. Remind the user of the claim command and the worktree rule (one-liner).

### `/beads init` (bootstrap in a new repo)

1. Check `which bd`; install if needed.
2. Run `bd init --setup-exclude --skip-agents --skip-hooks --role maintainer --non-interactive`. The `--setup-exclude` flag keeps beads local-only via `.git/info/exclude`; `--skip-agents` prevents bd from overwriting an existing AGENTS.md.
3. Configure GitHub integration:
   ```bash
   REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner)
   bd config set github.repository "$REPO"
   ```
4. Import issues: `GITHUB_TOKEN=$(gh auth token) bd github sync --pull-only` (after a `--dry-run` preview if the user wants to see the scope first).
5. Install git hooks: `bd hooks install`.
6. Silence auto-export warning: `bd config set export.auto false`.
7. Offer to write a local copy of the protocol to `docs/beads-agent-protocol.md` in the repo, with a pointer from the repo's `AGENTS.md` (if it exists). Ask before writing.
8. Offer to add the `BEADS_ACTOR` setup line to AGENTS.md or a shell init file.

### `/beads claim <id>` (claim + worktree)

1. Require the user has set `BEADS_ACTOR` (`echo $BEADS_ACTOR` — if empty, tell them to `export BEADS_ACTOR="claude-$(hostname -s)"` or equivalent for their tool).
2. Run `bd update <id> --claim`.
3. On error `"already claimed by <X>"`: stop; suggest picking a different `bd ready` item.
4. On success:
   ```bash
   REPO_NAME=$(basename "$(git rev-parse --show-toplevel)")
   SHORT=$(echo <id> | sed 's/.*-//')
   git worktree add "../${REPO_NAME}-${SHORT}" -b "beads/${SHORT}"
   cd "../${REPO_NAME}-${SHORT}"
   ```
5. Read the bead: `bd show <id>`. Follow the `External:` link to the backing GH issue for the full spec.

### `/beads ship` (PR-review lifecycle)

Once an implementation bead has a PR open:

1. Create the review bead:
   ```bash
   REVIEW_ID=$(bd create "review PR #<N>" \
     --type task --priority <same as impl> \
     --parent <impl-id> \
     --external-ref "<PR URL>" \
     --silent)
   ```
2. Link: `bd link <impl-id> $REVIEW_ID --type blocks` (impl blocked by review).
3. Record: `bd audit record --kind tool_call --tool-name bd --issue-id <impl-id> --response "opened PR #<N>, created review bead $REVIEW_ID"`.

On review approved → `bd close $REVIEW_ID`; impl bead becomes unblocked; merge PR (which auto-closes the GH issue via `fixes #N`); `bd close <impl-id>`.

On changes requested → create an address-changes bead linked to the impl bead; block the review bead on it.

---

# Protocol (canonical — referenced by all modes above)

## Actor identity

Every agent sets `BEADS_ACTOR` before running `bd` so the claim mutex has distinct owners. Convention: `<tool>-<hostname>`:

```bash
export BEADS_ACTOR="claude-$(hostname -s)"
export BEADS_ACTOR="codex-$(hostname -s)"
export BEADS_ACTOR="cursor-$(hostname -s)"
```

If unset, bd falls back to git `user.name` then `$USER`. Multiple agents sharing an actor defeats the claim mutex — set it explicitly.

## Claim

```bash
bd update <id> --claim
```

- **Atomic mutex.** Sets `status=in_progress`, `assignee=$BEADS_ACTOR`, `started_at=<now>`.
- Errors `"issue already claimed by <X>"` if another actor holds it — skip and pick the next `bd ready` item.
- Idempotent for the same actor (safe to retry).
- A claimed bead disappears from `bd ready` for everyone else.

## Work in an isolated worktree

**Implementation beads: always use a dedicated git worktree.** Prevents two agents from colliding in the filesystem.

```bash
REPO_NAME=$(basename "$(git rev-parse --show-toplevel)")
SHORT=$(echo <id> | sed 's/.*-//')
git worktree add "../${REPO_NAME}-${SHORT}" -b "beads/${SHORT}"
cd "../${REPO_NAME}-${SHORT}"
```

**Worktree is OPTIONAL for**: review-only beads with no file edits; tiny docs/config edits where the current worktree is clean.

**Worktree is REQUIRED for**: any bead that may run formatters, tests with generated output, package installs, broad search/replace, or touches shared files.

**If you skip the worktree and find unexpected local changes**: stop. Move to a worktree before continuing.

When done: `git worktree remove "../${REPO_NAME}-${SHORT}"`.

## Release

- `bd close <id>` — work complete. Terminal.
- `bd update <id> --status open` — giving up / decomposing / blocked on external. Non-terminal; bead goes back to ready queue.

**`bd close` does NOT close the backing GitHub Issue.** The GH Issue closes when a commit with `fixes #N` lands on the default branch. For beads-native work (no backing GH issue), `bd close` is sufficient.

## Stale claim recovery

**Force-release is exceptional repair, not queue hygiene.** The stale-claim path (`bd update <id> --status open --assignee ""`) is an unchecked write — any actor can steal any claim. Abuse it and agents will undo each other's work.

Force-release is appropriate only when **all three** are true:

1. `started_at` is at least **4 hours** old (implementation beads) or **30 minutes** (review/dispatch beads).
2. No recent git activity from the prior claimant: `git log --author=<actor> --since='4 hours ago'`.
3. No active worktree with uncommitted changes belonging to the prior claimant.

If all three hold:

```bash
bd audit record --kind tool_call --tool-name bd --issue-id <id> \
  --response "force-release: started_at=<ts>, no recent activity from <prior-actor>, worktree empty"
bd update <id> --status open --assignee ""
```

The `bd audit record` call is **mandatory** for force-release.

## PR-review lifecycle

Implementation bead stays `in_progress` throughout review (there is no `in-review` status in bd). The review bead BLOCKS the implementation bead via `bd link --type blocks`.

On PR approved: `bd close <review-id>` — impl bead becomes unblocked; merge PR (which auto-closes the GH issue via `fixes #N`); `bd close <impl-id>`.

On changes requested: create an `"address review on PR #N"` bead parented to the impl bead; review bead stays open until re-approval (or close it and create a fresh review bead after address bead closes — one bead = one actionable unit).

## Commits

- `fixes #N` (GitHub Issue number) stays the canonical closure target. Own line at end of commit body.
- **Never** put a bead ID as a closure reference in commits. Bead IDs may appear in body as context only.
- For beads-native work (no backing GH issue): no `fixes` line; describe work in subject, mention bead ID in body.
- The `prepare-commit-msg` git hook (installed by `bd hooks install`) adds an agent identity trailer automatically.

## Reconcile (on-demand, not scheduled)

```bash
GITHUB_TOKEN=$(gh auth token) bd github sync            # bidirectional
GITHUB_TOKEN=$(gh auth token) bd github sync --pull-only
GITHUB_TOKEN=$(gh auth token) bd github sync --dry-run
```

**GH wins for implementation beads**: GH-side state changes (close, reopen, label) propagate on next sync.

**Beads wins for beads-native beads** (PR-review, address-changes, bootstrap epics): no GH counterpart.

Run at: session start (long sessions), suspected drift, after offline periods.

## Audit trail

`bd history <id>` reports Dolt commit author as `"root"` — useless for per-agent forensics. Use `bd audit record` manually at these checkpoints:

| Event | Required audit record |
|---|---|
| Force-releasing another claimant's bead | ✅ mandatory |
| Abandoning a claim (`bd update --status open` after claiming) | ✅ mandatory |
| Creating a PR-review bead | ✅ mandatory |
| Review approved / changes-requested transitions | ✅ mandatory |
| Swarm / gate / merge-slot decisions | ✅ mandatory |
| Manual `bd github sync --prefer-local` resolving drift | ✅ mandatory |
| Normal claim (`bd update --claim`) | ❌ skip — bead state captures ownership |
| Normal close (`bd close`) | ❌ skip |

Records append to `.beads/interactions.jsonl`. Git commit forensics are handled separately by `prepare-commit-msg`.

## Anti-patterns

- **Never `bd edit`** — opens `$EDITOR`, hangs non-interactive agents. Always use `bd update <id> --flag`.
- **Use stdin for tricky content** — `bd create "..." --body-file -` or `--stdin` when the description has backticks, `!`, or nested quotes.
- **Always `--json` for programmatic use** — pretty-print is for humans.
- **Don't auto-steal stale claims** — force-release is exceptional repair.
- **Don't run `bd` from inside a worktree you're about to delete** — run from the primary repo path.
- **Don't skip the audit record** when the table above says it's mandatory.

## Known gaps (accepted limitations)

- **No heartbeat primitive** — bd has no way to signal "I'm still working." The 4-hour stale threshold is a compromise.
- **Per-agent audit is manual** — `bd audit record` discipline depends on agents actually calling it.
- **Force-release is unchecked** — protected only by convention.
- **Imported bead IDs are ugly** (e.g., `<prefix>-<timestamp>-<ordinal>-<hash>`). Only hand-created beads get short IDs.

## Important

- `bd init` creates `.beads/` (backed by Dolt) and modifies `.gitignore` and `.git/info/exclude`. Review changes before committing.
- `bd hooks install` writes to `.git/hooks/` with section markers; coexists with existing hooks.
- The `prepare-commit-msg` hook adds an `Agent:` trailer — don't strip it.
- If you have an existing `.githooks/` directory that's not wired via `core.hooksPath`, it's orphaned; migrate intentionally.
