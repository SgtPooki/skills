#!/usr/bin/env python3
"""slopcheck — measure structural erosion and code duplication in a codebase.

Metrics are modeled on SlopCodeBench (arXiv:2603.24755):

  * EROSION: the fraction of total "complexity mass" that lives in
    high-complexity functions (CCN > 10), with mass(f) = CCN(f) * sqrt(NLOC(f))
    per the paper. High erosion means complexity is concentrating in a few
    god-functions instead of being distributed across small, focused ones.

  * DUPLICATION: the fraction of source lines that appear in duplicated
    blocks (structural clones). A proxy for the paper's "verbosity" metric.

  * DEAD CODE (Python only): unused imports/variables and redefinitions via
    ruff or pyflakes when available. New dead code fails the gate.

Usage:
    python slopcheck.py baseline [PATH]   Record the baseline (once per project)
    python slopcheck.py check    [PATH]   Compare against baseline; exit 1 if gates fail.
                                          On PASS the baseline auto-advances (ratchet),
                                          so tolerances are per-iteration, not cumulative slack.
    python slopcheck.py report   [PATH]   Print current metrics, no gating

Options:
    --ccn-threshold N     CCN above which a function counts as high-complexity (default 10)
    --max-ccn N           Hard ceiling for any single function's CCN (default 15)
    --erosion-tolerance F Allowed increase in erosion vs baseline (default 0.02)
    --dup-tolerance F     Allowed increase in duplication vs baseline (default 0.005)
    --grandfather-growth N Max CCN growth allowed in an already-hot function (default 2)
    --clone-window N      Minimum consecutive similar lines to count as a clone (default 6)
    --json                Emit machine-readable JSON instead of text
    --baseline-file PATH  Where the baseline lives (default: PATH/.slopcheck/baseline.json)
    --force               With `baseline`: allow overwriting an existing baseline
                          (also requires SLOPCHECK_ALLOW_RESET=1 in the environment)

Anti-gaming policy (deliberate; do not work around it):
  * Tolerances/thresholds LOOSER than the defaults are ignored unless the
    environment variable SLOPCHECK_ALLOW_OVERRIDE=1 is set — a human decision,
    not an in-session one. Stricter values are always honored.
  * `baseline` refuses to overwrite an existing baseline. The baseline advances
    automatically on every passing `check`; there is never a reason to re-run
    `baseline` mid-task. Overwriting requires --force AND SLOPCHECK_ALLOW_RESET=1.

Requires: pip install lizard  (language-agnostic complexity analysis, ~20 languages)
The clone detector is built in. Dead-code detection uses ruff or pyflakes when
present and is skipped (with a warning) otherwise.

Exit codes: 0 = OK / gates pass, 1 = gates fail, 2 = usage or environment error.
"""

import argparse
import hashlib
import json
import math
import os
import re
import shutil
import subprocess
import sys

try:
    import lizard
except ImportError:
    sys.stderr.write(
        "slopcheck: the 'lizard' package is required.\n"
        "Install it with: pip install lizard  (add --break-system-packages if needed)\n"
    )
    sys.exit(2)

METRICS_VERSION = 2  # v2: erosion mass = CCN * sqrt(NLOC); dead-code gate; ratchet baseline

DEFAULTS = {
    "ccn_threshold": 10,
    "max_ccn": 15,
    "erosion_tolerance": 0.02,
    "dup_tolerance": 0.005,
    "dup_line_cap": 50,
    "grandfather_growth": 2,
}

EXCLUDE_DIRS = {
    ".git", ".hg", ".svn", "node_modules", "vendor", "venv", ".venv", "env",
    "__pycache__", ".mypy_cache", ".pytest_cache", ".ruff_cache", ".tox",
    "dist", "build", "target", "out", ".next", ".slopcheck", "coverage",
    ".idea", ".vscode", "site-packages",
}

SOURCE_EXTENSIONS = {
    ".py", ".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".java", ".go",
    ".rs", ".c", ".h", ".cpp", ".cc", ".hpp", ".cs", ".rb", ".php", ".swift",
    ".kt", ".kts", ".scala", ".m", ".mm", ".lua", ".pl", ".r",
}

COMMENT_PREFIXES = ("#", "//", "--", ";", "*", "/*", '"""', "'''")

DEAD_CODE_RULES = "F401,F811,F841"  # unused import, redefinition, unused variable


def load_ignore_patterns(root, args):
    """Project-specific exclude globs, one per line, matched against the
    path relative to the scanned root (posix separators). Lines starting
    with '#' are comments. Looked up next to the baseline file first (so a
    repo's ignore rules apply even when scanning a worktree/copy of it),
    then at <root>/.slopcheck/ignore."""
    candidates = []
    bp = baseline_path(root, args)
    candidates.append(os.path.join(os.path.dirname(bp), "ignore"))
    candidates.append(os.path.join(root, ".slopcheck", "ignore"))
    patterns = []
    for c in candidates:
        if os.path.isfile(c):
            with open(c) as fh:
                for line in fh:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        patterns.append(line.rstrip("/"))
            break
    return patterns


def _is_ignored(rel_posix, patterns):
    import fnmatch
    for p in patterns:
        if fnmatch.fnmatch(rel_posix, p) or fnmatch.fnmatch(rel_posix, p + "/*") \
                or rel_posix == p or rel_posix.startswith(p + "/"):
            return True
    return False


def find_source_files(root, ignore_patterns=()):
    files = []
    for dirpath, dirnames, filenames in os.walk(root):
        rel_dir = os.path.relpath(dirpath, root).replace(os.sep, "/")
        dirnames[:] = [
            d for d in dirnames
            if d not in EXCLUDE_DIRS and not d.startswith(".")
            and not _is_ignored(f"{rel_dir}/{d}".lstrip("./"), ignore_patterns)
        ]
        for name in filenames:
            rel = f"{rel_dir}/{name}".lstrip("./")
            if os.path.splitext(name)[1].lower() in SOURCE_EXTENSIONS \
                    and not _is_ignored(rel, ignore_patterns):
                files.append(os.path.join(dirpath, name))
    return sorted(files)


def function_mass(ccn, nloc):
    """Paper-aligned complexity mass: CC(f) * sqrt(SLOC(f))."""
    return ccn * math.sqrt(max(nloc, 1))


def analyze_complexity(files, ccn_threshold, root):
    """Run lizard over files; return (function_records, erosion)."""
    functions = []
    for info in lizard.analyze_files(files):
        for fn in info.function_list:
            functions.append({
                "file": os.path.relpath(info.filename, root),
                "name": fn.long_name.strip(),
                "ccn": fn.cyclomatic_complexity,
                "nloc": fn.nloc,
            })
    total_mass = sum(function_mass(f["ccn"], f["nloc"]) for f in functions)
    hot_mass = sum(function_mass(f["ccn"], f["nloc"]) for f in functions
                   if f["ccn"] > ccn_threshold)
    erosion = (hot_mass / total_mass) if total_mass else 0.0
    return functions, erosion


def normalize_line(line):
    """Normalize a source line for clone comparison: strip whitespace and
    collapse string/number literals so near-identical logic still matches."""
    s = line.strip()
    if not s or s.startswith(COMMENT_PREFIXES):
        return None
    s = re.sub(r'"[^"]*"', '"S"', s)
    s = re.sub(r"'[^']*'", "'S'", s)
    s = re.sub(r"\b\d+(\.\d+)?\b", "N", s)
    s = re.sub(r"\s+", " ", s)
    return s


def detect_duplication(files, window):
    """Built-in structural clone detection.

    Slides a `window`-line hash over the normalized lines of every file; any
    window hash seen more than once marks all its lines as duplicated.
    Returns (duplicated_line_count, total_line_count, ratio).
    """
    per_file = []  # (file, [(orig_lineno, normalized), ...])
    for path in files:
        try:
            with open(path, encoding="utf-8", errors="replace") as fh:
                raw = fh.readlines()
        except OSError:
            continue
        norm = []
        for i, line in enumerate(raw):
            n = normalize_line(line)
            if n is not None:
                norm.append((i, n))
        per_file.append((path, norm))

    hash_locations = {}  # window_hash -> list of (file_idx, start_pos)
    for fi, (_, norm) in enumerate(per_file):
        for start in range(len(norm) - window + 1):
            chunk = "\n".join(n for _, n in norm[start:start + window])
            h = hashlib.md5(chunk.encode()).hexdigest()
            hash_locations.setdefault(h, []).append((fi, start))

    dup_lines = [set() for _ in per_file]  # per-file sets of duplicated positions
    for locations in hash_locations.values():
        if len(locations) < 2:
            continue
        for fi, start in locations:
            dup_lines[fi].update(range(start, start + window))

    total = sum(len(norm) for _, norm in per_file)
    duplicated = sum(len(s) for s in dup_lines)
    ratio = (duplicated / total) if total else 0.0
    return duplicated, total, ratio


def count_dead_code(files, root):
    """Count unused imports/variables/redefinitions in Python files.

    Uses ruff when available, falling back to pyflakes. Returns
    (count or None, tool_name or None). None count means "could not measure".
    """
    py_files = [f for f in files if f.endswith(".py")]
    if not py_files:
        return 0, "n/a"
    if shutil.which("ruff"):
        try:
            proc = subprocess.run(
                ["ruff", "check", "--select", DEAD_CODE_RULES,
                 "--output-format", "json", "--no-cache", *py_files],
                capture_output=True, text=True, cwd=root, timeout=120)
            return len(json.loads(proc.stdout or "[]")), "ruff"
        except (subprocess.SubprocessError, json.JSONDecodeError, OSError):
            pass
    try:
        import pyflakes  # noqa: F401
        proc = subprocess.run(
            [sys.executable, "-m", "pyflakes", *py_files],
            capture_output=True, text=True, cwd=root, timeout=120)
        pat = re.compile(r"imported but unused|assigned to but never used|redefinition of")
        return sum(1 for line in proc.stdout.splitlines() if pat.search(line)), "pyflakes"
    except (ImportError, subprocess.SubprocessError, OSError):
        return None, None


def collect_metrics(path, args):
    files = find_source_files(path, load_ignore_patterns(path, args))
    functions, erosion = analyze_complexity(files, args.ccn_threshold, path)
    dup_count, line_count, dup_ratio = detect_duplication(files, args.clone_window)
    dead_code, dead_tool = count_dead_code(files, path)
    hot = sorted((f for f in functions if f["ccn"] > args.ccn_threshold),
                 key=lambda f: -f["ccn"])
    max_ccn = max((f["ccn"] for f in functions), default=0)
    return {
        "version": METRICS_VERSION,
        "files_analyzed": len(files),
        "function_count": len(functions),
        "erosion": round(erosion, 4),
        "duplication": round(dup_ratio, 4),
        "duplicated_lines": dup_count,
        "total_code_lines": line_count,
        "max_ccn": max_ccn,
        "dead_code": dead_code,
        "dead_code_tool": dead_tool,
        "high_complexity_functions": [
            {"file": f["file"], "name": f["name"], "ccn": f["ccn"], "nloc": f["nloc"]}
            for f in hot
        ],
    }


def baseline_path(path, args):
    if args.baseline_file:
        return args.baseline_file
    return os.path.join(path, ".slopcheck", "baseline.json")


def write_baseline(bp, metrics):
    os.makedirs(os.path.dirname(bp) or ".", exist_ok=True)
    with open(bp, "w") as fh:
        json.dump(metrics, fh, indent=2)


def enforce_override_policy(args):
    """Clamp any gate parameter looser than the defaults unless a human has
    set SLOPCHECK_ALLOW_OVERRIDE=1. Stricter values always pass through.
    Returns a list of warning strings for anything that was clamped."""
    if os.environ.get("SLOPCHECK_ALLOW_OVERRIDE") == "1":
        return []
    clamped = []
    looser = [
        ("ccn_threshold", lambda v, d: v > d),
        ("max_ccn", lambda v, d: v > d),
        ("erosion_tolerance", lambda v, d: v > d),
        ("dup_tolerance", lambda v, d: v > d),
        ("dup_line_cap", lambda v, d: v > d),
        ("grandfather_growth", lambda v, d: v > d),
    ]
    for name, is_looser in looser:
        val, dflt = getattr(args, name), DEFAULTS[name]
        if is_looser(val, dflt):
            setattr(args, name, dflt)
            clamped.append(
                f"--{name.replace('_', '-')} {val} is looser than the default {dflt} "
                f"and was IGNORED. Loosening gates is a human decision: set "
                f"SLOPCHECK_ALLOW_OVERRIDE=1 to permit it, and say so in your final report.")
    return clamped


def print_report(metrics, header):
    print(f"== {header} ==")
    print(f"  files analyzed        : {metrics['files_analyzed']}")
    print(f"  functions             : {metrics['function_count']}")
    print(f"  erosion               : {metrics['erosion']:.1%}  "
          f"(mass CCN*sqrt(NLOC) in CCN>threshold functions)")
    print(f"  duplication           : {metrics['duplication']:.1%}  "
          f"({metrics['duplicated_lines']}/{metrics['total_code_lines']} lines in clones)")
    print(f"  max function CCN      : {metrics['max_ccn']}")
    if metrics.get("dead_code") is not None:
        print(f"  dead code             : {metrics['dead_code']} finding(s) "
              f"({metrics.get('dead_code_tool')})")
    hot = metrics["high_complexity_functions"]
    if hot:
        print(f"  high-complexity functions ({len(hot)}):")
        for f in hot[:10]:
            print(f"    CCN {f['ccn']:>3}  nloc {f['nloc']:>4}  {f['file']}  {f['name']}")
        if len(hot) > 10:
            print(f"    ... and {len(hot) - 10} more")


def cmd_baseline(path, args):
    bp = baseline_path(path, args)
    if os.path.exists(bp):
        if not (args.force and os.environ.get("SLOPCHECK_ALLOW_RESET") == "1"):
            sys.stderr.write(
                "slopcheck: a baseline already exists and will not be overwritten.\n"
                "The baseline advances automatically on every passing `check`; there is\n"
                "no reason to re-run `baseline` mid-task (doing so would launder\n"
                "accumulated slop into accepted history). To intentionally reset,\n"
                f"a human should run with --force and SLOPCHECK_ALLOW_RESET=1: {bp}\n")
            return 2
    metrics = collect_metrics(path, args)
    write_baseline(bp, metrics)
    if args.json:
        print(json.dumps({"action": "baseline", "metrics": metrics}, indent=2))
    else:
        print_report(metrics, "baseline recorded")
        print(f"  saved to: {bp}")
    return 0


def cmd_report(path, args):
    metrics = collect_metrics(path, args)
    if args.json:
        print(json.dumps({"action": "report", "metrics": metrics}, indent=2))
    else:
        print_report(metrics, "current metrics")
    return 0


def cmd_check(path, args):
    warnings = enforce_override_policy(args)
    metrics = collect_metrics(path, args)
    bp = baseline_path(path, args)
    baseline = None
    if os.path.exists(bp):
        with open(bp) as fh:
            baseline = json.load(fh)
        if baseline.get("version") != METRICS_VERSION:
            warnings.append(
                f"baseline was recorded by an older slopcheck (metrics v"
                f"{baseline.get('version', 1)} != v{METRICS_VERSION}); trajectory gates "
                "are skipped this run and the baseline will be upgraded on PASS.")
            baseline = None

    failures = []

    # Gate 1: hard ceiling on any single function's complexity.
    worst = [f for f in metrics["high_complexity_functions"] if f["ccn"] > args.max_ccn]
    if worst:
        if baseline:
            known = {(f["file"], f["name"]): f["ccn"]
                     for f in baseline.get("high_complexity_functions", [])
                     if f["ccn"] > args.max_ccn}
            new_worst = [f for f in worst if (f["file"], f["name"]) not in known]
            grandfathered = [f for f in worst if (f["file"], f["name"]) in known]
            if new_worst:
                failures.append(
                    f"{len(new_worst)} function(s) newly exceed CCN {args.max_ccn}: "
                    + "; ".join(f"{f['name']} (CCN {f['ccn']}, {f['file']})" for f in new_worst[:5]))
            grown = [f for f in grandfathered
                     if f["ccn"] > known[(f["file"], f["name"])] + args.grandfather_growth]
            if grown:
                failures.append(
                    f"{len(grown)} grandfathered function(s) grew more than "
                    f"+{args.grandfather_growth} CCN — legacy debt must shrink, not grow: "
                    + "; ".join(
                        f"{f['name']} (CCN {known[(f['file'], f['name'])]} -> {f['ccn']}, {f['file']})"
                        for f in grown[:5]))
            still = [f for f in grandfathered if f not in grown]
            if still:
                warnings.append(
                    f"{len(still)} pre-existing function(s) still exceed CCN "
                    f"{args.max_ccn} — refactor opportunistically.")
        else:
            failures.append(
                f"{len(worst)} function(s) exceed CCN {args.max_ccn}: "
                + "; ".join(f"{f['name']} (CCN {f['ccn']}, {f['file']})" for f in worst[:5]))

    # Gates 2 & 3: trajectory — don't get worse than baseline.
    if baseline:
        d_erosion = metrics["erosion"] - baseline["erosion"]
        d_dup = metrics["duplication"] - baseline["duplication"]
        if d_erosion > args.erosion_tolerance:
            failures.append(
                f"erosion rose {d_erosion:+.1%} (baseline {baseline['erosion']:.1%} -> "
                f"{metrics['erosion']:.1%}); complexity is concentrating. Extract helpers "
                f"from the functions listed above.")
        d_dup_lines = metrics["duplicated_lines"] - baseline.get("duplicated_lines", 0)
        if d_dup > args.dup_tolerance or d_dup_lines > args.dup_line_cap:
            failures.append(
                f"duplication rose {d_dup:+.1%} / {d_dup_lines:+d} clone lines "
                f"(ratio tolerance {args.dup_tolerance:.1%}, absolute cap "
                f"{args.dup_line_cap} lines); code is being copy-pasted instead of shared.")
        # Gate 4: dead code must not accumulate.
        if metrics.get("dead_code") is not None and baseline.get("dead_code") is not None:
            if metrics["dead_code"] > baseline["dead_code"]:
                failures.append(
                    f"dead code rose ({baseline['dead_code']} -> {metrics['dead_code']} "
                    f"findings via {metrics.get('dead_code_tool')}); remove unused "
                    f"imports/variables and leftover definitions.")
    else:
        warnings.append("no baseline found — absolute gates only. "
                        "Run 'slopcheck.py baseline' at the start of each project.")
    if metrics.get("dead_code") is None:
        warnings.append("dead-code detection unavailable (install ruff or pyflakes); "
                        "review unused imports/variables manually in Step 4.")

    passed = not failures
    if passed and os.path.exists(bp):
        # Ratchet: advancing the baseline on PASS makes the tolerances
        # per-iteration and removes any reason to re-run `baseline`.
        write_baseline(bp, metrics)

    if args.json:
        print(json.dumps({
            "action": "check", "passed": passed, "metrics": metrics,
            "baseline": baseline, "failures": failures, "warnings": warnings,
        }, indent=2))
    else:
        print_report(metrics, "check")
        if baseline:
            print(f"  vs baseline erosion   : {baseline['erosion']:.1%} -> "
                  f"{metrics['erosion']:.1%}")
            print(f"  vs baseline duplication: {baseline['duplication']:.1%} -> "
                  f"{metrics['duplication']:.1%}")
        for w in warnings:
            print(f"  WARN: {w}")
        if failures:
            print("\nRESULT: FAIL — do not declare this work done yet.")
            for f in failures:
                print(f"  FAIL: {f}")
            print("\nFix by refactoring (extract functions, unify duplicated logic, "
                  "delete dead code), re-run your tests, then re-run this check.")
        else:
            print("\nRESULT: PASS — quality gates satisfied (baseline advanced).")
    return 0 if passed else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("command", choices=["baseline", "check", "report"])
    ap.add_argument("path", nargs="?", default=".")
    ap.add_argument("--ccn-threshold", type=int, default=DEFAULTS["ccn_threshold"])
    ap.add_argument("--max-ccn", type=int, default=DEFAULTS["max_ccn"])
    ap.add_argument("--erosion-tolerance", type=float, default=DEFAULTS["erosion_tolerance"])
    ap.add_argument("--dup-tolerance", type=float, default=DEFAULTS["dup_tolerance"])
    ap.add_argument("--dup-line-cap", type=int, default=DEFAULTS["dup_line_cap"])
    ap.add_argument("--grandfather-growth", type=int, default=DEFAULTS["grandfather_growth"])
    ap.add_argument("--clone-window", type=int, default=6)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--baseline-file", default=None)
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    path = os.path.abspath(args.path)
    if not os.path.isdir(path):
        sys.stderr.write(f"slopcheck: not a directory: {path}\n")
        return 2

    if args.command == "baseline":
        return cmd_baseline(path, args)
    if args.command == "report":
        return cmd_report(path, args)
    return cmd_check(path, args)


if __name__ == "__main__":
    sys.exit(main())
