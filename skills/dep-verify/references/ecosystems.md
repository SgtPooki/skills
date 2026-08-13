# Ecosystem-specific commands

Detect the ecosystem from the files the PR touches, then use the matching
section. For ecosystems not listed, apply the same categories (artifact diff,
metadata compare, publish timestamp, provenance, frozen install, tree
explanation) using that ecosystem's native tooling — the categories are
universal even where the commands differ. Substitute the package manager the
repo actually uses (presence of `pnpm-lock.yaml`, `yarn.lock`, `uv.lock`,
etc. tells you).

## Contents

- [npm / pnpm / yarn](#npm--pnpm--yarn)
- [GitHub Actions](#github-actions)
- [Docker / containers](#docker--containers)
- [Go modules](#go-modules)
- [Python](#python)
- [Rust / Cargo](#rust--cargo)
- [Ruby, Java, .NET (quick table)](#ruby-java-net-quick-table)

## npm / pnpm / yarn

Manifest: `package.json`. Lockfiles: `package-lock.json` / `pnpm-lock.yaml` /
`yarn.lock`.

```bash
# --- What changed (artifact-level, authoritative for what ships) ---
npm diff --diff=<pkg>@<old> --diff=<pkg>@<new>            # full published-tarball diff
npm diff --diff=<pkg>@<old> --diff=<pkg>@<new> --diff-name-only
# Web mirrors of the same idea: npmdiff.dev, diff.intrinsic.com,
# app.renovatebot.com/package-diff?name=<pkg>&from=<old>&to=<new>

# --- Metadata compare (run for BOTH versions and diff the output) ---
npm view <pkg>@<ver> peerDependencies engines exports main module types type scripts dependencies

# --- Publish timestamp / release age ---
npm view <pkg> time --json          # timestamps for every version

# --- Provenance & signatures (after the frozen install) ---
npm audit signatures                # verifies registry signatures + provenance attestations
npm view <pkg>@<ver> dist.attestations gitHead repository.url dist.tarball
# gitHead should exist as the upstream tag: git ls-remote <repo> | grep <gitHead>
# npmjs.com package page shows the green "Provenance" check per version.

# --- Tarball inspection without executing anything ---
npm pack <pkg>@<ver> --dry-run      # file list; watch for new .js blobs, binaries
npm view <pkg>@<ver> scripts        # preinstall/install/postinstall = execution vector

# --- Advisories & malware feeds ---
npm audit
npx -y osv-scanner scan --lockfile package-lock.json   # includes OpenSSF malicious-packages feed

# --- Lockfile lint (npm/yarn; validates resolved hosts + https) ---
npx -y lockfile-lint -p package-lock.json --type npm --allowed-hosts npm --validate-https

# --- Blast radius ---
npm explain <pkg>   # or: pnpm why <pkg> / yarn why <pkg>
rg -n "from ['\"]<pkg>(/|['\"])|require\(['\"]<pkg>" --type-add 'src:*.{js,jsx,ts,tsx,mjs,cjs,vue,svelte}' -tsrc

# --- Frozen install + verification suite (scripts disabled for audit) ---
npm ci --ignore-scripts             # or: pnpm install --frozen-lockfile / yarn install --immutable
npm run build && npx tsc --noEmit && npm run lint && npm test

# --- Packaging sanity when exports/module format changed ---
npx -y publint <pkg>@<new>
npx -y @arethetypeswrong/cli <pkg>@<new>

# --- Bundle size (frontend deps) ---
# bundlephobia.com/package/<pkg>@<ver> for the package; size-limit/compare in-repo builds for real impact
```

npm-specific notes:

- `npm ci` (not `npm install`) treats the lockfile as read-only and enforces
  integrity hashes — that is itself a security check.
- After auditing with `--ignore-scripts`, remember some packages genuinely
  need their build scripts; note in the report if the project's normal
  install runs scripts.
- Peer-dependency conflicts surface at install time on npm 7+; a clean
  frozen install is evidence peers still resolve.

## GitHub Actions

Manifest: `.github/workflows/*.yml`. No lockfile — **the pin is the
lockfile**, which is why tag pins are dangerous: tags are mutable, and the
tj-actions/changed-files attack (CVE-2025-30066) retroactively re-pointed
every version tag at a malicious commit. Actions run with your secrets.

```bash
# The bump should be a full 40-char commit SHA with the version as a comment:
#   uses: owner/action@<sha>   # vX.Y.Z
# A tag-only pin (uses: owner/action@v4) is itself a finding: recommend SHA pinning.

# Verify the new SHA actually belongs to the action's repo (impostor-commit check —
# forks' commits are addressable from the parent repo URL, so check the branch/tag list):
gh api repos/<owner>/<action>/commits/<sha> --jq .sha        # exists?
gh api repos/<owner>/<action>/tags --jq '.[].name'           # advertised tag matches?
git ls-remote https://github.com/<owner>/<action> | grep <sha>

# Diff the action source between old and new SHAs — this IS the artifact diff:
gh api "repos/<owner>/<action>/compare/<old-sha>...<new-sha>" --jq '.files[].filename'
# Then read the patch. Red flags: changes to action.yml entrypoints, new
# network calls, base64 blobs, anything touching $GITHUB_ENV/$GITHUB_OUTPUT,
# memory-dumping, or fetching remote scripts (gist/raw URLs).

# Blast radius: which workflows use it, with what permissions/secrets?
rg -n "<owner>/<action>@" .github/workflows/
# Check each workflow's `permissions:` block and secret usage — an action bump
# in a workflow with write perms + secrets deserves the strictest review.
```

## Docker / containers

Manifest: `Dockerfile`, `docker-compose.yml`, K8s manifests.

```bash
# Prefer digest pins: image:tag@sha256:...  (tags are mutable, digests aren't)
# Compare old vs new image:
docker pull <image>:<old> && docker pull <image>:<new>
docker history <image>:<new>                       # layer-by-layer commands
docker inspect <image>:<new> --format '{{json .Config}}' | jq   # env, entrypoint, user changed?
# Diff filesystems if warranted: container-diff, dive, or export+diff
# Vulnerabilities: docker scout cves <image>:<new>  or  trivy image <image>:<new>
# Base-image release notes: check the image's repo/Docker Hub page for the tag.
# Verify signed images where the publisher signs (cosign verify <image>@<digest>).
```

## Go modules

Manifest: `go.mod`; lockfile: `go.sum`. Go has strong built-in integrity: the
module proxy + checksum database (sum.golang.org) make artifact/repo
divergence much harder — focus on compatibility and new transitives.

```bash
go mod why <module>                    # why is it in the tree
go mod graph | grep <module>
# Diff between versions (module zips are reproducible from VCS):
go mod download <module>@<old> <module>@<new>
diff -r $(go env GOMODCACHE)/<module>@<old> $(go env GOMODCACHE)/<module>@<new>
# Or use the repo compare view — for Go it matches the artifact.
gorelease -base=<old> -version=<new>   # API compatibility report (golang.org/x/exp/cmd/gorelease)
go build ./... && go vet ./... && go test ./...
govulncheck ./...                      # calls-based vulnerability analysis
# go.sum diff: entries should only be added/updated for the bumped module + new transitives.
```

## Python

Manifest: `pyproject.toml` / `requirements*.txt`; lockfiles: `poetry.lock` /
`uv.lock` / `Pipfile.lock` / hashed requirements.

```bash
# Publish time + metadata:
curl -s https://pypi.org/pypi/<pkg>/<ver>/json | jq '.urls[].upload_time, .info.requires_dist, .info.requires_python'
# Artifact diff (wheels/sdists are just archives):
pip download <pkg>==<old> --no-deps -d /tmp/old && pip download <pkg>==<new> --no-deps -d /tmp/new
# unzip wheels, diff -r. Red flags: setup.py/build-backend code changes (install-time execution!),
# new console_scripts, new binary .so files, obfuscated blobs.
# PyPI attestations (PEP 740) show on the pypi.org file page for supporting projects.
pipdeptree --reverse --packages <pkg>      # who depends on it
pip-audit                                   # known vulns
osv-scanner scan --lockfile poetry.lock     # or uv.lock / requirements.txt
# Frozen install + suite:
uv sync --frozen  # or: poetry install --sync / pip install --require-hashes -r requirements.txt
pytest && mypy . && ruff check .
```

Python-specific: `setup.py` and build backends execute at install time —
treat any change to them exactly like an npm postinstall change.

## Rust / Cargo

```bash
cargo tree -i <crate>                  # inverse deps (blast radius)
# Diff published crate (crates.io artifacts, not just git):
cargo install cargo-crate; cargo crate diff <crate> <old> <new>   # or download .crate files from static.crates.io and diff
# build.rs and proc-macros execute at build time — review changes to them like install scripts.
cargo update --dry-run
cargo build --locked && cargo test --locked && cargo clippy
cargo audit                            # RustSec advisories
cargo semver-checks check-release      # API-compat check for lib crates
# Cargo.lock diff: checksum entries only for the bumped crate + legit transitives.
```

## Ruby, Java, .NET (quick table)

| Task | Ruby (Bundler) | Java (Maven/Gradle) | .NET (NuGet) |
|---|---|---|---|
| Why in tree | `gem dependency <gem> --reverse-dependencies` / `bundle why` | `mvn dependency:tree` / `gradle dependencies` | `dotnet nuget why` |
| Frozen install | `bundle install --frozen` (`BUNDLE_FROZEN=true`) | lockfiles via versions-maven-plugin / Gradle locking | `dotnet restore --locked-mode` |
| Advisories | `bundle audit` (ruby_advisory-db) | OWASP dependency-check, `mvn versions:display-dependency-updates` | `dotnet list package --vulnerable` |
| Artifact diff | `gem fetch <gem> -v <ver>` × 2, unpack + diff | download jars from Maven Central, `diffoscope`/decompile-diff | download .nupkg × 2, unzip + diff |
| Install-time exec | native extensions (`extconf.rb`) | none at install; check plugins | build targets/props in package |
| Signatures | `gem cert` (rarely used) | PGP signatures on Central | NuGet signed packages (required on nuget.org) |
