# GitHub Writing

Write GitHub issues and PR descriptions that are self-contained, specific, and easy to scan.

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

## Documentation Voice (docs, READMEs, design notes)

Write for a future reader who has no history of how things used to be and no stake in why the change happened. Apply this to any persistent documentation file, not just PR/issue text.

### Future-oriented, not change-oriented

Documentation describes the system as it is now. It is not a changelog and not a PR description.

- Bad: "We changed the callback names from X to Y to make them consistent."
- Good: "Progress events use the `onFooStarted` / `onFooComplete` naming pattern."
- Bad: "Previously the API exposed N callbacks; now it exposes M unified events."
- Good: "The API exposes M unified progress events listed below."

If contrast with a prior version genuinely helps a reader (e.g., migration guide), put it in a clearly scoped "Migration" or "Upgrading from vN" section. Otherwise cut it.

Before committing docs, re-read each paragraph as your future self with no memory of the change. If a line only makes sense to someone who lived through the diff, delete it.

### Neutral framing of upstream / dependencies

Do not critique upstream projects, SDKs, or dependencies in documentation. It reads as snobbish, ages badly, and creates friction with maintainers and partners.

Avoid:
- "Upstream did X poorly, so we do Y."
- "The underlying SDK's design is confusing, which is why we wrap it."
- "We fix the awkward callback shape from the dependency."

Prefer:
- State what this project does, in its own terms.
- If you must reference upstream behavior for technical accuracy, describe it factually: "Synapse emits per-callback events; this library aggregates them into a single progress stream."
- Describe tradeoffs as design choices for this project, not as corrections to someone else's work.

### Cut change-justification

Lines that exist to justify a decision to reviewers belong in the PR description, commit message, or an ADR — not in user-facing docs. Ask of every sentence: "Would a reader who arrived a year from now care?" If no, remove it.

### Verify before asserting

If a doc states how a tool, compiler, library, or API behaves, the writer must have verified that behavior — by reading the source, running it, or checking authoritative docs. Confident-sounding claims that turn out to be false are worse than no claim at all. If unsure, link to the authoritative reference instead of paraphrasing it.

### Link, don't restate

When the source code, type definition, or API spec is the authoritative truth, link to it rather than copying it into prose. Restated definitions drift from the source and become subtly wrong. Examples and illustrative snippets are fine; verbatim copies of type defs that already live in the repo are not.

## Anti-AI Smell

Avoid:
- `Additionally`
- `Furthermore`
- `It is worth noting`
- `comprehensive`
- `robust`
- `leverages`
- `facilitates`
- `ensure`
- closing summaries that repeat the body
- symmetrical bullet lists that make every point look equally important
- headings for one-sentence sections
- bullet lists with only one item

Em dashes are allowed when they read naturally, but do not use the formula `X — not Y, but Z`.

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
