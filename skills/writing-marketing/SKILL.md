---
name: writing-marketing
description: >-
  Write persuasion-first broadcast copy: sales pitches and pitch emails, cold
  outreach, X/Twitter promotional posts and threads, landing/launch copy, and
  replies courting a prospect. Always use with writing-core (it routes,
  supplies the prose non-negotiables, and provides the writingcheck gate).
  Do NOT select for docs (writing-docs), tracker text (github-writing),
  decision records (writing-spec), or project release notes
  (writing-community) unless the user EXPLICITLY asks for a
  persuasion/sales/conversion pass on an existing draft ("more salesy", "more
  persuasive", "stronger hook", "position this better") — then it runs in
  pass mode: the base scenario keeps structure and the gate; this skill
  contributes hook, specificity, and its honesty rules. Ambiguous requests
  ("improve", "make it compelling", "polish") keep the base scenario only.
  When the user signs the message personally, add their author-voice overlay
  (e.g. my-voice).
---

# Marketing writing

Write copy whose job is conversion: a stranger reads it and replies, clicks,
shares, or buys. The mirror of the other scenario skills — those inform a
reader who already wants the information; this one must first earn the want.
The rules distill the pre-AI persuasion canon (Schwartz, Hopkins, Caples,
Ogilvy, Collier, Cialdini, Halbert, Sugarman, Ries & Trout, Dunford, Heath,
Berger, Sharp, Klaff, Greene); the per-source rule sets live in `references/`.
The canon is battle-tested tradition, not controlled research — where it
conflicts with 2026 channel reality (spam filters, platform norms, law), the
modern-constraints rules below win.

## Honesty boundary (before anything else)

Persuade, never deceive. The **disclosure test** decides what's allowed: a
legitimate mechanism still works after the prospect knows you're using it
(mirroring, generosity, real scarcity, restraint); a manipulative one collapses
the moment it's named (fake scarcity, invented proof, manufactured fear,
engineered confusion). Detection = destruction: one counterfeit trigger,
discovered, permanently discounts every future message from the sender.
Concretely:

- Scarcity and urgency only when real, dated, and explainable ("2 pilot seats
  left because onboarding is hands-on"), never as pressure decoration.
- Social proof named and verifiable; no invented testimonials, no borrowed
  authority, no fabricated demand.
- Name a real cost the reader already pays — never manufacture anxiety they
  didn't have.
- Invite comparison with alternatives; never isolate the prospect from them.
- Stop pushing after the offer is made. One clean close, then silence. No
  pursuing past a no.

## Modern constraints (these override the canon)

The canon predates ML spam filters, sender-reputation scoring, platform
ranking algorithms, email law, and AI-saturated inboxes. Three standing rules:

- **Cold email runs the compliance & deliverability preflight** in
  `references/cold-email-compliance.md` before anything else: jurisdiction
  gate (EU/UK consumers, Germany/Austria, unknown → don't send), truthful
  subject and sender, physical address + human-phrased opt-out, no fake
  "Re:/Fwd:", 0–1 links on your own domain, no shorteners, no attachments.
- **Saturation: specificity must be unfakeable.** Template personalization
  ("quick question about {company}") is itself a detected pattern — for
  filters and humans alike. The opener detail must be something only real
  attention produces: their changelog, their talk, their bug, their metric.
  Classic "power words" (*Free*, *Act now*, *Announcing*) are now spam and
  pattern bait; the canon's formula words are historical winners to test, not
  defaults.
- **Platform culture overrides copy doctrine.** HN, LinkedIn, Product Hunt,
  and Reddit each punish specific persuasion registers — check
  `references/platform-norms.md` before posting there. HN in particular
  rejects nearly everything this skill optimizes for; write for it in
  technical plain-speak with disclosed affiliation and stated limitations.

## 1. Diagnose before drafting: the two dials

Set both dials before writing a word — they determine what the opening is
allowed to say. Full stage-by-stage rules: `references/awareness-stages.md`.

**Awareness** (what this reader knows): unaware → problem-aware →
solution-aware → product-aware → most-aware. Open exactly at the reader's
stage, never ahead of it. Cold email and X posts are problem-aware at best —
no product name in the subject or hook. A solicited pitch is solution-aware —
cap problem education at one paragraph. When unsure, write to the less-aware
stage.

**Sophistication** (how many similar claims they've heard — count competitors'
promises): fresh market → state the claim plainly; crowded → lead with a named
mechanism (HOW, not WHAT); exhausted → sell identity, not claims. A bare
benefit claim ("ship faster!") in a saturated vertical doesn't underperform —
it marks you as spam.

## 2. The persuasion laws (every draft)

1. **One desire, one claim, one CTA.** Pick the single strongest pre-existing
   desire and channel it — copy cannot create desire, only focus it. One
   differentiating claim (own one word; two claims = zero owned). One
   low-commitment ask ("want the writeup?" beats "book a demo").
2. **Specifics are the persuasion engine.** Every superlative converts to a
   measured fact, named mechanism, or gets deleted. "Cold start dropped from
   4.2s to 300ms" — generalities are discounted on sight; exact figures are
   not. Verify every number (writing-core's no-fabricated-specifics rule is
   load-bearing here: an invented stat is both slop and fraud).
3. **The whose-need audit.** Every anti-pattern in this genre reduces to
   self-absorption. For each sentence ask whose need it serves: if it exists
   to relieve *your* anxiety (to seem credible, pre-defend, close faster), cut
   it. The reader must win the subject count.
4. **Zero supplication.** No "just checking in", "sorry to bother", "no
   worries if not", "any chance you could", "let me know your thoughts". The
   linter enforces the list. Replace pleading closers with a decision fork you
   own: "If X fits, reply and I'll send Y; if not, no reply needed."
5. **Give before the ask.** Every touch hands over something usable on its
   own — an insight, a finding, a patch, the writeup itself — delivered in the
   message, not gated behind the call. Never framed as a quid pro quo.
6. **Earn the next sentence.** The subject line exists to get line one read;
   line one to get line two. Hunt for the sentence where you'd stop reading
   and fix that exit ramp. Keep the first sentence short (often 3–10 words) —
   but specificity beats brevity: one researched clause outperforms a terse
   generic opener.
7. **Sell the changed Tuesday.** The after-state in concrete operational
   detail ("your deploys stop paging you at 2am"), second person, future-paced
   — not the feature list. Emotion decides; the numbers you supply are the
   logic that lets them defend the yes.
8. **Diagnose the pain, positive-frame the promise, never shame the reader.**
   The canon looks split — Hopkins/Caples ban gloom, Schwartz dramatizes the
   problem, Berger wants high-arousal anger — and this is the reconciliation:
   dramatize only a real cost the reader already feels (diagnosis), aim any
   anger at the situation or a third party, promise the bright after-state,
   and never moralize at the reader ("most founders get this wrong" is both
   shaming and backfiring negative proof).

## 3. Channel playbooks

### Pitch (deck, one-pager, pitch email)

Load `references/frame-control.md` + `references/dunford-positioning.md`.

- Announce brevity ("3-minute read"), then keep it.
- Order: frame + why-now → big idea → story/intrigue → mechanism + headline
  numbers → the deal → decision step with a date. Not team bios first.
- Big-idea template as a drafting check: "For [target], dissatisfied with
  [current], [product] is a [known category] that [one claim]. Unlike
  [competitor], we [one differentiator]."
- Credentials: 2–3 lines of deeds, then move on. Explaining your authority is
  proof you don't hold the frame.
- Quarantine the analysis: dense numbers in an appendix, after the ask.
- Admit one real limitation before the strongest claim — arguing against
  interest is the cheapest credibility available.

### Cold email / cold DM

Run the preflight in `references/cold-email-compliance.md` first, then load
`references/cold-outreach.md` + `references/collier-letters.md` +
`references/awareness-stages.md`.

- A-pile test: everything must read as one named person writing to one named
  person. Subject like a colleague's note (lowercase, specific, no brackets,
  no emoji); plain text; 3–7 short paragraphs.
- First line: a provably-researched specific about *them* (their talk, their
  changelog, their bug) — accurate attention is the gift. Never "I hope this
  finds you well", never flattery-shaped filler.
- Deliver the value in the body; make the ask free and reversible ("if it's
  not useful, delete it — I won't send another").
- Give a reason-why for the offer ("we take two design partners per quarter
  because…"). Unexplained generosity smells like a scam.
- First line joins the conversation already going on in the reader's head
  (Collier): name their current, provable preoccupation before your offer
  exists in the email.
- Qualify hard: 50 perfectly-picked recipients beat 5,000 sprayed (which also
  burns your domain). Target recent behavior (new funding, new hire, adjacent
  tool adopted), not ICP fit.

**Follow-up sequence** (Collier's measured pattern, still the best data we
have): plan 3–5 touches, then stop — his fifth letter rebounded to 2% after
1%, and everything past five was fruitless. Each touch must add new
information (a result, a milestone, a deadline) AND change the vehicle and
motive — new format, new angle, new appeal — because non-responders to appeal
A aren't dead, they're mis-baited. A contentless bump is supplication. End the
sequence cleanly and say you're ending it; suppress opt-outs forever.

### X/Twitter promo posts and threads

Load `references/stickiness-virality.md` + `references/awareness-stages.md`;
for ongoing presence (not one post), also `references/brand-growth.md`.

- The hook is the headline: open with the pattern break, dramatized problem,
  or identification — never "I built X". Product name appears after the
  problem and mechanism have landed.
- One core claim per post, in words a stranger uses (curse-of-knowledge
  strip: no term that only makes sense after reading your docs).
- One concrete artifact per post: number, screenshot, before/after, exact
  command. The feed discounts unproven claims to zero.
- Write for the sharer's status, not yours: hand over a remarkable fact they
  can retell to look smart. Self-congratulation doesn't get amplified.
- Tie to a frequent trigger (a weekly pain, a daily tool) and pick one
  high-arousal emotion (awe, righteous anger, excitement) — calm-informative
  is read, not spread.
- Retelling test for threads: if someone recounts it at lunch, does the
  product survive the retelling, or only the punchline?
- The hook's promise must be paid off in full — a stiffed curiosity loop
  spends trust you can't rebuild.
- For the ongoing feed (Sharp): cadence beats virality, same distinctive
  assets every post, anchor posts to category entry points ("when CI goes
  red…"), and write every post for someone seeing you for roughly the first
  time — light buyers, not the fans, are where growth lives.

### Landing / launch page

Load `references/dunford-positioning.md` + `references/direct-response.md` +
`references/ogilvy.md`.

- Hero line = "[category] that [differentiated value] for [who]" — the
  positioning chain compressed to one testable sentence. Category before any
  feature or adjective; the reader can't evaluate "fast" until they know fast
  compared to what.
- Page order mirrors the sales narrative: problem/insight → what people do
  today and where it falls short (including do-nothing) → what a real fix
  looks like → product-as-category → proof. Features never lead.
- Proof hierarchy: named customer + exact number > reproducible benchmark >
  testimonial > adjective. Humanize every stat; name the hardest case you
  handle (the Sinatra test).
- This is the channel where long copy earns its keep (interested readers read
  everything): sub-heads every few paragraphs, second person, every sentence
  carries a verifiable fact. Captions on every image — they're read more than
  body copy. No body text in reverse type.
- State who it's wrong for next to the pricing; anchor the price against a
  familiar alternative. Risk-reversal near the CTA. One CTA per awareness
  stage: try-it for solution-aware visitors, docs/proof for skeptics.
- Launch day is one spike in a permanent presence, not the event — keep name,
  claim, and assets identical before, during, and after.

### Platform launches (HN, LinkedIn, Product Hunt, Reddit)

Load `references/platform-norms.md` — its rules override this skill's
persuasion register wherever they conflict. Highlights: Show HN needs a
try-it-now artifact, a plain factual title, and a first comment with
backstory + how it works + known limitations; LinkedIn buries external links
and rewards hook-first native posts; Reddit requires disclosed affiliation
and a 10:1 contribution ratio; Product Hunt is a credibility play, not a
customer channel.

### Outreach replies (inbound prospect, warm thread)

Load `references/persuasion-principles.md` + the **anti-seducer table and
ethical boundary only** from `references/seduction-transfer.md` (§1 and §4 —
the archetype and funnel sections are opt-in reading, not reply-drafting
material; their register doesn't belong in business threads).

- Mirror their framing and vocabulary before adding your point — write the
  first paragraph as if from inside their standup.
- Match the ask to the earned trust; escalate micro-commitments (reply →
  resource → call), never jump to the close.
- Never argue with an objection in public; concede or redirect — onlookers
  side with composure.
- Answer the question fully (generosity), state the one next step, stop. End
  sequences cleanly: "closing the loop — I'll stop here" beats trailing off.

## 4. Positioning consistency (cross-channel)

The bio, the pitch, and the email must carry the same category and the same
primary claim — inconsistency resets the position to zero. Exclude someone
explicitly ("for solo devs", "for repos under 10k stars"); copy with no
excluded audience has no audience. (Examples throughout this skill are
dev-tools-shaped; the rules are category-generic.)

Three positioning layers, load as needed:

- `references/dunford-positioning.md` — the modern B2B method (category as
  context, real competitive alternatives incl. do-nothing, the three plays).
  Wins over Ries & Trout for B2B products on conflicts.
- `references/positioning.md` — Ries & Trout: the ladder, one owned word,
  against-positioning, the don't list.
- `references/brand-growth.md` — the Sharp correction layer: distinctive
  assets, category entry points, light buyers, consistency. Wins on *where to
  spend attention*; the others win on what one piece of copy must say.

## Pass mode: persuasion pass on another scenario's draft

Activate only when the user explicitly asks for a persuasion/sales/conversion
pass on an existing draft ("more salesy", "stronger hook", "sell it harder").
Do not infer it from "compelling", "engaging", or "polish". In pass mode, use
ONLY this section plus the honesty boundary and persuasion laws 1–3 — do not
load the channel playbooks, the awareness/sophistication dials, or any
section-ordering rules; those are for base-scenario work and will restructure
the artifact.

- Edit prose in place. Preserve every section header and template element of
  the base artifact; add no headline, CTA block, sales narrative, testimonial,
  or offer the base scenario doesn't already call for.
- Sharpen the existing opening inside the base artifact's first required
  section: BLUF that sells the *why-care*, not a slogan.
- Convert vague benefits to measured specifics; cut supplication and hype;
  surface the one claim the piece should own.
- The honesty boundary applies in full — never introduce urgency, scarcity,
  proof, or claims not already supported by cited evidence, source
  inspection, or user-provided facts.
- Gate with the BASE scenario (not `writing-marketing`), adding
  `--overlay my-voice` when active. The checker doesn't run `Marketing.*`
  rules in this mode, so walk the honesty checklist manually: no manufactured
  urgency, no invented scarcity, no unverifiable proof, no hype, no
  supplication.
- If the author-voice overlay applies, run that pass after this one, then
  re-gate — voice finishes last.

## 5. Gate before delivering (mandatory)

(In pass mode, gate with the base scenario instead — see Pass mode above.)
Run writing-core's checker with this scenario:

```bash
python3 <writing-core-skill-path>/scripts/writingcheck.py writing-marketing draft.md
# or pipe ephemeral text:
echo "$DRAFT" | python3 <writing-core-skill-path>/scripts/writingcheck.py writing-marketing -
```

The `Marketing.*` rules block on supplication, manufactured urgency, and
unverifiable hype; scarcity claims and negative social proof surface as
advisories with rewrite guidance (real, numbered, explained scarcity is
allowed — see the honesty boundary). writing-core's 3-pass limit and
deliberate-findings protocol apply. Then the checks the linter can't do:
every claim survives the reader fact-checking it, every scarcity/proof
statement is literally true, and — for cold email — the compliance preflight
in `references/cold-email-compliance.md` passed (jurisdiction, address,
opt-out, truthful headers).

## Reserved: conversational selling

Back-and-forth selling (negotiation threads, live DM exchanges, objection
handling over multiple turns — Voss-style mirroring/labeling, calibrated
questions) is out of scope for this broadcast-focused skill. When that
follow-up is researched, it lands as `references/conversational-selling.md`
and a playbook section here.

## References (load per channel, as marked above)

- `references/awareness-stages.md` — Schwartz: awareness + sophistication
  dials, intensification, belief chains, channel mapping.
- `references/direct-response.md` — Hopkins + Caples: headline laws,
  specificity, tested winners and losers.
- `references/ogilvy.md` — Ogilvy: research-first big ideas, respect-the-
  reader, brand compounding, layout rules for landing pages.
- `references/cold-outreach.md` — Halbert + Sugarman: A-pile mechanics,
  slippery slide, psychological triggers.
- `references/collier-letters.md` — Collier: enter the reader's mental
  conversation, six essentials, measured five-touch follow-up sequences.
- `references/cold-email-compliance.md` — the mandatory cold-email preflight:
  jurisdiction law (CAN-SPAM/GDPR/PECR/CASL), deliverability, copy rules.
- `references/persuasion-principles.md` — Cialdini: the 7 principles with
  backfire conditions and per-channel starting hypotheses.
- `references/positioning.md` — Ries & Trout: category, one word, ladder,
  templates.
- `references/dunford-positioning.md` — Dunford: positioning as context,
  competitive alternatives, the three plays, sales-narrative order.
- `references/brand-growth.md` — Sharp/Ehrenberg-Bass correction layer:
  mental availability, distinctive assets, light buyers, consistency.
- `references/stickiness-virality.md` — Heath + Berger: SUCCESs + STEPPS for
  hooks and shareability.
- `references/platform-norms.md` — HN/Show HN, LinkedIn, Product Hunt,
  Reddit: channel culture that overrides copy doctrine.
- `references/frame-control.md` — Klaff: anti-neediness and frame rules,
  STRONG structure (evidence caveats up front; the banned-supplication list
  is the durable core).
- `references/seduction-transfer.md` — Greene: anti-seducer anti-patterns and
  the encode/reject ethical split (replies load §1 + §4 only).
