#!/usr/bin/env node
/**
 * dx-audit deterministic scorer.
 *
 * Rolls up per-check scores (0/1/3/5, or "na") into category -> surface ->
 * overall scores using the dx-audit weights. Handles N/A by excluding the
 * item and renormalizing the remaining weights at that level — so a scoped-out
 * check or an absent surface never penalizes the score.
 *
 * Usage:
 *   node score.mjs <checks.json>            # prints scorecard JSON + table
 *   node score.mjs <checks.json> --out scorecard.json
 *   node score.mjs <checks.json> --quiet    # JSON only, no table
 *
 * Input shape (checks.json):
 * {
 *   "repo": "name",
 *   "commit": "sha",
 *   "surfaces": {
 *     "cli":            { "categories": { "<cat>": [ { "check": "id", "score": 0|1|3|5|"na", "priority": "P0", "note": "" } ] } },
 *     "library_api":    { ... },
 *     "server_service": "na",          // whole surface absent/out-of-scope
 *     "github_action":  { ... }
 *   }
 * }
 *
 * Canonical category keys (others are ignored with a warning):
 *   onboarding | correctness | errors | automation | docs
 *
 * Scores: 0 missing/harmful, 1 partial, 3 acceptable, 5 strong. "na" = excluded
 * (absent or explicitly out of declared scope). Anything else throws.
 */

import { readFileSync, writeFileSync } from 'node:fs'

const SURFACE_WEIGHTS = { cli: 25, library_api: 30, server_service: 30, github_action: 15 }
const CATEGORY_WEIGHTS = { onboarding: 25, correctness: 25, errors: 20, automation: 20, docs: 10 }
const VALID_SCORES = new Set([0, 1, 3, 5])
const SURFACE_LABEL = {
  cli: 'CLI',
  library_api: 'Programmatic library/API',
  server_service: 'Server/service',
  github_action: 'GitHub Action',
}

function band(score) {
  if (score == null) return 'N/A'
  if (score >= 90) return 'Outstanding'
  if (score >= 75) return 'Strong'
  if (score >= 60) return 'Acceptable (DX debt)'
  if (score >= 40) return 'Poor'
  return 'Critical'
}

function status(score) {
  if (score == null) return 'na'
  if (score >= 75) return 'pass'
  if (score >= 60) return 'warn'
  return 'fail'
}

/** Weighted average over entries [{value 0..1, weight}], renormalizing to present weights. Returns null if none present. */
function weightedAvg(entries) {
  const present = entries.filter((e) => e.value != null)
  if (present.length === 0) return null
  const totalW = present.reduce((s, e) => s + e.weight, 0)
  if (totalW === 0) return null
  return present.reduce((s, e) => s + e.value * (e.weight / totalW), 0)
}

function scoreCategory(checks, surface, cat) {
  const norm = checks.map((c) => {
    if (c.score === 'na') return null
    if (!VALID_SCORES.has(c.score)) {
      throw new Error(`Invalid score ${JSON.stringify(c.score)} for ${surface}.${cat}.${c.check} (expected 0/1/3/5/"na")`)
    }
    return c.score / 5
  })
  // each check equally weighted inside a category
  const avg = weightedAvg(norm.map((value) => ({ value, weight: 1 })))
  return avg == null ? null : avg // 0..1
}

function scoreSurface(surfaceObj, surface) {
  if (surfaceObj === 'na' || surfaceObj == null) return { score: null, categories: {} }
  const cats = surfaceObj.categories ?? {}
  const catScores = {}
  for (const cat of Object.keys(cats)) {
    if (!(cat in CATEGORY_WEIGHTS)) {
      console.warn(`warning: unknown category "${cat}" in ${surface} — ignored`)
      continue
    }
    catScores[cat] = scoreCategory(cats[cat], surface, cat) // 0..1 or null
  }
  const entries = Object.keys(CATEGORY_WEIGHTS).map((cat) => ({
    value: catScores[cat] ?? null,
    weight: CATEGORY_WEIGHTS[cat],
  }))
  const surfaceNorm = weightedAvg(entries) // 0..1 or null
  return {
    score: surfaceNorm == null ? null : Math.round(surfaceNorm * 100),
    categories: Object.fromEntries(
      Object.entries(catScores).map(([k, v]) => [k, v == null ? null : Math.round(v * 100)]),
    ),
  }
}

function main() {
  const args = process.argv.slice(2)
  const inPath = args.find((a) => !a.startsWith('--'))
  const outIdx = args.indexOf('--out')
  const outPath = outIdx >= 0 ? args[outIdx + 1] : null
  const quiet = args.includes('--quiet')
  if (!inPath) {
    console.error('usage: node score.mjs <checks.json> [--out scorecard.json] [--quiet]')
    process.exit(2)
  }

  const input = JSON.parse(readFileSync(inPath, 'utf8'))
  const surfaces = {}
  for (const surface of Object.keys(SURFACE_WEIGHTS)) {
    if (!(surface in (input.surfaces ?? {}))) continue
    const s = scoreSurface(input.surfaces[surface], surface)
    surfaces[surface] = { score: s.score, status: status(s.score), rating: band(s.score), categories: s.categories }
  }

  const overallEntries = Object.keys(surfaces).map((surface) => ({
    value: surfaces[surface].score == null ? null : surfaces[surface].score / 100,
    weight: SURFACE_WEIGHTS[surface],
  }))
  const overallNorm = weightedAvg(overallEntries)
  const overall = overallNorm == null ? null : Math.round(overallNorm * 100)

  const scorecard = {
    repo: input.repo ?? null,
    commit: input.commit ?? null,
    timestamp: input.timestamp ?? null,
    surface_weights: SURFACE_WEIGHTS,
    category_weights: CATEGORY_WEIGHTS,
    surfaces,
    overall_score: overall,
    overall_rating: band(overall),
  }

  const json = JSON.stringify(scorecard, null, 2)
  if (outPath) {
    writeFileSync(outPath, json + '\n')
    if (!quiet) console.error(`wrote ${outPath}`)
  }
  if (quiet) {
    if (!outPath) process.stdout.write(json + '\n')
    return
  }

  // human table
  console.log('')
  console.log('Surface                       Score  Status  Rating')
  console.log('----------------------------  -----  ------  ----------------------')
  for (const surface of Object.keys(SURFACE_WEIGHTS)) {
    if (!(surface in surfaces)) continue
    const s = surfaces[surface]
    const score = s.score == null ? ' n/a' : String(s.score).padStart(4)
    console.log(`${SURFACE_LABEL[surface].padEnd(28)}  ${score}   ${s.status.padEnd(6)}  ${s.rating}`)
  }
  console.log('----------------------------  -----  ------  ----------------------')
  console.log(`${'OVERALL'.padEnd(28)}  ${String(overall ?? 'n/a').padStart(4)}   ${status(overall).padEnd(6)}  ${band(overall)}`)
  console.log('')
  if (!outPath) process.stdout.write(json + '\n')
}

main()
