---
title: Properties & Descriptors
summary: "@property lets attribute access (obj.x) secretly run method code, so you can compute, validate, or protect a value without changing the caller-facing API. Descriptors are the general protocol underneath — the same machinery that powers properties and even ordinary methods."
prereqs: []
---

# Properties & Descriptors — Managed Attributes

In Python you start with plain attributes — `self.radius = r`, and callers read `c.radius`. The thesis of this chapter: **`@property` lets that *same* attribute access run *method* code behind the scenes**, so you can compute a value on the fly, validate an assignment, or make an attribute read-only — all *without* changing how callers write `obj.x`. This is why Python culture says don't write `get_x()`/`set_x()` up front: a plain attribute can be *upgraded* to a managed one later, invisibly. Underneath `@property` sits the general **descriptor protocol** (`__get__`/`__set__`), the same mechanism that turns functions into bound methods.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **The core idea.**

- `@property` makes the *same* attribute access **run method code**.
- You can compute, validate, or make an attribute read-only.
- Callers still write `obj.x` — the API doesn't change.
- The **descriptor protocol** (`__get__`/`__set__`) is the machinery underneath.

</div>

We build from the everyday tool (`@property`) down to the protocol that explains it. Every output below was produced by running the code.

<div style="border-left:4px solid #15448e;background:rgba(21,68,142,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

📘 **How to read the Intuition boxes.** Each one is built in three moves:

1. **The mechanism** — what the interpreter is *actually doing*.
2. **A concrete bite** — a specific, runnable way the naive assumption fails.
3. **The earned rule** — the decision heuristic, now justified rather than asserted, plus its cost.

</div>

---

## Table of Contents

1. [`@property` for a computed attribute](#1-property-for-a-computed-attribute)
2. [A setter with validation](#2-a-setter-with-validation)
3. [Read-only by omitting the setter](#3-read-only-by-omitting-the-setter)
4. [Why properties beat `get_x()`/`set_x()`](#4-why-properties-beat-get_xset_x)
5. [The descriptor protocol](#5-the-descriptor-protocol)
6. [Mental-model summary](#6-mental-model-summary)
7. [Gotcha checklist](#7-gotcha-checklist)

---

## 1. `@property` for a computed attribute

`@property` turns a method into a *managed attribute*: callers access it like data (no parentheses), but each access runs the method. The classic use is a value *derived* from others — here, a circle's area computed from its radius.

```python run
class Circle:
    def __init__(self, radius):
        self.radius = radius
    @property
    def area(self):
        return 3.141592653589793 * self.radius ** 2

c = Circle(2)
print(c.area)        # no parentheses - access, not call
c.radius = 3
print(c.area)        # recomputed from the new radius
```

**Output:**
```
12.566370614359172
28.274333882308138
```

**Analysis.** `area` is defined as a *method* but accessed as an *attribute* — `c.area`, not `c.area()`. The `@property` decorator is what makes that work. Crucially, `area` stores nothing: each access recomputes from the current `radius`, so after `c.radius = 3` the area updates automatically. There is no stale value to keep in sync.

**Intuition.**
*Mechanism.* `@property` wraps the getter function in a *property object* and binds it to the class attribute `area`. When you write `c.area`, attribute lookup finds that property object on the class and calls its `__get__`, which runs your getter with `self = c`. The result is computed on demand — `area` never occupies a slot in `c.__dict__`.

*Concrete bite.* Because it runs on *every* access, a property is recomputed each time — convenient for correctness, but it is **not** a cached field:

```python run
class Circle:
    def __init__(self, radius):
        self.radius = radius
    @property
    def area(self):
        print("computing area")     # side effect to make recomputation visible
        return 3.141592653589793 * self.radius ** 2

c = Circle(2)
_ = c.area
_ = c.area      # computed AGAIN
```
```
computing area
computing area
```

Two accesses, two computations. For a cheap formula that's ideal. For an expensive one, naive `@property` recomputes every time — reach for `functools.cached_property` to compute once and store the result.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** **Use `@property` for a value derived from other attributes, so it can never go stale.** The cost is that the getter runs on *every* access — fine for arithmetic, wasteful for expensive work (use `functools.cached_property` then, accepting that a cached value won't track later changes to its inputs).

</div>

---

## 2. A setter with validation

A property can also intercept *assignment*. Pair the getter with a `@<name>.setter` method, and `obj.x = value` runs your code — the natural place to validate.

```python run
class Circle:
    def __init__(self, radius):
        self.radius = radius          # goes through the setter
    @property
    def radius(self):
        return self._radius
    @radius.setter
    def radius(self, value):
        if value < 0:
            raise ValueError(f"radius must be non-negative, got {value}")
        self._radius = value

c = Circle(2)
print(c.radius)
c.radius = 5
print(c.radius)
```

**Output:**
```
2
5
```

**Analysis.** There are now two `radius` methods: the getter (returns the private `self._radius`) and the setter (validates, then stores). Even `__init__`'s `self.radius = radius` flows through the setter, so the validation runs at construction too. The real value lives in `_radius` (the leading underscore signals "internal"); `radius` is the *managed* public name. Valid assignments succeed silently.

**Intuition.**
*Mechanism.* `@radius.setter` attaches a setter function to the *same* property object created by `@property`. Now `c.radius = 5` doesn't write to `c.__dict__["radius"]`; instead the property's `__set__` runs your setter with `value = 5`. The actual storage is wherever the setter puts it — by convention a "private" `self._radius`. Reading and writing `radius` are now two different functions you control.

*Concrete bite.* An invalid assignment is rejected *at the point of assignment*, by your `raise`:

```python run
class Circle:
    def __init__(self, radius):
        self.radius = radius
    @property
    def radius(self):
        return self._radius
    @radius.setter
    def radius(self, value):
        if value < 0:
            raise ValueError(f"radius must be non-negative, got {value}")
        self._radius = value

c = Circle(2)
c.radius = -1        # rejected by the setter
```
```
Traceback (most recent call last):
  File "/w/main.py", line 14, in <module>
    c.radius = -1        # rejected by the setter
    ^^^^^^^^
  File "/w/main.py", line 10, in radius
    raise ValueError(f"radius must be non-negative, got {value}")
ValueError: radius must be non-negative, got -1
```

`c.radius = -1` *looks* like a plain assignment, but it invoked the setter, which raised `ValueError`. The object can never hold a negative radius — the invariant is enforced at the boundary, not merely documented.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** **Add a setter when an attribute has an invariant to enforce on write (range, type, immutability of derived state).** The cost is the getter/setter pair plus a backing `_name` field; the benefit is that callers keep writing `obj.x = v` while *you* guarantee the value is always valid — the check lives in one place instead of at every call site.

</div>

---

## 3. Read-only by omitting the setter

Define a property with a getter and **no** setter, and the attribute becomes read-only — assignment is rejected by the property machinery itself.

```python run
class Circle:
    def __init__(self, radius):
        self._radius = radius
    @property
    def radius(self):
        return self._radius

c = Circle(2)
print(c.radius)
c.radius = 5         # no setter defined
```

**Output:**
```
2
```
```
Traceback (most recent call last):
  File "/w/main.py", line 10, in <module>
    c.radius = 5         # no setter defined
    ^^^^^^^^
AttributeError: property 'radius' of 'Circle' object has no setter
```

**Analysis.** Reading `c.radius` works (`2`); the assignment crashes. Note `__init__` writes to `self._radius` *directly* (not `self.radius`), since there's no setter to go through. The error is raised by the property object — not by any code we wrote — because a getter-only property defines `__get__` but no `__set__`.

**Intuition.**
*Mechanism.* A property object always defines `__set__`; when you supply no setter, that `__set__` simply raises `AttributeError`. Because the property lives on the *class* and defines `__set__`, it is a **data descriptor** — and data descriptors take priority over the instance `__dict__`. So Python doesn't quietly fall back to creating an instance attribute; it routes the assignment to the property's `__set__`, which refuses.

*Concrete bite.* The exact wording on Python 3.13 names the property and class:

```python run
class Circle:
    def __init__(self, radius):
        self._radius = radius
    @property
    def radius(self):
        return self._radius

Circle(2).radius = 5
```
```
Traceback (most recent call last):
  File "/w/main.py", line 8, in <module>
    Circle(2).radius = 5
    ^^^^^^^^^^^^^^^^
AttributeError: property 'radius' of 'Circle' object has no setter
```

On 3.13 the message is `property 'radius' of 'Circle' object has no setter` (older Pythons said the terser `can't set attribute`). It is an `AttributeError` either way — the read-only guarantee holds, and the message tells you precisely which property refused.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** **Omit the setter to make an attribute read-only through the public API.** The cost is that "read-only" is a convention, not a fortress — `c._radius = 5` still works, because the underscore field is only *protected by naming*. Use it to prevent *accidental* writes and to signal intent; don't mistake it for true immutability (for that, see `frozen=True` dataclasses in [advanced OOP](/synapse/programming-languages/python/object-oriented/advanced-oop)).

</div>

---

## 4. Why properties beat `get_x()`/`set_x()`

The Pythonic argument for properties is concrete: **start with a plain attribute, and upgrade to a property later without touching a single caller.** Begin with the simplest thing.

```python run
class Account:
    def __init__(self, balance):
        self.balance = balance      # plain attribute

a = Account(100)
print(a.balance)
a.balance = 250                      # callers write plain assignment
print(a.balance)
```

**Output:**
```
100
250
```

**Analysis.** `balance` is an ordinary attribute — no ceremony, no getter, no setter. Callers read and write it directly. In a Java-style design you'd have written `getBalance()`/`setBalance()` *defensively from day one*, just in case validation became necessary. Python lets you defer that decision, because the attribute can become managed later with no API change.

**Intuition.**
*Mechanism.* `obj.x` is the public interface whether `x` is a plain attribute *or* a property — the syntax is identical. Promoting a plain attribute to a property changes only the *class*, not any *caller*: every `a.balance` read and `a.balance = v` write keeps working, now routed through your getter/setter. Callers literally cannot tell the difference.

*Concrete bite.* Add validation later by converting `balance` to a property — the caller code from above is **byte-for-byte unchanged** and still runs:

```python run
class Account:
    def __init__(self, balance):
        self.balance = balance      # still goes through the setter now
    @property
    def balance(self):
        return self._balance
    @balance.setter
    def balance(self, value):
        if value < 0:
            raise ValueError("balance cannot be negative")
        self._balance = value

a = Account(100)
print(a.balance)        # caller code is UNCHANGED
a.balance = 250
print(a.balance)
```
```
100
250
```

Same output as the plain-attribute version, same caller lines — but now negative balances are impossible. Had you exposed `getBalance()`/`setBalance()` instead, you'd have *forced* that ceremony on callers forever, for a check you didn't need yet.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** **Don't write getters/setters preemptively — expose a plain attribute, and reach for `@property` only when you actually need computation or validation.** The cost of guessing wrong (starting plain, upgrading later) is *zero*, because the upgrade is caller-invisible; the cost of defensive getters is permanent boilerplate and a clumsier API. Add the property the day the invariant appears, not before.

</div>

---

## 5. The descriptor protocol

`@property` is convenient but not magic — it's one example of a **descriptor**: any object that defines `__get__` (and optionally `__set__`). When such an object is a *class* attribute, Python routes attribute access through its methods. This is also how plain methods become bound methods. You can write your own descriptor to reuse managed-attribute behavior across many attributes.

```python run
class Positive:
    def __set_name__(self, owner, name):
        self.name = "_" + name
    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return getattr(obj, self.name)
    def __set__(self, obj, value):
        if value <= 0:
            raise ValueError(f"{self.name[1:]} must be positive, got {value}")
        setattr(obj, self.name, value)

class Product:
    price = Positive()
    quantity = Positive()
    def __init__(self, price, quantity):
        self.price = price
        self.quantity = quantity

p = Product(10, 3)
print(p.price, p.quantity)
p.price = 20
print(p.price)
```

**Output:**
```
10 3
20
```

**Analysis.** `Positive` is a descriptor: `__get__` reads the backing field, `__set__` validates then writes it. `__set_name__` is a convenience hook Python calls when the class body runs, telling the descriptor the attribute name it was assigned to (`price`, `quantity`), so each instance stores into a distinct `_price`/`_quantity`. Declaring `price = Positive()` and `quantity = Positive()` reuses the *same validation logic* for two attributes — something a `@property` can't do without writing the getter/setter twice.

**Intuition.**
*Mechanism.* When `Positive` is a class attribute, `p.price` calls `Positive.__get__(self, p, Product)` and `p.price = 20` calls `Positive.__set__(self, p, 20)`. Because the descriptor defines `__set__`, it's a *data descriptor* and intercepts the assignment instead of letting it land in `p.__dict__`. The same protocol underlies methods: a plain function is a (non-data) descriptor whose `__get__` returns a *bound* method — which is why `obj.method` automatically receives `self`. `@property` is just a ready-made data descriptor.

*Concrete bite.* The shared validation fires for *both* attributes from one class — here it rejects a bad `price` at construction, via `__set__`:

```python run
class Positive:
    def __set_name__(self, owner, name):
        self.name = "_" + name
    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return getattr(obj, self.name)
    def __set__(self, obj, value):
        if value <= 0:
            raise ValueError(f"{self.name[1:]} must be positive, got {value}")
        setattr(obj, self.name, value)

class Product:
    price = Positive()
    def __init__(self, price):
        self.price = price

Product(-5)
```
```
Traceback (most recent call last):
  File "/w/main.py", line 18, in <module>
    Product(-5)
    ~~~~~~~^^^^
  File "/w/main.py", line 16, in __init__
    self.price = price
    ^^^^^^^^^^
  File "/w/main.py", line 10, in __set__
    raise ValueError(f"{self.name[1:]} must be positive, got {value}")
ValueError: price must be positive, got -5
```

`self.price = price` in `__init__` routed through `Positive.__set__`, which rejected `-5`. One descriptor class enforces the rule for `price`, `quantity`, and any other `Positive()` attribute you add — no per-attribute boilerplate.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** **Reach for `@property` for one-off managed attributes; write a descriptor when the *same* managed behavior must be reused across many attributes or classes.** The cost of a descriptor is more concept (three dunders, data-vs-non-data priority, `__set_name__`); the payoff is DRY validation/computation logic — exactly what frameworks (ORM fields, typed-attribute libraries) are built on. For a single attribute, the descriptor is overkill: `@property` is the same machinery with less ceremony.

</div>

---

## 6. Mental-model summary

| Principle | Consequence |
|-----------|-------------|
| `@property` makes `obj.x` run getter code | Accessed without `()`; recomputed on every access (not cached) |
| A `@x.setter` runs on `obj.x = v` | The place to validate writes; store the real value in `_x` |
| Omitting the setter makes it read-only | Assignment raises `AttributeError: property '…' has no setter` (3.13) |
| `obj.x` is the same API for attribute or property | Start plain, upgrade to `@property` later with zero caller changes |
| `@property` *is* a data descriptor (`__get__`/`__set__`) | Data descriptors override the instance `__dict__`; methods are descriptors too |
| A custom descriptor reuses logic across attributes | One `Positive` class validates many fields; what `@property` can't share |

## 7. Gotcha checklist

<div style="border-left:4px solid #da5233;background:rgba(218,82,51,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

- **Property returns the method object instead of a value →** you wrote `c.area()` with parentheses; a property is accessed as `c.area`, no call.
- **`RecursionError` in a getter/setter →** the getter returned `self.radius` (itself) instead of the backing `self._radius`; store and read the private field.
- **`AttributeError: property '…' has no setter` →** the property is getter-only (read-only by design); add a `@<name>.setter`, or write the backing `_field` directly.
- **An expensive property is slow when read in a loop →** plain `@property` recomputes each access; use `functools.cached_property` (accepting it won't track later input changes).
- **Validation in a custom descriptor never fires →** you defined only `__get__` (a non-data descriptor); the instance `__dict__` shadows it — add `__set__` to make it a data descriptor.

</div>

---

<div style="border-left:4px solid #6d28d9;background:rgba(109,40,217,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

🧪 **Predict, then check.** Write a `Temperature` class storing `_celsius`, with a `celsius` property (getter + validating setter that rejects values below `-273.15`) and a `fahrenheit` property. Make `fahrenheit` *computed* from `celsius` on read (`c * 9 / 5 + 32`) with a setter that converts back and assigns through `self.celsius`. First predict what `t.fahrenheit = 32` then `t.celsius` prints. Then predict the exact error type and message (on 3.13) if you make `fahrenheit` getter-only and run `t.fahrenheit = 100`. Finally, predict whether converting `celsius` from a plain attribute to this property would require changing any code that does `t.celsius = 20` — and why.

</div>

## Your Turn

Before you move on, check your understanding with the coach — explain the idea, apply it, weigh the trade-offs, then defend your reasoning.

<div class="concept-coach"></div>
