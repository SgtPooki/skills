---
name: peer-review
description: Get cross-review from Cursor, Codex, or Claude CLI agents for specs, plans, code changes, pull requests, or design decisions. Use when work in this repository needs feedback from a different agent, especially for specs and significant changes before ratification or merge.
allowed-tools: Bash, Read, Glob, Grep
metadata:
  short-description: Run cross-agent reviews from the repo
---

# Peer Review

Get feedback on specs, plans, code changes, or design decisions from Cursor, Codex, or Claude CLI agents.

Accept arguments in the form `[cursor|codex|claude|gemini] <prompt>`.
- If the first word is exactly `cursor`, `codex`, `claude`, or `gemini` and is followed by non-whitespace text, use only that tool.
- Otherwise, run all available tools in parallel.
- If no prompt is provided, summarize the current conversation context as the review target.

Examples:
- `/peer-review cursor Review this spec for completeness`
- `/peer-review codex What's wrong with this API design?`
- `/peer-review claude Review this PR for edge cases`
- `/peer-review gemini Review this architecture for scalability`
- `/peer-review Review this spec` (sends to all available agents in parallel)

## Tools available

| Tool | CLI | Best for |
|------|-----|----------|
| **Cursor** | `cursor-agent --print` | UX review, design feedback, architecture, spec review |
| **Claude** | `claude -p` | Deep code review, spec review, architecture analysis |
| **Codex** | `codex exec` (plans/designs/arbitrary review) | Arbitrary review prompts with codebase context |
| **Codex** | `codex review --uncommitted` (local code changes only) | Reviewing uncommitted code changes in a repo |
| **Gemini (Antigravity)** | `agy -p` | Long-context review, architecture review, cross-cutting analysis |

**When to use `codex review` vs `codex exec`:**
- `codex review --uncommitted` — ONLY when reviewing actual uncommitted changes in the current repo
- `codex exec` — for everything else: spec review, plan review, design feedback, reviewing content from conversation/issues, code that isn't in the local diff

## Steps

1. Parse arguments.
   - Match `cursor`, `codex`, or `claude` as the first word only if that exact word is present and followed by non-whitespace text.
   - Treat `/peer-review claude` with no remaining prompt as an error and ask for a prompt.
   - Treat `/peer-review` with no prompt as a request to summarize the current conversation context and run all available tools.

2. Check prerequisites:
   ```bash
   which cursor-agent 2>/dev/null  # for cursor reviews (NOT `cursor` — that's the GUI/Electron binary)
   which codex 2>/dev/null         # for codex reviews
   which claude 2>/dev/null        # for claude reviews
   which agy 2>/dev/null           # for gemini reviews (Antigravity CLI)
   ```
   Skip missing tools and report them. If every tool is missing, fail.

3. Determine the workspace path:
   ```bash
   REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
   ```

4. Prepare the prompt. External CLIs do not inherit the current session context, so serialize everything needed for review.
   - **CRITICAL:** Always prepend the following instruction to every prompt sent to an external agent:
     `"You are being invoked as a reviewer. Provide YOUR OWN review directly. Do NOT delegate by invoking other peer-review CLIs (cursor, codex, gemini, claude) — you ARE the reviewer, not a dispatcher. File-inspection tools (Read, Glob, Grep, Bash for read-only commands like git/ls/cat) are EXPECTED and encouraged — use them to ground your review in actual code."`
   - This prevents recursive agent invocation (e.g. Codex calling Cursor/Claude from within its review) while making clear that file-inspection tools are not blocked. Without that clarification, reviewers sometimes refuse to read repo files at all and produce ungrounded reviews.
   - Include the full spec text when reviewing a spec.
   - Fetch and include the GitHub issue body with `gh issue view` when reviewing an issue.
   - Include file paths or diffs when reviewing code.
   - State the kind of feedback required.
   - For large prompts such as full diffs or long specs, write the prompt to a temp file:
     ```bash
     PROMPT_FILE=$(mktemp /tmp/peer-review-XXXXXXXXXXXX)
     mv "$PROMPT_FILE" "${PROMPT_FILE}.md"
     PROMPT_FILE="${PROMPT_FILE}.md"
     cat > "$PROMPT_FILE" <<'EOF'
     Your long review prompt here...
     EOF
     ```
   - Pass the file content via stdin or command substitution as described in step 5.

5. Run the review:

   **Cursor** (any review type):
   ```bash
   # Short prompts:
   cd "$REPO_ROOT" && cursor-agent --print --force --output-format text "Your prompt here"

   # Long prompts (avoid argv limits — write to temp file first):
   cd "$REPO_ROOT" && cursor-agent --print --force --output-format text "$(cat "$PROMPT_FILE")"
   ```
   Notes:
   - The CLI binary is `cursor-agent`, NOT `cursor`. `cursor` (and `cursor agent`) is the GUI/Electron
     launcher — it ignores `--print`/`--trust`/`--workspace` (Chromium warns "not in the list of known
     options") and opens a window instead of producing review output. Always use `cursor-agent`.
   - Use `--print` for non-interactive execution; `--force` auto-approves tool use so it doesn't block.
   - `cursor-agent` operates on the current working directory, so `cd "$REPO_ROOT"` first (no `--workspace` flag).
   - Use `"$(cat "$PROMPT_FILE")"` for long prompts because cursor-agent has no stdin mode.
   - If the prompt exceeds about 100 KB, send a summary plus a pointer to the temp file.

   **Claude** (any review type):
   ```bash
   # Short prompts:
   cd "$REPO_ROOT" && claude -p "Your prompt here" --allowedTools Bash,Read,Glob,Grep

   # Long prompts (use stdin):
   cd "$REPO_ROOT" && cat "$PROMPT_FILE" | claude -p - --allowedTools Bash,Read,Glob,Grep
   ```
   Notes:
   - Use `claude -p` for non-interactive execution.
   - Restrict review runs to `Bash,Read,Glob,Grep`.
   - Change into the repo root before invoking Claude.
   - Let Claude read files with its tools when needed for code review.

   **Codex** (plan/design/arbitrary review):
   ```bash
   # Short prompts:
   codex exec "Your prompt here"

   # Long prompts (use stdin):
   cat "$PROMPT_FILE" | codex exec -
   ```
   Notes:
   - Use `codex exec -` for stdin-based prompts of any size.
   - Change into the relevant repo before invoking Codex.
   - Add `--skip-git-repo-check` only when not in a git repo.
   - Do not hardcode a model.

   **Codex** (uncommitted code changes only):
   ```bash
   codex review --uncommitted "Optional custom review instructions"
   ```
   Notes:
   - Require `--uncommitted` for working tree review.
   - Use this only for real local diffs, not for conversation content.

   **Gemini** (via the Antigravity `agy` CLI — any review type):
   ```bash
   # Short prompts:
   cd "$REPO_ROOT" && agy -p "Your prompt here" \
     --model "Gemini 3.1 Pro (High)" --dangerously-skip-permissions --print-timeout 8m

   # Long prompts (use stdin — pass `-` as the prompt argument):
   cd "$REPO_ROOT" && cat "$PROMPT_FILE" | agy -p - \
     --model "Gemini 3.1 Pro (High)" --dangerously-skip-permissions --print-timeout 8m
   ```
   Notes:
   - The standalone `gemini` CLI (`@google/gemini-cli`) is deprecated: its free-tier OAuth now fails with
     `IneligibleTierError` ("no longer supported for Gemini Code Assist for individuals … migrate to
     Antigravity"). Use `agy` instead — it's the Antigravity terminal agent and authenticates through the
     Antigravity app. (The `antigravity` command itself is the GUI/Electron IDE launcher, not a headless
     agent — don't use it for reviews.)
   - `agy -p`/`--print`/`--prompt` runs a single prompt non-interactively and prints the response. `-p -`
     reads the prompt from stdin (use for long prompts).
   - `--dangerously-skip-permissions` auto-approves tool/permission requests so the run doesn't block on a
     prompt; `agy` runs against the current working directory, so `cd "$REPO_ROOT"` first (or pass `--add-dir`).
   - Pick a model with `--model` using its display name from `agy models` (e.g. `"Gemini 3.1 Pro (High)"`,
     `"Gemini 3.5 Flash (High)"`; Claude and GPT-OSS models are also offered). Default is a Flash tier.
   - Print mode waits up to `--print-timeout` (default 5m); raise it for large diffs/specs.

6. When running multiple reviews in parallel, use background execution for all Bash calls. Present every completed result even if one review fails.

7. Handle failures explicitly.
   - Show stderr output when a tool exits non-zero.
   - Report timeouts after 5 minutes.
   - Never swallow errors silently.

8. Present results with clear labels.
   - In conversation, use `## Cursor feedback`, `## Claude feedback`, and `## Codex feedback`.
   - For GitHub issues, post separate comments headed `## Review: Cursor`, `## Review: Claude`, and `## Review: Codex`.

9. Apply feedback as new comments rather than editing the original spec or plan.
   - Preserve the original spec as the starting context.
   - After each review round, post a consolidated improvements comment describing accepted feedback and resulting changes.
   - Include both the original spec and prior improvement comments in later review prompts so the reviewer sees the current state.
   - Maintain an auditable trail from original spec to accepted improvements.

## Important

- Serialize context into prompts because external CLIs cannot see the current session conversation.
- All tools may take 1-5 minutes to respond.
- Specify the feedback type clearly, such as spec completeness, API design, or code quality.
- `codex exec` requires a git repo unless `--skip-git-repo-check` is passed.
- Cursor has no stdin mode, so use a temp file for large prompts. Claude and Codex support stdin.
- Keep the reviewer different from the authoring agent. If Claude wrote the work, review with Cursor or Codex. If Cursor wrote it, review with Claude or Codex.
