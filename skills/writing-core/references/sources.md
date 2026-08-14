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
- Williams, *Style: Lessons in Clarity and Grace*, 1981–2021 — the source
  Gopen & Swan applied to science: characters as subjects, actions as verbs,
  cohesion (old-before-new) vs coherence (topic strings), metadiscourse,
  conditional (not banned) passive and nominalization. Basis of the
  nominalization fixes in `revision-pass.md`.
- Lanham, *Revising Prose*, 1979 — the Paramedic Method and the lard factor;
  the operationalized form of "omit needless words". Basis of
  `revision-pass.md`.
- Nielsen & Morkes, "Concise, SCANNABLE, and Objective", 1997 — controlled
  web-usability experiment: +58% concise, +47% scannable, +27% objective
  (non-promotional) language, +124% combined. Empirical basis for the
  no-marketing-language and scannability rules.

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

- Booth, Colomb & Williams, *The Craft of Research*, 1995 — the argument
  model (claim → reasons → evidence → warrant → acknowledgment and response)
  and the problem-statement formula (context + destabilizing condition +
  cost). Basis of writing-spec's Argument check.
- Garner, *Legal Writing in Plain English*, 2001, and the Language-Change
  Index — tabulated conditions for dense conditional logic; graded (not
  binary) treatment of contested usage. For normative spec language read
  adversarially.
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

## Corroboration, with caveats

Consulted, not rule sources. Strunk & White's durable rules (stress position,
subject near verb, one topic per paragraph, parallelism) are already here via
Gopen & Swan and plain language; its grammar folklore is corpus-falsified
(Pullum, "50 Years of Stupid Grammar Advice", 2009). Pinker's *Sense of
Style* restates Williams/Gopen & Swan ground from psycholinguistics; its
classic style (from Thomas & Turner, *Clear and Simple as the Truth*) fits
tutorials and explanations but is by its own authors' taxonomy wrong for
reference docs, runbooks, and trackers, where the reader has a job. Graff &
Birkenstein's *They Say / I Say* supplies the fair-summary and naysayer moves
behind writing-spec's Argument check (no empirical validation; the literal
templates are academic register — don't lift them). Le Guin's *Steering the
Craft* backs the read-aloud test and one-name-per-concept repetition. Becker,
Sword, and Schimel: hedging as defensive armor, the stated-vs-enacted gap
that justifies a checker, and the OCAR overclaim guard.

## Persuasion and marketing (writing-marketing)

The persuasion canon behind `writing-marketing`; per-source rule extractions
with citations live in `skills/writing-marketing/references/`.

- Hopkins, *Scientific Advertising*, 1923; Caples, *Tested Advertising
  Methods* — specificity over superlatives, headline laws, tested
  winners/losers. `direct-response.md`.
- Schwartz, *Breakthrough Advertising*, 1966 — awareness stages, market
  sophistication, intensification, belief chains. `awareness-stages.md`.
- Cialdini, *Influence*, 1984/2021 — the 7 principles with backfire
  conditions; smuggler-vs-detective ethics. `persuasion-principles.md`.
- Ries & Trout, *Positioning*, 1981 — category, one owned word, the ladder.
  `positioning.md`.
- Halbert, *The Boron Letters*; Sugarman, *The Adweek Copywriting Handbook* —
  A-pile mechanics, slippery slide, triggers. `cold-outreach.md`.
- Heath & Heath, *Made to Stick*, 2007; Berger, *Contagious*, 2013 — SUCCESs
  and STEPPS; stickiness and shareability. `stickiness-virality.md`.
- Klaff, *Pitch Anything*, 2011 — frame control, prizing, anti-supplication
  (used with stated evidence caveats). `frame-control.md`.
- Ogilvy, *Confessions of an Advertising Man*, 1963; *Ogilvy on
  Advertising*, 1983 — research-first big ideas, respect-the-reader, brand
  compounding, landing-page layout. `ogilvy.md`.
- Collier, *The Robert Collier Letter Book*, 1931 — enter the reader's mental
  conversation; measured five-touch sequences. `collier-letters.md`.
- Dunford, *Obviously Awesome*, 2019 — positioning as context-setting; the
  modern B2B correction to Ries & Trout. `dunford-positioning.md`.
- Sharp, *How Brands Grow*, 2010 (Ehrenberg-Bass) — mental availability,
  distinctive assets, light buyers; correction layer with stated B2C-data
  caveats. `brand-growth.md`.
- Current-law and platform references (CAN-SPAM/GDPR/PECR/CASL, Gmail sender
  requirements, Show HN guidelines) — `cold-email-compliance.md`,
  `platform-norms.md`; date-stamped, verify before quoting.
- Greene, *The Art of Seduction*, 2001 — anti-seducer anti-patterns and the
  encode/reject ethical split; only disclosure-surviving mechanisms encoded.
  `seduction-transfer.md`.
