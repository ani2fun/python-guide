---
title: Class vs Instance; Encapsulation
summary: Attributes defined on the class are shared by every instance, while attributes set on `self` are per-instance, and attribute lookup checks the instance first and the class second. This split explains the mutable-class-attribute trap, what `@classmethod` and `@staticmethod` are for, and why Python encapsulates by convention rather than enforcement.
prereqs: []
---

# Class vs Instance — Shared State, Private Names

In [Classes & Objects](/synapse/programming-languages/python/object-oriented/classes-and-objects) every attribute lived on the instance, set through `self`. But you can also attach attributes and methods to the *class itself*, and the two kinds behave very differently. The thesis: **attributes defined on the class are *shared* by all instances; attributes set on `self` are *per-instance*; and a lookup like `d.x` checks the instance first, then falls back to the class.** That single lookup rule explains a notorious trap, two method decorators, and Python's whole approach to "private" data.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **The core idea.**

- Class attributes are **shared** by all instances.
- Attributes set on `self` are **per-instance**.
- A lookup like `d.x` checks the instance first, then falls back to the class.

</div>

This builds directly on instance attributes and `__dict__` from the previous tutorial. Every output below was produced by running the code — including the deliberate tracebacks.

<div style="border-left:4px solid #15448e;background:rgba(21,68,142,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

📘 **How to read the Intuition boxes.** Each one is built in three moves:

1. **The mechanism** — what the interpreter is *actually doing*.
2. **A concrete bite** — a specific, runnable way the naive assumption fails.
3. **The earned rule** — the decision heuristic, now justified rather than asserted, plus its cost.

</div>

---

## Table of Contents

1. [Class attributes vs instance attributes](#1-class-attributes-vs-instance-attributes)
2. [The mutable-class-attribute trap](#2-the-mutable-class-attribute-trap)
3. [`@classmethod`](#3-classmethod)
4. [`@staticmethod`](#4-staticmethod)
5. [Encapsulation conventions](#5-encapsulation-conventions)
6. [Mental-model summary](#6-mental-model-summary)
7. [Gotcha checklist](#7-gotcha-checklist)

---

## 1. Class attributes vs instance attributes

An assignment in the class body — outside any method — creates a *class attribute*, shared by every instance. An assignment to `self.x` inside `__init__` creates an *instance attribute*, unique to that object. Here `species` is shared; `name` is per-instance.

```python run
class Dog:
    species = "Canis"          # class attribute: shared

    def __init__(self, name):
        self.name = name       # instance attribute: per-object

a = Dog("Rex")
b = Dog("Fido")
print(a.species, b.species)
print(a.name, b.name)
```

**Output:**
```
Canis Canis
Rex Fido
```

**Analysis.** `species` was defined once, in the class body, so `a.species` and `b.species` both find the *same* class-level value, `"Canis"`. `name` was set on `self`, so each dog has its own — `Rex` and `Fido`. When you read `a.species`, Python does not find `species` in `a`'s own `__dict__`, so it looks at the class and finds it there. That fallback is the lookup rule in action.

**Intuition.**
*Mechanism.* Reading `a.x` searches `a.__dict__` first; if `x` is absent, it searches `type(a).__dict__` (the class). So a class attribute acts as a shared default visible through every instance, until an instance overrides it with its own attribute of the same name.

*Concrete bite.* That asymmetry surprises people on *writes*. Assigning `a.species = ...` does **not** change the class attribute — it creates an instance attribute that *shadows* it, for that one object only:

```python run
class Dog:
    species = "Canis"

    def __init__(self, name):
        self.name = name

a = Dog("Rex")
b = Dog("Fido")
a.species = "Lupus"
print(a.species)
print(b.species)
print(Dog.species)
print(a.__dict__)
print(b.__dict__)
```

**Output:**
```
Lupus
Canis
Canis
{'name': 'Rex', 'species': 'Lupus'}
{'name': 'Fido'}
```

`a.species = "Lupus"` wrote into `a.__dict__` (see the last two lines — `a` now carries `species`, `b` does not). Reads on `a` find that instance copy first, so `a.species` is `"Lupus"`. But `b.species` and `Dog.species` are unchanged at `"Canis"`: the assignment never touched the class. Writing through an instance always lands *on the instance*, never on the class behind it.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Use class attributes for values genuinely common to all instances (constants, shared defaults) and instance attributes for anything that varies per object; remember that `instance.attr = value` always creates or updates an *instance* attribute, never the class one. The cost of forgetting this is the illusion that you edited shared state when you only shadowed it on one object — a bug that hides until another instance reveals the unchanged original.

</div>

---

## 2. The mutable-class-attribute trap

Section 1's shadowing rule applies to *assignment* (`=`). But *mutating* a shared object (calling `.append`, say) is not an assignment — it reaches through to the one shared object. A mutable class attribute is therefore shared in the most dangerous way.

```python run viz=array:a.tricks
class Dog:
    tricks = []                # mutable class attribute — ONE list, shared

    def __init__(self, name):
        self.name = name

a = Dog("Rex")
b = Dog("Fido")
a.tricks.append("sit")
print(a.tricks)
print(b.tricks)
print(a.tricks is b.tricks)
```

**Output:**
```
['sit']
['sit']
True
```

**Analysis.** We taught only `a` to `"sit"` — yet `b.tricks` shows `"sit"` too. The reason is the last line: `a.tricks is b.tricks` is `True`. There is exactly *one* list, created once when the class was defined, and both dogs see it. `a.tricks.append("sit")` is not an assignment — it does not shadow anything — so it mutates that single shared list, and every instance observes the change.

**Intuition.**
*Mechanism.* `tricks = []` runs *once*, at class-definition time, producing one list object stored on the class. `a.tricks` and `b.tricks` both fall back to the class and return that *same* list. `.append` mutates it in place; there is no per-instance copy to shadow it, because you never assigned `a.tricks = ...`. One object, many viewers.

*Concrete bite — the fix.* Create the mutable state *per instance*, inside `__init__`, so each object gets its own list:

```python run viz=array:a.tricks
class Dog:
    def __init__(self, name):
        self.name = name
        self.tricks = []       # fresh list for THIS instance

a = Dog("Rex")
b = Dog("Fido")
a.tricks.append("sit")
print(a.tricks)
print(b.tricks)
print(a.tricks is b.tricks)
```

**Output:**
```
['sit']
[]
False
```

Now `self.tricks = []` runs once *per instance*, so `a` and `b` get different lists — `a.tricks is b.tricks` is `False`. Teaching `a` to `"sit"` leaves `b` empty, as intended. The rule: shared *immutable* defaults on the class are fine (you can only shadow them, never mutate them), but shared *mutable* state belongs in `__init__`.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Put any attribute you will *mutate* (lists, dicts, sets, custom mutable objects) in `__init__` as `self.x = ...`; reserve class attributes for immutable shared values. This is the same hazard as the mutable-default-argument trap in [functions-in-depth](/synapse/programming-languages/python/how-python-works/functions-in-depth) — a mutable created once and silently shared. The cost of getting it wrong is cross-contamination between instances that looks impossible until you check `is`.

</div>

---

## 3. `@classmethod`

A method marked `@classmethod` receives the *class* as its first argument — named `cls` by convention — instead of an instance. Its classic use is an *alternate constructor*: a second way to build an instance, beyond `__init__`.

```python run
class Dog:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    @classmethod
    def from_string(cls, s):
        name, age = s.split(",")
        return cls(name, int(age))   # cls is Dog — builds an instance

    def __repr__(self):
        return f"Dog({self.name!r}, {self.age})"

d = Dog.from_string("Rex,3")
print(d)
print(type(d))
```

**Output:**
```
Dog('Rex', 3)
<class '__main__.Dog'>
```

**Analysis.** `from_string` is a classmethod, so calling `Dog.from_string("Rex,3")` passed `Dog` itself as `cls`. The method parsed the string, then called `cls(name, int(age))` — i.e. `Dog("Rex", 3)` — to build and return a real instance. The result is an ordinary `Dog`, as `type(d)` confirms. It is a constructor with a different *input shape* (a `"name,age"` string) that funnels back into `__init__`.

**Intuition.**
*Mechanism.* `@classmethod` changes what the first parameter receives: not the instance, but the class object. So `cls` is `Dog` here. Calling `cls(...)` is the same as calling `Dog(...)` — it runs `__init__` and yields an instance. The method *has* the class but does not *have* an instance.

*Concrete bite.* To make the contrast concrete, a classmethod can show you exactly what it receives — the class, not an instance:

```python run
class Dog:
    @classmethod
    def whoami(cls):
        return cls

print(Dog.whoami())
print(Dog.whoami() is Dog)
```

**Output:**
```
<class '__main__.Dog'>
True
```

`whoami` returns `cls`, and the output is the *class* `Dog` (`Dog.whoami() is Dog` is `True`) — there is no instance anywhere in this code. That is the defining difference from an instance method: an instance method's `self` is one dog; a classmethod's `cls` is the `Dog` blueprint.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Reach for `@classmethod` when a method needs the class but not a specific instance — most often as an alternate constructor (`from_string`, `from_dict`, `from_json`) that builds and returns `cls(...)`. The cost is remembering that `cls` is the class, so calling `cls()` *makes* an object rather than acting on an existing one; the payoff is one obvious, named entry point per construction shape instead of free-floating factory functions.

</div>

---

## 4. `@staticmethod`

A method marked `@staticmethod` receives *neither* `self` nor `cls`. It is a plain function that simply *lives inside* the class for organisational reasons — namespaced under the class, but with no access to instance or class state.

```python run
class Dog:
    def __init__(self, age):
        self.age = age

    @staticmethod
    def human_years(dog_years):
        return dog_years * 7      # no self, no cls — pure function

print(Dog.human_years(3))
d = Dog(3)
print(d.human_years(d.age))
```

**Output:**
```
21
21
```

**Analysis.** `human_years` takes only `dog_years` — no `self`, no `cls`. It is a self-contained calculation that conceptually belongs to dogs, so we keep it under `Dog` rather than as a loose module function. You can call it on the class (`Dog.human_years(3)`) or through an instance (`d.human_years(d.age)`); both behave identically because the instance is *not* passed in. It is grouping, not coupling.

**Intuition.**
*Mechanism.* `@staticmethod` suppresses the automatic first argument entirely. So `d.human_years(d.age)` does *not* secretly pass `d` — unlike a normal method, where `d.bark()` becomes `Dog.bark(d)`. A staticmethod is exactly the function you wrote, reachable via the class's namespace. The three method kinds differ only in that hidden first argument: an instance method gets the instance (`self`), a classmethod gets the class (`cls`), a staticmethod gets nothing.

*Concrete bite.* That "nothing extra" is the cost — a staticmethod has no `self`, so reaching for instance state inside one fails:

```python run
class Dog:
    def __init__(self, age):
        self.age = age

    @staticmethod
    def human_years():
        return self.age * 7    # BUG: a staticmethod has no self

print(Dog(3).human_years())
```
```
Traceback (most recent call last):
  File "/w/main.py", line 9, in <module>
    print(Dog(3).human_years())
          ~~~~~~~~~~~~~~~~~~^^
  File "/w/main.py", line 7, in human_years
    return self.age * 7    # BUG: a staticmethod has no self
           ^^^^
NameError: name 'self' is not defined
```

Inside `human_years` there is no `self` — the decorator stripped it — so `self.age` is an undefined name. A method that needs the instance must be a regular method (or a classmethod for the class); `@staticmethod` is only for one that needs neither.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Use `@staticmethod` for a helper that logically belongs with the class but uses no instance or class state — a small utility you want discoverable as `Dog.human_years` rather than buried among module-level functions. The cost is exactly the bite above (no access to `self`/`cls`); the judgement call is honesty — if it never needs either, a plain module function is often just as good, so reach for a staticmethod when the *grouping* genuinely aids readers.

</div>

---

## 5. Encapsulation conventions

Many languages enforce privacy with keywords. Python does not. Instead it uses *naming conventions*: a leading underscore (`_x`) means "internal, please don't touch," and a double leading underscore (`__x`) triggers *name mangling*, which makes accidental access harder — but not impossible.

```python run
class Account:
    def __init__(self, balance):
        self._balance = balance      # "internal" — convention only
        self.__secret = "pin1234"    # name-mangled

    def reveal(self):
        return self.__secret

acc = Account(100)
print(acc._balance)
print(acc.reveal())
```

**Output:**
```
100
pin1234
```

**Analysis.** `_balance` is readable from outside (`acc._balance` works) — the single underscore is purely a *signal* to other programmers, enforced by nothing. `__secret` is accessible *inside* the class via `self.__secret`, which is why `reveal()` returns `"pin1234"`. The double underscore looks stricter, and from inside the class it behaves normally. The twist is what happens from *outside*.

**Intuition.**
*Mechanism.* A leading underscore is convention only — Python attaches no special behaviour to `_balance`. A *double* leading underscore triggers name mangling: inside `class Account`, the compiler rewrites `__secret` to `_Account__secret`. References *within the class* are rewritten too, so `self.__secret` still works. But code outside the class that writes `acc.__secret` is *not* rewritten — so it looks for an attribute that does not exist under that name.

*Concrete bite.* Accessing the double-underscore name from outside fails — the real attribute is stored under its mangled name:

```python run
class Account:
    def __init__(self, balance):
        self._balance = balance
        self.__secret = "pin1234"

acc = Account(100)
print(acc.__secret)
```

**Output:**
```
Traceback (most recent call last):
  File "/w/main.py", line 7, in <module>
    print(acc.__secret)
          ^^^^^^^^^^^^
AttributeError: 'Account' object has no attribute '__secret'
```

There is no attribute literally named `__secret` — it was stored as `_Account__secret`. But this is *obfuscation, not security*: spell the mangled name yourself and it opens right up.

```python run
class Account:
    def __init__(self, balance):
        self._balance = balance
        self.__secret = "pin1234"

acc = Account(100)
print(acc._Account__secret)
print(acc.__dict__)
```

**Output:**
```
pin1234
{'_balance': 100, '_Account__secret': 'pin1234'}
```

`acc._Account__secret` returns `"pin1234"`, and `acc.__dict__` shows the mangled key in plain sight. Name mangling exists to avoid *accidental* clashes (e.g. a subclass defining its own `__secret`), not to lock data away. Nothing in Python is truly private.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Use a single leading underscore to mark "internal — not part of the public interface," and reserve double underscores for the narrow case of avoiding attribute-name collisions in subclasses. Lean on convention, not enforcement: the cost of Python's approach is that a determined caller *can* reach anything (so privacy is a social contract, not a guarantee); the benefit is that `_name` documents intent without the ceremony — and the rare maintenance escape hatch — of hard access control.

</div>

---

## 6. Mental-model summary

| Principle | Consequence |
|-----------|-------------|
| Lookup checks the instance first, then the class | A class attribute is a shared default until an instance shadows it |
| Assignment through an instance always lands on the instance | `a.species = "X"` shadows; `Dog.species` and `b` stay unchanged |
| A mutable class attribute is one shared object | `a.tricks.append(...)` is seen by `b`; put mutable state in `__init__` |
| `@classmethod` receives the class (`cls`), not an instance | Ideal for alternate constructors: `return cls(...)` builds an object |
| `@staticmethod` receives nothing extra; `_x`/`__x` are convention | Privacy is by naming, not enforcement — `__x` is only mangled, not locked |

## 7. Gotcha checklist

<div style="border-left:4px solid #da5233;background:rgba(218,82,51,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

- **Editing `instance.attr` "didn't change the class" →** assignment through an instance shadows, never mutates the class attribute; assign to `Cls.attr` if you truly mean the shared one.
- **One instance's list change appears on all instances →** it is a mutable *class* attribute (one shared object); move it into `__init__` as `self.x = []`.
- **Inside a `@classmethod`, `cls(...)` confuses you →** `cls` *is* the class, so `cls(...)` builds an instance (it is the alternate-constructor idiom).
- **`AttributeError` on a `__double` name from outside →** it was name-mangled to `_ClassName__name`; that is expected, not a bug.
- **Treating `__x` as truly private →** it is obfuscation only — `obj._ClassName__x` still works; Python encapsulates by convention (`_x`), not enforcement.

</div>

---

<div style="border-left:4px solid #6d28d9;background:rgba(109,40,217,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

🧪 **Predict, then check.** Define `class Counter:` with a class attribute `count = 0` and an `__init__` that does `Counter.count += 1`. Predict `Counter.count` after building three `Counter()` instances, and explain why `self.count += 1` would behave differently (hint: read-then-shadow). Then give a class a class attribute `log = []`, append to it from two instances, and predict whether the second instance sees the first's entry — and the one-line `__init__` fix. Two predictions that pin down shared-vs-shadowed and the mutable trap.

</div>

## Your Turn

Before you move on, check your understanding with the coach — explain the idea, apply it, weigh the trade-offs, then defend your reasoning.

<div class="concept-coach"></div>
