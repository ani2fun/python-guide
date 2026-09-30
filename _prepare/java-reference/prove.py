#!/usr/bin/env python3
"""Prove every Java fence in the book: it compiles on Java 21, runs, and prints what the page says.

The book claims output in one grammar, and this script reads that grammar rather than adding any:

  **Output:**                          stdout must equal the block, byte for byte (trailing
                                       whitespace per line and at the end ignored)
  **Output** *(a thrown exception…)*   stdout, then the FIRST stderr line (the JVM's
  **Output** *(prints `5`, then crashes)*  "Exception in thread …" line); the run must exit non-zero
  **Output** *(when you type `36`)*    the backticked values are fed as stdin lines; the terminal
                                       echo of what was typed is removed before comparing
  **Output** *(illustrative …)*        the output varies per run: compile and run only
  **Output** *(real captured …)*       output from outside the sandbox: needs a sentinel
  **Compiler error:**                  javac must REJECT the fence, and the block's lines must open
                                       javac's stderr (the block may stop early: "first of several")

Sentinels on the fence's first line (CLAUDE.md C4) exempt a fence from running:
  // requires: <dependency> — not runnable in the sandbox     → not run; compiled when it is
                                                                one `class Main` file
  // expects-exception: <why>                                 → must exit non-zero
  // expects-nondeterministic: <why>                          → compiled and run, not compared
  // expects-hang: <why>                                      → must still be running after 5 s;
                                                                what it printed by then must equal
                                                                the Output block

Compile-error proofs (CLAUDE.md J7): a commented-out illegal line carries a marker,

    // int x = 3.5;   // ✗ javac: possible lossy conversion from double to int

and this script uncomments that one line, compiles, and requires the quoted text in javac's
stderr. The claim "this does not compile" is then checked, not asserted.

Usage:
    python3 _tooling/prove.py                 # the whole book
    python3 _tooling/prove.py 01-first-steps/03-numbers-and-arithmetic.md
    python3 _tooling/prove.py --json          # machine-readable, for ledger.py

Exit 1 when any fence fails. There is deliberately no --update: a mismatch is a finding about
the book, and the Output block is fixed by hand after deciding which side is wrong.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
from dataclasses import asdict, dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TIMEOUT = 25
FURNITURE = {"readme", "claude", "agents", "license", "licence", "contributing",
             "code_of_conduct", "security", "changelog"}

FENCE_OPEN = re.compile(r"^```java\b([^\n]*)$")
OUTPUT_LABEL = re.compile(r"^\*\*(Output|Compiler error)(?::\*\*|\*\*\s*\*\((.*)\):\*)\s*$")
SENTINEL = re.compile(r"^\s*//\s*(requires|expects-exception|expects-nondeterministic|expects-hang):\s*(.*)$")
HANG_WAIT = 5
COMPILE_MARK = re.compile(r"^(\s*)//\s?(.*?)\s*//\s*✗ javac:\s*(.+?)\s*$")


def java_home() -> str:
    """JDK 21: $JAVA21_HOME, else macOS `java_home -v 21`, else a Linux /usr/lib/jvm/*21* install.
    Launcher messages differ between versions (JDK 25 changed the "main method" errors), so the
    proofs need 21 itself, not merely `--release 21`."""
    if os.environ.get("JAVA21_HOME"):
        return os.environ["JAVA21_HOME"]
    try:
        return subprocess.run(["/usr/libexec/java_home", "-v", "21"], capture_output=True,
                              text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        pass
    for home in sorted(Path("/usr/lib/jvm").glob("*21*")) if Path("/usr/lib/jvm").is_dir() else []:
        if (home / "bin" / "javac").exists():
            return str(home)
    return ""


JAVA_HOME = java_home()
JAVAC = os.path.join(JAVA_HOME, "bin", "javac") if JAVA_HOME else "javac"
JAVA = os.path.join(JAVA_HOME, "bin", "java") if JAVA_HOME else "java"


@dataclass
class Fence:
    file: str
    line: int
    meta: str
    code: str
    label: str | None = None        # None: no Output block; "" : plain **Output:**
    kind: str = "Output"            # or "Compiler error"
    expected: str | None = None
    status: str = ""
    note: str = ""
    marks: list = field(default_factory=list)


def lessons(paths: list[str]) -> list[Path]:
    if paths:
        return [Path(p).resolve() for p in paths]
    out = []
    for md in sorted(ROOT.rglob("*.md")):
        rel = md.relative_to(ROOT)
        if any(part.startswith(("_", ".")) for part in rel.parts):
            continue
        if md.stem.lower() in FURNITURE:
            continue
        out.append(md)
    return out


def parse(md: Path) -> list[Fence]:
    lines = md.read_text(encoding="utf-8").split("\n")
    fences, i = [], 0
    while i < len(lines):
        m = FENCE_OPEN.match(lines[i])
        if not m:
            i += 1
            continue
        j = i + 1
        while j < len(lines) and not lines[j].startswith("```"):
            j += 1
        fence = Fence(str(md.relative_to(ROOT)), i + 1, m.group(1).strip(), "\n".join(lines[i + 1:j]))
        # The Output block belongs to this fence when only blank lines separate them.
        k = j + 1
        while k < len(lines) and not lines[k].strip():
            k += 1
        if k < len(lines):
            lm = OUTPUT_LABEL.match(lines[k].strip())
            if lm and k + 1 < len(lines) and lines[k + 1].startswith("```"):
                end = k + 2
                while end < len(lines) and not lines[end].startswith("```"):
                    end += 1
                fence.kind = lm.group(1)
                fence.label = lm.group(2) or ""
                fence.expected = "\n".join(lines[k + 2:end])
        fences.append(fence)
        i = j + 1
    return fences


def norm(text: str) -> str:
    return "\n".join(line.rstrip() for line in text.replace("\r\n", "\n").split("\n")).strip("\n")


def sandbox_source(code: str) -> str:
    """What the Run button compiles (synapse `java_rewriter.rs`, CLAUDE.md C1): a source containing
    `class Main` passes through untouched; otherwise the first column-0 class is renamed to Main."""
    if re.search(r"\bclass\s+Main\b", code):
        return code
    return re.sub(r"^((?:(?:public|final|abstract)\s+)*class\s+)\w+", r"\1Main", code, count=1, flags=re.M)


def compile_in(tmp: str, code: str) -> subprocess.CompletedProcess:
    Path(tmp, "Main.java").write_text(sandbox_source(code), encoding="utf-8")
    return subprocess.run([JAVAC, "--release", "21", "-encoding", "UTF-8", "Main.java"], cwd=tmp,
                          capture_output=True, text=True, timeout=120)


def run_in(tmp: str, stdin: str | None) -> subprocess.CompletedProcess:
    return subprocess.run([JAVA, "-cp", ".", "Main"], cwd=tmp, capture_output=True, text=True,
                          input=stdin if stdin is not None else None,
                          stdin=None if stdin is not None else subprocess.DEVNULL, timeout=TIMEOUT)


def prove_marks(fence: Fence) -> None:
    """Uncomment each ✗-marked line in turn and require javac to reject it with the quoted text."""
    lines = fence.code.split("\n")
    for idx, line in enumerate(lines):
        m = COMPILE_MARK.match(line)
        if not m:
            continue
        indent, stmt, message = m.groups()
        trial = lines[:idx] + [indent + stmt] + lines[idx + 1:]
        with tempfile.TemporaryDirectory() as tmp:
            proc = compile_in(tmp, "\n".join(trial))
        ok = proc.returncode != 0 and message in proc.stderr
        got = next((l for l in proc.stderr.splitlines() if "error:" in l), "compiled cleanly")
        fence.marks.append({"line": fence.line + 1 + idx, "ok": ok, "expected": message,
                            "got": got.split("error:", 1)[-1].strip()})


def prove_rejected(fence: Fence, comp: subprocess.CompletedProcess) -> Fence:
    """A **Compiler error:** block: javac must fail, and print what the page shows."""
    if comp.returncode == 0:
        fence.status, fence.note = "mismatch", "the page shows a compiler error, but javac accepted it"
        return fence
    expected = norm(fence.expected or "").split("\n")
    actual = norm(comp.stderr).split("\n")
    for n, e in enumerate(expected):
        a = actual[n] if n < len(actual) else ""
        if e != a:
            fence.status, fence.note = "mismatch", f"javac line {n + 1}: page {e!r} ≠ javac {a!r}"
            return fence
    fence.status = "rejected"
    return fence


def prove_hang(fence: Fence, tmp: str) -> Fence:
    """The page says the program never ends: it must still be running after HANG_WAIT seconds."""
    try:
        proc = subprocess.run([JAVA, "-cp", ".", "Main"], cwd=tmp, capture_output=True, text=True,
                              stdin=subprocess.DEVNULL, timeout=HANG_WAIT)
    except subprocess.TimeoutExpired as hung:
        printed = hung.stdout.decode() if isinstance(hung.stdout, bytes) else (hung.stdout or "")
        shown = norm(fence.expected or "")
        # A block in parentheses, "(no output at all …)", describes silence.
        # Threads that print before hanging may print in either order: compare the lines as a set.
        same = sorted(norm(printed).split("\n")) == sorted(shown.split("\n"))
        if (not printed.strip()) if shown.startswith("(") else same:
            fence.status = "proved"
            fence.note = f"still running after {HANG_WAIT} s, as the page says"
            return fence
        fence.status, fence.note = "mismatch", f"hung as claimed, but printed {norm(printed)[:80]!r}"
        return fence
    fence.status, fence.note = "mismatch", f"the page says it hangs, but it exited {proc.returncode}"
    return fence


def prove(fence: Fence) -> Fence:
    first = next((l for l in fence.code.split("\n") if l.strip()), "")
    sm = SENTINEL.match(first)
    sentinel = sm.group(1) if sm else None
    label = (fence.label or "").lower()
    runnable = fence.meta.startswith("run")

    if sentinel == "requires":
        fence.status, fence.note = "exempt", sm.group(2)[:80]
        # A single-file program that only needs a flag or a library still compiles here: prove that.
        if re.search(r"\bclass\s+Main\b", fence.code) and not re.search(r"^(\s*package\b|\s*import org\.|public\s+(class|interface|record|enum)\s+(?!Main\b))",
                          fence.code, re.M):
            with tempfile.TemporaryDirectory() as tmp:
                comp = compile_in(tmp, fence.code)
            if comp.returncode:
                err = next((l for l in comp.stderr.splitlines() if "error:" in l), "")
                fence.status, fence.note = "compile-fail", err.split("Main.java:", 1)[-1][:140]
            else:
                fence.note = "compiles; " + fence.note
        return fence
    if not runnable and not sentinel and "when you type" not in label:
        fence.status = "unclassified"
        fence.note = "plain ```java fence: make it `java run` with an Output block, or add a sentinel"
        return fence
    if "real captured" in label and not sentinel:
        fence.status = "unclassified"
        fence.note = "output captured outside the sandbox: needs a sentinel"
        return fence

    stdin = None
    if "when you type" in label:
        typed = re.findall(r"`([^`]*)`", fence.label)
        stdin = "\n".join(typed) + "\n"

    with tempfile.TemporaryDirectory() as tmp:
        comp = compile_in(tmp, fence.code)
        if fence.kind == "Compiler error":
            return prove_rejected(fence, comp)
        if comp.returncode:
            err = next((l for l in comp.stderr.splitlines() if "error:" in l), comp.stderr.strip()[:120])
            fence.status, fence.note = "compile-fail", err.split("Main.java:", 1)[-1][:140]
            return fence
        prove_marks(fence)
        if sentinel == "expects-hang":
            return prove_hang(fence, tmp)
        runs = []
        try:
            for _ in range(2):
                runs.append(run_in(tmp, stdin))
        except subprocess.TimeoutExpired:
            fence.status, fence.note = "timeout", f"still running after {TIMEOUT} s"
            return fence

    first_run, second_run = runs
    throws = ("exception" in label or "crash" in label or "error" in label or "throws" in label
              or sentinel == "expects-exception")
    varies = "illustrative" in label or "vary" in label or sentinel == "expects-nondeterministic"
    stderr_head = next((l for l in first_run.stderr.splitlines() if l.strip()), "")
    actual = first_run.stdout
    if throws and fence.expected is not None:
        # stdout, then as many stderr lines as the page shows (a stack trace may be trimmed)
        shown = len(norm(fence.expected).split("\n")) - len(norm(first_run.stdout).split("\n")) \
            + (1 if not first_run.stdout.strip() else 0)
        actual = first_run.stdout + "\n".join(first_run.stderr.splitlines()[:max(shown, 1)]) + "\n"

    if throws and first_run.returncode == 0:
        fence.status, fence.note = "mismatch", "the page says it throws, but it exited 0"
    elif not throws and first_run.returncode != 0:
        fence.status, fence.note = "run-fail", f"exit {first_run.returncode}: {stderr_head[:120]}"
    elif not first_run.stdout.strip() and not throws:
        fence.status, fence.note = "no-output", "runs but prints nothing"
    elif varies:
        fence.status, fence.note = "illustrative", "runs; output not compared (varies per run)"
    elif first_run.stdout != second_run.stdout:
        fence.status, fence.note = "nondeterministic", "two runs printed different output, and the page does not say so"
    elif fence.expected is None:
        fence.status, fence.note = "no-output-block", "runs, but the page shows no Output block to prove"
    else:
        expected = fence.expected
        if stdin is not None:
            for value in re.findall(r"`([^`]*)`", fence.label):
                expected = expected.replace(value + "\n", "", 1)
        if norm(actual) == norm(expected):
            fence.status = "proved"
        else:
            fence.status = "mismatch"
            exp_lines, act_lines = norm(expected).split("\n"), norm(actual).split("\n")
            for n, (e, a) in enumerate(zip(exp_lines + [""] * len(act_lines), act_lines + [""] * len(exp_lines))):
                if e != a:
                    fence.note = f"line {n + 1}: page {e!r} ≠ run {a!r}"
                    break
    if fence.status in ("proved", "illustrative") and any(not m["ok"] for m in fence.marks):
        fence.status = "mark-fail"
        bad = next(m for m in fence.marks if not m["ok"])
        fence.note = f"line {bad['line']}: expected javac {bad['expected']!r}, got {bad['got']!r}"
    return fence


GOOD = {"proved", "rejected", "illustrative", "exempt"}


def main(argv: list[str]) -> int:
    as_json = "--json" in argv
    paths = [a for a in argv if not a.startswith("--")]
    if not os.path.exists(JAVAC):
        print(f"no JDK 21 javac at {JAVAC}; run _tooling/setup_jdk21.sh or set JAVA21_HOME", file=sys.stderr)
        return 2
    results = [prove(f) for md in lessons(paths) for f in parse(md)]
    if as_json:
        print(json.dumps([asdict(r) | {"code": None} for r in results], indent=1))
    else:
        by_file: dict[str, list[Fence]] = {}
        for r in results:
            by_file.setdefault(r.file, []).append(r)
        for file, fences in by_file.items():
            bad = [f for f in fences if f.status not in GOOD]
            marks = sum(len(f.marks) for f in fences)
            print(f"{'✓' if not bad else '✗'} {file}: {len(fences) - len(bad)}/{len(fences)} proved"
                  + (f", {marks} compile-error mark(s)" if marks else ""))
            for f in bad:
                print(f"    ✗ :{f.line} {f.status}: {f.note}")
        counts: dict[str, int] = {}
        for r in results:
            counts[r.status] = counts.get(r.status, 0) + 1
        print("\n" + "  ".join(f"{k} {v}" for k, v in sorted(counts.items(), key=lambda kv: -kv[1])))
    return 0 if all(r.status in GOOD for r in results) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
