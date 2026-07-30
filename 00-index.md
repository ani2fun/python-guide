---
title: Python
summary: A single progressive Python text, absolute beginner to advanced. Thirty-five tutorials in strict read order, each deriving the language's behaviour from one generative idea rather than listing features. Built on verified, runnable code and a three-move "Intuition" standard that turns rules into things you can re-derive.
prereqs: []
---

# Python

Most Python tutorials hand you a pile of features and ask you to remember them. This one does the opposite: it finds the **one generative idea** under each topic and shows every rule as a *consequence* of it. You should finish each chapter able to re-derive the rules, not just recite them — and able to predict what a snippet prints before you run it.

The book is a single text, read top to bottom. It starts assuming **you have never written a line of code in any language** and ends on typing, concurrency, and the data model. Early chapters introduce every term before using it; later chapters assume the earlier ones are done and move at a fluent reader's pace. What never changes is the standard of explanation: every claim is backed by code that was actually run, and every rule comes with its cost.

## Reading conventions

- **Every code block with a Run button is real.** Cortex executes it in a sandboxed **Python 3.13** runner — the same one that produced every `Output:` block in this book. Click ▶ Run, edit the code, run it again. The output you see is the output we verified.
- **Blocks without a Run button are deliberate** — short fragments, or snippets shown precisely because they *break*. Their output is still shown and still real.
- **Every chapter is built on a thesis** stated in its first paragraph, and a fixed rhythm: concept → code → verified output → analysis ("what happened") → an **Intuition** box ("why it must be so").

<div style="border-left:4px solid #15448e;background:rgba(21,68,142,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

📘 **How to read the Intuition boxes.** Each one is built in three moves:

1. **The mechanism** — what the interpreter is *actually doing*.
2. **A concrete bite** — a specific, runnable way the naive assumption fails.
3. **The earned rule** — the decision heuristic, now justified rather than asserted, plus its cost.

</div>

This note repeats, word for word, at the top of every chapter, so a returning reader can skip it.

---

## The six tiers

The book climbs six tiers. Earlier tiers are prerequisites for later ones; topics that matter most return later at greater depth (the **spiral** — e.g. variables get a gentle pass in Tier 0 and a rigorous "object model" pass in Tier 3, which references back rather than re-teaching).

```mermaid
---
config:
  theme: base
  themeVariables:
    primaryColor: "#dbeafe"
    primaryBorderColor: "#3b82f6"
    primaryTextColor: "#1e3a5f"
    lineColor: "#64748b"
---
flowchart TD
  T0["Tier 0 — First Steps<br/>values · numbers · text · input/output"]
  T1["Tier 1 — Control Flow<br/>booleans · if · loops · lists · functions"]
  T2["Tier 2 — Working with Data<br/>sequences · dicts &amp; sets · comprehensions"]
  T3["Tier 3 — How Python Works<br/>object model · iterators · errors · modules"]
  T4["Tier 4 — Object-Oriented Python<br/>classes · inheritance · dunders"]
  T5["Tier 5 — Advanced &amp; Idiomatic<br/>typing · stdlib · concurrency · performance"]
  T0 --> T1 --> T2 --> T3 --> T4 --> T5
  T1 -. "deep pass" .-> T3
  T1 -. "deep pass" .-> T2
  style T0 fill:#fef9c3,stroke:#eab308
```

---

## Curriculum map

**Tier 0 — First Steps** *(zero programming background)* — you run your first program and work with values, numbers, text, and I/O.

1. [What Python Is & Running Code](/synapse/programming-languages/python/first-steps/what-is-python)
2. [Variables & Basic Types](/synapse/programming-languages/python/first-steps/variables-and-types)
3. [Numbers & Arithmetic](/synapse/programming-languages/python/first-steps/numbers-and-arithmetic)
4. [Strings, the Basics](/synapse/programming-languages/python/first-steps/strings-the-basics)
5. [Input & Output](/synapse/programming-languages/python/first-steps/input-and-output)

**Tier 1 — Control Flow** *(beginner)* — make decisions and repeat work; first real programs.

6. [Booleans, Comparisons & Logic](/synapse/programming-languages/python/control-flow/booleans-and-logic)
7. [Conditionals](/synapse/programming-languages/python/control-flow/conditionals)
8. [Loops](/synapse/programming-languages/python/control-flow/loops)
9. [Loop Control & Patterns](/synapse/programming-languages/python/control-flow/loop-control-and-patterns)
10. [Lists, the Basics](/synapse/programming-languages/python/control-flow/lists-the-basics)
11. [Functions, the Basics](/synapse/programming-languages/python/control-flow/functions-the-basics)

**Tier 2 — Working with Data** *(early intermediate)* — the core data structures and the comprehensions that operate on them.

12. [Sequences & the Sequence Protocol](/synapse/programming-languages/python/working-with-data/sequences)
13. [Dictionaries & Sets](/synapse/programming-languages/python/working-with-data/dictionaries-and-sets)
14. [Comprehensions](/synapse/programming-languages/python/working-with-data/comprehensions)
15. [Strings in Depth](/synapse/programming-languages/python/working-with-data/strings-in-depth)

**Tier 3 — How Python Works Underneath** *(intermediate)* — the mental model that turns "weird" behaviour into predictable behaviour.

16. [The Object Model](/synapse/programming-languages/python/how-python-works/the-object-model)
17. [Iterators, Iterables & Generators](/synapse/programming-languages/python/how-python-works/iterators-and-generators)
18. [Functions in Depth](/synapse/programming-languages/python/how-python-works/functions-in-depth)
19. [Errors & Exceptions](/synapse/programming-languages/python/how-python-works/errors-and-exceptions)
20. [Modules, Packages & Imports](/synapse/programming-languages/python/how-python-works/modules-and-packages)
21. [Files & Context Managers](/synapse/programming-languages/python/how-python-works/files-and-context-managers)

**Tier 4 — Object-Oriented Python** *(intermediate → advanced)* — model with classes; understand the object system deeply.

22. [Classes & Objects](/synapse/programming-languages/python/object-oriented/classes-and-objects)
23. [Class vs Instance; Encapsulation](/synapse/programming-languages/python/object-oriented/class-vs-instance)
24. [Inheritance & `super`](/synapse/programming-languages/python/object-oriented/inheritance-and-super)
25. [Dunder Methods & Operator Overloading](/synapse/programming-languages/python/object-oriented/dunder-methods)
26. [Properties & Descriptors](/synapse/programming-languages/python/object-oriented/properties-and-descriptors)
27. [Advanced OOP](/synapse/programming-languages/python/object-oriented/advanced-oop)

**Tier 5 — Advanced & Idiomatic** *(advanced)* — typing, the standard library, the data model as a whole, concurrency, performance, shipping.

28. [Type Hints & Static Typing](/synapse/programming-languages/python/advanced/type-hints)
29. [Standard-Library Tour](/synapse/programming-languages/python/advanced/standard-library-tour)
30. [The Data Model](/synapse/programming-languages/python/advanced/the-data-model)
31. [Concurrency — Threads, Processes & the GIL](/synapse/programming-languages/python/advanced/concurrency-and-the-gil)
32. [Async Python](/synapse/programming-languages/python/advanced/async-python)
33. [Async in Practice](/synapse/programming-languages/python/advanced/async-in-practice)
34. [Performance, Profiling & Memory](/synapse/programming-languages/python/advanced/performance-and-profiling)
35. [Testing, Debugging & Packaging](/synapse/programming-languages/python/advanced/testing-and-packaging)

---

## Three reading paths

**Path A — Your first programming language ever.** Start at Tutorial 1 and walk straight through. Do not skip; each chapter assumes the one before it. Type every example, then change it and predict the new output before running. Tiers 0–1 are the whole game at first — values, decisions, loops, and functions. Everything after is built on those.

**Path B — You program in another language, new to Python.** Skim Tier 0 for the syntax and the surprises (integer vs true division, `input()` returning a string, immutable strings), then slow down at **Tier 3 — How Python Works**. The object model (names vs objects), iterators, and the function model are where Python differs most from C-family and Java mental models, and where transferred assumptions cause the subtlest bugs.

**Path C — You know Python, filling gaps.** Use the tier map to find your boundary and read forward. The highest-leverage deep passes are the object model (16), iterators & generators (17), functions in depth (18), the data model as a whole (30), and concurrency (31–33).

---

## A note on the runner

Every runnable block executes in an isolated **Python 3.13** sandbox — no setup, no install, nothing to break. Each block runs on its own (state does not carry from one block to the next), so self-contained examples repeat any setup they need. Anonymous runs work; signing in lets you edit-and-run and raises your hourly quota. You do **not** need Python installed locally to read this book — though by Tier 5 you'll want it, and Tutorial 35 shows how to set it up properly.
