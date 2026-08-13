---
name: writing-docs
description: >-
  Write persistent project documentation: READMEs, tutorials, how-to guides,
  reference docs, explanations, and migration guides. Always use with
  writing-core. Do NOT use for PR descriptions or issues (github-writing),
  decision records like ADRs/RFCs (writing-spec, even when stored under
  docs/), or release notes and announcements (writing-community).
---

# Writing Docs

Write documentation for a future reader who has no history of how things used
to be and no stake in why a change happened. Language here is state-oriented
("X provides Y") — the mirror of github-writing, which is change-oriented.

## Pick the mode first (Diátaxis)

Every page is exactly one of four modes. Decide before writing; do not mix
modes on one page.

| Mode | Reader's situation | Form |
|---|---|---|
| Tutorial | Learning, needs a guaranteed win | Sequential lesson; you own the path and the outcome |
| How-to | Working, has a goal | Numbered steps solving one real task; assume competence |
| Reference | Working, needs facts | Dry, complete, consistent; structured for lookup, not reading |
| Explanation | Studying, wants understanding | Discursive; context, alternatives, why it is the way it is |

Mixing modes is the root cause of most bad docs: a tutorial that stops to
explain design ("why" belongs in explanation), or a reference entry that
teaches (examples belong; lessons don't).

## Structure rules

- **Minimalism (Carroll).** Task-oriented chunks. Let the reader act within the
  first screen. Support error recognition and recovery ("If you see E404 here,
  the manifest is unpinned; run..."). Cut narrative preambles and "In this
  section we will..." scaffolding.
- **Every page is page one (Baker).** Readers arrive by search. Each page
  establishes its own context in the first lines, stands alone, and links
  laterally instead of assuming the previous page was read. Exception:
  tutorials are sequential by design — inside a tutorial, earlier steps may be
  assumed.
- **Reference entries get runnable examples.** Developers split their reading
  roughly evenly between reference and cookbook content; an entry without a
  copy-pasteable example forces them to leave the page.

## Documentation voice

### Future-oriented, not change-oriented

Documentation describes the system as it is now. It is not a changelog and not
a PR description.

- Bad: "We changed the callback names from X to Y to make them consistent."
- Good: "Progress events use the `onFooStarted` / `onFooComplete` naming pattern."
- Bad: "Previously the API exposed N callbacks; now it exposes M unified events."
- Good: "The API exposes M unified progress events listed below."

If contrast with a prior version genuinely helps a reader, put it in a clearly
scoped "Migration" or "Upgrading from vN" section — the one place
change-oriented language is allowed here. Otherwise cut it.

Before committing docs, re-read each paragraph as your future self with no
memory of the change. If a line only makes sense to someone who lived through
the diff, delete it.

### Neutral framing of upstream / dependencies

Do not critique upstream projects, SDKs, or dependencies in documentation. It
reads as snobbish, ages badly, and creates friction with maintainers and
partners.

Avoid:
- "Upstream did X poorly, so we do Y."
- "The underlying SDK's design is confusing, which is why we wrap it."

Prefer:
- State what this project does, in its own terms.
- If upstream behavior matters for accuracy, describe it factually: "Synapse
  emits per-callback events; this library aggregates them into a single
  progress stream."
- Describe tradeoffs as design choices for this project, not as corrections to
  someone else's work.

### Cut change-justification

Lines that exist to justify a decision to reviewers belong in the PR
description, commit message, or an ADR — not in user-facing docs. Ask of every
sentence: "Would a reader who arrived a year from now care?" If no, remove it.

### Link, don't restate

When the source code, type definition, or API spec is the authoritative truth,
link to it rather than copying it into prose. Restated definitions drift from
the source and become subtly wrong. Examples and illustrative snippets are
fine; verbatim copies of type defs that already live in the repo are not.

(Claims about tool/library behavior follow writing-core's verify-before-
asserting rule: run it, read the source, or link the authority.)

## Style mechanics

Google developer-docs style is enforced as advisory notes by the linter
(vendored Vale package) — sentence case headings, active voice, present tense,
second person. Fix the notes when they're right; overrule them when the repo's
existing convention differs.

Note triage: `Google.Passive`, `Google.Will`, and `Google.Headings` are usually
worth acting on. `Google.Parens`, `Google.Semicolons`, `Google.Acronyms`, and
`Google.WordList` are frequently ignorable for a developer audience — scan
them once, don't chase them.

## Gate

```bash
python3 <writing-core-skill-path>/scripts/writingcheck.py writing-docs path/to/page.md
```

Run before presenting any doc as done. Fix errors (max 3 passes), treat notes
as judgment calls.
