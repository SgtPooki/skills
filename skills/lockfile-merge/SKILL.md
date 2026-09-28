---
name: lockfile-merge
description: Merge a base branch (usually main or staging) into a feature branch and resolve package lockfile conflicts by regenerating the lockfile from the base branch's copy. Use when a merge or "update branch from main/staging" hits conflicts in pnpm-lock.yaml or package-lock.json, or when asked to bring a PR branch up to date with its base.
---

# Lockfile merge

Bring a branch up to date with its base when the lockfile conflicts. Never hand-edit conflict markers in a lockfile, and never rebase to avoid them: merge.

## Steps

1. Merge the base branch (the PR's base: usually `main`, in some repos `staging`; look it up with `gh pr view --json baseRefName -q .baseRefName`):
   ```bash
   git fetch origin
   git merge origin/<base>
   ```
2. If the lockfile conflicts, take the base branch's copy. If any `package.json` also conflicts, resolve it first, since the install reads it:
   ```bash
   git checkout origin/<base> -- <lockfile>
   ```
3. Regenerate it with the repo's package manager (`pnpm-lock.yaml` → pnpm, `package-lock.json` → npm) so this branch's dependency changes are re-applied on top, then stage it:
   ```bash
   pnpm install   # or: npm install
   git add <lockfile>
   ```
4. Resolve any other conflicted files normally, then finish the merge with the default message. Do not edit it:
   ```bash
   git commit --no-edit
   ```

## After the merge

- Confirm the lockfile diff against the base only contains this branch's intended dependency changes: `git diff origin/<base> -- <lockfile>`.
- Run the repo's install-sensitive checks (build, typecheck, tests) before pushing.
- Push normally. A merge never needs a force push.
