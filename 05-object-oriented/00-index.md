---
title: Object-Oriented Python
summary: Tier 4 — modelling with classes and understanding Python's object system deeply. Classes and instances, class vs instance state, inheritance and super, dunder methods, properties and descriptors, and advanced OOP (MRO, ABCs, dataclasses). From "what is a class" to the data model.
prereqs: []
---

# Object-Oriented Python

A class bundles **data** (attributes) with **behaviour** (methods) and lets you stamp out many objects from one definition. Tier 4 takes you from your first `class` to the machinery that makes Python's own types work. The thesis of the tier: **objects in Python aren't a separate world — they're the [object model](/synapse/programming-languages/python/how-python-works/the-object-model) from Tier 3 with syntax for defining your own types**, and the "dunder" methods are how your objects plug into the language's built-in behaviour.

Six chapters, in order:

1. [**Classes & Objects**](/synapse/programming-languages/python/object-oriented/classes-and-objects) — `class`, `__init__`, instance attributes, methods, and `self`.
2. [**Class vs Instance; Encapsulation**](/synapse/programming-languages/python/object-oriented/class-vs-instance) — shared class state vs per-instance state, `@classmethod`/`@staticmethod`, the underscore conventions.
3. [**Inheritance & `super`**](/synapse/programming-languages/python/object-oriented/inheritance-and-super) — subclassing, overriding, `super()`, is-a vs has-a.
4. [**Dunder Methods & Operator Overloading**](/synapse/programming-languages/python/object-oriented/dunder-methods) — `__repr__`, `__eq__`/`__hash__`, `__len__`/`__getitem__`, operators.
5. [**Properties & Descriptors**](/synapse/programming-languages/python/object-oriented/properties-and-descriptors) — `@property`, validation, and the descriptor protocol.
6. [**Advanced OOP**](/synapse/programming-languages/python/object-oriented/advanced-oop) — MRO & C3, multiple inheritance, mixins, abstract base classes, `dataclasses`.

These assume Tier 3 — especially [the object model](/synapse/programming-languages/python/how-python-works/the-object-model) (names and objects), [functions in depth](/synapse/programming-languages/python/how-python-works/functions-in-depth) (decorators, which `@property`/`@classmethod` are), and [hashing](/synapse/programming-languages/python/working-with-data/dictionaries-and-sets) (which `__eq__`/`__hash__` builds on). The dunder methods here feed directly into [The Data Model](/synapse/programming-languages/python/advanced/the-data-model) in Tier 5.

<div style="border-left:4px solid #15448e;background:rgba(21,68,142,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

📘 **How to read the Intuition boxes.** Each one is built in three moves:

1. **The mechanism** — what the interpreter is *actually doing*.
2. **A concrete bite** — a specific, runnable way the naive assumption fails.
3. **The earned rule** — the decision heuristic, now justified rather than asserted, plus its cost.

</div>
