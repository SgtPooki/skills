---
name: writing-spec
description: >-
  Write decision and constraint documents: ADRs, RFCs, design specs, and
  requirement docs — anything that records or constrains a decision, even when
  stored under docs/. Always use with writing-core. Do NOT use for docs that
  explain current behavior (writing-docs) or for tracker text (github-writing).
---

# Writing Specs

Write documents that record decisions or constrain future behavior. The
register is precise and technical: exact terms, testable statements, no
approximation. The reader is an expert; do not explain what they already know.

## Pick the mode, apply only that mode's machinery

### ADR mode (architecture decision records)

Use the MADR skeleton, nothing more:

1. **Context** — the forces in play, stated factually. What hurts today, with
   numbers where they exist.
2. **Options** — each option with its honest costs. Two options minimum; a
   decision with one option is an announcement, not a decision record.
3. **Decision** — what was chosen and the deciding factor.
4. **Consequences** — what gets better, what gets worse, what becomes
   impossible. Include the losses; a consequences section with only upsides is
   marketing.

One decision per ADR. Number them; never edit a superseded ADR — write a new
one that references it.

### Requirements mode

- Every requirement must be testable, and every requirement is paired with a
  validation condition: how you will know it is met. "The gateway MUST survive
  restart without dropping sessions. Validation: restart under 50 active
  sessions; all 50 survive." A requirement you can't validate is a wish.
- RFC 2119/8174 keywords (MUST, SHOULD, MAY...) only when the document
  declares them ("The key words MUST, SHOULD... are to be interpreted as
  described in RFC 2119") or the repo already writes specs that way. Without
  the declaration, use plain "must"/"should" consistently.
- One requirement per statement. "The parser MUST accept v2 manifests and
  SHOULD warn on v1" is two requirements; split them.

### Architecture mode

Use C4 vocabulary — context, container, component, code — instead of the
ambiguous "service"/"module"/"system" soup. Name the level you're describing
at the top of each section, and don't mix levels within a diagram or section.

## Terminology discipline (all modes)

One term per concept. Define it once, at first use, then use it verbatim
everywhere — no elegant variation. If two words are floating around for the
same thing ("dataset" vs "collection"), the spec's job is to kill one of them.

## Sentence mechanics

Specs are where sentence position matters most. Read
`<writing-core-skill-path>/references/reader-mechanics.md` before writing long
specs: subject-verb proximity, and putting the normative point in the stress
position at the sentence's end.

## Gate

```bash
python3 <writing-core-skill-path>/scripts/writingcheck.py writing-spec path/to/spec.md
```

The spec config allows normative keywords and parallel requirement lists.
Deferred machinery for unusually rigorous requirement work (EARS syntax) is
described in `references/ears.md`.
