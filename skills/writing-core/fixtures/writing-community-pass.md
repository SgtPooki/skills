# widget-cli 3.0

widget-cli 3.0 is out. Manifest conversion is now schema-aware, and two flags
changed meaning. If you use `--strict` in CI, read the breaking change below
before upgrading.

## Breaking

`--strict` now also rejects deprecated keys, matching the documented v2 schema.
Pipelines that pass deprecated keys will start failing. Migration: run
`widget-cli migrate manifest.json` once; it rewrites deprecated keys in place.

## Added

- `widget-cli schemas` lists supported schema versions with their release dates.

## Fixed

- Exit code 3 is now returned for unknown schema versions. It was 1, which made
  the case indistinguishable from a parse failure.

Full changelog: CHANGELOG.md. Report issues on the tracker.
