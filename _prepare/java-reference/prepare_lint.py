#!/usr/bin/env python3
"""The /prepare gate for a java-guide lesson: the register, the chain, and the proofs.

Adapted from the study system (`study/tools/rewrite.py --prepare --lint` and `study/tools/state.py`
review parsing), which defines how a technical document is prepared before anyone studies it. This
copy keeps the thresholds and the review criteria, and maps the standard study sections onto this
book's own shape, because `study/books.json` reads this book's `Mental-model summary` and
`Gotcha checklist` headings.

What a script can hold of a lesson's quality:
  register    sentences ≤ 30 words, mean ≤ 20, no 5-line walls of prose, no hedges
  objectives  a `**You'll be able to:**` line, 2–5 outcomes, each a verb the reader can be seen doing
  sections    Mental-model summary · Gotcha checklist (a symptom | cause | fix table) ·
              ✅ Check yourself (a quiz or <details> per objective) · 📚 Sources
  cites       every <abbr title="…">[n]</abbr> resolves to source n; every source is cited
  unverified  `[?]` in the lesson and `### Unverified` in its session record agree
  review      the record's six criteria all score ≥ 4 after the fix
  proofs      prove.py passes on the lesson

Depth, truth and sequence are the review's, not this script's.

Usage:
    python3 _tooling/prepare_lint.py 04-core-libraries/04-equals-and-hashcode.md
    python3 _tooling/prepare_lint.py <lesson> --no-run         # skip prove.py
    python3 _tooling/prepare_lint.py <lesson> --scaffold       # write the session record skeleton
    python3 _tooling/prepare_lint.py --all --summary            # one line per lesson
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
import prove  # noqa: E402

# ── the register (rewrite.py 616–725) ────────────────────────────────────────────────────────
HEDGES = (
    ("basically", r"\bbasically\b"), ("essentially", r"\bessentially\b"), ("sort of", r"\bsort of\b"),
    ("kind of", r"\bkind of\b"), ("just", r"\bjust\b"), ("really", r"\breally\b"),
    ("actually", r"\bactually\b"), ("simply", r"\bsimply\b"), ("quite", r"\bquite\b"),
    ("rather", r"\brather\b(?! than)"), ("fairly", r"\bfairly\b"), ("in a sense", r"\bin a sense\b"),
    ("more or less", r"\bmore or less\b"), ("somewhat", r"\bsomewhat\b"),
)
LONG_SENTENCE = 30
TARGET_SENTENCE = 20
WALL = 5
LIST_ITEM = re.compile(r"^(\d+[.)]|[-*+])\s")


def prose_of(text: str) -> str:
    """The prose: fences, tables, headings, comments, HTML tags and frontmatter out."""
    text = re.sub(r"\A---.*?\n---\n", "", text, flags=re.S)
    text = re.sub(r"^```.*?^```\s*$", "", text, flags=re.M | re.S)
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    text = re.sub(r"<abbr title=\"[^\"]*\">\[\d+\]</abbr>", "", text)
    text = re.sub(r"<[^>]+>", "", text)
    # The objectives line is a list separated by `;`: each objective is its own unit.
    text = re.sub(r"^\*\*You'll be able to:\*\*(.*)$",
                  lambda m: "\n".join("- " + g.strip() for g in m.group(1).split(";")), text, flags=re.M)
    lines = [line for line in text.splitlines() if not line.lstrip().startswith(("|", "#", ">"))]
    return "\n".join(lines)


def sentences_in(prose: str) -> list[str]:
    """Sentences, with a list item always its own unit."""
    units, run = [], []
    for line in prose.splitlines() + [""]:
        stripped = line.strip()
        if not stripped or LIST_ITEM.match(stripped):
            if run:
                units.append(" ".join(run))
            run = [LIST_ITEM.sub("", stripped)] if stripped else []
        else:
            run.append(stripped)
    out = []
    for unit in units:
        out += [s.strip() for s in re.split(r"(?<=[.!?])\s+(?=[A-Z`*\"'(])", unit) if len(s.split()) > 2]
    return out


def walls(text: str) -> list[str]:
    """A paragraph the eye slides off: WALL+ consecutive prose lines with no list marker, or — as
    this book writes a paragraph on one line — WALL+ sentences in one paragraph."""
    found, run = [], []
    for line in prose_of(text).splitlines() + [""]:
        stripped = line.strip()
        if stripped and not LIST_ITEM.match(stripped):
            run.append(stripped)
        else:
            para = " ".join(run)
            if len(run) >= WALL or len(sentences_in(para)) >= WALL:
                found.append(para[:90])
            run = []
    return found


def hedges_in(text: str) -> list[str]:
    low = text.lower()
    return sorted({label for label, pattern in HEDGES if re.search(pattern, low)})


# ── the chain (rewrite.py 727–805, state.py 650–700) ─────────────────────────────────────────
WEAK_VERBS = ("understand", "know", "learn", "appreciate", "grasp", "be familiar", "be aware",
              "get a feel", "see")
OBJECTIVES = (2, 5)
REVIEW_CRITERIA = (
    ("accuracy", "Accuracy & currency — every claim true now, sourced or derived"),
    ("clarity", "Clarity for this reader — no term used before it is defined"),
    ("sequence", "Sequence — each section rests only on what came before it"),
    ("practice", "Worked example, non-example, checks with hidden solutions"),
    ("misconceptions", "Misconceptions, edge cases, troubleshooting covered"),
    ("actionability", "Actionable — the reader can DO the objectives afterwards"),
)
REVIEW_PASS = 4
# (heading pattern, what it must hold). The numbered prefix "## 5. " is optional.
SECTIONS = (
    ("Mental-model summary", "a principle → consequence table"),
    ("Gotcha checklist", "a symptom | cause | fix table"),
    ("✅ Check yourself", "one quiz fence or <details> per objective"),
    ("📚 Sources", "numbered sources, each cited in the text"),
)


def section(text: str, heading: str) -> str | None:
    m = re.search(r"^## (?:\d+\.\s+)?" + re.escape(heading) + r"[^\n]*\n(.*?)(?=^## |\Z)", text, re.M | re.S)
    return re.sub(r"<!--.*?-->", "", m.group(1), flags=re.S) if m else None


def objectives_in(text: str) -> list[str] | None:
    m = re.search(r"\*\*You'll be able to:\*\*\s*(.+)$", text, re.M)
    if not m:
        return None
    parts = [re.sub(r"^(and|then)\s+", "", p.strip(" ."), flags=re.I) for p in m.group(1).split(";")]
    return [p for p in parts if p]


def objective_problems(text: str) -> list[str]:
    goals = objectives_in(text)
    if goals is None:
        return ["no `**You'll be able to:**` line — the objectives are the lesson's contract"]
    bad = []
    if not OBJECTIVES[0] <= len(goals) <= OBJECTIVES[1]:
        bad.append(f"{len(goals)} objective(s) — {OBJECTIVES[0]} to {OBJECTIVES[1]}, separated by `;`")
    for goal in goals:
        if goal.lower().startswith(WEAK_VERBS):
            bad.append(f"objective starts with a verb nobody can check: \"{goal[:60]}\"")
    return bad


def section_problems(text: str) -> list[str]:
    bad = []
    for heading, holds in SECTIONS:
        body = section(text, heading)
        if body is None:
            bad.append(f"section `{heading}` is missing — it holds {holds}")
        elif not body.strip(" \n-"):
            bad.append(f"section `{heading}` is empty")
    gotchas = section(text, "Gotcha checklist") or ""
    header = next((l for l in gotchas.splitlines() if l.strip().startswith("|")), "").lower()
    if gotchas and not all(word in header for word in ("symptom", "cause", "fix")):
        bad.append("`Gotcha checklist` has no `| Symptom | Likely cause | Fix |` table")
    return bad


def cite_problems(text: str) -> list[str]:
    cited = {int(n) for n in re.findall(r"<abbr title=\"[^\"]*\">\[(\d+)\]</abbr>", text)}
    body = section(text, "📚 Sources") or ""
    numbered = {int(n) for n in re.findall(r"^\s*(\d+)[.)]\s", body, re.M)}
    bad = [f"cite [{n}] has no source {n} under 📚 Sources" for n in sorted(cited - numbered)]
    bad += [f"source {n} is never cited" for n in sorted(numbered - cited)]
    return bad


def check_problems(text: str) -> list[str]:
    goals = objectives_in(text) or []
    body = section(text, "✅ Check yourself") or ""
    checks = body.count("```quiz") + body.count("<details>")
    if goals and checks < len(goals):
        return [f"{checks} check(s) under ✅ Check yourself for {len(goals)} objective(s)"]
    return []


def subsection(text: str, name: str) -> str:
    m = re.search(r"^### " + re.escape(name) + r"[^\n]*\n(.*?)(?=^### |^## |\Z)", text, re.M | re.S)
    return m.group(1) if m else ""


def unverified_problems(text: str, record: str) -> list[str]:
    marks = len(re.findall(r"\[\?\]", prose_of(text)))
    listed = [l for l in re.findall(r"^- (.+)$", subsection(record, "Unverified"), re.M)
              if not l.strip().startswith("_None")]
    if marks and not listed:
        return [f"{marks} `[?]` claim(s) in the lesson, none listed under ### Unverified"]
    if listed and not marks:
        return [f"{len(listed)} unverified claim(s) listed, none marked `[?]` where it is made"]
    return []


def review_problems(record: str) -> list[str]:
    rows = {}
    for line in subsection(record, "Review").splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 4 or cells[0].lower().startswith(("criterion", "---")):
            continue
        key = cells[0].split("—")[0].split(" ")[0].strip().lower()
        m = re.match(r"([1-5])\b", cells[3])
        rows[key] = int(m.group(1)) if m else None
    bad = []
    for key, _ in REVIEW_CRITERIA:
        if key not in rows:
            bad.append(f"`{key}` has no row in ### Review")
        elif rows[key] is None:
            bad.append(f"`{key}` has no After score")
        elif rows[key] < REVIEW_PASS:
            bad.append(f"`{key}` scores {rows[key]} after the fix — {REVIEW_PASS} is the floor")
    return bad


def frontmatter_problems(text: str) -> list[str]:
    fm = re.match(r"\A---\n(.*?)\n---\n", text, re.S)
    if not fm:
        return ["no frontmatter"]
    return [f"frontmatter has no `{k}:`" for k in ("title", "summary") if not re.search(rf"^{k}:\s*\S", fm.group(1), re.M)]


# ── the session record ───────────────────────────────────────────────────────────────────────
def record_path(lesson: Path) -> Path:
    return lesson.with_name(f"_{lesson.stem}.session.md")


RECORD = """# {title} — preparation record

The /prepare chain for `{rel}`, in order. Not rendered (the leading `_`). The lesson is edited in
place; this file is the evidence behind each change.

## Research

### Audience

- *Holds already* (earlier lessons, never re-taught):
- *Must not be assumed* (defined where it first appears):

### Gaps in the chapter

Four lenses, most severe first: prerequisite, step, edge, structure. Plus this lesson's rows in
`_prepare/coverage-map.md`.

| Gap | Kind | Filled where | Source |
|---|---|---|---|
| | | | |

### Plan

| Section | Carries | Why here |
|---|---|---|
| | | |

### Unverified

- _None._

### Fact-check

A separate pass over the FINISHED draft, as a checker: every number, name, version, code line and
cite. Only what changed or was flagged is listed.

| Claim | Verdict | Fix |
|---|---|---|
| | | |

### Review

Scored 1–5 before the fix, the single highest-impact fix named, scored again after. Every `After`
must reach 4.

| Criterion | Before | Highest-impact fix | After |
|---|---|---|---|
{rows}

## What changed, and why

| Change | Why |
|---|---|
| | |
"""


def scaffold(lesson: Path) -> None:
    path = record_path(lesson)
    if path.exists():
        print(f"  {path.relative_to(ROOT)} exists — left untouched")
        return
    title = re.search(r"^title:\s*\"?(.+?)\"?\s*$", lesson.read_text(encoding="utf-8"), re.M)
    rows = "\n".join(f"| {k} — {label} | | | |" for k, label in REVIEW_CRITERIA)
    path.write_text(RECORD.format(title=title.group(1) if title else lesson.stem,
                                  rel=lesson.relative_to(ROOT), rows=rows), encoding="utf-8")
    print(f"  wrote {path.relative_to(ROOT)}")


# ── the report ───────────────────────────────────────────────────────────────────────────────
def lint(lesson: Path, run: bool = True, quiet: bool = False) -> int:
    text = lesson.read_text(encoding="utf-8")
    record = record_path(lesson).read_text(encoding="utf-8") if record_path(lesson).exists() else ""
    sents = sentences_in(prose_of(text))
    lengths = [len(s.split()) for s in sents] or [0]
    mean = sum(lengths) / len(lengths)
    long = [(n, s[:80]) for n, s in zip(lengths, sents) if n > LONG_SENTENCE]
    wall = walls(text)
    hedges = hedges_in(prose_of(text))
    checks = (
        ("frontmatter", frontmatter_problems(text)),
        ("objectives", objective_problems(text)),
        ("sections", section_problems(text)),
        ("cites", cite_problems(text)),
        ("unverified", unverified_problems(text, record)),
        ("checks", check_problems(text)),
        ("review", review_problems(record) if record else ["no session record — run with --scaffold"]),
    )
    proofs = []
    if run:
        proofs = [prove.prove(f) for f in prove.parse(lesson)]
    bad_proofs = [f for f in proofs if f.status not in prove.GOOD]
    problems = len(long) + len(wall) + len(hedges) + (mean > TARGET_SENTENCE) \
        + sum(len(b) for _, b in checks) + len(bad_proofs)
    rel = lesson.relative_to(ROOT)
    if quiet:
        print(f"{'✓' if not problems else '✗'} {rel}: {problems} problem(s) — mean {mean:.0f} words, "
              f"{len(long)} long, {len(wall)} wall(s), {len(hedges)} hedge(s), "
              + ", ".join(f"{n} {len(b)}" for n, b in checks if b)
              + (f", proofs {len(bad_proofs)}" if bad_proofs else ""))
        return problems
    print(f"\n  {rel}\n\n  register: {len(sents)} sentence(s), mean {mean:.0f} words, longest {max(lengths)}"
          + (f" — target ≤ {TARGET_SENTENCE}" if mean > TARGET_SENTENCE else ""))
    for n, s in long:
        print(f"    ✗ {n} words: {s}…")
    for s in wall:
        print(f"    ✗ a wall of prose, no list: {s}…")
    for h in hedges:
        print(f"    ✗ hedge: {h!r}")
    for name, bad in checks:
        for line in bad:
            print(f"    ✗ {name}: {line}")
        if not bad:
            print(f"    ✓ {name}")
    if run:
        for f in proofs:
            mark = "✓" if f.status in prove.GOOD else "✗"
            if mark == "✗":
                print(f"    ✗ proof :{f.line} {f.status}: {f.note}")
        print(f"    {'✓' if not bad_proofs else '✗'} proofs: {len(proofs) - len(bad_proofs)}/{len(proofs)}")
    print(f"\n  {'clean.' if not problems else f'{problems} thing(s) to fix.'}\n")
    return problems


def main(argv: list[str]) -> int:
    run = "--no-run" not in argv
    paths = [a for a in argv if not a.startswith("--")]
    lessons = prove.lessons(paths) if (paths or "--all" in argv) else []
    if not lessons:
        print(__doc__)
        return 2
    lessons = [l for l in lessons if not l.name.endswith("00-index.md")] if "--all" in argv else lessons
    if "--scaffold" in argv:
        for lesson in lessons:
            scaffold(lesson)
        return 0
    total = sum(lint(l, run, quiet="--summary" in argv) for l in lessons)
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
