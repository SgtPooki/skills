#!/usr/bin/env python3
"""writingcheck — prose quality gate for agent-drafted text.

Wraps Vale (lexical slop, markdown-aware) and adds structural checks Vale
cannot express. The gate blocks on errors only; warnings/suggestions are
advisory. PASS means "no known mechanical smells" — it does NOT mean the
draft's claims are verified; sourcing numbers and facts stays the writer's
job. See ../SKILL.md for the workflow.

Usage:
    python3 <skill-path>/scripts/writingcheck.py <scenario> [file | -]
    python3 <skill-path>/scripts/writingcheck.py --selftest

Scenarios (must match a layer-2 writing skill name):
    writing-docs | github-writing | writing-spec | writing-community
    core   (fallback when no layer-2 skill applies)

Options:
    --overlay my-voice   Add the built-in author-voice idiom checks
                         (em-dash ban, no emoji). This is the only overlay
                         the checker ships; it is not a plugin system.
    --json               Machine-readable output (includes "mode":
                         "full" | "reduced")
    --selftest           Run golden fixtures + subprocess path tests

Input:
    A file path, or '-' to read the draft from stdin (for ephemeral text such
    as PR bodies, issue text, and commit messages that never exist on disk).
    All checks run in memory; a temp file is created only for Vale, and if no
    writable temp dir exists the script degrades to reduced checks instead of
    crashing.

Exit codes: 0 = pass, 1 = errors found, 2 = usage/environment error.
If Vale is missing or unusable, the script reports the reduced mode
explicitly and never silently skips.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
VALE_DIR = SKILL_DIR / "vale"
FIXTURES_DIR = SKILL_DIR / "fixtures"
SCENARIOS = (
    "core",
    "writing-docs",
    "github-writing",
    "writing-spec",
    "writing-community",
)

VALE_INSTALL_HINT = (
    "vale not found. Install: `brew install vale` (macOS) or "
    "see https://vale.sh/docs/install. Falling back to reduced checks "
    "(Slop word rules + structural checks only; grammar/style rules skipped)."
)

SUMMARY_HEADINGS = re.compile(
    r"^(summary|conclusion|conclusions|wrap[- ]?up|in summary|final thoughts|closing thoughts)$",
    re.IGNORECASE,
)

EMOJI = re.compile(
    "[\U0001f300-\U0001faff\U00002600-\U000027bf\U0001f1e6-\U0001f1ff⬀-⯿️]"
)

FENCE_RE = re.compile(r"^\s*(```|~~~)")
BULLET_RE = re.compile(r"^\s{0,3}[-*+]\s+(.*)$")
CHANGELOG_HEADINGS = re.compile(
    r"^(added|changed|deprecated|removed|fixed|security|breaking( changes?)?)$",
    re.IGNORECASE,
)
# Unattributed-stat heuristic: percentages, multipliers, percentile claims.
STAT_RE = re.compile(r"~?\d+(?:\.\d+)?\s*(?:%|×|x\s+(?:faster|slower|more|fewer))|\bp\d{2}\b")
LINKISH = re.compile(r"https?://|\]\(|\bsee\b|\bmeasured\b|\bbenchmark", re.IGNORECASE)


def finding(line: int, check: str, message: str, severity: str = "error") -> dict:
    return {"line": line, "severity": severity, "check": check, "message": message}


def strip_code(text: str) -> tuple[str, bool]:
    """Blank out fenced code blocks and inline code, preserving line count.

    Fences are paired: an opener without a closer (a real agent failure mode)
    blanks only up to EOF but is REPORTED via the returned flag so the caller
    can surface it — an unclosed fence must never silently disable linting.
    """
    out, in_fence = [], False
    for line in text.splitlines():
        if FENCE_RE.match(line):
            in_fence = not in_fence
            out.append("")
        elif in_fence:
            out.append("")
        else:
            out.append(re.sub(r"`[^`]*`", "", line))
    return "\n".join(out), in_fence


# ---------------------------------------------------------------------------
# Vale integration + fallback lexical scan


def run_vale(scenario: str, text: str, path: Path | None) -> tuple[list[dict], str]:
    """Return (findings, mode). mode: 'full' when Vale ran, else 'reduced'.

    All degradations are explicit: missing binary, unwritable temp dir, Vale
    crash, or unparseable output each fall back to the reduced lexical scan.
    """
    vale = shutil.which("vale")
    if not vale:
        return fallback_lexical(text), "reduced"
    tmp_path, cleanup = path, False
    if tmp_path is None:
        try:
            tmp = tempfile.NamedTemporaryFile(
                mode="w", suffix=".md", delete=False, encoding="utf-8"
            )
            tmp.write(text)
            tmp.close()
            tmp_path, cleanup = Path(tmp.name), True
        except OSError:
            print("VALE_TEMP_UNAVAILABLE: no writable temp dir; reduced checks.", file=sys.stderr)
            return fallback_lexical(text), "reduced"
    config = VALE_DIR / f"{scenario}.ini"
    proc = subprocess.run(
        [vale, "--config", str(config), "--output=JSON", str(tmp_path)],
        capture_output=True,
        text=True,
    )
    if cleanup:
        tmp_path.unlink(missing_ok=True)
    # Vale: 0 = clean, 1 = alerts found; anything else is a Vale failure.
    if proc.returncode not in (0, 1):
        print(f"VALE_ERROR (exit {proc.returncode}): {proc.stderr.strip()[:300]}", file=sys.stderr)
        return fallback_lexical(text), "reduced"
    findings = []
    if proc.stdout.strip():
        try:
            for file_alerts in json.loads(proc.stdout).values():
                for a in file_alerts:
                    findings.append(
                        finding(a["Line"], a["Check"], a["Message"], a["Severity"])
                    )
        except (json.JSONDecodeError, KeyError, TypeError):
            print("VALE_ERROR: unparseable Vale output; reduced checks.", file=sys.stderr)
            return fallback_lexical(text), "reduced"
    return findings, "full"


def load_slop_rule(rule_file: Path) -> dict:
    """Parse one Slop rule. Uses PyYAML when available; otherwise a minimal
    line parser that handles the flat token/raw lists these rules use (it is
    NOT a general YAML parser — keep Slop rules flat)."""
    try:
        import yaml  # type: ignore

        return yaml.safe_load(rule_file.read_text())
    except ImportError:
        body = rule_file.read_text()
        rule: dict = {"level": "error", "tokens": [], "raw": []}
        m = re.search(r"^level:\s*(\w+)", body, re.M)
        if m:
            rule["level"] = m.group(1)
        section = None
        for line in body.splitlines():
            if re.match(r"^tokens:\s*$", line):
                section = "tokens"
            elif re.match(r"^raw:\s*$", line):
                section = "raw"
            elif re.match(r"^\S", line):
                section = None
            elif section:
                m = re.match(r"^\s+-\s+(['\"]?)(.+?)\1\s*$", line)
                if m:
                    rule[section].append(m.group(2))
        return rule


def fallback_lexical(text: str) -> list[dict]:
    """Reduced lexical scan when Vale is unavailable: apply the Slop style's
    rules directly so the rule source stays single-sourced."""
    findings = []
    prose, _ = strip_code(text)
    lines = prose.splitlines()
    for rule_file in sorted((VALE_DIR / "styles" / "Slop").glob("*.yml")):
        rule = load_slop_rule(rule_file)
        regexes = []
        if rule.get("tokens"):
            regexes.append(r"\b(?:" + "|".join(rule["tokens"]) + r")\b")
        regexes += rule.get("raw") or []
        for rx in regexes:
            try:
                creg = re.compile(rx, re.IGNORECASE)
            except re.error:
                continue
            for i, line in enumerate(lines, 1):
                m = creg.search(line)
                if m:
                    findings.append(
                        finding(
                            i,
                            f"Slop.{rule_file.stem}",
                            f"matched '{m.group(0)}'",
                            rule.get("level", "error"),
                        )
                    )
    return findings


# ---------------------------------------------------------------------------
# Structural checks (markdown-aware, scenario-scoped)


def parse_sections(lines: list[str]) -> list[dict]:
    sections = []
    for i, line in enumerate(lines):
        m = re.match(r"^(#{1,6})\s+(.*)$", line)
        if m:
            sections.append({"line": i + 1, "level": len(m.group(1)), "title": m.group(2).strip()})
    return sections


def group_bullet_lists(lines: list[str]) -> list[list[tuple[int, str]]]:
    """Group consecutive top-level bullets into lists. Blank lines and indented
    continuation lines extend the current list; continuation text counts toward
    the bullet's length."""
    lists: list[list[tuple[int, str]]] = []
    current: list[tuple[int, str]] = []
    for i, line in enumerate(lines, 1):
        m = BULLET_RE.match(line)
        if m:
            current.append((i, m.group(1)))
        elif current and (line.strip() == "" or re.match(r"^\s{2,}\S", line)):
            if line.strip():
                ln, txt = current[-1]
                current[-1] = (ln, txt + " " + line.strip())
        elif current:
            lists.append(current)
            current = []
    if current:
        lists.append(current)
    return lists


def one_item_exempt(scenario: str, heading: str) -> bool:
    if scenario == "writing-spec" and re.search(r"consequence", heading, re.IGNORECASE):
        return True
    return scenario == "writing-community" and bool(CHANGELOG_HEADINGS.match(heading))


def check_bullet_lists(scenario: str, lines: list[str], sections: list[dict]) -> list[dict]:
    def enclosing_heading(line_no: int) -> str:
        title = ""
        for s in sections:
            if s["line"] < line_no:
                title = s["title"]
        return title

    findings = []
    # Parallel lists are legitimate in reference docs and issue templates —
    # symmetry is advisory there, blocking elsewhere.
    sym_severity = "warning" if scenario in ("writing-docs", "github-writing") else "error"
    for lst in group_bullet_lists(lines):
        head = enclosing_heading(lst[0][0])
        if len(lst) == 1 and not one_item_exempt(scenario, head or ""):
            findings.append(
                finding(lst[0][0], "Structure.OneItemList", "Single-bullet list — write it as a sentence.")
            )
        if len(lst) >= 4 and scenario != "writing-spec":
            counts = [len(item.split()) for _, item in lst]
            # Backtick-led bullets are API/field lists; symmetry is expected.
            if all(item.lstrip().startswith("`") for _, item in lst):
                continue
            if max(counts) - min(counts) <= 1 and min(counts) >= 6:
                findings.append(
                    finding(
                        lst[0][0],
                        "Structure.SymmetricBullets",
                        f"{len(lst)} bullets of near-identical length ({min(counts)}-"
                        f"{max(counts)} words) — vary emphasis or merge; not every point "
                        "deserves equal weight.",
                        sym_severity,
                    )
                )
    return findings


def check_closing_summary(lines: list[str], sections: list[dict]) -> list[dict]:
    """Summary/Conclusion heading in the final 30% of the document."""
    if not sections or len(lines) <= 10:
        return []
    cutoff = len(lines) * 0.7
    return [
        finding(
            s["line"],
            "Structure.ClosingSummary",
            f"'{s['title']}' section at the end — if it restates the body, delete it; "
            "readers already read the body.",
        )
        for s in sections
        if s["line"] >= cutoff and SUMMARY_HEADINGS.match(s["title"])
    ]


def check_thin_sections(scenario: str, lines: list[str], sections: list[dict]) -> list[dict]:
    """Headings whose entire section is a single short sentence. Advisory in
    github-writing: issue/PR templates legitimately have short sections."""
    severity = "warning" if scenario == "github-writing" else "error"
    findings = []
    for idx, s in enumerate(sections):
        end = sections[idx + 1]["line"] - 1 if idx + 1 < len(sections) else len(lines)
        body = " ".join(l.strip() for l in lines[s["line"] : end] if l.strip())
        if body and len(body) < 120 and body.count(". ") == 0 and not BULLET_RE.match(body):
            findings.append(
                finding(
                    s["line"],
                    "Structure.HeadingOverOneSentence",
                    f"Heading '{s['title']}' covers a single sentence — fold it into surrounding prose.",
                    severity,
                )
            )
    return findings


def check_unattributed_stats(lines: list[str]) -> list[dict]:
    """Advisory: numbers that look like performance/proportion claims with no
    nearby source. Heuristic — the writer's verify-before-asserting duty is
    NOT discharged by passing this check."""
    findings = []
    for i, line in enumerate(lines, 1):
        if STAT_RE.search(line) and not LINKISH.search(line):
            findings.append(
                finding(
                    i,
                    "Claims.UnattributedStat",
                    "Stat-like claim with no visible source — verify it, link it, or cut it.",
                    "warning",
                )
            )
    return findings


def check_markdown_mechanics(lines: list[str], base_dir: Path | None) -> list[dict]:
    """Advisory markdown integrity: table row width mismatches, and dead
    relative links when the draft is a real file on disk."""
    findings = []
    header_cols, table_start = None, 0
    for i, line in enumerate(lines, 1):
        if line.strip().startswith("|"):
            cols = line.strip().strip("|").count("|") + 1
            if header_cols is None:
                header_cols, table_start = cols, i
            elif cols != header_cols and not re.match(r"^\s*\|[\s:|-]+\|?\s*$", line):
                findings.append(
                    finding(
                        i,
                        "Markdown.TableWidth",
                        f"Row has {cols} cells; the table starting at L{table_start} has {header_cols}.",
                        "warning",
                    )
                )
        else:
            header_cols = None
    if base_dir:
        for i, line in enumerate(lines, 1):
            for m in re.finditer(r"\]\(([^)#?\s]+)\)", line):
                target = m.group(1)
                if re.match(r"^[a-z]+:", target):
                    continue
                if not (base_dir / target).exists():
                    findings.append(
                        finding(i, "Markdown.DeadLink", f"Relative link target not found: {target}", "warning")
                    )
    return findings


def check_github_shape(scenario: str, lines: list[str], sections: list[dict]) -> list[dict]:
    """Advisory: a long, sectioned github draft should carry a purpose-bearing
    heading. Skipped for short drafts (commit messages, comments)."""
    if scenario != "github-writing" or not sections:
        return []
    words = sum(len(l.split()) for l in lines)
    if words < 80:
        return []
    purpose = re.compile(r"what changed|description|summary|impact|motivation|context|problem", re.IGNORECASE)
    if any(purpose.search(s["title"]) for s in sections):
        return []
    return [
        finding(
            sections[0]["line"],
            "Structure.NoPurposeHeading",
            "Sectioned draft with no purpose-bearing heading (What changed / Description / Impact...).",
            "warning",
        )
    ]


def structural_checks(scenario: str, text: str, base_dir: Path | None = None) -> list[dict]:
    prose, unclosed = strip_code(text)
    lines = prose.splitlines()
    sections = parse_sections(lines)
    findings = (
        check_bullet_lists(scenario, lines, sections)
        + check_closing_summary(lines, sections)
        + check_thin_sections(scenario, lines, sections)
        + check_unattributed_stats(lines)
        + check_markdown_mechanics(lines, base_dir)
        + check_github_shape(scenario, lines, sections)
    )
    if unclosed:
        findings.append(
            finding(
                len(lines),
                "Markdown.UnclosedFence",
                "Unclosed code fence — everything after it was treated as code and NOT prose-linted. Close the fence and re-run.",
            )
        )
    return findings


def overlay_checks(overlay: str, text: str) -> list[dict]:
    """Built-in author-voice idiom checks (the only overlay shipped). Generic
    rules only — the personal voice profile itself lives outside this repo."""
    findings = []
    if overlay != "my-voice":
        return findings
    prose, _ = strip_code(text)
    for i, line in enumerate(prose.splitlines(), 1):
        if "—" in line or "–" in line:
            findings.append(
                finding(
                    i,
                    "Voice.EmDash",
                    "Em/en dash — replace with a comma, colon, parentheses, or a new sentence.",
                )
            )
        if EMOJI.search(line):
            findings.append(finding(i, "Voice.Emoji", "Unicode emoji — remove it."))
    return findings


# ---------------------------------------------------------------------------


def check(scenario: str, text: str, path: Path | None, overlay: str | None) -> tuple[list[dict], str]:
    vale_findings, mode = run_vale(scenario, text, path)
    base_dir = path.parent if path else None
    findings = vale_findings + structural_checks(scenario, text, base_dir)
    if overlay:
        findings += overlay_checks(overlay, text)
    return findings, mode


def run_fixture(fixture: Path) -> tuple[bool, list[dict]]:
    m = re.match(r"(.+)-(pass|fail)$", fixture.stem)
    if not m:
        return True, []
    scenario, expected = m.group(1), m.group(2)
    if scenario not in SCENARIOS:
        scenario = "core"
    findings, _ = check(scenario, fixture.read_text(encoding="utf-8"), fixture, None)
    errors = [f for f in findings if f["severity"] == "error"]
    ok = bool(errors) if expected == "fail" else not errors
    return ok, errors


def selftest_subprocess_paths() -> int:
    """Exercise the invocation paths golden fixtures can't: stdin, overlay,
    and the Vale-missing fallback."""
    script = str(Path(__file__).resolve())
    cases = [
        ("stdin pipe", ["python3", script, "github-writing", "-"], "Fixed the retry test.\n", 0, None),
        ("stdin slop", ["python3", script, "core", "-"], "This delves into things.\n", 1, None),
        ("overlay em-dash", ["python3", script, "core", "-", "--overlay", "my-voice"], "A line — with a dash.\n", 1, None),
        ("vale-missing", ["python3", script, "core", "-"], "This delves into things.\n", 1, "/usr/bin:/bin"),
    ]
    failures = 0
    for name, cmd, stdin, want, path_env in cases:
        env = dict(__import__("os").environ)
        if path_env:
            env["PATH"] = path_env
        proc = subprocess.run(cmd, input=stdin, capture_output=True, text=True, env=env)
        ok = proc.returncode == want
        print(f"  {'ok' if ok else 'FAIL'}  path:{name} (exit {proc.returncode}, want {want})")
        if not ok:
            failures += 1
            print(f"        {proc.stdout.strip()[:200]} {proc.stderr.strip()[:200]}")
    return failures


def selftest() -> int:
    """Golden fixtures (*-fail.md → >=1 error, *-pass.md → clean) plus
    subprocess tests for stdin/overlay/fallback paths."""
    failures = 0
    for fixture in sorted(FIXTURES_DIR.glob("*.md")):
        ok, errors = run_fixture(fixture)
        print(f"  {'ok' if ok else 'FAIL'}  {fixture.name}  ({len(errors)} errors)")
        if not ok:
            failures += 1
            for f in errors[:5]:
                print(f"        L{f['line']} {f['check']}: {f['message']}")
    failures += selftest_subprocess_paths()
    print("selftest:", "PASS" if failures == 0 else f"{failures} case(s) failed")
    return 0 if failures == 0 else 1


def read_input(arg: str) -> tuple[str | None, Path | None]:
    """Return (text, path). Stdin is read fully into memory — no temp file."""
    if arg == "-":
        if sys.stdin.isatty():
            print("stdin requested ('-') but nothing is piped in.", file=sys.stderr)
            return None, None
        return sys.stdin.read(), None
    path = Path(arg)
    if not path.exists():
        print(f"no such file: {path}", file=sys.stderr)
        return None, None
    return path.read_text(encoding="utf-8"), path


def report(errors: list[dict], advisory: list[dict], mode: str, as_json: bool) -> None:
    if as_json:
        print(json.dumps({"mode": mode, "errors": errors, "advisory": advisory}, indent=2))
        return
    for f in errors:
        print(f"ERROR  L{f['line']}  {f['check']}: {f['message']}")
    for f in advisory:
        print(f"note   L{f['line']}  {f['check']}: {f['message']}")
    verdict = "PASS" if not errors else "FAIL"
    scope = "" if mode == "full" else " (reduced checks — Vale unavailable)"
    print(f"{verdict}{scope}: {len(errors)} error(s), {len(advisory)} advisory")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("scenario", nargs="?", choices=SCENARIOS)
    ap.add_argument("input", nargs="?", help="file path, or '-' for stdin")
    ap.add_argument("--overlay", choices=["my-voice"], help="built-in author-voice overlay (single-tenant)")
    ap.add_argument("--json", action="store_true", dest="as_json")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    if args.selftest:
        return selftest()
    if not args.scenario or not args.input:
        ap.error("scenario and input are required (or use --selftest)")

    text, path = read_input(args.input)
    if text is None:
        return 2
    if not shutil.which("vale"):
        print(f"VALE_MISSING: {VALE_INSTALL_HINT}")
    findings, mode = check(args.scenario, text, path, args.overlay)
    errors = [f for f in findings if f["severity"] == "error"]
    advisory = [f for f in findings if f["severity"] != "error"]
    report(errors, advisory, mode, args.as_json)
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
