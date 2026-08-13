# Sources

The bibliography behind the writing-* skill family. Sources are deliberately
weighted toward pre-LLM-era, evidence-based work so the guidance is not
circularly derived from AI-generated writing advice.

## Prose mechanics and clarity

- Gopen & Swan, "The Science of Scientific Writing", American Scientist, 1990 —
  position-based reading: subject-verb proximity, topic/stress position.
  Basis of `reader-mechanics.md`.
- Orwell, "Politics and the English Language", 1946 — six rules; rule 6 ("break
  any of these rules sooner than say anything outright barbarous") is the
  escape hatch quoted in writing-core.
- Zinsser, *On Writing Well*, 1976 — cut every needless word; clarity,
  simplicity, humanity.
- BLUF (US military, formalized 1988) and Minto's Pyramid Principle —
  answer-first structure. NN/g eyetracking (2006, replicated 2017): ~79% of
  web readers scan, reading ~20-28% of a page — front-load everything.

## Plain language (the audience dial)

- ISO 24495-1:2023 — plain language principles: relevant, findable,
  understandable, actionable.
- Kimble, *Writing for Dollars, Writing to Please* — 60 empirical studies on
  plain-language outcomes.
- ASD-STE100 Simplified Technical English — one word one meaning, short
  sentences, active voice (the thinking, not the controlled dictionary).
- plainlanguage.gov, GOV.UK style guide.

## Documentation structure (writing-docs)

- Diátaxis (Procida) — tutorial / how-to / reference / explanation; one mode
  per page.
- Carroll, *The Nurnberg Funnel*, 1990 — minimalism: task-oriented chunks,
  support error recognition and recovery.
- Baker, *Every Page is Page One*, 2013 — self-contained topics; readers
  arrive by search. Suspended for tutorials, which are sequential.
- Redish, *Letting Go of the Words* — web content as conversation.
- Meng et al., "How Developers Use API Documentation" (SIGDOC) — developers
  split time roughly evenly between reference and cookbook content; optimized
  docs measurably reduce task errors.
- ISO/IEC/IEEE 26514:2022 and IEC/IEEE 82079-1:2019 — audience-and-task
  analysis as the root of documentation quality.
- Google developer documentation style guide (enforced via the vendored Vale
  package, not paraphrased).

## Specs and decisions (writing-spec)

- RFC 2119 / RFC 8174 — normative keywords, only when declared.
- MADR (adr.github.io) — ADR template.
- EARS (Mavin, RE'09) — requirement syntax for safety-critical-grade
  requirements; deferred to reference status.
- C4 model (Brown) — context / container / component / code vocabulary.
- RFC 7322, W3C manual of style — terminology consistency in standards prose.

## GitHub artifacts (github-writing)

- Chris Beams, "How to Write a Git Commit Message", 2014 — imperative mood,
  50/72.
- Conventional Commits; Conventional Comments; Keep a Changelog; SemVer.
