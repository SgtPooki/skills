# Persuasion principles (Cialdini, *Influence*, incl. 2021 Unity edition)

Rule extraction for broadcast business writing: pitches, cold email, X/Twitter
promo, outreach replies. Each principle: mechanism, application rules, and the
backfire condition. The governing law is at the end (ethics: detection =
destruction).

## Reciprocity

**Mechanism.** People feel obligated to repay what they receive first — the giver, not the asker, controls the exchange.

Rules for broadcast copy:

- Give before you ask: the email or post must contain something usable on its own (a specific insight, audit finding, template, benchmark) before any CTA appears.
- Make the gift specific to the recipient/audience, not generic ("I noticed your checkout flow drops the coupon field on mobile" beats "here's our free ebook").
- Never frame the gift as conditional ("in exchange for 15 minutes…") — a stated quid pro quo converts a gift into a transaction and kills the obligation effect.
- In a cold email, the value must be delivered *in the email body*, not gated behind the call you're asking for.

**Backfire.** Obviously mass-produced or self-serving "gifts" (a link to your own pricing page, a generic PDF) read as bait; the trigger inverts into suspicion. Reciprocity decays — keep the ask near the gift in time.

## Commitment and consistency

**Mechanism.** People align future behavior with prior commitments, especially commitments that are active, effortful, public, and voluntary.

Rules for broadcast copy:

- One CTA per message, small and low-commitment ("worth a 10-minute look?" not "book a 60-minute demo"). Vendor studies consistently find single specific low-commitment asks outperform multiple or heavy asks in cold email; the exact lift varies by study, so treat any quoted percentage as that vendor's data, not a law.
- Ask questions the reader will answer "yes" to about *their own stated goals or public positions* ("you wrote that reliability is your 2026 priority — does X still block that?"), then connect the ask to that commitment.
- Get micro-commitments in sequence across a campaign (reply → resource → call), never all at once.
- Never manufacture a commitment the reader didn't make ("as someone who cares deeply about X…") — presumed commitments read as manipulation.

**Backfire.** Foot-in-the-door escalated too fast, or commitments extracted by trickery, produce reactance and unsubscribes; coerced commitments don't bind at all.

## Social proof

**Mechanism.** Under uncertainty, people infer correct behavior from what similar others do.

Rules for broadcast copy:

- Cite proof from *comparable* others — same role, industry, or size as the reader ("12 Series-A dev-tools teams use this"), not raw global counts; similarity drives the effect.
- Use named, verifiable, specific proof: a named customer, a number with a source, a linkable case study. Ban unattributed superlatives ("industry-leading", "loved by thousands").
- Quantify outcomes, not adoption alone ("cut build times 40% at Acme" beats "trusted by Acme").
- Never state a negative norm: "most teams still ignore this", "90% of people get this wrong", "hardly anyone has signed up yet" — delete or invert to the positive norm.

**Backfire.** Negative social proof normalizes the bad behavior: in Cialdini's Petrified Forest study, the sign "many past visitors have removed wood" produced 7.92% theft vs 1.67% under the injunctive "please don't remove wood" sign (other conditions ran ~4–5%). Copy lamenting how few people do X teaches readers that not-doing-X is normal. Fabricated testimonials, once detected, destroy all future proof claims from that sender.

## Liking

**Mechanism.** People say yes to those they like — driven by similarity, genuine compliments, and cooperation toward shared goals.

Rules for broadcast copy:

- Open with a true, specific point of similarity or a specific compliment about the recipient's actual work ("your post on X changed how we do Y") — verifiable, not flattery-shaped filler ("love what you're building!").
- Write like a person: contractions, first person, the reader's own vocabulary; strip corporate register from outreach and replies.
- Frame the interaction as cooperative ("we're trying to solve the same problem from the other side") rather than adversarial selling.
- In replies, mirror the other person's framing and terminology before adding your point.

**Backfire.** Generic or false flattery is detected instantly, marks the message as automated, and drops reply rates below no-compliment baselines. Phishing research suggests liking/similarity cues are among the most effective in email — which means they are also heavily abused, and recipients are calibrated against fake rapport.

## Authority

**Mechanism.** People defer to credible experts — credibility = expertise + trustworthiness.

Rules for broadcast copy:

- State credentials only when concrete and relevant to the claim ("we run 4,000 nodes in production", "author of the RFC"); prefer a third party or the case study to convey them.
- Cite evidence, not adjectives: link the benchmark, the paper, the postmortem. "Fastest" is banned without the measurement.
- Admit a genuine weakness or limitation before your strongest point ("this isn't for teams under 5 seats, but…") — arguing against interest raises credibility.
- Never borrow authority you don't have: no fake badges, no "as seen in" without a real placement, no implied endorsements.

**Backfire.** Self-proclaimed authority ("we're the experts in…") triggers skepticism. In email, heavy authority signaling combined with urgency is a known phishing signature and arouses suspicion rather than compliance.

## Scarcity

**Mechanism.** Perceived loss and limited availability raise desirability; people are more motivated by what they stand to lose than what they gain.

Rules for broadcast copy:

- State scarcity only when real, specific, and explainable: "3 of 10 pilot seats left", "price changes March 1" — never "limited spots" or "act fast". Test: if you can't explain *why* it's scarce ("we cap at two clients per quarter"), don't claim it.
- Frame the loss, not only the gain: name what the reader forfeits by not acting (a concrete capability, price, or window).
- Never reuse a deadline: an "ending" offer that reappears next week is a detectable lie; countdown timers that reset are banned.
- Use exclusivity honestly ("early access is invite-only this quarter, here's your invite") rather than manufactured urgency.

**Backfire.** The most fragile principle. Detected fake scarcity triggers reactance, anger, and brand-switching (Biraglia et al. 2021: customers who miss a "limited" product show higher intent to switch to competitors, mediated by anger). Scarcity language in cold email also pattern-matches to spam filters and phishing heuristics.

## Unity

**Mechanism.** Sharing an *identity* — "one of us" (profession, place, tribe, cause) — makes influence dramatically easier than mere liking; "we" relationships get more trust, help, and forgiveness.

Rules for broadcast copy:

- Invoke a shared identity only if you genuinely hold it, and name it specifically: "as a fellow maintainer", "from one bootstrapper to another" — never a vague "we're all in this together".
- Use "we/us" language for a real community the reader belongs to (your users, the OSS project), and give it a name and shared vocabulary in ongoing posts.
- Co-create: ask the audience for input or naming ("which should we ship first?") — asking for *advice* (not just "feedback") puts the reader in a merged we-state with you.
- In public posts, speak as a member of the audience's group, not a vendor addressing it.

**Backfire.** Claiming a tribe you don't belong to is the fastest credibility kill available — in-group members detect impostors immediately. Unity framing also polarizes: it hardens out-groups against you.

## Ethics: detection = destruction

Cialdini's line: the ethical practitioner is a **detective** who finds a principle *already truly present* in the situation and surfaces it; the manipulator is a **smuggler** who imports a counterfeit trigger (fake scarcity, invented proof, borrowed authority). The argument is economic, not just moral: each principle works via a shortcut that is *accurate when the evidence is genuine*; the moment counterfeiting is detected, the reader rejects this message, permanently discounts every future signal from the sender, and tells others. Linter-friendly form: **every persuasion claim in the copy must be true, specific, and survivable if the reader fact-checks it.**

## Which principles fit which channel (starting hypotheses, not settled rankings)

Head-to-head academic comparisons are thin, and the phishing literature — the closest thing to adversarial evidence on email compliance — disagrees internally about which principle ranks first. Treat these as defaults to test, not laws:

- **Cold email (1:1 outreach):** phishing/social-engineering studies suggest similarity/liking cues are especially potent in email — which also means recipients are increasingly calibrated against fakes of them. Authority + scarcity *combined* is the canonical phishing pattern and arouses suspicion. Default to test first: genuine-similarity opener → delivered value → single small ask; social proof as support; scarcity rarely and only when explainable.
- **Public posts (X/Twitter, broadcast):** social proof and unity are the natural fits — public channels make "what similar others do" and "who we are" visible and shareable. Scarcity works better here than in email when publicly checkable (real launches, capped cohorts). Authority works best as demonstrated expertise (showing the work), not stated credentials.
- **Everywhere:** active, public, written commitments bind more than passive ones — asks that get the reader to *do* something visible (reply, vote) beat asks to merely read.

## Sources

- https://www.influenceatwork.com/7-principles-of-persuasion/
- https://news.wpcarey.asu.edu/20250422-gentle-science-persuasion-part-seven-unity
- https://www.suebehaviouraldesign.com/en/blog/cialdini-principles-of-persuasion/
- https://onlinelibrary.wiley.com/doi/full/10.1002/mar.21489 (Biraglia et al., scarcity → anger → brand switching)
- https://www.tandfonline.com/doi/full/10.1080/15534510500181459 (Cialdini et al., Petrified Forest norms study)
- https://arxiv.org/pdf/2412.18485 (persuasion tactics observed in phishing corpora; note: ranks tactic *prevalence*, not effectiveness — the liking-effectiveness finding comes from separate compromise-prediction studies)
- https://cxl.com/blog/cialdinis-principles-persuasion/
- https://whali.co.uk/blog/psychology-behind-cold-emails (Salesfolk single-CTA reply-rate data)
- https://bakadesuyo.com/2013/06/robert-cialdini-influence/ (smuggler vs detective ethics)
