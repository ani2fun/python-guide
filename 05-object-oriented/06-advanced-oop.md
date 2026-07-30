---
title: Advanced OOP
summary: Multiple inheritance is resolved by the MRO (C3 linearization), which fixes the single order Python searches for methods and the path cooperative super() walks. Mixins and abstract base classes structure designs, and dataclasses delete the __init__/__repr__/__eq__ boilerplate.
prereqs: []
---

# Advanced OOP — MRO, Mixins, ABCs & dataclasses

Single inheritance is a chain; multiple inheritance is a graph, and a graph has no obvious "search order." The thesis of this chapter: **Python imposes one deterministic order on that graph — the MRO, computed by C3 linearization — and everything about multiple inheritance follows from it.** The MRO decides which method wins, and it's the exact path `super()` walks (so `super()` calls the *next class in the MRO*, not necessarily a literal parent). On top of that foundation, three tools shape real designs: **mixins** add slices of behavior, **abstract base classes** declare required methods, and **dataclasses** erase the `__init__`/`__repr__`/`__eq__` boilerplate.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **The core idea.**

- Multiple inheritance is a graph with no obvious search order.
- The **MRO** (C3 linearization) imposes one deterministic order.
- It decides which method wins and the path `super()` walks.
- Mixins, abstract base classes, and dataclasses build on top.

</div>

We start with the MRO because the rest is built on it, then layer the design tools. Every output below was produced by running the code.

<div style="border-left:4px solid #15448e;background:rgba(21,68,142,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

📘 **How to read the Intuition boxes.** Each one is built in three moves:

1. **The mechanism** — what the interpreter is *actually doing*.
2. **A concrete bite** — a specific, runnable way the naive assumption fails.
3. **The earned rule** — the decision heuristic, now justified rather than asserted, plus its cost.

</div>

---

## Table of Contents

1. [MRO & C3 linearization](#1-mro--c3-linearization)
2. [Multiple inheritance & cooperative `super()`](#2-multiple-inheritance--cooperative-super)
3. [Mixins](#3-mixins)
4. [Abstract base classes (`abc`)](#4-abstract-base-classes-abc)
5. [`dataclasses`](#5-dataclasses)
6. [Mental-model summary](#6-mental-model-summary)
7. [Gotcha checklist](#7-gotcha-checklist)

---

## 1. MRO & C3 linearization

When a class inherits from several bases, Python needs one unambiguous order in which to look up attributes and methods. That order is the **MRO** (Method Resolution Order), computed by the **C3 linearization** algorithm. Consider the classic diamond: `A` at the top, `B` and `C` both inheriting `A`, and `D` inheriting both `B` and `C`.

```python run
class A:
    def who(self):
        return "A"

class B(A):
    pass

class C(A):
    pass

class D(B, C):
    pass

print(D.__mro__)
```

**Output:**
```
(<class '__main__.D'>, <class '__main__.B'>, <class '__main__.C'>, <class '__main__.A'>, <class 'object'>)
```

```d2
direction: up

object: object
A: A
B: B
C: C
D: D

D -> B: 1
D -> C: 2
B -> A: 3
C -> A: 4
A -> object: 5
```

**Analysis.** The MRO is `D → B → C → A → object`. The numbered edges in the diagram trace it: from `D` Python visits `B` first (it's listed first in `class D(B, C)`), then `C`, then their shared parent `A`, then the universal base `object`. The key property is that `A` appears **once**, *after both* `B` and `C` — C3 guarantees a parent never precedes any of its children, and each class appears exactly once. Method lookup for `d.who()` walks this list left to right and stops at the first class that defines `who`.

**Intuition.**
*Mechanism.* C3 linearization merges the MROs of all bases plus the local base order into a single list, subject to two constraints: children come before parents, and the left-to-right order you wrote (`B` before `C`) is preserved. The result is the tuple in `D.__mro__`. Attribute and method lookup is a linear scan of exactly this tuple — there is no re-descending into the graph.

*Concrete bite.* When the constraints can't be satisfied, the class statement itself fails — C3 refuses rather than guessing:

```python run
class A: pass
class B(A): pass
class C(A, B): pass
```
```
Traceback (most recent call last):
  File "/w/main.py", line 3, in <module>
    class C(A, B): pass
TypeError: Cannot create a consistent method resolution order (MRO) for bases A, B
```

`class C(A, B)` demands `A` before `B` (you listed it first), but `B` is a *subclass* of `A`, so the child-before-parent rule demands `B` before `A`. The two orders contradict, so Python raises at class-creation time. The fix is to list bases most-derived-first: `class C(B, A)`.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** **Read `Class.__mro__` whenever multiple inheritance surprises you — it is the single source of truth for what method runs.** The cost of multiple inheritance is exactly this: you must reason about a linearized order, not a simple parent. When a hierarchy gets confusing enough that you're printing the MRO often, that's the signal to flatten it — prefer composition or a single mixin over a deep diamond.

</div>

---

## 2. Multiple inheritance & cooperative `super()`

`super()` does **not** mean "my parent class." It means "the *next* class in the MRO, relative to where I am." With multiple inheritance, that next class can be a *sibling* you never directly inherited from. Done right, each class calls `super()` once and the whole MRO runs in order — *cooperative* inheritance.

```python run
class Base:
    def __init__(self):
        print("Base.__init__")

class Left(Base):
    def __init__(self):
        print("Left.__init__ start")
        super().__init__()
        print("Left.__init__ end")

class Right(Base):
    def __init__(self):
        print("Right.__init__ start")
        super().__init__()
        print("Right.__init__ end")

class Child(Left, Right):
    def __init__(self):
        print("Child.__init__ start")
        super().__init__()
        print("Child.__init__ end")

print([c.__name__ for c in Child.__mro__])
Child()
```

**Output:**
```
['Child', 'Left', 'Right', 'Base', 'object']
Child.__init__ start
Left.__init__ start
Right.__init__ start
Base.__init__
Right.__init__ end
Left.__init__ end
Child.__init__ end
```

**Analysis.** The MRO is `Child → Left → Right → Base → object`. Now watch `Left`'s `super().__init__()`: it calls **`Right`**, not `Base` — even though `Left` inherits from `Base`, not `Right`. That's because `super()` follows the *MRO*, and `Right` is the class after `Left` in `Child`'s MRO. Each `__init__` runs its "start," delegates via `super()`, and only prints its "end" after the rest of the chain returns — so the "end" lines unwind in reverse, like nested function calls.

**Intuition.**
*Mechanism.* `super()` is bound to *(the current class, the instance's type)*. It looks up the *instance's* MRO (`type(self).__mro__`), finds the current class in it, and dispatches to the method on the **next** class along. Because the instance is a `Child`, every `super()` in the chain uses `Child`'s MRO — so `Left`'s `super()` resolves to `Right`. This is why it's called *cooperative*: each class trusts `super()` to reach the next participant, and `Base` (which calls no `super()`) terminates the chain.

*Concrete bite.* The "next" class depends on the *instance's* MRO, so the same `Left.__init__` delegates to different classes depending on what was instantiated:

```python run
class Base:
    def __init__(self):
        print("Base.__init__")

class Left(Base):
    def __init__(self):
        print("Left -> super() goes to:", type(self).__mro__[type(self).__mro__.index(Left) + 1].__name__)
        super().__init__()

class Right(Base):
    def __init__(self):
        super().__init__()

class Child(Left, Right):
    pass

print("Instantiating Left directly:")
Left()
print("Instantiating Child:")
Child()
```
```
Instantiating Left directly:
Left -> super() goes to: Base
Base.__init__
Instantiating Child:
Left -> super() goes to: Right
Base.__init__
```

Identical `Left.__init__` code, two different targets for `super()`: `Base` when you make a `Left`, but `Right` when you make a `Child` — because `super()` reads the *instance's* MRO, and `Child`'s MRO inserts `Right` after `Left`. (The trailing `Base.__init__` in each case is the chain reaching its terminus — `Right.__init__` also calls `super()`, which lands on `Base`.) If you'd hard-coded `Base.__init__(self)` instead of `super()`, `Right.__init__` would be **skipped** when constructing a `Child`.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** **In a cooperative hierarchy, always call `super().method(...)` (never name a base class directly), and keep signatures compatible across the chain.** The cost is discipline — every participant must call `super()` and accept compatible arguments, or the chain breaks mid-way (often by silently skipping a class). The payoff is that mixins and diamonds initialize correctly in MRO order without each class needing to know its siblings.

</div>

---

## 3. Mixins

A **mixin** is a small class that contributes one slice of behavior, designed to be combined with others rather than used alone. It typically defines methods but no `__init__`, and assumes the host class provides the data it needs. Here a `JsonMixin` adds serialization to any class with instance attributes.

```python run
import json

class JsonMixin:
    def to_json(self):
        return json.dumps(self.__dict__)

class User(JsonMixin):
    def __init__(self, name, age):
        self.name = name
        self.age = age

u = User("Ada", 36)
print(u.to_json())
```

**Output:**
```
{"name": "Ada", "age": 36}
```

**Analysis.** `JsonMixin` has no data and no constructor of its own — it only adds a `to_json` method that reads `self.__dict__` (the instance's attribute dictionary). `User` supplies the data; mixing in `JsonMixin` grants it serialization. The same mixin would work on *any* class whose attributes are JSON-serializable, which is the whole point: behavior factored out for reuse, attached by inheritance.

**Intuition.**
*Mechanism.* A mixin is an ordinary class; "mixin" is a *role*, not a language feature. Listed among a class's bases, its methods join the MRO and become available on instances. Because `to_json` reads `self.__dict__` rather than hard-coded fields, it adapts to whatever the host class stores — the mixin depends on an *interface* (having instance attributes), not on a specific class.

*Concrete bite.* A mixin only works if the host actually provides what the mixin assumes — break that contract and it fails at *call* time, not definition time:

```python run
import json

class JsonMixin:
    def to_json(self):
        return json.dumps(self.__dict__)

class Box(JsonMixin):
    def __init__(self, item):
        self.item = item

print(Box({1, 2, 3}).to_json())   # a set is not JSON-serializable
```
```
Traceback (most recent call last):
  File "/w/main.py", line 11, in <module>
    print(Box({1, 2, 3}).to_json())   # a set is not JSON-serializable
          ~~~~~~~~~~~~~~~~~~~~~~^^
  File "/w/main.py", line 5, in to_json
    return json.dumps(self.__dict__)
           ~~~~~~~~~~^^^^^^^^^^^^^^^
  File "/usr/lib/python3.13/json/__init__.py", line 231, in dumps
    return _default_encoder.encode(obj)
           ~~~~~~~~~~~~~~~~~~~~~~~^^^^^
  File "/usr/lib/python3.13/json/encoder.py", line 200, in encode
    chunks = self.iterencode(o, _one_shot=True)
  File "/usr/lib/python3.13/json/encoder.py", line 261, in iterencode
    return _iterencode(o, 0)
  File "/usr/lib/python3.13/json/encoder.py", line 180, in default
    raise TypeError(f'Object of type {o.__class__.__name__} '
                    f'is not JSON serializable')
TypeError: Object of type set is not JSON serializable
```

The mixin assumed every attribute is JSON-serializable; a `set` isn't, so `json.dumps` raises — and it surfaces only when `to_json` runs, deep in the mixin (note how the traceback descends all the way into the standard library's `json` encoder). The mixin's hidden precondition ("all attributes are serializable") wasn't enforced anywhere.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** **Use mixins to factor a single, reusable behavior onto classes that satisfy the mixin's implicit contract; keep them narrow and stateless.** The cost is that the contract is *implicit* — the mixin trusts the host to provide the right attributes, and violations show up at call time, not assembly time. Keep each mixin to one job and document what it assumes, or that convenience becomes a debugging hunt.

</div>

---

## 4. Abstract base classes (`abc`)

An **abstract base class** declares methods that subclasses *must* implement, and refuses to be instantiated until they do. You build one with `ABC` as a base and `@abstractmethod` on the required methods.

```python run
from abc import ABC, abstractmethod

class Shape(ABC):
    @abstractmethod
    def area(self):
        ...

class Square(Shape):
    def __init__(self, side):
        self.side = side
    def area(self):
        return self.side ** 2

print(Square(4).area())
```

**Output:**
```
16
```

**Analysis.** `Shape` inherits `ABC` and marks `area` with `@abstractmethod` — a declaration of "every concrete `Shape` must define `area`." `Square` provides a real `area`, so it's a complete, instantiable class: `Square(4).area()` returns `16`. The ABC defines the *interface* (the contract); subclasses provide the *implementation*. The body `...` is just a placeholder — the method is meant to be overridden, never called.

**Intuition.**
*Mechanism.* `ABC` uses a metaclass (`ABCMeta`) that records which methods are still abstract. At *instantiation* time, the constructor checks: if any `@abstractmethod` remains unimplemented in the concrete class, it raises `TypeError` instead of building the object. So the enforcement is at object creation, not at `class` definition — you *can* define an incomplete subclass; you just can't instantiate it.

*Concrete bite.* Instantiating a subclass that forgot the abstract method fails with a precise message naming the class and the missing method:

```python run
from abc import ABC, abstractmethod

class Shape(ABC):
    @abstractmethod
    def area(self):
        ...

class Blob(Shape):
    pass

Blob()
```
```
Traceback (most recent call last):
  File "/w/main.py", line 11, in <module>
    Blob()
    ~~~~^^
TypeError: Can't instantiate abstract class Blob without an implementation for abstract method 'area'
```

`Blob` inherits `Shape` but never defines `area`, so `Blob()` raises `TypeError: Can't instantiate abstract class Blob without an implementation for abstract method 'area'` (the exact 3.13 wording). The same error guards the ABC itself — `Shape()` fails identically, because `Shape` has an abstract `area` too. The contract is enforced the moment someone tries to create an object.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** **Use an ABC when you want to *guarantee* subclasses implement an interface, and to fail loudly (at construction) if they don't.** The cost is ceremony and a hard dependency on inheriting your base — heavier than Python's usual duck typing, where any object with the right methods just works. Reach for ABCs at real boundaries (plugin systems, framework hooks) where an early, clear failure beats a late `AttributeError`; for informal contracts, duck typing is lighter.

</div>

---

## 5. `dataclasses`

Most classes that just *hold data* need an `__init__` that assigns fields, a `__repr__` for debugging, and an `__eq__` for comparison — the same three methods, written by hand, every time. The `@dataclass` decorator generates all of them from your field declarations.

```python run
from dataclasses import dataclass

@dataclass
class Point:
    x: int
    y: int

p = Point(1, 2)
print(p)                      # auto __repr__
print(p == Point(1, 2))       # auto __eq__
print(p == Point(3, 4))
```

**Output:**
```
Point(x=1, y=2)
True
False
```

**Analysis.** No `__init__`, `__repr__`, or `__eq__` in the source — yet `Point(1, 2)` constructs, `print(p)` gives a clean `Point(x=1, y=2)`, and `==` compares by *value* (`True` for equal coordinates). `@dataclass` reads the class-level annotations (`x: int`, `y: int`) and synthesizes those methods. The annotations are required: they're how the decorator discovers the fields and their order.

**Intuition.**
*Mechanism.* At class-definition time, `@dataclass` inspects `__annotations__`, then code-generates `__init__` (parameters in declaration order), `__repr__`, and `__eq__` (a tuple-wise comparison of the fields), injecting them into the class. By default it does **not** generate `__hash__` — because it generated `__eq__`, the same rule from [dunder methods](/synapse/programming-languages/python/object-oriented/dunder-methods) applies, and instances are unhashable unless you opt in.

*Concrete bite.* A default (mutable) dataclass is unhashable — `frozen=True` both freezes it *and* makes it hashable:

```python run
from dataclasses import dataclass

@dataclass(frozen=True)
class Point:
    x: int
    y: int

p = Point(1, 2)
print({p, Point(1, 2)})       # hashable now; equal -> collapses
print(len({p, Point(1, 2)}))
p.x = 9                        # frozen: assignment is blocked
```
```
{Point(x=1, y=2)}
1
Traceback (most recent call last):
  File "/w/main.py", line 11, in <module>
    p.x = 9                        # frozen: assignment is blocked
    ^^^
  File "<string>", line 16, in __setattr__
dataclasses.FrozenInstanceError: cannot assign to field 'x'
```

`frozen=True` makes instances immutable: now they're hashable, so `{p, Point(1, 2)}` works and the two equal points collapse to one entry (`len` is `1`). The price is immutability — `p.x = 9` raises `FrozenInstanceError`, because a frozen dataclass overrides `__setattr__` to forbid writes (an object you can hash must not change its hashed fields). A plain `@dataclass Point` would instead raise `TypeError: unhashable type: 'Point'` the moment you put it in a set.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** **Reach for `@dataclass` for plain data-holding classes — it deletes the `__init__`/`__repr__`/`__eq__` boilerplate; add `frozen=True` when you need immutability or hashability (dict keys, set members).** The cost is small: `@dataclass` is for *data*, and adds machinery you don't want on classes that are mostly behavior or need custom construction logic. For a bag of fields, though, it's strictly less code and fewer bugs than hand-written dunders.

</div>

---

## 6. Mental-model summary

| Principle | Consequence |
|-----------|-------------|
| The MRO (C3) is the single search order for methods | Read `Class.__mro__`; each class appears once, parents after children |
| Contradictory base order is rejected at class creation | `class C(A, B)` where `B(A)` → `TypeError: ... consistent MRO` |
| `super()` calls the *next class in the MRO*, not "the parent" | In a diamond, a class's `super()` can dispatch to a *sibling* |
| A mixin adds one behavior via an implicit contract | Works on any host that provides what the mixin reads; fails at call time if not |
| An ABC forbids instantiation until abstractmethods are implemented | `TypeError: Can't instantiate abstract class ...` at construction time |
| `@dataclass` generates `__init__`/`__repr__`/`__eq__` | No `__hash__` by default (unhashable); `frozen=True` adds immutability + hashing |

## 7. Gotcha checklist

<div style="border-left:4px solid #da5233;background:rgba(218,82,51,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

- **A method from the "wrong" base runs in multiple inheritance →** lookup follows the MRO, not your mental tree; print `Class.__mro__` to see the real order.
- **`TypeError: Cannot create a consistent method resolution order` →** you listed a parent before its child in the bases; reorder most-derived-first (`class C(B, A)`).
- **A base class's `__init__` is silently skipped →** someone called `Base.__init__(self)` directly instead of `super().__init__()`, breaking the cooperative chain.
- **`TypeError: Can't instantiate abstract class ...` →** the (sub)class still has an unimplemented `@abstractmethod`; implement it, or you tried to instantiate the ABC itself.
- **`TypeError: unhashable type` on a dataclass in a set/dict →** a plain `@dataclass` defines `__eq__` so it's unhashable; use `@dataclass(frozen=True)`.
- **`FrozenInstanceError: cannot assign to field` →** the dataclass is `frozen=True` (immutable); build a new instance (e.g. `dataclasses.replace(obj, x=9)`) instead of mutating.

</div>

---

<div style="border-left:4px solid #6d28d9;background:rgba(109,40,217,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

🧪 **Predict, then check.** Define a diamond: `Animal` with `speak(self)` returning `"..."`; `Dog(Animal)` and `Cat(Animal)` each overriding `speak`; and `Chimera(Dog, Cat)`. First predict `Chimera.__mro__` and what `Chimera().speak()` returns (which override wins?). Then make all four `__init__`s cooperative with `super().__init__()` and a print in each, and predict the order of prints when you construct a `Chimera`. Finally, rewrite `Animal` as `@dataclass(frozen=True)` with a `name: str` field and predict two things: whether `Animal("Rex") == Animal("Rex")` is `True`, and what happens if you then run `a = Animal("Rex"); a.name = "Max"`.

</div>

## Your Turn

Before you move on, check your understanding with the coach — explain the idea, apply it, weigh the trade-offs, then defend your reasoning.

<div class="concept-coach"></div>
