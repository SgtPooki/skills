#!/usr/bin/env python3
"""A/B a SKILL.md edit against a fixed probe set.

Prose edits to a SKILL.md change agent behavior, and writingcheck.py cannot
see that: it tests the linter, not the skill. This runs the same probes under
two versions of a skill file and reports what moved.

    ./run.py --probes probes/bluf.jsonl                  # HEAD vs working tree
    ./run.py --probes probes/bluf.jsonl --model gemma4:31b-q8
    ./run.py --report-only                               # re-grade saved outputs

Arms are "baseline" (the file as committed at HEAD) and "candidate" (the
working tree). With no uncommitted change to the skill under test the two arms
are identical, which is itself a useful harness self-check.

Grading is deliberately partial. The mechanical signals below catch the
regression this harness exists to catch — an exception in one scenario leaking
into the others — but a human still reads the diffs. Nothing here decides
whether prose is good.
"""
import argparse, json, re, subprocess, sys, tempfile, urllib.request
from pathlib import Path

EVAL_DIR = Path(__file__).resolve().parent
SKILLS_DIR = EVAL_DIR.parent.parent           # skills/
REPO_ROOT = SKILLS_DIR.parent                 # repo root
CORE = "skills/writing-core/SKILL.md"         # repo-relative; the file under test
CHECKER = SKILLS_DIR / "writing-core" / "scripts" / "writingcheck.py"

# A full run is 2 generations per probe. Keep that off shared/remote endpoints
# unless the caller opts in: omp falls back to its configured default provider
# when a bare model name does not match anything locally.

# First-sentence buildup: the failure BLUF exists to prevent.
THROAT_CLEARING = re.compile(
    r"^\s*(in this|this document|this (post|guide|article|readme)\s+(will|aims|covers)"
    r"|we (are|'re) (excited|thrilled|pleased)|before we|first,? let|let's (talk|start|dive)"
    r"|it is worth noting|it's worth noting|as (you|we) (may|might) know)",
    re.IGNORECASE,
)


# A capable model asked for a brief instead of drafting. Scoring that as if it
# were the artifact silently turns "asked a question" into a BLUF or hook
# signal, so it is reported as its own outcome and excluded from comparison.
ASKED_FOR_BRIEF = re.compile(
    r"\b(i need (specific )?(details|to know|a few|more)|before (i|drafting)"
    r"|to avoid fabricat|i'd be (violating|making up)|what i need from you"
    r"|could you (confirm|tell me|share)|i can't write .{0,40}without)\b",
    re.IGNORECASE,
)


def sentences(text: str, n: int) -> str:
    """First n sentences of the first non-heading, non-blank prose line."""
    for line in text.splitlines():
        s = line.strip()
        if not s or s.startswith(("#", "```", "|", ">", "---")):
            continue
        s = re.sub(r"^[-*+]\s+", "", s)
        return " ".join(re.split(r"(?<=[.!?])\s+", s)[:n])
    return ""


def skill_text(arm: str, scenario: str, candidate_file: str | None = None) -> str:
    if arm == "candidate" and candidate_file:
        core = Path(candidate_file).read_text()
    elif arm == "baseline":
        core = subprocess.run(["git", "show", f"HEAD:{CORE}"], cwd=REPO_ROOT,
                              capture_output=True, text=True, check=True).stdout
    else:
        core = (REPO_ROOT / CORE).read_text()
    scen = (SKILLS_DIR / scenario / "SKILL.md").read_text()
    return f"{core}\n\n---\n\n{scen}"


def generate(probe: dict, arm: str, model: str, host: str, num_ctx: int,
             timeout: int, backend: str = "ollama", candidate_file: str | None = None) -> str:
    """POST straight to the local model server.

    Deliberately not routed through an agent CLI: those resolve a bare model
    name by fuzzy match and fall back to whatever default provider is
    configured, which can be a shared remote endpoint. A direct call to an
    explicit host cannot silently go somewhere else. Pinning num_ctx matters
    too -- a model loaded at its full advertised context can take tens of GB
    of VRAM and fail every request with a compute error.
    """
    sys_prompt = (
        skill_text(arm, probe["scenario"], candidate_file)
        + "\n\n---\n\nFollow the skills above. Output only the requested artifact, "
          "with no preamble and no commentary about your process."
    )
    if backend == "claude-cli":
        # Runs from /tmp so no project CLAUDE.md is picked up. A user-level
        # ~/.claude/CLAUDE.md still applies to both arms equally.
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as fh:
            fh.write(sys_prompt)
            sp_file = fh.name
        try:
            proc = subprocess.run(
                ["claude", "-p", "--model", model, "--system-prompt-file", sp_file,
                 "--disallowed-tools", "Bash,Read,Write,Edit,Glob,Grep,WebFetch,WebSearch"],
                input=probe["prompt"], cwd="/tmp",
                capture_output=True, text=True, timeout=timeout)
        except subprocess.TimeoutExpired:
            return "__ERROR__ timeout"
        finally:
            Path(sp_file).unlink(missing_ok=True)
        if proc.returncode != 0:
            return f"__ERROR__ exit {proc.returncode}: {proc.stderr.strip()[:300]}"
        return proc.stdout.strip() or "__ERROR__ empty response"

    body = json.dumps({
        "model": model,
        "messages": [
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": probe["prompt"]},
        ],
        "stream": False,
        "think": False,
        "options": {"num_ctx": num_ctx, "temperature": 0},
    }).encode()
    req = urllib.request.Request(f"{host}/api/chat", data=body,
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            payload = json.load(r)
    except Exception as e:  # noqa: BLE001 - surfaced in the report as ERR
        return f"__ERROR__ {type(e).__name__}: {str(e)[:200]}"
    text = (payload.get("message") or {}).get("content", "").strip()
    return text or "__ERROR__ empty response"


def grade(probe: dict, text: str) -> dict:
    if text.startswith("__ERROR__"):
        return {"error": True}
    out = EVAL_DIR / ".tmp-grade.md"
    out.write_text(text)
    proc = subprocess.run(["python3", str(CHECKER), probe["scenario"], str(out)],
                          capture_output=True, text=True)
    out.unlink(missing_ok=True)
    errors = len([l for l in proc.stdout.splitlines() if l.startswith("ERROR")])

    g = {"error": False, "lint_errors": errors, "words": len(text.split()),
         "asked": bool(ASKED_FOR_BRIEF.search(text[:1200]))}
    if g["asked"]:
        return g
    if probe["bluf"]:
        # Must open with the point. Buildup is the regression signal.
        g["throat_clearing"] = bool(THROAT_CLEARING.search(sentences(text, 1)))
    else:
        # Marketing base: the hook must not lead with the product name.
        product = probe.get("product", "")
        g["product_in_hook"] = product.lower() in sentences(text, 2).lower()
    return g


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--probes", default=str(EVAL_DIR / "probes" / "bluf.jsonl"))
    ap.add_argument("--model", default="mistral-small3.2:24b")
    ap.add_argument("--host", default="http://localhost:11434",
                    help="Model server. Must be loopback unless --allow-remote.")
    ap.add_argument("--backend", choices=("ollama", "claude-cli"), default="ollama")
    ap.add_argument("--candidate-file",
                    help="Use this file as the candidate arm's core SKILL.md "
                         "instead of the working tree, to test a variant in place.")
    ap.add_argument("--num-ctx", type=int, default=32768,
                    help="Context window to pin. Left unpinned, a model can load at its "
                         "full advertised context, consume tens of GB of VRAM, and fail "
                         "every request with a compute error.")
    ap.add_argument("--allow-remote", action="store_true",
                    help="Permit a non-loopback host. Off by default: a full run is two "
                         "generations per probe, which is not traffic to send to a shared "
                         "endpoint by accident.")
    ap.add_argument("--out", default=str(EVAL_DIR / "runs"))
    ap.add_argument("--timeout", type=int, default=600)
    ap.add_argument("--report-only", action="store_true")
    args = ap.parse_args()

    if not args.report_only and args.backend == "ollama" and not args.allow_remote:
        if not re.match(r"^https?://(localhost|127\.0\.0\.1|\[::1\])(:\d+)?/?$", args.host):
            print(f"refusing to run: --host {args.host!r} is not loopback. A full run is two "
                  f"generations per probe; pass --allow-remote to send that off-box.",
                  file=sys.stderr)
            return 2

    probes = [json.loads(l) for l in Path(args.probes).read_text().splitlines() if l.strip()]
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    results = {}

    for probe in probes:
        for arm in ("baseline", "candidate"):
            path = out_dir / f"{probe['id']}.{arm}.md"
            if args.report_only:
                if not path.exists():
                    print(f"  skip {probe['id']}/{arm}: no saved output", file=sys.stderr)
                    continue
                text = path.read_text()
            else:
                print(f"  running {probe['id']}/{arm} ...", file=sys.stderr, flush=True)
                text = generate(probe, arm, args.model, args.host, args.num_ctx,
                                args.timeout, args.backend, args.candidate_file)
                path.write_text(text)
            results[(probe["id"], arm)] = grade(probe, text)

    print(f"\n{'probe':<14} {'arm':<10} {'lint':>5} {'words':>6}  signal")
    print("-" * 60)
    regressions = []
    for probe in probes:
        for arm in ("baseline", "candidate"):
            g = results.get((probe["id"], arm))
            if g is None:
                continue
            if g["error"]:
                print(f"{probe['id']:<14} {arm:<10} {'ERR':>5}")
                continue
            if g.get("asked"):
                sig = "asked for brief (not scored)"
            elif probe["bluf"]:
                sig = "buildup opener" if g["throat_clearing"] else "opens with point"
            else:
                sig = "product in hook" if g["product_in_hook"] else "hook stage-appropriate"
            print(f"{probe['id']:<14} {arm:<10} {g['lint_errors']:>5} {g['words']:>6}  {sig}")
        b, c = results.get((probe["id"], "baseline")), results.get((probe["id"], "candidate"))
        if b and c and (b.get("asked") or c.get("asked")):
            if b.get("asked") != c.get("asked"):
                regressions.append(
                    f"{probe['id']}: one arm drafted and the other asked for a brief — "
                    f"probe is underspecified, not comparable")
        elif b and c and not b["error"] and not c["error"]:
            if probe["bluf"] and c.get("throat_clearing") and not b.get("throat_clearing"):
                regressions.append(f"{probe['id']}: candidate opens with buildup, baseline did not")
            if c["lint_errors"] > b["lint_errors"]:
                regressions.append(
                    f"{probe['id']}: lint errors {b['lint_errors']} -> {c['lint_errors']}")

    print()
    if regressions:
        print("REGRESSIONS")
        for r in regressions:
            print(f"  - {r}")
    else:
        print("No mechanical regressions. Read the diffs before trusting this:")
        print(f"  for f in {out_dir}/*.baseline.md; do diff -u \"$f\" \"${{f%.baseline.md}}.candidate.md\"; done")
    return 1 if regressions else 0


if __name__ == "__main__":
    sys.exit(main())
