---
title: The Object Model
summary: Everything in Python is an object, and names are just labels bound to objects — so assignment never copies. The deep pass that makes is vs ==, mutability, aliasing, shallow vs deep copy, argument passing, and the None/True/False singletons all predictable.
prereqs: []
---

# The Object Model — Why Assignment Never Copies

The single most clarifying idea in Python: **everything is an object, and variables are just names bound to objects.** Once this clicks, a whole category of "weird" behavior — aliasing bugs, mutable-default traps, copy surprises, `is` vs `==` confusion — stops being weird and becomes predictable. This is the foundation the rest of the language sits on.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **The core idea.**

- An object lives in memory.
- A name is a label pointing at an object.
- Assignment points a name at an object — it **never copies** the object.

</div>

This is the deep pass of [Variables & Basic Types](/synapse/programming-languages/python/first-steps/variables-and-types) and the identity/truthiness ideas from [Booleans, Comparisons & Logic](/synapse/programming-languages/python/control-flow/booleans-and-logic) — it assumes you've met both and now asks *what is actually happening in memory*. The aliasing trap previewed in [Lists, the Basics](/synapse/programming-languages/python/control-flow/lists-the-basics) gets its full explanation here. Every output below was produced by running the code.

<div style="border-left:4px solid #15448e;background:rgba(21,68,142,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

📘 **How to read the Intuition boxes.** Each one is built in three moves:

1. **The mechanism** — what the interpreter is *actually doing*.
2. **A concrete bite** — a specific, runnable way the naive assumption fails.
3. **The earned rule** — the decision heuristic, now justified rather than asserted, plus its cost.

</div>

---

## Table of Contents

1. [Names are not variables](#1-names-are-not-variables)
2. [Identity vs equality: `is` vs `==`](#2-identity-vs-equality-is-vs-)
3. [Mutability: the great divide](#3-mutability-the-great-divide)
4. [Aliasing — the bug this all prevents](#4-aliasing--the-bug-this-all-prevents)
5. [Copying: assignment vs shallow vs deep](#5-copying-assignment-vs-shallow-vs-deep)
6. [How arguments are passed](#6-how-arguments-are-passed)
7. [Singletons: `None`, `True`, `False`](#7-singletons-none-true-false)
8. [Mental-model summary](#8-mental-model-summary)

---

## 1. Names are not variables

In many languages a variable is a *box* that holds a value; assignment copies the value into the box. **Python is not like that.** In Python:

> An **object** lives in memory. A **name** is a label pointing at an object. Assignment makes a name point at an object — it never copies the object.

```python run viz=array:a
a = [1, 2, 3]   # create a list object; point name 'a' at it
b = a           # point name 'b' at the SAME object (no copy!)
b.append(4)     # mutate that one object
print(a)
```

**Output:**
```
[1, 2, 3, 4]
```

**Analysis.** `b = a` did not copy the list. It made `b` a second label on the *same* object. So `b.append(4)` and `a` see the identical change — there's only one list, with two names.

**Intuition.**
*Mechanism.* The `=` operator does exactly one thing: it binds a name to whatever object is on the right. It never inspects, copies, or clones that object. After `b = a`, the names `a` and `b` are two labels tied to one object in memory; there is no second list anywhere.

*Concrete bite.* This is the source of the classic "shared default" corruption:

```python run viz=hashmap:DEFAULTS
DEFAULTS = {"retries": 3}
user = DEFAULTS          # alias, NOT a copy
user["retries"] = 99     # you think you're editing 'user'...
print(DEFAULTS)          # you edited the shared original
```

**Output:**
```
{'retries': 99}
```

You meant to give `user` its own settings and instead mutated the program-wide defaults, because `user = DEFAULTS` never made a second dict. Every later caller now reads `retries == 99`.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Treat `=` as "attach a label," never "make a copy." When you actually need an independent object — anything you'll mutate without disturbing the source — you must copy *deliberately* (`dict(d)`, `list(x)`, `x[:]`, or `copy.deepcopy`; see §5). The cost of forgetting isn't a crash — it's silent shared state, the hardest kind of bug to find.

</div>

---

## 2. Identity vs equality: `is` vs `==`

Two different questions you can ask about objects:

- `==` asks **"are these equal in value?"** (calls `__eq__`)
- `is` asks **"are these the literally same object?"** (compares identity — memory address, via `id()`)

```python run
x = [1, 2]
y = [1, 2]      # a separate list that happens to be equal
z = x           # the same object as x

print(x == y)   # equal values?
print(x is y)   # same object?
print(x is z)   # same object?
```

**Output:**
```
True
False
True
```

**Analysis.** `x` and `y` hold equal *values*, so `==` is `True` — but they're two distinct objects in memory, so `is` is `False`. `z` is the same object as `x` (from `z = x`), so `x is z` is `True`. Identity is about *which object*; equality is about *what value*.

### The `is` trap with numbers and strings

```python run
print(256 is 256)
```

**Output:**
```
True
```

Python also emits a warning to stderr, because comparing a literal with `is` is almost always a mistake:

```
/w/main.py:1: SyntaxWarning: "is" with 'int' literal. Did you mean "=="?
  print(256 is 256)
```

**Analysis.** CPython *caches* small integers (−5 to 256) and some short strings, so `is` may *accidentally* return `True` for them — but this is an implementation detail you must never rely on. `1000 is 1000` might be `True` in one context and `False` in another. Python itself warns you here, exactly because the answer is an accident of the cache rather than something the language guarantees.

**Intuition.**
*Mechanism.* `==` and `is` ask the interpreter to do two fundamentally different things. `x == None` is **not** a primitive comparison — it's a disguised *method call*, rewritten as roughly `x.__eq__(None)`, and `__eq__` is ordinary code any class may define however it likes. So `==`'s answer is decided by the object on the left. `x is None` calls *no* method: it compares object identity directly — "is `x` bound to the one and only `None` object?" — a raw check the interpreter performs itself, which nothing can override.

*Concrete bite.* An object can therefore make `==` lie, while `is` stays truthful:

```python run
class Sneaky:
    def __eq__(self, other):
        return True        # claims to equal everything

s = Sneaky()
print(s == None)    # True   <- the object lied
print(s is None)    # False  <- reality
```

**Output:**
```
True
False
```

And the famous real-world version is numerical code, where `==` doesn't even return a bool (this needs `numpy`, so it's shown rather than run here):

```python
import numpy as np
arr = np.array([1, 2, 3])
arr == None      # array([False, False, False])  <- element-wise!
if arr == None:  # ValueError: truth value of an array is ambiguous
    ...
arr is None      # False  <- correct and safe
```

`float('nan')` breaks `==` from the other side — it isn't even equal to itself (`nan == nan` is `False`), yet `nan is nan` is `True`.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** "`is None`, never `== None`" isn't style — it's choosing the comparison that *can't be hijacked*. Use `is` for the three singletons (`None`, `True`, `False`), where you mean "literally *this* object"; reserve `==` for "equal in value," where routing through `__eq__` is the whole point. Corollary: never use `is` on numbers or strings (Python warns you), because the caching that makes it *sometimes* work is an implementation accident.

</div>

---

## 3. Mutability: the great divide

Every Python object is either **mutable** (can be changed in place) or **immutable** (cannot). This single property explains most of the type system's behavior.

| Immutable | Mutable |
|-----------|---------|
| `int`, `float`, `bool`, `complex` | `list` |
| `str` | `dict` |
| `tuple`, `frozenset` | `set` |
| `bytes`, `None` | `bytearray`, most custom objects |

```python run
s = "hello"
try:
    s[0] = "H"          # try to mutate a string in place
except TypeError as e:
    print("TypeError:", e)

s2 = s.upper()          # methods return a NEW object instead
print(s)                # original untouched
print(s2)
```

**Output:**
```
TypeError: 'str' object does not support item assignment
hello
HELLO
```

**Analysis.** Strings are immutable — there is no way to change one in place, so `s[0] = "H"` raises. String "modification" methods like `.upper()`, `.replace()`, `.strip()` always return a *brand-new* string and leave the original alone. Lists, by contrast, *can* be changed in place (`.append`, item assignment).

**Intuition.**
*Mechanism.* For an immutable object there is no operation that alters its value — so any syntax that *looks* like mutation must instead build a new object and rebind the name. Watch `+=` on an int, which feels in-place but isn't:

```python run
x = 5
y = x      # both names point at the int 5
x += 1     # does NOT change 5; builds a new int 6 and rebinds x
print(x, y)   # y still sees the original 5
```

**Output:**
```
6 5
```

`y` is untouched precisely because `x += 1` couldn't modify the shared `5`; it created a separate `6`. (Contrast a list, where `x.append(...)` *does* change the shared object, so an aliased `y` would see it — §4.)

*Concrete bite.* Immutability is why naïve string-building is a performance trap. Each `+=` on a string can't extend the existing one — it allocates a *new* string and copies everything so far (`pieces` stands for your data):

```python
s = ""
for chunk in pieces:          # N pieces
    s += chunk                # step k copies k characters
```

That's `1 + 2 + ... + N` ≈ **O(N²)** character copies — a loop that's instant for 1,000 pieces and crawls for 1,000,000. The mutable-buffer alternative does O(N) work:

```python
parts = []
for chunk in pieces:
    parts.append(chunk)       # O(1) each
result = "".join(parts)       # one pass, O(N)
```

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Immutable means "value fixed for life; 'editing' makes a new object." So accumulate with a mutable buffer and convert once — `parts = []; parts.append(chunk); "".join(parts)` — turning O(N²) into O(N). And choose *immutable* types when you need a value that's safe to share freely or to use as a dict key / set member (§5, and [Dictionaries & Sets](/synapse/programming-languages/python/working-with-data/dictionaries-and-sets)), since nothing can mutate it out from under you.

</div>

---

## 4. Aliasing — the bug this all prevents

Combine §1 (names don't copy) with §3 (some objects mutate), and you get **aliasing**: two names on one mutable object, where a change through one is visible through the other.

```python run viz=grid:original
original = [[1, 2], [3, 4]]
assigned = original                 # same object (alias)
original[0].append(99)

print(original)
print(assigned)                     # sees the change too
```

**Output:**
```
[[1, 2, 99], [3, 4]]
[[1, 2, 99], [3, 4]]
```

**Analysis.** `assigned = original` created an alias, not a copy. Mutating the inner list through `original` is visible through `assigned`, because both names point at the one outer list (whose first element is the one inner list).

**Intuition.**
*Mechanism.* Aliasing isn't a special feature — it's the unavoidable consequence of "names bind objects" (§1) meeting "objects can mutate" (§3). When two names reference one mutable object, there is no "copy" to protect either view; both are windows onto the same memory.

*Concrete bite.* The sharpest version is the "list times N" matrix, which looks like it builds a grid of independent rows but doesn't:

```python run viz=grid:board
board = [[0] * 3] * 3     # the OUTER list holds three refs to ONE inner list
board[0][0] = 1
print(board)              # one edit hit "every row"
```

**Output:**
```
[[1, 0, 0], [1, 0, 0], [1, 0, 0]]
```

`[inner] * 3` doesn't make three lists — it makes three references to the single `inner`. Setting `board[0][0]` mutates that one shared list, so it appears in "all three rows." People lose hours to this exact bug.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Whenever you have a mutable object reachable by more than one name (including elements built by `*` repetition, or an argument passed into a function), assume a change through any path is visible through all of them — and copy deliberately if you need isolation. The correct grid is a [comprehension](/synapse/programming-languages/python/working-with-data/comprehensions) that builds a fresh inner list each time: `[[0] * 3 for _ in range(3)]`. Knowing *which* kind of copy you need is the next section.

</div>

---

## 5. Copying: assignment vs shallow vs deep

There are three distinct levels of "copy," and confusing them causes real bugs.

```python run
import copy

original = [[1, 2], [3, 4]]

assigned = original             # NOT a copy — same object
shallow  = copy.copy(original)  # new outer list, SAME inner lists
deep     = copy.deepcopy(original)  # new outer AND new inner lists

original[0].append(99)          # mutate an inner list

print("original:", original)
print("assigned:", assigned)    # same object -> sees it
print("shallow: ", shallow)     # shares inner lists -> sees it
print("deep:    ", deep)        # fully independent -> does NOT
```

**Output:**
```
original: [[1, 2, 99], [3, 4]]
assigned: [[1, 2, 99], [3, 4]]
shallow:  [[1, 2, 99], [3, 4]]
deep:     [[1, 2], [3, 4]]
```

The three depths map onto memory like this — `assigned` and `shallow` both still reach the *original* inner lists, while only `deep` gets its own:

```d2
direction: right

original: "original" { shape: oval }
assigned: "assigned" { shape: oval }
shallow: "shallow" { shape: oval }
deep: "deep" { shape: oval }

outer1: "outer list" { shape: rectangle }
outer2: "new outer (deep)" { shape: rectangle }

inner1: "[1, 2]" { shape: rectangle }
inner2: "[3, 4]" { shape: rectangle }
copy1: "[1, 2] copy" { shape: rectangle }
copy2: "[3, 4] copy" { shape: rectangle }

original -> outer1
assigned -> outer1: "alias"
shallow -> outer1: "new outer,\nshared inners"
deep -> outer2

outer1 -> inner1
outer1 -> inner2
outer2 -> copy1
outer2 -> copy2
```

**Analysis.** Three different behaviors:
- **Assignment** (`assigned = original`): no copy at all; same object; sees every change.
- **Shallow copy** (`copy.copy`, also `list(x)`, `x[:]`, `dict(x)`): makes a new *outer* container, but its elements are the *same* inner objects. So mutating a shared inner list shows up in the shallow copy.
- **Deep copy** (`copy.deepcopy`): recursively copies the outer container *and* everything nested inside, producing a fully independent clone.

**Intuition.**
*Mechanism.* A shallow copy duplicates exactly one layer — the outer container — and then *reuses the same references* for everything inside it. So `shallow` is a genuinely new list, but `shallow[0]` and `original[0]` are the *same* inner list object. Deep copy recursively rebuilds every nested object, so nothing is shared at any level.

*Concrete bite.* This is the §4 matrix bug wearing a disguise: people "fix" it with a copy and pick the wrong depth.

```python run
import copy
template = [[0, 0], [0, 0]]
grid = copy.copy(template)     # NEW outer list... but SAME two inner lists
grid[0][0] = 9
print(template)                # original mutated anyway!
```

**Output:**
```
[[9, 0], [0, 0]]
```

The shallow copy gave a new outer list while still sharing the inner rows, so editing `grid` corrupted `template`. Only `copy.deepcopy(template)` (or rebuilding inner lists) isolates them.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Match copy depth to structure. **Flat** data (a list of numbers/strings, a dict of scalars)? Shallow is correct and cheap — `list(x)`, `x[:]`, `dict(x)`. **Nested** data you'll mutate independently? You need `deepcopy`. The tradeoff is real: `deepcopy` walks the entire object graph and is correspondingly slow, so don't reach for it reflexively — reach for it precisely when nested-mutation independence matters.

</div>

---

## 6. How arguments are passed

Python's argument passing is often mislabeled "pass by value" or "pass by reference." It's neither — it's **pass by object reference** (a.k.a. "call by sharing"): the function receives a *new name bound to the same object* as the caller's.

The practical consequence depends entirely on whether you **mutate** the object or **rebind** the name:

```python run viz=array:data
def mutate(lst):
    lst.append("X")     # mutates the object the caller passed

def rebind(lst):
    lst = ["new"]       # rebinds the LOCAL name only

data = [1, 2]

mutate(data)
print("after mutate:", data)    # caller's object changed

rebind(data)
print("after rebind:", data)    # caller's object UNchanged
```

**Output:**
```
after mutate: [1, 2, 'X']
after rebind: [1, 2, 'X']
```

**Analysis.** Inside `mutate`, the parameter `lst` is a second name for the caller's list; `.append` changes that shared object, so the caller sees it. Inside `rebind`, `lst = ["new"]` makes the *local* name `lst` point at a brand-new list — it does **not** affect what the caller's `data` points to. So after `rebind`, `data` is unchanged (still `[1, 2, 'X']` from the earlier mutate).

**Intuition.**
*Mechanism.* Calling `f(data)` runs an invisible `lst = data` — the parameter becomes another name for the *same* object (§1), not a copy of it. From there the §3/§4 rules apply across the function boundary: **mutating** reaches through the shared reference to the one object (caller sees it); **rebinding** just repoints the local name (caller does not).

*Concrete bite.* This makes "helper" functions that touch their arguments quietly dangerous:

```python run viz=array:data
def top_three(scores):
    scores.sort(reverse=True)   # sorts IN PLACE — mutates the caller's list
    return scores[:3]

data = [3, 1, 4, 1, 5]
top_three(data)
print(data)        # caller's list got reordered as a side effect
```

**Output:**
```
[5, 4, 3, 1, 1]
```

The caller just wanted the top three and unknowingly had their original list permanently reordered, because `.sort()` mutated the shared object.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** A function that *mutates* an argument changes the caller's world; a function that *rebinds* a parameter does not. Default to **not** mutating inputs — compute and `return` a new object (`sorted(scores)` instead of `scores.sort()`), or copy at the top if you must mutate locally. When a function genuinely is meant to mutate (like `list.sort` itself), make that obvious in its name and docs. This is also exactly why mutable default arguments are a trap (see [Functions in Depth](/synapse/programming-languages/python/how-python-works/functions-in-depth)).

</div>

---

## 7. Singletons: `None`, `True`, `False`

Some objects exist exactly *once* in a running program — there is only ever one `None` object. These are **singletons**.

```python run
n = None
print(n is None)        # the canonical identity check

a = None
b = None
print(a is b)           # both names point at the one None object
```

**Output:**
```
True
True
```

**Analysis.** There is a single `None` object in the entire interpreter; every `None` you write refers to that one object. So `is None` is both correct and fast (a pointer comparison, no `__eq__` call). The same is true for `True` and `False`.

**Intuition.**
*Mechanism.* Because there's exactly one `None` object, "is this value missing?" is literally "is this name pointing at *that* object?" — an identity check `is None` answers with a single pointer comparison, no method call involved (§2). It's unambiguous and impossible to override.

*Concrete bite.* The trap is conflating "is `None`" with "is falsy," usually via `or`. They are not the same, because `0`, `""`, `[]`, and `False` are all falsy but are *legitimate values*, not absence:

```python run
def make_request(timeout=None):
    timeout = timeout or 30      # BUG: 0 is falsy, so it becomes 30
    return timeout

print(make_request(0))   # caller asked for "no timeout", got 30 instead!

def fixed(timeout=None):
    if timeout is None:          # only true absence triggers the default
        timeout = 30
    return timeout

print(fixed(0))          # correct
```

**Output:**
```
30
0
```

`timeout or 30` silently overrides a deliberate `0`; `if timeout is None` distinguishes "the caller passed nothing" from "the caller passed a falsy value." (This is the deep version of the truthiness rules from [Booleans, Comparisons & Logic](/synapse/programming-languages/python/control-flow/booleans-and-logic).)

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Use `is` for the three singletons (`None`, `True`, `False`) whenever you mean "literally this object" — it's the one place `is` is unequivocally correct, and it's why the idiom is `if x is None`, not `== None` or `if not x`. Reserve truthiness (`if not x`) for when you really do mean "empty or zero or false," and reach for `is None` when you mean "no value was supplied." Mixing the two is one of the most common real bugs in Python.

</div>

---

## 8. Mental-model summary

Everything above is generated by a handful of core facts:

| Principle | Consequence |
|-----------|-------------|
| Objects live in memory; **names are labels** pointing at them | Assignment binds names, never copies objects |
| `==` compares **value**; `is` compares **identity** | Use `==` for values; `is` only for singletons like `None` |
| Objects are **mutable or immutable** | Immutable "changes" make new objects; mutable ones change in place |
| Two names on one mutable object = **aliasing** | Change through one name is seen through the other |
| Copies come in three depths | Assignment (none) → shallow (top layer) → deep (everything) |
| Functions get a **copy of the reference** | Mutating an argument is visible to the caller; rebinding it is not |
| `None`/`True`/`False` are **singletons** | `is None` is the correct, fast "no value" check |

### Gotcha checklist

<div style="border-left:4px solid #da5233;background:rgba(218,82,51,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

- **Expecting `b = a` to copy a list →** it's an alias; use `a[:]`, `list(a)`, or `copy.deepcopy`.
- **Using `is` to compare numbers or strings →** use `==`; `is` is only for identity/singletons (Python warns you).
- **Shallow-copying a nested structure and mutating an inner element →** inner objects are shared; use `deepcopy`.
- **`[[0] * 3] * 3` →** three refs to one inner list; use `[[0] * 3 for _ in range(3)]`.
- **A function unexpectedly changing the caller's list →** it mutated the shared object; return a new one instead.
- **`if x == None` →** write `if x is None`; and `x or default` silently overrides falsy values like `0`/`""`.

</div>

---

<div style="border-left:4px solid #6d28d9;background:rgba(109,40,217,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

🧪 **Predict, then check.** Retype the §5 copy example and predict each of the four outputs before running — the moment you can explain why `shallow` sees the change but `deep` doesn't, you own Python's memory model. Next comes [Iterators & Generators](/synapse/programming-languages/python/how-python-works/iterators-and-generators), where the same "object, not a box" lens explains lazy evaluation.

</div>

## Your Turn

Before you move on, check your understanding with the coach — explain the idea, apply it, weigh the trade-offs, then defend your reasoning.

<div class="concept-coach"></div>
