---
title: Working with Data
summary: Tier 2 — the core data structures and the comprehensions that operate on them. A deep pass on sequences (list/tuple/str as one protocol), dictionaries and sets and the hashing that powers them, comprehensions, and strings in depth. Where you stop writing loops for everything.
prereqs: []
---

# Working with Data

Tier 1 gave you lists and loops. Tier 2 turns those into fluency with **data structures** — the containers that make programs fast and expressive — and the **comprehensions** that build them in a single line. The thesis of the tier: most everyday Python is choosing the right container and transforming it, and the right choice is dictated by the operation you do most (lookup, ordering, uniqueness).

Four chapters, in order:

1. [**Sequences & the Sequence Protocol**](/synapse/programming-languages/python/working-with-data/sequences) — list, tuple, and string as three implementations of *one* abstraction; the deep pass on indexing, slicing, and complexity.
2. [**Dictionaries & Sets**](/synapse/programming-languages/python/working-with-data/dictionaries-and-sets) — key→value maps and unique collections, both powered by hashing and O(1) lookup.
3. [**Comprehensions**](/synapse/programming-languages/python/working-with-data/comprehensions) — building lists, dicts, and sets (and lazy generators) in one readable expression.
4. [**Strings in Depth**](/synapse/programming-languages/python/working-with-data/strings-in-depth) — the format mini-language, text algorithms, and why naïve string-building is quadratic.

These chapters assume Tier 1: you should be comfortable with [lists](/synapse/programming-languages/python/control-flow/lists-the-basics), [loops](/synapse/programming-languages/python/control-flow/loops), and [booleans](/synapse/programming-languages/python/control-flow/booleans-and-logic). Several are *deep passes* that revisit a gentle Tier-0/1 topic with full rigour, referencing the earlier chapter rather than repeating it.

<div style="border-left:4px solid #15448e;background:rgba(21,68,142,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

📘 **How to read the Intuition boxes.** Each one is built in three moves:

1. **The mechanism** — what the interpreter is *actually doing*.
2. **A concrete bite** — a specific, runnable way the naive assumption fails.
3. **The earned rule** — the decision heuristic, now justified rather than asserted, plus its cost.

</div>
