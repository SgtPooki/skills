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
