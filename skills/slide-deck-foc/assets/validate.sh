#!/usr/bin/env bash
# Validate a single-file slide deck before publishing to FOC.
# Usage: validate.sh <deck.html>
# Exit 0 = passed, 1 = a blocking issue was found. Warnings do not fail.
# Mechanical checks only. Recompute the math and verify claims against source by hand.
set -uo pipefail

f="${1:-}"
[ -n "$f" ] || { echo "usage: validate.sh <deck.html>"; exit 2; }
[ -f "$f" ] || { echo "not found: $f"; exit 2; }

fail=0
hr() { printf '%s\n' "----------------------------------------"; }

# 1. Structure: balanced <section> and a real slide count.
# Match tags at line start so an example tag inside a comment is not miscounted.
open=$(grep -cE '^[[:space:]]*<section class="slide' "$f" || true)
close=$(grep -cE '^[[:space:]]*</section>' "$f" || true)
echo "slides: $open   (</section>: $close)"
if [ "$open" != "$close" ]; then echo "FAIL: <section> open/close mismatch ($open vs $close)"; fail=1; fi
if [ "$open" -lt 1 ]; then echo "FAIL: no slides found"; fail=1; fi

# 2. Em-dashes and en-dashes (the #1 voice tell). Use colons/commas/hyphens instead.
if grep -nE '—|–|&mdash;|&ndash;' "$f" >/dev/null; then
  echo "FAIL: em/en-dash(es) found (replace with colon, comma, parentheses, or hyphen):"
  grep -nE '—|–|&mdash;|&ndash;' "$f" | head
  fail=1
fi

# 3. AI-smell words (warn, not fail).
ai=$(grep -niE 'comprehensive|robust|leverages?|facilitate|furthermore|additionally|seamless|it is worth noting|in conclusion' "$f" || true)
if [ -n "$ai" ]; then echo "WARN: possible AI-smell words (say the specific thing instead):"; printf '%s\n' "$ai" | head; fi

# 4. Emoji (best-effort, needs perl). Decks should have none.
if command -v perl >/dev/null 2>&1; then
  emoji=$(perl -ne 'print "$.: $_" if /[\x{1F000}-\x{1FAFF}\x{2600}-\x{27BF}\x{2B00}-\x{2BFF}\x{FE0F}]/' "$f" 2>/dev/null || true)
  if [ -n "$emoji" ]; then echo "FAIL: emoji found (remove all):"; printf '%s\n' "$emoji" | head; fail=1; fi
fi

# 5. Self-contained: external CSS/JS/font/image will not load over IPFS.
ext=$(grep -niE '(src|href)="https?://|@import|fonts\.googleapis' "$f" || true)
if [ -n "$ext" ]; then echo "FAIL: external resource(s) found (deck will not render offline or from IPFS):"; printf '%s\n' "$ext" | head; fail=1; fi

# 6. Vague words (warn). Prefer specifics. Kept narrow to avoid false positives.
vague=$(grep -niE '\b(often|recently|a lot of)\b' "$f" || true)
if [ -n "$vague" ]; then echo "WARN: vague words (prefer a number, date, or named example):"; printf '%s\n' "$vague" | head; fi

hr
if [ "$fail" = "0" ]; then
  echo "PASS: structure, voice, and self-containment checks clean."
  echo "Still do by hand: recompute every number, reconcile cross-slide figures, verify claims against source."
  exit 0
else
  echo "FAILED: fix the items above before publishing."
  exit 1
fi
