# Verdict report template

Use this exact structure. Keep evidence concrete: commands run, versions,
dates, file paths, line references. Every ⚠️/❌ must appear again under
Findings with detail. Every check not performed must appear under "Not
verified" — silence is not safety.

```markdown
# Dependency audit: <pkg> <old> → <new>  (<repo> PR #<n>)

**Verdict: MERGE | MERGE WITH CAUTION | HOLD | REJECT**
<One-sentence justification. For MERGE WITH CAUTION: the exact condition,
e.g. "safe to merge after 2026-08-01 (release is 2 days old)". For HOLD:
the fix required. For REJECT: the red flag(s).>

## Summary table

| Check | Result | Evidence |
|---|---|---|
| PR authenticity (real bot, verified commits, files in scope) | ✅/⚠️/❌ | |
| Update class (direct/transitive, prod/dev, semver jump, security?) | ℹ️ | |
| Release age vs cooldown | ✅/⚠️ | published <date>, <n> days old |
| Changelog & breaking changes (all intermediate versions) | ✅/⚠️/❌ | |
| Artifact diff (install scripts, new deps, obfuscation, blobs) | ✅/⚠️/❌ | |
| Provenance / signatures / publisher continuity | ✅/⚠️/❌/n-a | |
| Advisory & malware-feed scan of exact new version | ✅/❌ | |
| Lockfile diff (scope, sources, integrity) | ✅/⚠️/❌ | |
| Blast radius (usage sites vs changed APIs) | ℹ️ | <n> usage sites |
| Build / typecheck / lint / full tests on PR branch | ✅/⚠️/❌ | |
| Coverage of the affected code paths | ✅/⚠️ | |

## Findings
<Numbered. Each: what, where (file:line / version / URL), why it matters,
severity (blocking / caution / info), and the recommended action.>

## Blast radius detail
<Which files/functions in this codebase use the package; which of those
touch changed APIs; grouped-PR: repeat per package.>

## Not verified
<Checks that could not be run and why (no local toolchain, ecosystem lacks
provenance, tests need secrets…), and what would close each gap.>

## Recommended next step
<For the human: merge command they would run, or the fix/migration steps,
or the wait-until date, or pin+report guidance. The skill itself does not
merge, approve, or comment on the PR.>
```

For a **grouped PR**, add a per-package verdict column table at the top; the
overall verdict is the worst individual verdict.
