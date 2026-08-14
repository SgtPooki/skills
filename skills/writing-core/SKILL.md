---
name: writing-core
description: >-
  Universal prose-quality layer for any drafting task — docs, PR descriptions,
  issues, specs, release notes, announcements. Load whenever you are about to
  write text a human will read (e.g. "write a README", "draft a PR
  description", "write the announcement"). Routes to the correct scenario
  writing skill and enforces the non-negotiables (no AI slop, no fabricated
  specifics, audience-first). Always use together with exactly one scenario
  skill; do not use alone unless no scenario skill matches.
---

# Writing core: route, draft, gate

## 1. Route first

Answer two questions before drafting:

**Who is the attributed author?** If the text is sent, signed, or published
from the user's own account — including project-neutral artifacts like PR
descriptions and issue bodies — add their author-voice skill (e.g. a personal
`my-voice` skill) as an overlay. Its mechanical rules (punctuation, emoji)
apply to everything they publish; its voice-register rules follow the
artifact's register. Skip the overlay only for text another account or bot
publishes on the project's behalf.

**What is the artifact?** Pick exactly one scenario skill:

| Artifact | Skill |
|---|---|
| Issue, PR description, review comment, commit message | `github-writing` |
| Persistent doc: README, tutorial, how-to, reference, migration guide | `writing-docs` |
| ADR, RFC, design spec, requirements — anything that records or constrains a decision, even when stored under `docs/` | `writing-spec` |
| Release note, announcement, changelog, project status post | `writing-community` |
| Persuasion copy: sales pitch, cold email, promo post/thread, landing/launch copy, prospect reply | `writing-marketing` |

Edge rules: a doc that *explains current behavior* is `writing-docs` even if it
lives next to ADRs; a doc that *records a decision* is `writing-spec` even if it
lives under `docs/`. Migration guides are `writing-docs` (their Migration
section is the one place change-oriented language is allowed there).

The community/marketing edge: text that speaks as the project to people who
already follow it (release note, status update) is `writing-community`; text
that must convert strangers into users or customers (launch copy, promo
thread, pitch) is `writing-marketing`. A launch announcement aimed at both
uses `writing-community` structure with `writing-marketing`'s hook and
positioning rules.

If unsure: **artifact purpose beats delivery mechanism.** An RFC posted as a
GitHub issue is an RFC — use `writing-spec`. A security advisory is an
announcement — use `writing-community` (incident register). A project
announcement the user signs personally is `writing-community` for structure
plus the author-voice overlay for idiom.

Default audience dial: spec → expert, docs/github → developer, community → mixed.

## 2. Non-negotiables while drafting

- **BLUF.** The first sentence of the document — and of every section — carries
  the point. Support follows. Never build up to the conclusion. A descriptive
  heading itself satisfies BLUF for its section: under `### Impact`, state the
  impact — don't write a summary sentence that repeats the heading.
- **No fabricated specifics.** Every number, date, version, and behavior claim
  must be verified (run it, read the source, or link the authority). If you
  can't source it, cut it or state the uncertainty. Never invent a statistic to
  strengthen a point.
- **Specificity over vagueness.** "2.3× slower on the p99 path" beats
  "significantly slower". If no specific exists, the claim probably doesn't
  belong.
- **Audience dial.** expert: full jargon, no definitions. developer: standard
  dev vocabulary, define project-specific terms at first use. mixed: define all
  terms at first use, prefer the everyday word. non-technical: no jargon,
  concrete analogies only where accurate.
- **No AI smell.** No filler transitions, no throat-clearing openers, no
  closing section that restates the body, no single-bullet lists, no runs of
  symmetrical bullets that give every point equal weight, no headings over
  one-sentence sections. The linter enforces the concrete word list — see
  step 3.
- **Hedges split two ways.** Epistemic hedges carry information ("untested on
  Windows", "as of v2.3") — keep them; deleting one is a correctness bug.
  Reflexive hedges are tics ("arguably") — cut them, never the epistemic kind.

Before running the checker on a full draft, do the one-pass tightening in
`references/revision-pass.md` — it fixes mechanically what the linter can only
flag.

## 3. Gate before delivering (mandatory)

Run the checker on every draft before presenting it as done. The checker lives
in this skill's directory — resolve `<writing-core-skill-path>` to wherever
this SKILL.md is installed (in the skills repo: `skills/writing-core`).

```bash
# file on disk:
python3 <writing-core-skill-path>/scripts/writingcheck.py <scenario> path/to/draft.md

# ephemeral text (PR body, issue text, commit message) — pipe it:
echo "$DRAFT" | python3 <writing-core-skill-path>/scripts/writingcheck.py github-writing -

# author-voice overlay active? add: --overlay my-voice
```

`<scenario>` is the scenario skill name (`writing-docs`, `github-writing`,
`writing-spec`, `writing-community`, `writing-marketing`), or `core` if none
matched. The checker
uses Vale with vendored configs when available and falls back to reduced checks
(reported as `VALE_MISSING` / "reduced checks" in the verdict line) when not —
it never silently skips.

**What a PASS means:** no known mechanical smells. It does NOT mean the draft's
claims are verified — the no-fabricated-specifics rule is discharged by YOU
(running commands, reading source, linking authorities), never by the linter.
`Claims.UnattributedStat` notes are hints, not the check itself.

Fix every ERROR and re-run, **at most 3 passes — then stop.** Intentional
structure may remain after that: present the draft and note, in one line each,
the findings you kept deliberately. Advisory notes are judgment calls, not
obligations. Do not weaken a true claim to satisfy the linter — rewrite the
sentence instead. Break any rule in this skill sooner than write something
barbarous.

Scope notes: the checker's built-in `--overlay` supports only `my-voice`
(single-tenant, not a plugin system). The rules and word lists are
English-only.

## 4. Composition and precedence

The skills compose: exactly one scenario skill owns structure, and overlays
stack on top, applied in any order across iterative passes. "Draft it for
GitHub" → "now do it in my voice" → "make it a little more salesy" is the
intended workflow — each pass edits the same draft, and the gate runs after
every pass.

- The scenario skill owns document structure and section templates.
- The author-voice overlay, when active, owns punctuation and idiom; its rules
  win over scenario-skill style on conflict.
- `writing-marketing` applied as a persuasion pass on another scenario's draft
  (only on request) contributes hook, specificity, and its honesty rules — the
  base scenario keeps its structure and remains the writingcheck `<scenario>`.
- This skill's non-negotiables (step 2) apply everywhere.

## References (load on demand)

- `references/reader-mechanics.md` — sentence-level mechanics (Gopen & Swan:
  subject-verb proximity, topic/stress position). Use for specs and long-form
  docs where sentence flow matters.
- `references/revision-pass.md` — the one-pass tightening procedure (Lanham's
  Paramedic Method) to run between drafting and the checker.
- `references/sources.md` — the bibliography behind these rules.
