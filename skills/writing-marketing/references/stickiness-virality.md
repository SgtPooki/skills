# Stickiness & virality (Heath & Heath, *Made to Stick*, 2007; Berger, *Contagious*, 2013)

The social-channel science: what makes a message memorable (SUCCESs) and what
makes it spread (STEPPS). Each element: mechanism in one sentence, imperative
rules for tweets/hooks/threads/pitches, and failure modes.

## The villain: the Curse of Knowledge

**Mechanism:** Once you know something you cannot un-know it, so you write in abstractions (the "tapper" hears the song in their head; the listener hears random knocking) and systematically overestimate how much lands.

- Before posting, strip every term your audience didn't use before they found your project — jargon, internal names, acronyms. If a word only makes sense after reading your docs, it cannot appear in the hook.
- Write the tweet for the person who has never heard of you, not the person who starred the repo. Test: would a stranger know what the thing *does* from this post alone?
- Failure mode: "Announcing v2.3 with improved DAG traversal semantics" — perfectly clear to you, knocking noises to everyone else.

## SUCCESs (Made to Stick)

### Simple — find the core

**Mechanism:** An idea sticks only when stripped to its single most important claim (the "commander's intent"); if you say three things, you say nothing.

- Write the one-sentence commander's intent for the post first ("after reading this, they should know/do X"), then delete every clause that doesn't serve X.
- One idea per tweet. If your draft has "and also," split it into a thread or cut it.
- Compress with what they already know: lead with an analogy to a familiar thing ("X for Y") rather than a feature list.
- Failure modes: burying the lead (core claim in tweet 4); mistaking "short" for "simple" (simple = core + compact, not vague); three benefits with equal weight so none is remembered.

### Unexpected — break a pattern, open a gap

**Mechanism:** Attention comes from violating an expectation; sustained interest comes from the gap theory of curiosity — a specific gap between what the reader knows and wants to know *hurts* until filled.

- Open with the surprising fact or counterintuitive claim, not the setup ("We deleted 40% of our code and got faster" beats "A thread on performance work").
- Before delivering information, make the reader want it: pose the concrete question your post answers — but only a question they'll actually feel.
- Break a pattern the reader actually holds: identify the common belief in your niche, lead by contradicting it, then pay it off.
- Failure modes: gimmickry (surprise unrelated to the core message); clickbait gaps never closed (destroys trust for every future post); opening a gap about something nobody cared to know (a gap needs two edges).

### Concrete — sensory-specific language

**Mechanism:** Memory works like Velcro — the more sensory hooks an idea has, the more of the brain it snags; concrete images persist while abstractions slide off.

- Replace every abstraction with something you can picture or count: not "improves performance," but "cold start dropped from 4.2s to 300ms."
- Show the artifact: the screenshot, the terminal output, the before/after diff, the exact command. One concrete image outperforms three adjectives.
- Describe what the user *does*, in physical steps ("paste the URL, hit enter, get a CID"), not what the product *is*.
- Failure modes: expert drift back to abstraction mid-thread; fake concreteness — vivid words with no referent ("blazing fast"); numbers with no anchor.

### Credible — believable from the inside

**Mechanism:** Absent outside authority, an idea vouches for itself through testable details, humanized statistics, and the "Sinatra test" — one example so demanding that passing it proves everything.

- Make claims falsifiable and let readers verify: "try it yourself" links, reproducible benchmarks, the exact repo and commit.
- Humanize every statistic to a human scale — not "10^18 operations," but "every photo on your phone, checked every second." A statistic's job is to make a relationship vivid, not to impress with size.
- Deploy your Sinatra example: name the single hardest case your thing handles ("this served traffic during the front-page HN spike") instead of listing ten easy ones.
- Failure modes: statistics as decoration; credibility borrowed from vague authority ("experts agree", "trusted by teams"); vivid-but-irrelevant details.

### Emotional — make them care

**Mechanism:** People act for one identifiable person, not for masses (the Mother Teresa effect), and care through self-interest and identity ("people like me do things like this").

- Frame benefits as second-person and immediate: "you stop paying for idle containers" — not "reduces infrastructure costs for organizations."
- Tell one user's story, not aggregate stats: one name defeats a number.
- Appeal to identity, not just utility: write so the target can say "I'm the kind of developer who self-hosts / owns their data."
- Failure modes: analytical framing killing feeling (priming calculation suppresses emotion — a stats table numbs the audience for the story after it); manufactured sentimentality; appealing to your own values instead of the audience's.

### Stories — simulation and inspiration

**Mechanism:** A story is a flight simulator — mental rehearsal confers much of the benefit of doing — and inspires via three plots: Challenge (underdog), Connection (bridge across a gap), Creativity (breakthrough).

- Structure the thread as a Challenge plot: real obstacle, failed attempts, specific turn, resolution — never as a feature announcement.
- Make the reader the protagonist of a simulation: walk the exact sequence they would perform, so reading the thread *is* a rehearsal of using the product.
- Collect stories rather than inventing them: the user anecdote, the bug war story, the support ticket with a happy ending, retold with concrete details intact.
- Failure modes: story with no plot ("we're excited to announce" is not a narrative); frictionless hero (no genuine struggle = an ad); moralizing the story explicitly instead of letting the reader draw the conclusion.

## STEPPS (Contagious)

### Social currency

**Mechanism:** People share what makes *them* look smart, insider, or ahead — sharing is self-presentation, so your content is their status purchase.

- Give the reader a remarkable fact they can retell to look clever — the one genuinely surprising thing about your product, pre-packaged in one sentence.
- Use scarcity and insider-ness honestly: early access, things only power users know ("the hidden flag that does X").
- Failure modes: content that makes *you* look good but not the sharer (self-congratulatory launch posts don't get retweeted — nobody gains status amplifying your ad); fake scarcity.

### Triggers

**Mechanism:** Top of mind means tip of tongue — people share what the environment just reminded them of; linkage to a *frequent* cue beats a clever cue-less message (Kit Kat welded itself to coffee breaks).

- Tie your product to something in the audience's weekly routine: a recurring pain ("every time CI goes red…"), a habitual moment (Monday deploys), a tool they open daily.
- Pick frequency over cleverness: a link to a daily annoyance beats a link to a rare, witty occasion.
- Time posts to the trigger: the "weekend project" post Friday morning; the incident-response thread the day after a famous outage.
- Failure modes: associating with a cue already owned by something else; a vivid but rare trigger; a great post with no environmental hook (one day of attention, no recurring recall).

### Emotion

**Mechanism:** Sharing is driven by physiological arousal, not valence — high-arousal emotions (awe, anger, anxiety, excitement, amusement) drive shares; low-arousal ones (sadness, contentment) suppress them.

- Kindle one high-arousal emotion on purpose: awe ("this runs on a $5 board"), righteous anger ("your cloud bill is subsidizing their margins"), excitement ("you can now do X in one command"). Pick one; write toward it.
- Audit the draft's emotional temperature: if the honest reaction is "huh, nice," rewrite for intensity or don't expect shares — informative-but-calm is read, not spread.
- Failure modes: function-only framing (correct, useful, arousal-zero posts die quietly); rage-baiting your own community; mistaking your excitement for the reader's.

### Public

**Mechanism:** Behavior is imitated only when observable — private consumption spreads nothing; visible use advertises itself.

- Build behavioral residue into what you share: badges, "built with X" footers, quotable terminal output, distinctive screenshots.
- Make usage self-revealing and screenshot-worthy: design the output people will paste into their own posts.
- Show the crowd: retweet users' posts, surface adoption — visible adopters are the ad.
- Failure modes: great DX with no visible trace; publicizing the *undesired* behavior ("most people don't back up their data" normalizes not backing up — make the desired behavior look common, never the failure).

### Practical value

**Mechanism:** People share news-you-can-use to help people they care about; value is judged against a reference point, and narrowly framed, specific tips beat broad ones.

- Package one narrowly-scoped, immediately usable tip per post: "cut Docker image size 80% with one flag" beats "10 thoughts on container optimization." Narrow targeting makes the forward feel personal.
- Frame the gain against an explicit reference point in its most impressive honest form: "was 4GB, now 400MB."
- Failure modes: broad listicles useful to everyone and forwarded to no one; value stated abstractly ("saves time and money"); burying the useful bit under the promotion.

### Stories

**Mechanism:** People don't share information, they tell stories — the product must be a load-bearing character, a Trojan horse the story can't be retold without.

- Apply the retelling test: if someone recounts your thread at lunch, does your product survive the retelling, or only the punchline? (Viral ads whose brand fell out of every retelling bought reach and sold nothing.)
- Lead with a genuinely tellable narrative and smuggle the pitch inside it, rather than appending a story to a pitch.
- Failure modes: viral wrapper, forgettable payload; Trojan horse with nothing inside; a "story" that is actually a testimonial quote — no arc, nothing to retell.

## Composite checklist for a single post

1. One core claim, stated first, in words a stranger uses (Simple, Curse of Knowledge).
2. Opens by violating an expectation or posing a felt question — and pays it off (Unexpected).
3. Contains something picturable or countable, anchored to a reference point (Concrete, Practical value).
4. Claim verifiable by the reader; stats on a human scale; hardest example named (Credible).
5. Second-person benefit; one identifiable human, not an aggregate (Emotional).
6. Reads as a plot with real struggle in which the product is load-bearing (Stories ×2).
7. Sharer gains status by amplifying it; tied to a frequent cue; emotion is high-arousal; leaves visible residue (Social currency, Triggers, Emotion, Public).

## Sources

- https://readingraphics.com/book-summary-made-to-stick/
- https://growthsummary.com/book-summary/made-to-stick/
- https://www.marketing-psycho.com/made-to-stick/
- https://readingraphics.com/book-summary-contagious-why-things-catch-on/
- https://knowledge.wharton.upenn.edu/article/contagious-jonah-berger-on-why-things-catch-on/
- https://www.searchlaboratory.com/us/2014/07/contagious-content-stepps-and-the-science-of-shareability/
