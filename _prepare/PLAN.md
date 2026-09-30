# The /prepare pass for the Python guide — plan

Written 2026-09-30, at the end of the java-guide pass, so that next week's sessions can start
without re-deriving anything. Not rendered: the leading `_` keeps `_prepare/` out of the book.
Work on branch **`prepare-gate`** (this branch). `main` holds only the book.

The model is the java-guide pass, which finished on 2026-09-30:
- It prepared 37 lessons.
- It wrote two new lessons for coverage gaps.
- It proved 540 fences.
- It ended with a running-app check.

Its runbook, tooling and exemplar record are copied into `_prepare/java-reference/` for reference.
The full archive is the tag `archive/prepare-gate` in the java-guide repo.

## 1. Where the book stands (measured 2026-09-30)

| | |
|---|---|
| Lessons | 35, in 6 chapters (first-steps 5, control-flow 6, working-with-data 4, how-python-works 6, object-oriented 6, advanced 8) |
| Python fences | 406: 361 `python run`, 26 `python run viz=…`, 19 plain `python` (static, no Run button) |
| Output blocks | about 290, so roughly **115 runnable fences have no Output block**: unproved claims |
| Objectives / checks / sources | **none** in any lesson |
| Already verified | `04-how-python-works/03-functions-in-depth.md`: all 79 fences run and checked (commits `54795e1`, `7ec7062`), but no objectives, checks or sources |
| Label styles | mixed: `**Output:**`, `**Output (illustrative timing)**`, `**Output** (when you type …)`, `**Output** (then an error)`. Normalise to the java-guide forms (§3 below) |
| `validate-book` | passes, with one warning: `book.json` `order: 6` is ignored for a satellite (remove it, as java-guide did in `d8c78ba`) |

## 2. Facts established for the sandbox (do not re-derive)

- The Run button compiles and runs through synapse's go-judge. **Python there is 3.13.5** (Debian 13).
  - Prove against **`python3.13`**, which is installed at `~/.local/bin/python3.13`. Do not use the default `python3`, which is 3.14.
  - The charter's "avoid syntax newer than 3.9" is a style rule for readers. The proof target is 3.13.
- The sandbox's Python stdout is UTF-8 (`sys.stdout.encoding` is `utf-8`, and UTF-8 mode is on), so non-ASCII output is safe.
  - Java needed a fix for this (synapse `6c57a62`). Python did not.
- **Only a fence whose meta has the bare `run` token is runnable** (`synapse/web/src/lib/markdown/render.ts:36-42`). A plain ```` ```python ```` fence renders as static code.
  - The local `CLAUDE.md` Part C says the opposite, and is wrong. Fix it in session 0, as java-guide's charter was fixed.
- Plain `run` fences get **empty stdin**. A fence that reads `input()` needs a `(when you type …)` label, and should stay a plain fence with a runnable twin, as java-guide does.
- Lesson URLs are `/synapse/programming-languages/python/<chapter-slug>/<lesson-slug>`, and chapter indexes are at `…/<chapter-slug>/index`.
- `graphify-out/` is ignored by git here, and by the walker since synapse `f61c853`.
- The sandbox API is `POST /api/run` with `{"language": "python", "source": …}`, through the dev server on :5373.
  - It is rate-limited: expect about 5 s per fence when run one at a time, and back off on HTTP 429.
  - `java-guide`'s running-app check used a small script over it: `sandbox_check.py`, in that session's scratchpad, not kept. Rebuild it from `prove.py`'s `parse()` if needed.

## 3. Session 0 — port the tooling (first session next week)

1. **`_tooling/prove.py` for Python.** Start from `java-reference/prove.py`:
   - Keep `parse()`, the label table, `norm()`, the two-run determinism check, stdin labels and the exit/stderr handling for exceptions.
   - Replace javac/java with `python3.13 main.py` (stdin closed, 25 s timeout).
   - A Python exception prints a **traceback**, so the stderr "first lines" rule becomes "the last line" (`ZeroDivisionError: division by zero`), or the traceback head. Decide once and write it into the runbook.
   - There is no compiler, so `**Compiler error:**` has no equivalent. A `SyntaxError` is a run failure whose traceback ends with the error. Label it `**Output** *(a SyntaxError…)*`.
   - Sentinels use `#` instead of `//`: `# requires:`, `# expects-exception:`, `# expects-nondeterministic:`, `# expects-hang:`. The charter's C4 examples use `//`, which is wrong for Python; fix them.
   - Accept the book's existing label spellings, or normalise them to the java forms in the first chapter pass. Prefer normalising.
2. **`_tooling/prepare_lint.py`.** It is mostly language-agnostic (register, objectives, sections, cites, review). Point it at `prove.py` and keep the thresholds.
3. **`_tooling/ledger.py`.** Copy it unchanged, and adjust the paths if needed.
4. **`_prepare/RUNBOOK.md`.** Adapt `java-reference/RUNBOOK.md`:
   - Python sources: the Python Language Reference 3.13, the Library Reference 3.13, PEPs and the Python Tutorial, all at docs.python.org/3.13.
   - Python proof conventions (from step 1).
   - The same chain, commit, landing and report rules.
5. **`_prepare/coverage-map.md`.** Build it against:
   - the chapters of the Python Language Reference;
   - one published objective list: the **PCAP-31-03** or **PCEP-30-02** syllabus from the Python Institute. Check which is current, and cite the page.

   Mark each row covered, partial or GAP. A GAP too big for a section becomes a Part 3 lesson, written after the loop, as Dates & Times and Localization were for Java.
6. **Baseline run.** Run `python3 _tooling/prove.py | tail -1` and record the counts here, then `ledger.py`. Expect many "no Output block" fences.
7. **Housekeeping.**
   - Remove `order` from `book.json` (on both branches).
   - Fix the local `CLAUDE.md` Part C: runnable fences, the 3.13 target, and `#` sentinels.

## 4. The chain, per lesson (as java-guide `RUNBOOK.md` §3)

Scaffold the record, then work through: audience, objectives, gaps (four lenses plus coverage-map rows), plan, and draft as surgery. The draft adds:
- a non-example per mechanism;
- a symptom / cause / fix gotcha table;
- ✅ checks, one per objective;
- 📚 sources.

After the draft: a separate fact-check pass, a review scored 1–5 on six criteria (every After ≥ 4), the gates (`prove.py` and `prepare_lint.py` clean), `ledger.py`, then one commit per lesson, pushed to `prepare-gate`.

Rules carried over:
- **Never type an Output block.** Paste it from a run, or fill it by script from the fence's own run. This matters most for output with invisible characters.
- **A mismatch is a finding.** Decide which side is wrong. There is no `--update`.
- **One chapter per session.** At the chapter's end, land its lesson files on `main` by path (runbook §7a), and report in the §9 shape.
- The user is the sole author of every commit: no AI attribution.
- No subagents unless the user approves them first.

## 5. Order of work

| Session | Work |
|---|---|
| 0 | tooling port, runbook, coverage map, baseline (§3) |
| 1 | `01-first-steps` (5 lessons; the exemplar: prepare `01-what-is-python` first, the way java-guide's pilot set the shape) |
| 2 | `02-control-flow` (6) |
| 3 | `03-working-with-data` (4) |
| 4 | `04-how-python-works` (6; functions-in-depth already has verified fences, so it needs objectives, checks and sources more than proofs) |
| 5 | `05-object-oriented` (6) |
| 6 | `06-advanced` (8; concurrency and async fences need the `expects-nondeterministic` sentinel and illustrative labels) |
| 7 | Part 3 lessons from the coverage map's GAP rows, then the running-app check (every page, every fence through `/api/run`), then archive this branch as the tag `archive/prepare-gate` and delete it |
