---
name: writing-community
description: >-
  Write project-authored public communication: release notes, announcements,
  changelogs, launch posts, and status updates — text that speaks AS the
  project. Always use with writing-core. Do NOT use for the user's personal
  posts, replies, or messages (that's their personal author-voice skill); if
  the user personally announces project news, use this skill for structure
  and add the author-voice overlay for idiom.
---

# Writing Community

Write text the project publishes to its users: release notes, announcements,
status updates, launch posts. The audience is mixed — some readers are experts,
some found the project yesterday — so the audience dial defaults to mixed:
define terms at first use, prefer the everyday word, keep exact technical terms
where precision matters.

## The announcement shape

In this order, cutting sections that don't apply:

1. **What changed** — one or two sentences, first line of the post. A reader
   who stops here should still be correctly informed.
2. **Who is affected** — which users, which configurations, which versions.
3. **Action required** — what a reader must do, if anything, with the exact
   command or link. "No action needed" is a valid and useful statement.
4. **Compatibility / rollout** — breaking changes, deprecation timelines,
   rollout schedule.
5. **Links** — full changelog, docs, migration guide, issue tracker.

Breaking changes surface twice: named in the opening lines, then detailed under
compatibility with concrete migration steps. Never bury a breaking change under
feature news.

## Changelog-first workflow

Write the technical changelog before the human announcement, then derive:

1. Maintain the changelog per Keep a Changelog: `Added / Changed / Deprecated /
   Removed / Fixed / Security`, newest release on top, dated entries. Version
   numbers follow SemVer, and the changelog's claims must match what the
   version number promises. If the release already violated SemVer (a breaking
   change shipped in a minor version), document the reality honestly and flag
   the version-number mismatch explicitly — never hide the break to protect
   the number.
2. The release note is a curation of that changelog, not a rewrite: pick what
   affects readers, translate it to the mixed register, link each item to docs
   rather than re-explaining them.

## Tone

Warm but concrete. Enthusiasm is welcome when it's attached to a specific
("resume now survives network flaps — the retry queue persists across
restarts"), and empty when it isn't ("we're excited to ship tons of
improvements!"). Never oversell: if a feature is experimental, say so and say
what "experimental" means for the reader.

Status updates during incidents are their own register: facts, impact, current
state, next update time. No apology theater, no minimizing. One honest sentence
("Uploads are failing for ~20% of requests; we're rolling back") beats a
paragraph of reassurance.

Security advisories follow the same shape, tightened: affected versions →
impact (what an attacker can do) → fixed version → mitigation for those who
can't upgrade → CVE/GHSA link. No severity inflation and no soft-pedaling;
readers patch based on what you say.

## Gate

```bash
echo "$DRAFT" | python3 <writing-core-skill-path>/scripts/writingcheck.py writing-community -
```

Single-item changelog categories are allowed; the checker knows. Fix errors
(max 3 passes), treat notes as judgment calls.
