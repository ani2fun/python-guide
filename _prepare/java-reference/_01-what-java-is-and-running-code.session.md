# What Java Is & Running Code — preparation record

The /prepare chain for `01-first-steps/01-what-java-is-and-running-code.md`, in order. Not
rendered (the leading `_`). The lesson is edited in place; this file is the evidence behind each
change. Prepared 2026-09-27 (the pilot lesson of the pass).

## Research

### Audience

- *Holds already:* nothing. This is the book's first lesson, for a reader who has never
  programmed (`01-first-steps/00-index.md`: "assumes you have never programmed before").
- *Must not be assumed* (each defined in plain words where it first appears): program,
  statement, class, method, compiler, bytecode, JVM, JDK, **terminal** (the source used it
  undefined), command, run time vs compile time, standard output, comment.
- *The one thing an expert forgets a newcomer does not know:* a Java program is a plain text
  file, and its name is not free — `javac` requires a `public class Main` to sit in `Main.java`.

### Gaps in the chapter

Four lenses, most severe first. No coverage-map rows for this lesson.

| Gap | Kind | Filled where | Source |
|---|---|---|---|
| The lesson's key claim — the two stages fail differently — is shown only for compile errors. A run-time failure that prints the lines before it never appears, so the reader cannot see the contrast the closing box asks them to explain | step | §1, a non-example beside the missing-`;` error: `before` prints, then `/ by zero` | derived; proved by `prove.py` (JDK 21, 2026-09-27) |
| The file name must match the `public` class: `public class Hello` in `Main.java` is rejected. A beginner's first rename hits it, and the Run button hides it (the sandbox renames the class) | prerequisite | §2, a terminal session with javac's message | JLS §7.6 [2]; javac 21 output, run 2026-09-27 |
| Each wrong `main` gives a *different* launch message ("not found", "is not static", "must return … void"); the source said all give "not found" | edge | §3 table, 🪤 troubleshooting table | run on JDK 21 2026-09-27; JLS §12.1.4 [1] |
| `String... args` and any parameter name are also valid entry points; "matched literally" overstated it | edge | §3 | JLS §12.1.4 [1] |
| `java Main.class` fails — the rule "name the class, not the file" was stated, never shown | edge | §2 | `java` man page [5]; run 2026-09-27 |
| Comments do not nest: `/* … /* … */ … */` ends at the first `*/` and breaks the build | edge | §5, a compiler-error fence | JLS §3.7 [3]; javac 21 output via `prove.py` |
| `//` inside a string literal is text, not a comment | edge | ✅ check 5 | JLS §3.7 [3] |
| "Terminal" used with no definition | prerequisite | §2, first use | — |
| No objectives, no checks with hidden answers, the gotchas were bullets not a symptom → cause → fix table, no sources | structure | objectives line, ✅, 🪤 table, 📚 | `/prepare` chain |
| Forward references by number ("Tutorial 11", "Tier 2") break when lessons are added | structure | §3, replaced by links | — |

### Plan

| Section | Carries | Why here |
|---|---|---|
| Intro + objectives | compile-then-run in five short statements; the five objectives | the reader's first contact: plain explanation, no questions yet |
| §1 A first program | the smallest program; missing `;` (compile-time: nothing prints); **non-example** `10 / 0` (run-time: earlier lines print) | the contrast needs a program the reader has just seen, and it is the chapter's central idea |
| §2 Compile, then run | `javac`/`java`, terminal defined, class name not file name (`java Main.class` fails), file name = public class, source-file mode, jshell | commands come after the reader has seen both stages fail |
| §3 `main` | each word; valid variants; a table of the three launch messages | needs "class" and "method" from §1 and "run time" from §2 |
| §4 `println` | unchanged — already proved and short | — |
| §5 Comments | the two forms; commenting out; **non-example** nested comments | the last new syntax |
| 6 Mental-model summary | as before, updated rows | the study profile reads this heading |
| 7 Gotcha checklist | a symptom → likely cause → fix table | the study profile reads this heading |
| ✅ Check yourself | one check per objective: four quizzes and one `<details>` | after all mechanisms |
| 📚 Sources | eight primary sources | last |

### Unverified

- _None._

### Fact-check

A separate pass over the FINISHED draft, as a checker: every number, name, version, code line and
cite. Only what changed or was flagged is listed.

| Claim | Verdict | Fix |
|---|---|---|
| "`java Main.java` … essentially what the Run buttons here do for you" | WRONG — the sandbox runs `javac Main.java`, then `java -cp . Main` (CLAUDE.md C1, verified against `synapse-rs`) | says the Run buttons do the same two steps; source-file mode described on its own, cited [5] [6] |
| "This book targets JDK 21, the current long-term-support release" | WRONG since 16 Sep 2025 — JDK 25 is the newer LTS [8] | "JDK 21 is a long-term-support release [9] … JDK 25 is the newer one [8]" |
| "a typo in the signature (… a missing `static` …) gives … main method not found" | WRONG — JDK 21 says `Main method is not static in class Main`; a non-`void` return gives a third message (run 2026-09-27) | a table of the four declarations and their four messages; one troubleshooting row per message |
| "The entry point must be exactly … the JVM matches it literally" | WRONG in part — `String... args` and any parameter name are valid [1] (run: `main(String... words)` printed) | names the two free choices |
| "the line after the last printed one is the culprit" (draft's own troubleshooting row) | WRONG — the failing line need not print, or be next | points at the `at Main.main(Main.java:N)` line |
| "JDK 21 is a long-term-support release" (draft) | VERIFY — was uncited | cited [9] |
| `java Ghost`, `java Main.class`, `public class Hello` in `Main.java`, the jshell session, the four `main` declarations | OK — each run on Temurin 21.0.12 on 2026-09-27; outputs pasted, not typed | none |
| Every `Output:` and `Compiler error:` block (10 fences) | OK — `prove.py`: 10/10 | none |
| "javac requires a public class to sit in a file of the same name" | OK — JLS §7.6 lets a file-based host enforce it [2]; javac does | none |
| "The Run buttons hide this rule: they rename the first class to `Main`" | OK — `java_rewriter.rs` behaviour in CLAUDE.md C1; `prove.py` now applies the same rename | none |
| Quiz answers 1, 3 and 4, and the `<details>` answer | OK — 1 from the missing-`;` proof, 3 from the JDK 21 run, 4 and the string-literal answer from a run on 2026-09-27 (`xy` / `z` / `// not a comment`) | none |

### Review

Scored 1–5 before the fix, the single highest-impact fix named, scored again after. Every `After`
must reach 4.

| Criterion | Before | Highest-impact fix | After |
|---|---|---|---|
| accuracy — Accuracy & currency — every claim true now, sourced or derived | 3 — four claims false or overstated (Run button = source mode; "current LTS"; missing `static` → "not found"; "matched literally"); no sources | fix the four, cite nine primary sources, prove every block | 5 |
| clarity — Clarity for this reader — no term used before it is defined | 4 — terms defined at first use, except *terminal*; three paragraphs of 6–8 sentences | define *terminal*; split every paragraph of 5+ sentences; mean sentence 13 words, longest 29 | 5 |
| sequence — Sequence — each section rests only on what came before it | 4 — sound order; forward references by tutorial number ("Tutorial 11", "Tier 2") | links to the named lessons | 4 — the §1 non-example uses `10 / 0` before arithmetic is taught; the division is intuitive, and the lesson needs a run-time failure that early |
| practice — Worked example, non-example, checks with hidden solutions | 3 — worked examples and a bite per section; no run-time non-example; the Predict box has no hidden answer | the `10 / 0` non-example, the nested-comment non-example, four quizzes and a `<details>` | 5 |
| misconceptions — Misconceptions, edge cases, troubleshooting covered | 3 — a bullet checklist with one wrong row; no file-name rule, no nesting rule | an 11-row symptom → cause → fix table; the file-name and nesting edges | 5 |
| actionability — Actionable — the reader can DO the objectives afterwards | 4 — the reader can run code; the objectives were implicit | five objectives with one check each | 4 — the terminal objective is practised only on a quiz; the sandbox has no terminal |

## What changed, and why

| Change | Why |
|---|---|
| Objectives line; ✅ Check yourself (4 quizzes, 1 `<details>`); 📚 Sources (9) | the /prepare contract: a check per objective, a source per claim past the chapter |
| §1: the `10 / 0` run-time non-example | the lesson's central idea (the stages fail differently) had only one side shown |
| §2: *terminal* defined; `java Main.class` failure; the file-name rule; the Run button's real steps | gaps 2, 5, 8; fact-check row 1 |
| §3: the four launch messages; `String...` and free parameter names; JDK 25 note corrected | gaps 3, 4; fact-check rows 2–4 |
| §5: nested block comments, as a compiler-error proof | gap 6 |
| Gotcha checklist → 11-row troubleshooting table | the /prepare shape; one row per real message |
| Register: long paragraphs split, two hedges removed | lint: 31 problems → 0 |
| Baseline commit 7d397ce (earlier): two unlabelled output blocks labelled | `prove.py` could not prove them |
