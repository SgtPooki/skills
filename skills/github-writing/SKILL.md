---
name: github-writing
description: >-
  Write GitHub-native tracker and review text: issues, PR descriptions, review
  comments, and commit messages. Always use with writing-core (it routes,
  supplies the prose non-negotiables, and provides the writingcheck gate). Do
  NOT use for persistent docs (writing-docs), decision records (writing-spec),
  or public announcements/release notes (writing-community).
---

# GitHub Writing

Write GitHub issues, PR descriptions, review comments, and commit messages that
are self-contained, specific, and easy to scan. Language here is
change-oriented ("Added X", "Fixed Y") — the mirror of writing-docs, which
describes current state.

## Goal

A teammate should understand the problem, impact, and next action in under 60 seconds.

Soft length targets:
- Standard issue: ~150-250 words
- PR description: ~100-200 words
- Investigation tracker issue: ~150 words plus a linked memo

## Workflow

1. Extract the actionable crux.
2. Decide whether the source is an issue, PR, or investigation summary.
3. Keep GitHub focused on the tracker item.
4. Move long background, evidence, option analysis, and reviewer notes into a linked doc.
5. Delete filler, repeated context, and private-conversation framing.
6. Gate before posting: pipe the draft through
   `python3 <writing-core-skill-path>/scripts/writingcheck.py github-writing -`.

## Title Rules

- Follow the repo's existing title convention.
- If the repo uses typed prefixes, `[Type]: brief description`.
- Keep titles specific and skimmable.
- Avoid vague titles like `fix migration issue` or `update upload flow`.

Good:
- `[Bug]: Migrated Storacha datasets are hidden from dataset list`
- `Add upload-action support for explicit dataset IDs`

## Shared Rules

- The body must stand alone.
- Use plain language, but keep exact technical terms when they matter.
- Explain impact, not just symptoms.
- Never mention private conversation context.
- Link related issues/docs instead of assuming the reader knows them.
- Omit empty sections.
- Prefer short paragraphs over long bullet walls.
- Use headings only when they help scanning.
- Cut bullets already implied by another bullet in the same list. Repetition adds noise unless it adds a new constraint.

## Issue Structure

### Description

Start with the core problem: what is broken, missing, or confusing?

### Impact

Who is affected and what does it block?

### Steps to Reproduce

For bugs only. Use numbered, minimal steps.

### Expected Behavior

What should happen?

### Actual Behavior

What happens now?

### Environment

Only include OS, browser, app version, network, wallet type, or device when relevant.

### Additional Context

Logs, screenshots, related issues, minimal repros, or a linked investigation doc.

## PR Structure

Only `What changed` is required. Use the rest only when helpful.

### What changed

1-2 sentences explaining the change and why.

### How to verify

Commands or reviewer steps.

### Notes / risks

Only behavior changes, migrations, or uncertainty.

If the PR needs a migration section for consumers, write that section in docs
voice (state-oriented, scoped "Upgrading from vN") per writing-docs.

## Commit Messages

Follow Chris Beams' rules, plus the repo's own convention:

- Imperative mood in the subject: "Fix retry starvation", never "Fixed" or "Fixes".
- Subject ≤50 characters where practical; hard-wrap the body at 72.
- Blank line between subject and body; the body explains what and why, not how.
- If the repo uses Conventional Commits (`feat:`, `fix:`, `chore:`...), use
  them with the repo's established types and scopes. Do not introduce the
  convention into a repo that doesn't use it.
- Reference issues in the body or footer (`fixes #123`), not the subject.

## Review Comments

Follow Conventional Comments shape without ceremony:

- Lead with a label when it disambiguates: `blocking:` / `non-blocking:` /
  `question:` / `suggestion:`.
- Anchor every comment to the exact file/line or observed behavior.
- State the requested change, not just the objection. "Extract this into a
  guard clause" beats "this is hard to read".
- No "maybe consider possibly" hedging. If it matters, say it plainly; if it
  doesn't block, label it non-blocking.
- Praise is fine when specific; skip empty "LGTM, great work!" padding.

## Investigation Rule

Long source or multiple findings → split:
- Short GitHub issue for the actionable decision or task.
- Linked detail doc for evidence, options, rejected paths, logs, reviewer notes.

Pick doc surface by content type:
- **Gist** (default secret, link-only): raw evidence, logs, repros, code dumps, line-anchor links, markdown-native. Use public only when intentional.
- **Notion / Obsidian**: living memos, decision logs, multi-author edits, embedded media.

The GitHub issue should summarize root cause, impact, current workaround, and proposed next step. Do not paste the full investigation into the issue.

## Final Check

- First sentence explains the issue or change.
- A new reader can act without private context.
- Long evidence is linked, not pasted.
- Optional sections are removed before useful context is removed.
- writingcheck passed (or remaining findings were deliberate).
