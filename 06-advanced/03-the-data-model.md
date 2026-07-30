---
title: The Data Model
summary: Every piece of Python syntax — len(x), x + y, x[i], for, with, x() — dispatches to a dunder method, so the whole language is one consistent protocol system. Implement the right dunders and your objects behave like built-ins; this synthesizes iteration, context managers, and operator overloading into one idea.
prereqs: []
---

# The Data Model — One Protocol Idea Behind Everything

You've met dunder methods piecemeal: `__iter__` for [iteration](/synapse/programming-languages/python/how-python-works/iterators-and-generators), `__enter__`/`__exit__` for [context managers](/synapse/programming-languages/python/how-python-works/files-and-context-managers), `__eq__`/`__add__`/`__len__` for [operator overloading](/synapse/programming-languages/python/object-oriented/dunder-methods). This chapter unifies them. The thesis: **Python's "data model" is one consistent design — virtually every built-in operation and bit of syntax (`len(x)`, `x + y`, `x[i]`, `for`, `with`, `x()`, `if x`) is defined to call a corresponding dunder method** — so making your objects first-class is just implementing the protocols you need, and the language treats your type exactly like its own.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **The core idea.**

- The data model is **one consistent design**.
- Nearly all syntax (`len(x)`, `x + y`, `x[i]`, `for`, `with`) calls a **dunder** method.
- Making your objects first-class is just implementing the protocols you need.
- The language then treats your type exactly like its own.

</div>

This synthesizes Tiers 3–4. Every output below was produced by running the code.

<div style="border-left:4px solid #15448e;background:rgba(21,68,142,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

📘 **How to read the Intuition boxes.** Each one is built in three moves:

1. **The mechanism** — what the interpreter is *actually doing*.
2. **A concrete bite** — a specific, runnable way the naive assumption fails.
3. **The earned rule** — the decision heuristic, now justified rather than asserted, plus its cost.

</div>

---

## Table of Contents

1. [Dunders are protocols](#1-dunders-are-protocols)
2. [Operator overloading](#2-operator-overloading)
3. [Callable instances](#3-callable-instances)
4. [Built-ins dispatch to dunders](#4-built-ins-dispatch-to-dunders)
5. [One object, many protocols](#5-one-object-many-protocols)
6. [Mental-model summary](#6-mental-model-summary)
7. [Gotcha checklist](#7-gotcha-checklist)

---

## 1. Dunders are protocols

A "protocol" is a set of dunder methods that unlocks a piece of syntax. Implement `__len__` and `__getitem__`, and your object supports `len()`, indexing, **and** iteration and membership — for free.

```python run
class Deck:
    def __init__(self, cards):
        self._cards = list(cards)
    def __len__(self):
        return len(self._cards)
    def __getitem__(self, i):
        return self._cards[i]

d = Deck(["A", "K", "Q"])
print(len(d))           # __len__
print(d[0])             # __getitem__
print("K" in d)         # membership via __getitem__
print(list(d))          # iteration via __getitem__
```

**Output:**
```
3
A
True
['A', 'K', 'Q']
```

**Analysis.** We wrote only `__len__` and `__getitem__`, yet got four behaviours: `len()` (→ `3`), indexing (`d[0]` → `A`), membership (`"K" in d` → `True`), and iteration (`list(d)` → `['A', 'K', 'Q']`). Python *derives* iteration and membership from `__getitem__` (calling it with integer indices `0, 1, 2, …` until `IndexError`) when no `__iter__` exists. Two methods, four protocols — that's the leverage of the data model.

**Intuition.**
*Mechanism.* Built-in operations are defined in terms of dunders: `len(x)` calls `x.__len__()`, `x[i]` calls `x.__getitem__(i)`, and `for`/`in` fall back to repeatedly calling `__getitem__(0)`, `__getitem__(1)`, … until `IndexError` if there's no `__iter__`. Your class plugs into all of them by implementing the underlying methods.

*Concrete bite.* Without the protocol method, the built-in simply fails — there's nothing to call:

```python run
class Bare:
    pass
print(len(Bare()))   # no __len__
```
```
Traceback (most recent call last):
  File "/w/main.py", line 3, in <module>
    print(len(Bare()))   # no __len__
          ~~~^^^^^^^^
TypeError: object of type 'Bare' has no len()
```

`len()` is *defined* as "call `__len__`"; with no such method, Python raises `TypeError: object of type 'Bare' has no len()`. The built-in isn't magic — it's a dunder call.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** To make your object support a built-in operation, implement its dunder; check the data-model docs for which method a piece of syntax calls. The cost is that the mapping must be exact — `len()` needs `__len__` specifically (not `length` or `size`) — but the payoff is objects that work seamlessly with all of Python's syntax and built-ins.

</div>

---

## 2. Operator overloading

Operators are dunders too: `+` is `__add__`, `==` is `__eq__`, `<` is `__lt__`. Implement them and your objects work with the arithmetic and comparison syntax.

```python run
class Vec:
    def __init__(self, x, y): self.x, self.y = x, y
    def __repr__(self): return f"Vec({self.x}, {self.y})"
    def __add__(self, o): return Vec(self.x + o.x, self.y + o.y)
    def __eq__(self, o): return (self.x, self.y) == (o.x, o.y)

print(Vec(1, 2) + Vec(3, 4))
print(Vec(1, 2) == Vec(1, 2))
```

**Output:**
```
Vec(4, 6)
True
```

**Analysis.** `Vec(1,2) + Vec(3,4)` called `__add__`, returning a new `Vec(4, 6)`; `__repr__` made it print readably. `==` called `__eq__`, comparing the coordinate tuples. The `+` and `==` syntax now mean exactly what we defined for `Vec` — Python dispatched the operators to our methods.

**Intuition.**
*Mechanism.* `a + b` evaluates `type(a).__add__(a, b)`. The method decides what `+` means for that type and what it returns. If `__add__` can't handle the other operand, it should return the special value `NotImplemented` so Python can try the reflected `__radd__` — but a method that just assumes the operand's shape will crash instead.

*Concrete bite.* Our `__add__` blindly reads `o.x`, so adding a plain number explodes:

```python run
class Vec:
    def __init__(self, x, y): self.x, self.y = x, y
    def __add__(self, o): return Vec(self.x + o.x, self.y + o.y)

Vec(1, 2) + 5   # 5 has no .x
```
```
Traceback (most recent call last):
  File "/w/main.py", line 5, in <module>
    Vec(1, 2) + 5   # 5 has no .x
    ~~~~~~~~~~^~~
  File "/w/main.py", line 3, in __add__
    def __add__(self, o): return Vec(self.x + o.x, self.y + o.y)
                                              ^^^
AttributeError: 'int' object has no attribute 'x'
```

`Vec(1,2) + 5` calls `__add__` with `o = 5`; `5.x` doesn't exist, so `AttributeError`. A robust `__add__` checks `isinstance(o, Vec)` and returns `NotImplemented` otherwise, letting Python raise a clean `TypeError` (or try `__radd__`) instead of leaking this internal error.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Overload operators when your type has a genuine arithmetic/comparison meaning (vectors, money, dates) — it makes call sites read naturally. The cost is handling foreign operands: guard with `isinstance` and return `NotImplemented` for types you don't support, so Python's operator machinery can do the right thing rather than crashing inside your method.

</div>

---

## 3. Callable instances

`__call__` makes an *instance* callable like a function — `obj(args)` runs `obj.__call__(args)`. This blurs the line between objects and functions, useful for configurable function-like objects.

```python run
class Multiplier:
    def __init__(self, factor): self.factor = factor
    def __call__(self, x): return x * self.factor

triple = Multiplier(3)
print(triple(10))       # the instance is callable
print(callable(triple))
```

**Output:**
```
30
True
```

**Analysis.** `triple` is an *object*, but `triple(10)` works because `__call__` is defined — it runs `triple.__call__(10)`, returning `10 * 3`. `callable(triple)` is `True`. This is how you build objects that carry state but are invoked like functions (a parametrised callback, a stateful counter, a decorator class).

**Intuition.**
*Mechanism.* The `()` call syntax is itself a dunder: `obj(args)` is `type(obj).__call__(obj, args)`. Functions are simply objects whose type defines `__call__`; defining it on your class makes your instances callable by the same rule. "Callable" isn't a special category — it's "has `__call__`."

*Concrete bite.* The flip side: calling something whose type has **no** `__call__` is the familiar error:

```python run
x = 42
print(x())   # an int is not callable
```
```
Traceback (most recent call last):
  File "/w/main.py", line 2, in <module>
    print(x())   # an int is not callable
          ~^^
TypeError: 'int' object is not callable
```

`42()` fails with `TypeError: 'int' object is not callable` — `int` defines no `__call__`. (This is also the error behind the classic bug of shadowing a function name with a value, then trying to call it.)

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Use `__call__` when an object is conceptually "a function with state or configuration" — it reads more naturally than naming a `.run()` method. The cost/boundary: a callable object can be confusing if overused (readers expect `obj()` to be cheap and function-like), so reserve it for genuinely function-like roles.

</div>

---

## 4. Built-ins dispatch to dunders

The lesson generalises: built-in functions and even truth-testing call dunders. `len()` → `__len__`, `bool()`/`if` → `__bool__` (falling back to `__len__`), `str()` → `__str__`, `repr()` → `__repr__`.

```python run
class Loud:
    def __len__(self):
        print("len called")
        return 5
    def __bool__(self):
        print("bool called")
        return True

x = Loud()
print(len(x))
if x:
    print("truthy")
```

**Output:**
```
len called
5
bool called
truthy
```

**Analysis.** `len(x)` printed `len called` then `5` — it really did call `__len__`. The `if x:` printed `bool called` then `truthy` — truth-testing called `__bool__`. The print statements inside the dunders prove the dispatch: built-in operations are thin wrappers that call your methods.

**Intuition.**
*Mechanism.* Truth-testing (`if x`, `while x`, `bool(x)`) calls `__bool__`; if a class has no `__bool__`, Python falls back to `__len__` (zero length → falsy), and if neither exists, the object is always truthy. So "truthiness" ([Tutorial 6](/synapse/programming-languages/python/control-flow/booleans-and-logic)) is itself a protocol.

*Concrete bite.* That fallback means a container with `__len__` returning `0` is **falsy**, even with no `__bool__`:

```python run
class Empty:
    def __len__(self):
        return 0

e = Empty()
if e:
    print("truthy")
else:
    print("falsy - __len__ returned 0")
```
```
falsy - __len__ returned 0
```

`Empty()` has no `__bool__`, so `if e` falls back to `__len__`, which returns `0` → falsy. This is exactly why empty lists, strings, and dicts are falsy: their `__len__` is `0`. Your types inherit the same rule the moment you define `__len__`.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Define `__bool__` (or rely on `__len__`) to control how your object behaves in conditions — and remember an empty container should be falsy. The cost/boundary: if `__len__` can be `0` for an object you want *always* truthy, define an explicit `__bool__` returning `True`, or `if x:` will surprise you when it's "empty."

</div>

---

## 5. One object, many protocols

Because protocols are independent sets of dunders, a single object can implement several at once — be a context manager, have a repr, support iteration — and Python uses whichever the syntax calls for.

```python run
class Tag:
    def __init__(self, name): self.name = name
    def __enter__(self):
        print(f"<{self.name}>"); return self
    def __exit__(self, *a):
        print(f"</{self.name}>")
    def __repr__(self): return f"Tag({self.name!r})"

with Tag("b") as t:
    print(t)
```

**Output:**
```
<b>
Tag('b')
</b>
```

```d2
direction: right
obj: "your object" { shape: circle }
len: "len(x)\n__len__"
iter: "for x in obj\n__iter__ / __getitem__"
add: "x + y\n__add__"
call: "obj(...)\n__call__"
ctx: "with obj\n__enter__ / __exit__"
eq: "x == y\n__eq__ (+ __hash__)"
repr: "repr(x)\n__repr__"
obj -> len
obj -> iter
obj -> add
obj -> call
obj -> ctx
obj -> eq
obj -> repr
```

**Analysis.** `Tag` implements two protocols at once: context management (`__enter__`/`__exit__`) and display (`__repr__`). The `with` used the first, `print(t)` the second. The diagram is the whole chapter in one picture: your object sits at the centre, and each protocol you implement wires a piece of Python's syntax to one of your methods.

**Intuition.**
*Mechanism.* Each protocol is keyed to specific dunders and consulted only by the matching syntax — they don't interfere. But some protocols **interlock**: defining `__eq__` resets `__hash__` to `None` (two "equal" objects must hash alike — [Tutorial 25](/synapse/programming-languages/python/object-oriented/dunder-methods)), so adding equality silently removes hashability unless you restore it.

*Concrete bite.* That interlock is the data model's sharpest edge:

```python run
class P:
    def __init__(self, x): self.x = x
    def __eq__(self, o): return self.x == o.x

print({P(1)})   # defining __eq__ dropped __hash__
```
```
Traceback (most recent call last):
  File "/w/main.py", line 5, in <module>
    print({P(1)})   # defining __eq__ dropped __hash__
          ^^^^^^
TypeError: unhashable type: 'P'
```

Adding `__eq__` made `P` unhashable, so it can't go in a set or be a dict key — defining one protocol (equality) disabled another (hashing). Restore it with `__hash__ = ...` (e.g. `return hash(self.x)`), keeping the contract "equal objects hash equally."

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Implement exactly the protocols your object should support, and respect the ones that interlock — define `__hash__` alongside `__eq__` for immutable value types, pair `__enter__` with `__exit__`, pair `__lt__` with the rest (or use `functools.total_ordering`). The cost of the data model's consistency is that these contracts are real: break one (equal-but-unequal-hash) and containers misbehave. ([dataclasses](/synapse/programming-languages/python/object-oriented/advanced-oop) handle the `__eq__`/`__hash__` pairing for you.)

</div>

---

## 6. Mental-model summary

| Principle | Consequence |
|-----------|-------------|
| Built-in syntax dispatches to dunders | `len(x)`→`__len__`, `x+y`→`__add__`, `x()`→`__call__`, `if x`→`__bool__`/`__len__` |
| `__len__` + `__getitem__` give len, indexing, iteration, membership | Two methods, four behaviours; missing one → `TypeError` |
| Operators should handle foreign operands | A naive `__add__` crashes on a non-matching type; return `NotImplemented` |
| `__call__` makes instances callable | "Callable" just means "has `__call__`"; `42()` → `TypeError` |
| Truthiness falls back `__bool__` → `__len__` → True | An object with `__len__()==0` is falsy |
| Some protocols interlock | Defining `__eq__` drops `__hash__`; restore it for hashable value types |

## 7. Gotcha checklist

<div style="border-left:4px solid #da5233;background:rgba(218,82,51,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

- **`TypeError: object of type 'X' has no len()` →** implement `__len__` (the exact dunder `len()` calls).
- **`AttributeError` inside `__add__`/`__eq__` →** you assumed the other operand's shape; guard with `isinstance`, return `NotImplemented`.
- **`TypeError: 'X' object is not callable` →** the type has no `__call__` (often a shadowed function name).
- **An object I expected truthy is falsy →** its `__len__` returns 0; add an explicit `__bool__` returning `True`.
- **`unhashable type` after adding `__eq__` →** define `__hash__` too (or use a frozen `@dataclass`).

</div>

---

<div style="border-left:4px solid #6d28d9;background:rgba(109,40,217,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

🧪 **Predict, then check.** Build a `Range`-like class holding a `start` and `stop`, with `__len__` and `__getitem__`. Predict whether `len()`, `obj[0]`, `for x in obj`, and `x in obj` all work from just those two methods. Then add `__eq__` comparing `(start, stop)` and predict what `{Range(0,3)}` does — and how to fix it. That last step is the data model's core lesson: protocols are powerful *and* they interlock.

</div>

## Your Turn

Before you move on, check your understanding with the coach — explain the idea, apply it, weigh the trade-offs, then defend your reasoning.

<div class="concept-coach"></div>
