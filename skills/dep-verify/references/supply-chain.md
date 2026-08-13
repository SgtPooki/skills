# Supply-chain red flags and attack patterns

Why this file exists: every check in Phase 4 maps to a technique that has
actually been used to ship malware as a routine-looking version bump. Knowing
the pattern tells you what the evidence means when you find it.

## The red-flag taxonomy

Any of these in the new version is a finding; two or more together is
REJECT-territory until explained:

1. **New or changed install-time execution** — npm `preinstall`/`install`/
   `postinstall`/`prepare`, Python `setup.py`/build backend, Rust `build.rs`/
   proc-macros, Ruby native extensions. The #1 malware execution vector.
2. **Published artifact diverges from the git repo/tag** — files in the
   tarball absent from the repo, or no matching tag/commit for the version.
3. **New dependency that is young / low-download / low-reputation**,
   especially added in a patch release.
4. **Maintainer/publisher discontinuity** — ownership transfer, brand-new
   publishing account, first publish in years, or one account publishing
   bursts across unrelated packages.
5. **Obfuscation** — minified/hex-escaped/base64 code added to previously
   readable files, `eval`/`Function()`/`atob` chains, high-entropy strings,
   single-line 100KB additions.
6. **New capability the package never needed** — network calls, subprocess
   spawning, env-var enumeration, homedir/SSH/keychain crawling, IMDS
   endpoints (169.254.169.254), fresh domains or raw IPs, webhook.site.
7. **Binary blobs** — new `.node`/`.so`/`.exe` files or opaque "test data".
8. **Provenance regression** — earlier versions had provenance/signature
   attestations, the new one doesn't.
9. **Very fresh release** — see cooldown section below.
10. **Lockfile anomalies in the PR** — off-registry resolved URLs, http://,
    hash downgrades/removals, mass churn beyond the stated bump, a resolved
    URL pointing at a *different package name* than the entry key.

## Attack pattern reference

| Incident | Vector | What a reviewer could have caught |
|---|---|---|
| event-stream (2018) | Ownership handed to a volunteer; malicious new dep `flatmap-stream` | Ownership transfer + brand-new near-zero-download dep added in a minor + encrypted blob |
| ua-parser-js (2021) | npm account hijack | New `preinstall` script appearing in a patch release, fetching binaries |
| xz-utils (2024) | Multi-year social engineering to gain co-maintainership | Backdoor staged in binary "test files"; malicious build script existed **only in the release tarball, not the repo** |
| polyfill.io (2024) | Project/domain sold to a new owner | Runtime CDN dependency + ownership change; original author publicly warned |
| chalk/debug (Sept 2025) | Maintainer phished; attacker published within 16 minutes | Obfuscated code appended to clean files; no matching git commit for the version; provenance regression; on-registry only hours |
| Shai-Hulud worm (Sept + Nov 2025) | Stolen npm tokens; self-propagating publisher (500–700+ packages) | New `postinstall`/`preinstall` + new `bundle.js` in a patch bump; version bumps with zero repo activity; runs TruffleHog, exfiltrates to public repos |
| Fake Dependabot commits (2023) | Stolen PATs, forged `dependabot[bot]` author string | Author was not the real bot app; commits unsigned/unverified; PR touched workflow files |
| tj-actions/changed-files (2025) | Stolen bot PAT; every version tag retroactively re-pointed at malicious commit | Tag pins are mutable — SHA pinning; diff of action source showed memory-dump payload fetching from a gist |

Common thread: **the compromised version is almost always the newest one**,
and it is usually caught within hours-to-days. That is the entire argument
for cooldowns.

## Cooldown arithmetic

- Analysis of major incidents: 8 of 10 had exploitation windows under one
  week; chalk/debug lasted ~4–6 hours on-registry; Nx ~4–5 hours; axios RAT
  versions 2–3 hours.
- GitHub made a **3-day cooldown the Dependabot default** for version
  updates in July 2026 (security updates exempt). Renovate equivalent:
  `minimumReleaseAge`; pnpm: `minimumReleaseAge` in pnpm-workspace.yaml.
- Verdict guidance: release < 3 days old ⇒ MERGE WITH CAUTION at best, with
  the exact "safe after" date. Security fixes are the exception — weigh CVE
  severity/exploitability against freshness and state the tradeoff.

## Provenance: what it does and doesn't prove

- npm provenance (Sigstore/SLSA) binds the tarball to source repo + commit +
  CI workflow; `npm audit signatures` verifies it for the whole tree.
  GitHub artifact attestations: `gh attestation verify <file> -R <owner/repo>`.
- Provenance proves *where and how it was built* — not that the code is
  benign. A compromised CI can attest malicious code. So: provenance present
  and matching = strong positive signal; provenance regression = strong red
  flag; provenance absent = neutral for ecosystems/packages that never had it.

## Scanner shortlist

Use what's available; any hit on the exact new version is a finding:

- `osv-scanner` — OSV.dev incl. the OpenSSF **malicious-packages** feed
  (`MAL-` advisories), so it flags known-malicious versions, not just CVEs.
- `npm audit` / `pip-audit` / `cargo audit` / `govulncheck` — ecosystem
  advisory feeds (govulncheck is calls-based: it checks reachability).
- Socket.dev package pages (`socket.dev/npm/package/<name>`) — behavioral
  risk signals (install scripts, network access, obfuscation, maintainer
  churn) per version, viewable without installing anything.
- `guarddog npm scan <pkg> --version <v>` (Datadog) — local static analysis
  with malware-pattern Semgrep rules, also does PyPI/Go/Actions.
- deps.dev — OpenSSF Scorecard, dependency graph, provenance links per
  version.
