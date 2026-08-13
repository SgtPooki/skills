# Reader mechanics

Sentence-level rules from Gopen & Swan, "The Science of Scientific Writing"
(American Scientist, 1990). The core claim: readers interpret prose by
*position*. Meaning is not what the writer intends but what the structure leads
the reader to expect. Use these when drafting specs and long-form explanation,
and when a reviewer says a passage is "hard to follow" but can't say why.

## Subject-verb proximity

Readers hold their breath from subject to verb. Everything wedged between them
is read as an interruption and retained poorly.

Bad: "The scheduler, which was rewritten in v3 to use a priority heap after the
linked-list implementation caused starvation under load, assigns each job a
deadline."

Good: "The scheduler assigns each job a deadline. v3 rewrote it to use a
priority heap because the linked-list implementation caused starvation under
load."

## Topic position: old information first

The start of a sentence tells the reader whose story it is and links backward.
Begin sentences with material the reader has already seen; introduce the new
thing later in the sentence. Chains of sentences that each start with a brand-new
concept read as disconnected facts even when the logic is sound.

## Stress position: the point lands at the end

Readers naturally emphasize what closes a sentence. Put the thing you want
remembered at the end; put throwaway qualifiers anywhere else. If a sentence
ends on a triviality ("...as shown in the table above"), the triviality is what
sticks.

Applied to a requirement: "Under concurrent writes, the index MUST remain
consistent" stresses consistency. "The index MUST remain consistent under
concurrent writes" stresses the load condition. Choose deliberately.

## One unit, one point

A sentence makes one point; a paragraph develops one idea whose point appears
early (BLUF) or as the stressed close — not buried mid-paragraph. If you can't
say what a paragraph's single point is, split it.
