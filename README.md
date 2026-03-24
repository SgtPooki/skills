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
