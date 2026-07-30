---
title: Dunder Methods & Operator Overloading
summary: "Dunder" (double-underscore) methods are the hooks your objects implement so Python's built-in syntax and protocols dispatch to them — len(x), x + y, x == y, x[i], and for … in x all call dunders. Implement only the ones you need, and your objects start behaving like built-ins.
prereqs: []
---

# Dunder Methods — Plugging Into Python's Syntax

You've used `len()`, `+`, `==`, `[]`, and `for … in` since the first tutorials — always on built-ins. The thesis of this chapter: **those operators and built-in functions are not special-cased for `list` and `dict`; they dispatch to *methods with double-underscore names* — the "dunders" — and your own classes can implement them too.** When you write `len(x)`, Python calls `x.__len__()`; when you write `a + b`, it calls `a.__add__(b)`. Implement the right dunders and your objects plug straight into Python's syntax, behaving like built-ins to every caller and every library that relies on those protocols.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **The core idea.**

- Operators and built-ins aren't special-cased for `list`/`dict`.
- They dispatch to **dunder** (double-underscore) methods.
- `len(x)` calls `x.__len__()`; `a + b` calls `a.__add__(b)`.
- Implement them and your objects behave like **built-ins**.

</div>

The discipline is to implement *only the dunders you actually need* — they form the [data model](/synapse/programming-languages/python/advanced/the-data-model), a large protocol surface, but each one is opt-in. Every output below was produced by running the code.

<div style="border-left:4px solid #15448e;background:rgba(21,68,142,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

📘 **How to read the Intuition boxes.** Each one is built in three moves:

1. **The mechanism** — what the interpreter is *actually doing*.
2. **A concrete bite** — a specific, runnable way the naive assumption fails.
3. **The earned rule** — the decision heuristic, now justified rather than asserted, plus its cost.

</div>

---

## Table of Contents

1. [`__repr__` vs `__str__`](#1-__repr__-vs-__str__)
2. [`__eq__` and the `__hash__` consequence](#2-__eq__-and-the-__hash__-consequence)
3. [`__len__` and `__getitem__`](#3-__len__-and-__getitem__)
4. [Numeric dunders (`__add__`)](#4-numeric-dunders-__add__)
5. [Ordering (`__lt__`) and sorting](#5-ordering-__lt__-and-sorting)
6. [Mental-model summary](#6-mental-model-summary)
7. [Gotcha checklist](#7-gotcha-checklist)

---

## 1. `__repr__` vs `__str__`

Two dunders produce text for an object, with different audiences. `__repr__` is the *unambiguous developer* representation (shown in the REPL and inside containers); `__str__` is the *readable user* representation (used by `print` and `str`). If `__str__` is missing, `str()` falls back to `__repr__`.

```python run
class Temperature:
    def __init__(self, celsius):
        self.celsius = celsius
    def __repr__(self):
        return f"Temperature(celsius={self.celsius})"
    def __str__(self):
        return f"{self.celsius}°C"

t = Temperature(20)
print(t)            # uses __str__
print(str(t))       # uses __str__
print(repr(t))      # uses __repr__
print([t])          # a list uses __repr__ on its elements
```

**Output:**
```
20°C
20°C
Temperature(celsius=20)
[Temperature(celsius=20)]
```

**Analysis.** `print(t)` and `str(t)` both call `__str__`, giving the human-friendly `20°C`. `repr(t)` calls `__repr__`, giving the developer-friendly `Temperature(celsius=20)` — a string you could almost paste back into code. The last line is the key surprise: printing a *list* did **not** call `__str__` on the element. Containers format their contents with `__repr__`, because inside a data structure you want the unambiguous form, not the prettified one.

**Intuition.**
*Mechanism.* `str(x)` (and `print`) call `type(x).__str__`; if the class defines no `__str__`, the lookup walks up to `object.__str__`, which simply delegates to `__repr__`. `repr(x)` always calls `__repr__`. A container's own `__repr__` (and `__str__`) builds its text by calling `repr()` on each element — never `str()` — so your `__str__` is invisible inside lists, dicts, and tuples.

*Concrete bite.* Define only `__str__` and the developer view is still the useless default — and that default leaks the moment your object lands in a container:

```python run
class Money:
    def __init__(self, dollars):
        self.dollars = dollars
    def __str__(self):
        return f"${self.dollars}"

m = Money(5)
print(m)        # __str__ used: looks fine
print([m])      # no __repr__ -> ugly default
```

**Output (illustrative — the address varies per run):**
```
$5
[<__main__.Money object at 0x7e2885fd6900>]
```

(The `0x…` address is non-deterministic — yours will differ; it is shown here only to illustrate the default form.) `print(m)` looks fine, but `[m]` falls back to `object.__repr__`, exposing `<__main__.Money object at 0x…>`. That is exactly what you see when debugging a list of your objects in the REPL — opaque and unhelpful.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** **Always define `__repr__`; define `__str__` only when the user-facing form genuinely differs.** The cost of `__repr__` is one method; the payoff is that the REPL, debuggers, logs, and every container show something meaningful. If you write just one of the two, make it `__repr__` — because `str()` falls back to it, but `repr()` never falls back to `__str__`.

</div>

---

## 2. `__eq__` and the `__hash__` consequence

By default, `==` on instances means *identity* (same object). Define `__eq__` to make `==` mean *equal contents* — two `Point`s with the same coordinates compare equal.

```python run
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

print(Point(1, 2) == Point(1, 2))
print(Point(1, 2) == Point(3, 4))
```

**Output:**
```
True
False
```

**Analysis.** Without `__eq__`, `Point(1, 2) == Point(1, 2)` would be `False` (two distinct objects). Defining `__eq__` to compare `x` and `y` makes value-equality work as you'd expect. So far so good — but defining `__eq__` has a hidden, breaking consequence for hashing, covered next.

**Intuition.**
*Mechanism.* When you define `__eq__`, Python **sets `__hash__` to `None`** on that class. The reason is an invariant the language depends on: objects that compare equal *must* hash equal, so they land in the same bucket of a `set` or `dict`. Python can't guarantee your `__eq__` and the inherited identity-based `__hash__` agree, so rather than risk a silently broken container, it makes instances **unhashable** until you supply a matching `__hash__`. (See [hashability](/synapse/programming-languages/python/working-with-data/dictionaries-and-sets) for why containers require it.)

*Concrete bite.* The class above cannot go into a `set` or be used as a `dict` key:

```python run
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

p = Point(1, 2)
print({p})    # try to put in a set
```
```
Traceback (most recent call last):
  File "/w/main.py", line 9, in <module>
    print({p})    # try to put in a set
          ^^^
TypeError: unhashable type: 'Point'
```

You added `__eq__` to make comparison nicer and accidentally broke `set(points)` and every `dict` keyed on a `Point`. The fix is to define `__hash__` over the *same* fields `__eq__` uses:

```python run viz=hashmap:s
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y
    def __hash__(self):
        return hash((self.x, self.y))

p = Point(1, 2)
q = Point(1, 2)
s = {p, q}        # equal points collapse to one entry
print(len(s))
print(Point(1, 2) in s)
```
```
1
True
```

`hash((self.x, self.y))` reuses the tuple's hash, derived from exactly the fields that define equality. Now equal points hash equal: `{p, q}` collapses to one element, and membership testing works.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** **If you define `__eq__` and want instances usable in sets or as dict keys, define `__hash__` over the same fields — and only over fields that never change.** The cost is keeping the two methods in sync; the benefit is correct containers. If your objects are mutable and you mutate the hashed fields, leave them unhashable (the default after `__eq__`) — a mutating key silently corrupts a `dict`, which is far worse than a clear `TypeError`.

</div>

---

## 3. `__len__` and `__getitem__`

A container-like class earns `len(obj)` by defining `__len__`, and indexing `obj[i]` by defining `__getitem__`.

```python run viz=array:p.songs
class Playlist:
    def __init__(self, songs):
        self.songs = songs
    def __len__(self):
        return len(self.songs)
    def __getitem__(self, i):
        return self.songs[i]

p = Playlist(["a", "b", "c"])
print(len(p))
print(p[0])
print(p[-1])
```

**Output:**
```
3
a
c
```

**Analysis.** `len(p)` dispatches to `__len__`, which delegates to the wrapped list. `p[0]` and `p[-1]` dispatch to `__getitem__(self, i)` with `i` set to `0` and `-1`; because we pass the index straight to a real list, negative indexing works for free. The object now *looks* indexable to any caller.

**Intuition.**
*Mechanism.* `len(x)` calls `x.__len__()`; `x[i]` calls `x.__getitem__(i)`. There is a deeper payoff: if a class has **no** `__iter__`, Python's `for` loop falls back to calling `__getitem__` with `0, 1, 2, …`, stopping when it raises `IndexError`. So `__getitem__` alone makes an object iterable, even without an explicit iterator.

*Concrete bite.* The iteration fallback is real — this loop works with *only* `__getitem__`, no `__iter__` defined:

```python run viz=array:p.songs
class Playlist:
    def __init__(self, songs):
        self.songs = songs
    def __getitem__(self, i):
        return self.songs[i]

p = Playlist(["a", "b", "c"])
for song in p:        # works via integer-index fallback
    print(song)
```
```
a
b
c
```

Python calls `p[0]`, `p[1]`, `p[2]`, then `p[3]` raises `IndexError` (from the inner list), which the `for` loop treats as "stop." No `__iter__` was needed.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** **Define `__len__` and `__getitem__` to make a class behave like a sequence; lean on the `__getitem__` iteration fallback only for genuinely index-addressable data.** The cost of relying on the fallback is that it forces *integer* indexing semantics and only stops on `IndexError` — for anything lazy or non-integer-keyed, define `__iter__` explicitly ([iterators and generators](/synapse/programming-languages/python/how-python-works/iterators-and-generators)) so iteration doesn't accidentally depend on `[i]`.

</div>

---

## 4. Numeric dunders (`__add__`)

Arithmetic operators dispatch to numeric dunders: `a + b` calls `a.__add__(b)`. Define `__add__` to make `+` build a new object — here, vector addition.

```python run
class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def __repr__(self):
        return f"Vector({self.x}, {self.y})"
    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)

print(Vector(1, 2) + Vector(3, 4))
```

**Output:**
```
Vector(4, 6)
```

**Analysis.** `Vector(1, 2) + Vector(3, 4)` calls `__add__`, which returns a **new** `Vector(4, 6)` rather than mutating either operand — the right convention for `+`. The `__repr__` from §1 is what makes the printed result readable. But notice `__add__` blindly reads `other.x` and `other.y`, which only works if `other` is also a `Vector`.

**Intuition.**
*Mechanism.* `a + b` first tries `a.__add__(b)`. If that method returns the special sentinel `NotImplemented` (not the same as raising `NotImplementedError`), Python then tries the *reflected* call `b.__radd__(a)`; if both give up, it raises `TypeError`. Our `__add__` doesn't check the type of `other`, so it doesn't reach that polite fallback — it just tries to read attributes that may not exist.

*Concrete bite.* Adding a plain `int` reaches inside `__add__` and fails on the attribute access, not with a clean "unsupported operands" message:

```python run
class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def __repr__(self):
        return f"Vector({self.x}, {self.y})"
    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)

print(Vector(1, 2) + 5)
```
```
Traceback (most recent call last):
  File "/w/main.py", line 10, in <module>
    print(Vector(1, 2) + 5)
          ~~~~~~~~~~~~~^~~
  File "/w/main.py", line 8, in __add__
    return Vector(self.x + other.x, self.y + other.y)
                           ^^^^^^^
AttributeError: 'int' object has no attribute 'x'
```

`5` has no `.x`, so `other.x` raises `AttributeError` from *inside* your method — a leaky, confusing error. The disciplined version guards the type and returns `NotImplemented` for anything it can't handle (`if not isinstance(other, Vector): return NotImplemented`), which lets Python produce the standard `TypeError: unsupported operand type(s)` and gives the *other* operand a chance via `__radd__` (useful for, e.g., `5 + vec` or `sum(vectors)`).

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** **Implement `__add__` to return a new object, and guard the operand type — return `NotImplemented` (don't raise) for types you don't support.** The cost is a type check and remembering that `NotImplemented` ≠ `NotImplementedError`; the payoff is correct interaction with other types, sane error messages, and reflected operations like `__radd__` working as Python intends.

</div>

---

## 5. Ordering (`__lt__`) and sorting

Sorting and the `<` operator dispatch to `__lt__`. Define it, and a list of your objects becomes sortable with the built-in `sorted()`.

```python run
class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age
    def __repr__(self):
        return f"{self.name}({self.age})"
    def __lt__(self, other):
        return self.age < other.age

people = [Person("Ann", 30), Person("Bo", 25), Person("Cy", 35)]
print(sorted(people))
```

**Output:**
```
[Bo(25), Ann(30), Cy(35)]
```

**Analysis.** `sorted()` orders elements by repeatedly asking "is `a` less than `b`?" — i.e. calling `a.__lt__(b)`. Our `__lt__` compares `age`, so the list comes out youngest-first. We only had to define *one* comparison dunder for sorting to work, because that's the only one `sorted()` needs.

**Intuition.**
*Mechanism.* `sorted()` and `list.sort()` order elements using **only `<`** (`__lt__`) — they never need `>`, `<=`, or `==` for the sort itself. So a single `__lt__` is enough to sort. The other rich-comparison dunders (`__le__`, `__gt__`, `__ge__`) are independent: defining `__lt__` does *not* auto-define them.

*Concrete bite.* Without any `__lt__`, sorting a list of your objects fails immediately:

```python run
class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age

people = [Person("Ann", 30), Person("Bo", 25)]
print(sorted(people))
```
```
Traceback (most recent call last):
  File "/w/main.py", line 7, in <module>
    print(sorted(people))
          ~~~~~~^^^^^^^^
TypeError: '<' not supported between instances of 'Person' and 'Person'
```

`sorted()` tries to compare two `Person`s with `<`, finds no `__lt__` (and no inherited ordering), and raises. The fix is the `__lt__` above — or, if you need the *full* set of `<`, `<=`, `>`, `>=` consistently, decorate the class with `@functools.total_ordering` and define just `__lt__` and `__eq__`; it fills in the rest.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** **Define `__lt__` for sortability; reach for `functools.total_ordering` only when you also need the other comparison operators.** The cost of `total_ordering` is a slightly slower derived comparison and a required `__eq__`; the benefit is not hand-writing four near-identical methods. For the common case of "I just want `sorted()` to work," a lone `__lt__` — or, simpler still, `sorted(people, key=lambda p: p.age)` with no dunder at all — is enough.

</div>

---

## 6. Mental-model summary

| Principle | Consequence |
|-----------|-------------|
| Built-in syntax dispatches to dunders | `len(x)`→`__len__`, `x+y`→`__add__`, `x==y`→`__eq__`, `x[i]`→`__getitem__` |
| Containers format elements with `__repr__` | Define `__repr__` or your objects look like `<… at 0x…>` in lists/logs |
| Defining `__eq__` sets `__hash__` to `None` | Instances become unhashable; add `__hash__` to use them in sets/dict keys |
| `__getitem__` alone makes an object iterable | `for` falls back to `obj[0], obj[1], …` until `IndexError` |
| Numeric dunders should return `NotImplemented`, not raise | Lets the other operand try (`__radd__`) and yields a clean `TypeError` |
| `sorted()` uses only `__lt__` | One comparison dunder enables sorting; `total_ordering` fills in the rest |

## 7. Gotcha checklist

<div style="border-left:4px solid #da5233;background:rgba(218,82,51,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

- **Your object prints as `<… object at 0x…>` in a list/log →** you defined only `__str__` (or neither); define `__repr__`.
- **`TypeError: unhashable type` after adding `__eq__` →** Python set `__hash__` to `None`; define `__hash__` over the same (immutable) fields.
- **A `dict` keyed on your object behaves erratically →** you hashed a field you later mutated; hash only never-changing fields, or keep the object unhashable.
- **`AttributeError` from inside `__add__` when adding a non-matching type →** guard with `isinstance` and `return NotImplemented` instead of reading attributes blindly.
- **`TypeError: '<' not supported between instances` from `sorted()` →** define `__lt__` (or pass `key=…`); use `@functools.total_ordering` if you need all four comparisons.

</div>

---

<div style="border-left:4px solid #6d28d9;background:rgba(109,40,217,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

🧪 **Predict, then check.** Write a `Fraction` class with `__init__(self, num, den)`, a `__repr__` of the form `Fraction(1, 2)`, and an `__eq__` that treats `1/2` and `2/4` as equal (compare `num * other.den == other.num * den`). First predict what `{Fraction(1, 2), Fraction(2, 4)}` does *before* you add `__hash__` — set size, or an error? Then add a `__hash__` that makes the two collapse to one entry (hint: reduce by the gcd first, since equal fractions must hash equal), and predict the new `len(...)`. Finally, predict whether `sorted([Fraction(1, 2), Fraction(1, 3)])` works with no `__lt__` defined, and what error you'd see if not.

</div>

## Your Turn

Before you move on, check your understanding with the coach — explain the idea, apply it, weigh the trade-offs, then defend your reasoning.

<div class="concept-coach"></div>
