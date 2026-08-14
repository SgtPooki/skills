# Cold email compliance & deliverability preflight (as of Aug 2026)

Modern channel constraints override the direct-response canon: a legally
non-compliant or filter-flagged email converts at zero. Rules marked **[COPY]**
are checkable against the draft alone; **[INFRA]** need campaign/DNS context —
when that context is unknown, warn, don't pass. Verify penalty figures and
per-country rules before quoting them; they change.

## 0. Jurisdiction gate (run first, per recipient)

1. **Determine recipient jurisdiction and B2B/B2C status before drafting.** Unknown → treat as the strictest regime.
2. **US, B2B or B2C:** cold email is legal if CAN-SPAM-compliant (opt-out regime; no prior consent required). Apply section 1.
3. **UK, B2B corporate subscriber** (ltd/LLP at work address): permitted without consent under PECR reg. 22's corporate carve-out, but UK GDPR still applies to the individual — document a legitimate-interest assessment, provide/link a privacy notice in the first message, honor objection/erasure. UK sole traders count as individuals → treat as consumers → don't cold email.
4. **EU, B2B:** country-dependent (ePrivacy art. 13 lets states choose). **Germany and Austria: do not cold email** — UWG §7(2) requires prior express consent even B2B, enforced by cease-and-desist. Opt-out-style states (e.g. France, Ireland, Netherlands in practice): defensible only if the offer is relevant to the recipient's professional role, an LIA is documented, GDPR art. 14 information is provided, and opt-out is immediate. Can't name the country's rule → don't send.
5. **EU or UK consumer (personal address like gmail.com): do not cold email.** Opt-in required; legitimate interest doesn't cover it.
6. **Canada: do not cold email without a CASL consent basis** (express consent, existing business relationship within 24 months, or conspicuously-published role-relevant address without a no-solicitation notice — a scraped list does not qualify). Penalties up to CAD 10M.
7. **Jurisdiction unknown → don't send** (or route to a non-email channel).
8. **Prior opt-out (any regime) → never email again, never transfer the address.**

## 1. Legal content requirements (CAN-SPAM; good hygiene everywhere)

- **[INFRA] From, reply-to, and originating domain truthfully identify the sender.** No lookalike sender names.
- **[COPY] Subject line must not be deceptive.**
- **[COPY] No fake "Re:"/"Fwd:"/"following up on our call" when there was no prior thread.** Deceptive-header conduct under CAN-SPAM, and it destroys trust the moment the recipient checks. Hard fail.
- **[COPY] Don't disguise the pitch as a personal or transactional message** — a plainly commercial ask satisfies the identification requirement.
- **[COPY] Include a valid physical postal address** (street, registered PO box, or CMRA box). Footer is fine.
- **[COPY] Include a working opt-out** an ordinary person can recognize: reply-to-opt-out or a single page, no fee/login/extra data; keep it working ≥30 days; honor within 10 business days.
- **The sender is liable even when a tool/agency sends on their behalf.** Per-email penalties run ~$50k+ (inflation-adjusted annually — verify at ftc.gov before quoting).

## 2. Deliverability — infrastructure

Context: since 2024–2025, Google/Yahoo/Microsoft require SPF + DKIM + aligned
DMARC, one-click unsubscribe on marketing mail, and spam-complaint rates under
0.3% for bulk senders; Google now rejects (not just spam-folders)
non-compliant traffic. Below the 5,000/day threshold the same signals still
drive placement.

- **[INFRA] SPF and DKIM pass; DMARC published and aligned with the From: domain.**
- **[INFRA] Use a separate sending domain for cold outreach, never the primary company domain.**
- **[INFRA] Warm up new domains/inboxes for weeks before cold sends; never spike volume.** (Exact warm-up numbers are vendor folklore; "new domain + immediate volume = flagged" is the solid part.)
- **[INFRA] Keep per-inbox cold volume modest (~20–50/day is the 2026 practitioner band); scale with more inboxes, not bigger blasts.** Heuristic, not a provider-published limit.
- **[INFRA] Target spam-complaint rate under 0.1%; 0.3% is the enforcement cliff, not a budget.** Monitor via Google Postmaster Tools.
- **[INFRA] If it's templated and sequenced, treat it as bulk:** implement RFC 8058 one-click unsubscribe headers. True 1:1 low-volume outreach typically relies on a visible reply-to-opt-out instead; the boundary is genuinely fuzzy — when in doubt, comply as bulk.

## 3. Deliverability — the copy itself

Filters are ML- and reputation-driven; static spam-word lists are mostly
obsolete as a primary signal, but content patterns still contribute — and
Gmail's models now detect *templated sales copy itself*, so personalization is
a deliverability feature, not just a conversion one.

- **[COPY] Personalize substantively** — a detail that could only apply to this recipient, not merge-field name/company. Uniform bodies across a batch are themselves a detectable signal.
- **[COPY] Write for a reply** — replies are the strongest positive engagement signal a cold sender can earn. End with one low-friction question, not calendar link + deck + demo ask.
- **[COPY] Link budget: 0–1 links, on your own domain.** No URL shorteners (flagged); tracked links only via a custom tracking domain — never a shared one.
- **[COPY] Prefer plain text or minimal HTML; no images in a first touch; skip open-tracking pixels.** (Evidence on pure-plain vs light-HTML is mixed; the robust rule is "no heavy HTML, no images — format is second-order to reputation.")
- **[COPY] Avoid the residual hard patterns:** ALL-CAPS words, stacked punctuation, money-and-urgency framing ("act now", "limited time", "100% free", "guaranteed"), too-good-to-be-true claims. Density and combination matter more than any single word.
- **[COPY] Keep the body ~50–125 words; subject honest, lowercase-normal, specific** — internal-memo tone, not headline tone.
- **[COPY] No attachments in a cold first touch.**

## 4. The compliance footer that doesn't sound like bulk mail

- **[COPY] Minimum contents of every cold email:** real name + company, physical postal address, opt-out line.
- **[COPY] Phrase the opt-out as a human sentence:** "If this isn't relevant, reply 'no thanks' and I won't email again." Avoid "click here to unsubscribe from our mailing list" in a 1:1-styled note — it flags the mail as bulk to filters and humans alike. (If the mail genuinely is bulk, the RFC 8058 header + visible unsubscribe is required regardless of tone.)
- **[COPY] UK/EU legitimate-interest sends:** add a one-line source-and-rights notice ("I found your details on X; privacy notice: URL; reply 'stop' and I'll delete your details").
- **Honor every opt-out permanently, across sequences** — suppression list before every send. Post-opt-out sends are the most common enforcement pattern in recent ICO actions.

## 5. Auto-fail summary (any one blocks the send)

- Fake "Re:"/"Fwd:" or fabricated prior-contact claims.
- Deceptive subject or disguised sender.
- No physical address or no working opt-out.
- Recipient on suppression list.
- EU/UK consumer, Germany/Austria, or jurisdiction-unknown recipient without consent.
- Canadian recipient with no CASL basis.
- Sending domain lacks SPF/DKIM/aligned DMARC (when known).
- URL shortener in the body.

## Genuinely uncertain (flag, don't assert)

- Exact per-inbox volume and warm-up schedules (practitioner consensus only).
- Whether low-volume 1:1 sequences fall under the bulk one-click-unsubscribe mandate.
- Current CAN-SPAM per-email penalty figure (adjusts annually).
- Plain-text vs light-HTML (conflicting data; second-order).
- Which EU states allow B2B opt-out (shifts with national law — verify per country).

## Sources

- https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business (primary)
- https://support.google.com/a/answer/14229414 (primary — sender guidelines FAQ)
- https://www.salespeople.co.uk/explained/cold-email-pecr-regulation-22
- https://overloop.com/blog/b2b-cold-email-germany-gdpr-compliance
- https://reachoutly.com/cold-email/legality/
- https://redsift.com/guides/bulk-email-sender-requirements
- https://powerdmarc.com/gmail-enforcement-email-rejection/
- https://www.valimail.com/blog/one-click-unsubscribe/
- https://www.autobound.ai/blog/spam-trigger-words-sales-emails-deliverability-guide
