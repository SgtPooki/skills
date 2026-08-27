# Claude-signature vocabulary (discourage, don't ban)

Source: "The load-bearing vocabulary of Claude" (louisabraham.github.io/load-bearing/),
a corpus study of ~47k GitHub PR descriptions, Jan 2025 – Aug 2026. One vocabulary
cluster grew from ~1% to ~45% share of all PR prose in that window — the arrival of
Claude-written text. The words below are that cluster's strongest markers (10–120×
lift over the pre-Claude baseline).

## How to apply

Every word here is legitimate English and sometimes the precise term. **None is
banned.** The smell is *density*: these words at many times human base rate is what
makes text read as machine-written, the same way "delve/robust/comprehensive" did in
2023. When sweeping prose you wrote (PR descriptions, commit messages, comments,
docstrings, docs):

- **Two or more signature words in one paragraph** → rewrite the paragraph. State
  the concrete fact the metaphor was gesturing at ("this function is load-bearing"
  → "three call sites depend on this function's ordering guarantee").
- **A signature word used once, as the precise term** → keep it. "Invariant" in a
  correctness argument, "wall-clock" next to CPU time, "verbatim" describing an
  exact copy are the right words.
- Prefer the plain verb over the personified one: code *has* a bug, a test *fails*,
  a change *removes* a path — code does not "quietly refuse", "survive", or
  "sit beside" things.

## The markers, grouped by habit

**Structural metaphors** (code as a building):
load-bearing · seam · ladder · spine · rail · ceiling · headroom · wall ·
machinery · band · trap · hole · leg · arms

**Personified code** (code as an agent with intentions):
quietly · loudly · silently · honest / honestly / honesty · refuses / refusal ·
survives / survived · carries / carrying · sits / sitting · lives · walks ·
arrives · fires / fired · holds / holding · sees · tells · says · asks ·
declares · claims / claimed · judges

**Drama verbs** (routine changes narrated as events):
collapses · folds · degrades · swallowed · surfaced · flips / flipped ·
lands / landed · ships / shipped · recovers · widened · settled · fell ·
gains / gained · loses

**Emphatic qualifiers** (asserting sincerity or exactness):
genuinely / genuine · deliberately / deliberate · precisely · merely ·
structurally · unconditionally · identically · untouched · verbatim ·
nothing / nobody / never / ever / alone / forever (as emphasis)

**Signature jargon** (fine as terms of art, markers when decorative):
byte-identical · wall-clock · fan-out · in-flight · hand-rolled · throwaway ·
pre-fix · one-line · invariant · criterion · divergence · symptom ·
defect(s) · fabricated · cadence · caveat · headline · latent · inert ·
precedent · mechanical · corpus · sweep · baked (in) · keyed · capped
