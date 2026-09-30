# The /prepare pass — runbook

Self-contained instructions for continuing the java-guide quality pass in any session, local or
cloud. `CLAUDE.md` (the charter) is gitignored, so a cloud clone does not have it. Everything a
session needs is here or in `_tooling/`. Not rendered: the leading `_` keeps this out of the book.

## 1. What the pass is

Every lesson is brought under the study system's `/prepare` gate, with the focus on **proofs**:

- **Correctness.** Every fence compiles on JDK 21 and prints exactly its `**Output:**` block, and every
  "this does not compile" claim shows javac's real output. Every claim about Java past the
  lesson cites a primary source (JLS 21, JVMS 21, JDK 21 API or tool docs, a JEP, OpenJDK), or
  is marked `[?]`.
- **Completeness.** A researched gaps table per lesson, using four lenses, plus the lesson's rows in
  `_prepare/coverage-map.md` (the Oracle 1Z0-830 objectives and JLS 21 chapters).

Decisions already taken (do not re-ask):

- Edit lessons **in place**; keep the book's shape (numbered sections, `Mental-model summary`,
  `Gotcha checklist` — `study/books.json` reads those two headings).
- Java 21 stays the target (the Synapse sandbox runs Java 21).
- The full register applies (section 5).
- **The exemplar is `01-first-steps/01-what-java-is-and-running-code.md`, with its record
  `01-first-steps/_01-what-java-is-and-running-code.session.md`.** Match its shape, density and record.

## 2. Setup (once per session)

```bash
bash _tooling/setup_jdk21.sh          # installs openjdk-21 on Linux if missing
python3 _tooling/prove.py | tail -1   # expect: no failures (about 2 min for the whole book)
python3 _tooling/ledger.py --next     # the next lesson to prepare, in book order
```

## 3. The chain, per lesson (in this order; each link recorded in the lesson's session record)

0. `python3 _tooling/prepare_lint.py <lesson.md> --scaffold` writes `_<stem>.session.md` beside the lesson.
1. **Audience.** The book is linear. *Holds already* = what earlier lessons taught (never re-taught).
   *Must not be assumed* = every term not taught earlier; define it in plain words where it first appears.
2. **Read the whole lesson** before writing, plus the lessons it links.
3. **Objectives.** Write 2–5 outcomes on a `**You'll be able to:**` line, separated by `;`, placed after the intro and before
   the "How to read" box. Each outcome is a checkable verb: *predict, name, trace, write, explain why, pick*. Never
   *understand/know/learn*. The lesson's 🧪 *Predict, then check* box is the first draft.
4. **Gaps, before any writing.** Read as a sceptical novice, with four lenses:
   - **prerequisite:** a term used before it is defined;
   - **step:** a jump in the logic;
   - **edge:** a failure case, "what if";
   - **structure:** the order, or an objective nothing answers.

   Add the lesson's `GAP`/`partial` rows from `_prepare/coverage-map.md`. List the gaps most severe first. Never invent a gap.
   Research each gap against primary sources with WebFetch. Run every candidate example on JDK 21.
5. **Plan.** A table: section → what it carries → why it sits there. Place each gap.
6. **Draft, as surgery, not replacement.** Keep every proved fence byte-identical unless it is wrong. Keep the
   intuition shape (*Mechanism → Concrete bite → Earned rule*). Add:
   - **one non-example** per major mechanism (the common wrong way, shown and named), as a runnable fence;
   - `## 7. Gotcha checklist` as a `| Symptom | Likely cause | Fix |` table inside the red callout;
   - `## ✅ Check yourself`: one check per objective — ```` ```quiz ```` fences (strict JSON, `answer`
     equals one option exactly, the correct option NOT always first) and `<details>` with the answer;
   - `## 📚 Sources`: a numbered list, each cited inline as `<abbr title="Short source name, §x">[n]</abbr>`;
   - TOC entries `8. [Check yourself](#-check-yourself)` and `9. [Sources](#-sources)`;
   - replace "Tutorial N" / "Tier N" references with links to the named lesson.

   Keep the 🧪 box and `## Your Turn` + `<div class="concept-coach"></div>` last.
7. **Fact-check**, a separate pass as a checker: check every number, name, version, error message, code line and cite.
   Mark each claim `OK`, `VERIFY` (source it now, or mark it `[?]` and list it under `### Unverified`), or `WRONG`
   (fix it). Record only what changed or was flagged. The claims that read best are the ones to check hardest.
8. **Review.** Score six criteria 1–5, fix the worst, and score again: accuracy, clarity, sequence, practice,
   misconceptions, actionability. Every `After` must be ≥ 4, each with a one-line reason.
9. **Gates.** Both must be clean:
   ```bash
   python3 _tooling/prove.py <lesson.md>
   python3 _tooling/prepare_lint.py <lesson.md>
   ```
   Fill `## What changed, and why` in the record, run `python3 _tooling/ledger.py`, then commit (section 7).

## 4. Proof conventions (what `prove.py` checks)

| Label under a fence | Proof |
|---|---|
| `**Output:**` | stdout equals the block; two runs agree |
| `**Output** *(a thrown exception…)*` / `*(prints X, then a thrown exception)*` / `*(… error …)*` | exits non-zero; the block = stdout, then the first stderr lines |
| `**Output** *(when you type \`36\`)*` | backticked values fed as stdin lines |
| `**Output** *(illustrative …)*` | runs; output varies, not compared |
| `**Compiler error:**` | javac rejects it; its stderr opens with the block's lines (paste javac's real output; the block may stop early) |

Fence rules:

- **Fence shape.** ```` ```java run ````, `public class Main`, stdin never read. A program that needs context restates it inside its own fence.
- **Sentinels** go on the first line, when the sandbox cannot run a fence:
  - `// requires: <why>` for a flag, a library, a preview API or multiple files;
  - `// expects-hang: <why>` for a deadlock or visibility demo;
  - `// expects-exception: <why>`;
  - `// expects-nondeterministic: <why>`.
- **Not a program?** Use ```` ```text ````, not ```` ```java ````.
- **Output comes from runs.** Every Output, Compiler error and terminal block, every quiz answer and every table of messages comes from a run.
  Paste it, never type it. Run terminal-only claims (`java X.class`, `jshell`, flags) in the shell, and record the run in the fact-check.
- **No `--update`.** A mismatch is a finding: decide which side is wrong.

## 5. Register (what `prepare_lint.py` checks)

- Sentences ≤ 30 words; mean ≤ 20. One idea per sentence. Split with bullets rather than long clauses.
- No paragraph of 5+ sentences (the book writes a paragraph per line; split it, or turn it into bullets).
- No hedges: *basically, essentially, just, really, actually, simply, quite, rather (except "rather than"), fairly, sort of, kind of*.
- Numbers exact. Big-O and powers with Unicode (`O(N²)`), never LaTeX. Multiplication is `*` or ×, never `·`.
- Callouts only as the inline-styled `<div>` idiom already in the lessons, with blank lines around the inner markdown.
- Intra-book links: `/synapse/programming-languages/java/<chapter-slug>/<lesson-slug>`, with the numeric prefixes
  stripped. Link only to lessons that exist.

## 6. The session record

`_<stem>.session.md`, exactly the exemplar's sections:

- `## Research`, holding `### Audience`, `### Gaps in the chapter` (Gap | Kind | Filled where | Source), `### Plan`,
  `### Unverified`, `### Fact-check` (Claim | Verdict | Fix) and `### Review` (Criterion | Before | Highest-impact fix | After);
- then `## What changed, and why`.

## 7. Commits and pushes

- **One commit per lesson.** Stage the lesson, its session record and `_prepare/revision-ledger.md` by path.
  Never `git add -A`.
- The message follows the exemplar commit (`git log --grep "What Java Is"`): a subject naming the lesson, the fact-check fixes, the gaps filled, and the new parts.
- **The user (Aniket Kakde) is the sole author.** Never add a `Co-Authored-By:` trailer, a "Generated with"
  line or any AI attribution, in commits or PR descriptions.
- Work on branch `prepare-gate`. Push after each lesson: `git push origin HEAD:prepare-gate`. If that push is
  refused, push the session's own branch and open a PR into `prepare-gate`.

### 7a. Landing a finished chapter on `main`

`main` holds **only the book**. Since 2026-09-28 it has been one squashed commit (`6fd6495`), plus
one commit per landed chapter. The pass's working material lives **only on `prepare-gate`**: the
`_<stem>.session.md` records, `_prepare/`, `_tooling/`, `_media/`, and
`.github/workflows/render-d2.yml`. That workflow is kept off `main` because it would commit
`_media/d2` back to `main`. The D2 source stays inline in the lessons as ```` ```d2 ```` fences.

- **Never merge `prepare-gate` into `main`, and never open a PR.** Merging brings the history and
  the meta files with it.
- At the chapter's end, copy the chapter's lesson files onto `main` and make one commit. Lesson
  files start with a digit; session records start with `_`, so the glob below skips them:

  ```bash
  git checkout main && git pull --ff-only
  git checkout prepare-gate -- ':(glob)<chapter-dir>/[0-9]*.md'
  git status --short                                   # only <chapter-dir>/NN-*.md may appear
  git commit -m "Prepare <Chapter title> (lessons 01–NN) to the /prepare gate"
  git ls-tree -r --name-only HEAD | grep -E '(^|/)_' && echo "STOP: meta files on main"
  git push origin main
  git checkout prepare-gate
  ```

- A lesson that changes a file outside its chapter (a link target, `README.md`) copies that file the
  same way, by explicit path. Never copy a path that starts with `_`.

## 8. Scope and stopping

- **One chapter per session.** Stop at the chapter's end and report (section 9). Do not start the next chapter.
- A `GAP` too big for a section (Date-Time API, localization) is a new lesson, written after the loop. Do not write it inside a session.
- These checks cannot run in the cloud: `validate-book` (the PR's CI runs it) and the running-app check (the
  user runs it locally, per chapter). Say so in the report; don't claim them.
- No subagents.

## 9. The report at the end of a chapter

Terse, in this shape, nothing else:

```
Chapter <n> done: <k> lessons, commits <hash…>, pushed to <branch>.
Fact-check fixes (false claims found): <one line per lesson>.
Gaps filled: <one line per lesson>.
Proofs: <prove.py summary line>. Lint: clean for <lessons>.
Not run here: validate-book (CI), running-app check.
Verify locally: http://localhost:5373/synapse/programming-languages/java/<chapter>/<lesson> (one per lesson)
Next: <ledger.py --next>.
```

## 10. Carry-over notes

_None open._ The `01-first-steps/02` note was resolved when that lesson was prepared (definite
assignment, ranges, `var` and the rest are in the lesson and its session record).

## 11. Status and archive

The pass finished on 2026-09-30: every lesson DONE (`_prepare/revision-ledger.md`), and both
Part 3 lessons written — `04-core-libraries/07-dates-and-times.md` (coverage map 1.4) and
`06-advanced/09-localization.md` (10.1). Every lesson is on `main`.

This branch is then archived: the tag **`archive/prepare-gate`** points at its last commit, and
the branch itself is deleted. The tag keeps every session record, `_prepare/`, `_tooling/` and
`_media/`. To pick the work up again:

```bash
git fetch origin tag archive/prepare-gate
git checkout -b prepare-gate archive/prepare-gate        # resume the pass on a fresh branch
git checkout archive/prepare-gate -- _tooling _prepare/RUNBOOK.md   # or copy the tooling into another branch
```

`_tooling/` needs nothing from this book beyond its layout: `prove.py` and `prepare_lint.py`
walk every `.md` lesson under the repository root (skipping `_` and `.` paths), so the same files work in another
Java book laid out the same way. The leading `_` keeps them out of the rendered book wherever
they are copied.
