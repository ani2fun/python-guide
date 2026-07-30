---
title: How Python Works
summary: Tier 3 — the mental model that turns "weird" Python behaviour into predictable behaviour. The object model (names vs objects), the iteration protocol, functions as values, exceptions, modules, and context managers. The tier where the language stops surprising you.
prereqs: []
---

# How Python Works Underneath

Tiers 0–2 taught you to *use* Python. Tier 3 explains *why it behaves as it does* — the handful of underlying models that turn surprising behaviour into predictable behaviour. The thesis of the tier: **almost every Python "gotcha" is a consequence of one of a few mechanisms** — names bind to objects, iteration is a protocol, functions are objects, exceptions propagate up the stack — and once you hold those, you can derive the behaviour instead of memorising it.

Six chapters, in order:

1. [**The Object Model**](/synapse/programming-languages/python/how-python-works/the-object-model) — everything is an object; names are labels. `is` vs `==`, mutability, aliasing, copying, argument passing.
2. [**Iterators, Iterables & Generators**](/synapse/programming-languages/python/how-python-works/iterators-and-generators) — how `for` really works, and `yield` for lazy streams.
3. [**Functions in Depth**](/synapse/programming-languages/python/how-python-works/functions-in-depth) — functions as values: `*args`/`**kwargs`, closures, decorators, the mutable-default and late-binding traps.
4. [**Errors & Exceptions**](/synapse/programming-languages/python/how-python-works/errors-and-exceptions) — propagation, `try`/`except`/`else`/`finally`, custom exceptions, EAFP.
5. [**Modules, Packages & Imports**](/synapse/programming-languages/python/how-python-works/modules-and-packages) — organising code across files; the import-once-and-cache model.
6. [**Files & Context Managers**](/synapse/programming-languages/python/how-python-works/files-and-context-managers) — `with` and guaranteed cleanup via `__enter__`/`__exit__`.

Two of these are **deep passes** that revisit gentle Tier 0–1 topics with full rigour: [The Object Model](/synapse/programming-languages/python/how-python-works/the-object-model) deepens [Variables & Basic Types](/synapse/programming-languages/python/first-steps/variables-and-types), and [Functions in Depth](/synapse/programming-languages/python/how-python-works/functions-in-depth) deepens [Functions, the Basics](/synapse/programming-languages/python/control-flow/functions-the-basics). They reference the earlier passes rather than repeating them.

<div style="border-left:4px solid #15448e;background:rgba(21,68,142,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

📘 **How to read the Intuition boxes.** Each one is built in three moves:

1. **The mechanism** — what the interpreter is *actually doing*.
2. **A concrete bite** — a specific, runnable way the naive assumption fails.
3. **The earned rule** — the decision heuristic, now justified rather than asserted, plus its cost.

</div>
