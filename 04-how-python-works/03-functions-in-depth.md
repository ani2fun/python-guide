---
title: Functions in Depth
summary: A function is a first-class value — an object you can name, store, pass, and return — and almost every advanced feature is a consequence of that one fact. Covers *args/**kwargs, the mutable-default trap, LEGB scope & closures, lambdas & late binding, map/filter/key=, recursion, decorators, the functools toolkit, and purity.
prereqs: []
---

# Functions in Depth — A Function Is a Value

Most of what looks like a grab-bag of "advanced function features" — lambdas, closures, decorators, higher-order functions — is really *one idea* seen from different angles: **in Python a function is a value**, a first-class object like `5` or `"hello"`. Internalize that and the rest stops being a list of syntax to memorize and becomes a set of *consequences*.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **The core idea.**

- Lambdas, closures, and decorators look like a grab-bag of features.
- Really they are **one idea**: a function is a **value**, a first-class object like `5` or `"hello"`.
- Master that and the rest becomes a set of *consequences*.

</div>

This is the deep pass of [Functions, the Basics](/synapse/programming-languages/python/control-flow/functions-the-basics) — it assumes you've met `def`, `return`, and parameters, and pushes into the object nature of functions, scope, closures, decorators, and purity. It builds directly on [The Object Model](/synapse/programming-languages/python/how-python-works/the-object-model) (functions are objects with attributes) and on the generator expressions from [Comprehensions](/synapse/programming-languages/python/working-with-data/comprehensions). Every output below was produced by running the code.

<div style="border-left:4px solid #15448e;background:rgba(21,68,142,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

📘 **How to read the Intuition boxes.** Each one is built in three moves:

1. **The mechanism** — what the interpreter is *actually doing*.
2. **A concrete bite** — a specific, runnable way the naive assumption fails.
3. **The earned rule** — the decision heuristic, now justified rather than asserted, plus its cost.

</div>

---

## Table of Contents

- [Functions in Depth — A Function Is a Value](#functions-in-depth--a-function-is-a-value)
  - [Table of Contents](#table-of-contents)
  - [1. What a function actually is](#1-what-a-function-actually-is)
  - [2. Parameters, return, and None](#2-parameters-return-and-none)
  - [3. Arguments: positional, keyword, defaults](#3-arguments-positional-keyword-defaults)
  - [4. The mutable default argument trap](#4-the-mutable-default-argument-trap)
  - [5. `*args` and `**kwargs` (and call-site unpacking)](#5-args-and-kwargs-and-call-site-unpacking)
    - [In a definition: collect extras](#in-a-definition-collect-extras)
    - [At a call: spread out](#at-a-call-spread-out)
  - [6. Returning multiple values](#6-returning-multiple-values)
  - [7. Scope: LEGB, `global`, `nonlocal`](#7-scope-legb-global-nonlocal)
    - [Reading is a search. Assigning is local.](#reading-is-a-search-assigning-is-local)
    - [`nonlocal`: update what a closure remembers](#nonlocal-update-what-a-closure-remembers)
    - [Rebinding is not mutating](#rebinding-is-not-mutating)
  - [8. Docstrings, annotations, introspection](#8-docstrings-annotations-introspection)
  - [9. First-class and higher-order functions](#9-first-class-and-higher-order-functions)
  - [10. Lambdas and the late-binding trap](#10-lambdas-and-the-late-binding-trap)
  - [The late-binding trap](#the-late-binding-trap)
    - [It is not about loops](#it-is-not-about-loops)
    - [It is not about `lambda` either](#it-is-not-about-lambda-either)
    - [Proving they share one variable](#proving-they-share-one-variable)
    - [When it does *not* bite](#when-it-does-not-bite)
    - [A comprehension's private scope will not save you](#a-comprehensions-private-scope-will-not-save-you)
    - [Forcing an early snapshot](#forcing-an-early-snapshot)
  - [11. Closures](#11-closures)
  - [12. `map`, `filter`, `reduce`, and `key=`](#12-map-filter-reduce-and-key)
    - [`key=` in `sorted`, `min`, `max`](#key-in-sorted-min-max)
  - [13. Recursion](#13-recursion)
  - [14. Keyword-only and positional-only parameters](#14-keyword-only-and-positional-only-parameters)
  - [15. Decorators](#15-decorators)
    - [Basic decorator](#basic-decorator)
    - [Decorator that takes arguments](#decorator-that-takes-arguments)
    - [Stacking](#stacking)
  - [16. Generators and `yield`](#16-generators-and-yield)
    - [Why it matters: laziness and memory](#why-it-matters-laziness-and-memory)
  - [17. The `functools` toolkit](#17-the-functools-toolkit)
    - [`partial` — pre-fill arguments](#partial--pre-fill-arguments)
    - [`lru_cache` — memoization for free](#lru_cache--memoization-for-free)
  - [18. Pure functions and side effects](#18-pure-functions-and-side-effects)
  - [19. Mental-model summary](#19-mental-model-summary)
    - [Gotcha checklist](#gotcha-checklist)
  - [Your Turn](#your-turn)

---

## 1. What a function actually is

Before any syntax, the idea everything else hangs on: **a function is a value.** `def` does not declare something that lives in a separate world from your data — it builds an ordinary object and points a name at it. The name and the object are two different things, and four lines are enough to prove it:

```python run
def double(x):
    return x * 2

print(double)              # the object itself — no call, no parentheses
print(type(double))
alias = double             # bind a SECOND name to the SAME object
print(alias is double)     # not a copy: one object, two names
del double                 # drop the original name
print(alias(21))           # the object is alive and well without it
```

**Output (illustrative — the address varies per run):**
```
<function double at 0x7fc103ccf1a0>
<class 'function'>
True
42
```

**Analysis.** `def double(...)` does two things stapled together: it *builds a function object*, then *binds the name* `double` to it. `alias = double` binds a second name to that same object — `alias is double` is `True`, so nothing was copied. Then `del double` removes the original name, and the object doesn't notice: `alias(21)` still runs the same body. Names are labels; the function is the thing they're stuck to.

Once a function is just a value, it can go wherever a value goes — including into a dict, which turns a chain of `if`/`elif` into a lookup:

```python run viz=hashmap:ops
ops = {"+": lambda a, b: a + b,
       "-": lambda a, b: a - b}
print(ops["+"](3, 4))     # the function was stored in a dict and looked up by key
```

**Output:**
```
7
```

The functions sit in that dict exactly like the strings and ints you would normally store there. `ops["+"]` retrieves one and `(3, 4)` calls it — no `if op == "+"` ladder required.

**Intuition.**

*Mechanism.* `def` is not a declaration that the interpreter collects ahead of time. It is an ordinary **statement that executes** when control reaches it, constructing a function object and binding a name to it. That is why you can put a `def` inside an `if`, rebind the name afterwards, or build functions in a loop — and why the interpreter knows nothing whatsoever about a function until its `def` line has run.

*Concrete bite.* The tempting mental model — "the file is scanned first, so definitions are available everywhere" — fails the instant you call above the `def`:

```python run
print(greet("world"))       # the def below has not executed yet


def greet(name):
    return f"Hello, {name}"
```

**Output:**
```
Traceback (most recent call last):
  File "/w/main.py", line 1, in <module>
    print(greet("world"))       # the def below has not executed yet
          ^^^^^
NameError: name 'greet' is not defined
```

Nothing is wrong with the function. The `def` simply had not run yet, so no name had been bound. Move the call below the definition and it works — the only thing that changed is whether the binding statement had executed.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Internalize "a function is a value" and the rest of this lesson stops being a feature list and becomes a set of *consequences*: lambdas are nameless function values (§10), closures are functions carrying state (§11), decorators are functions that transform functions (§15), higher-order functions are just functions that take or return them (§9). The immediate practical payoff: when you catch yourself writing a long `if`/`elif` over a fixed set of cases, reach for a dict of functions instead.

</div>

---

## 2. Parameters, return, and None

A function talks to the outside world through two channels that beginners routinely merge into one. Keeping them apart is the whole of this section.

```python run
def greet(name):
    return f"Hello, {name}"

def shout(name):
    print(f"HELLO {name}")   # prints, but returns nothing

a = greet("Aniket")
b = shout("Aniket")
print(a)
print(b)
```

**Output:**
```
HELLO Aniket
Hello, Aniket
None
```

**Analysis.** `greet` *returns* a string; `shout` *prints* one and falls off the end. A function with no `return` returns `None` implicitly — which is why `b` is `None` rather than the text you just watched appear on screen.

The output order is worth a second look, because it surprises people. `HELLO Aniket` lands *first*, above `Hello, Aniket`, even though its `print` sits lower in the source. The call `shout("Aniket")` executes on the line that assigns `b` — two lines before `print(a)` runs. Output appears in the order statements *execute*, not the order `print` calls appear on the page.

Those three ways of producing `None` are all the same thing:

```python run
def implicit():
    pass                # falls off the end


def bare():
    return              # a bare return


def explicit():
    return None


print(implicit(), bare(), explicit())
print(implicit() is bare() is explicit() is None)
```

**Output:**
```
None None None
True
```

To a caller they are indistinguishable. So a bare `return` is not a way of returning "nothing" — it is an early exit that happens to hand back `None`, exactly like reaching the end of the body would.

**Intuition.**

*Mechanism.* `return` hands a value back to the *calling expression*; `print` writes text to standard output and itself evaluates to `None`. They are orthogonal channels — one talks to your program, the other talks to a human reading the terminal. Every function produces a value on the first channel whether you write `return` or not.

*Concrete bite.* Merging the two channels loses data you were certain you had:

```python run
def make_total(items):
    print(sum(items))      # prints, returns None

total = make_total([1, 2, 3])   # prints 6...
print(total * 2)
```

**Output:**
```
6
Traceback (most recent call last):
  File "/w/main.py", line 5, in <module>
    print(total * 2)
          ~~~~~~^~~
TypeError: unsupported operand type(s) for *: 'NoneType' and 'int'
```

You watch `6` appear and conclude that `total` is `6`. It isn't — `make_total` *displayed* 6 and *returned* `None`. Note where the program actually dies: one line downstream of the mistake, on code that is perfectly correct. That gap between the faulty line and the crashing line is what makes this bug feel mysterious.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Keep "show a human" (`print`) and "give the caller a value" (`return`) strictly separate. If any other part of your code needs the result, `return` it — printing is for display and debugging only. A useful smell test: if deleting every `print` from a function would break the code that calls it, the function is using the wrong channel.

</div>

---

## 3. Arguments: positional, keyword, defaults

Parameters are named in the definition; **arguments** are the values supplied at the call. Python offers three ways to match one to the other.

```python run
def describe(name, age, city="Unknown"):
    return f"{name}, {age}, from {city}"


print(describe("Alice", 30))                    # positional — matched by order
print(describe("Bob", age=25))                  # keyword — matched by name
print(describe(age=40, name="Carol"))           # keyword — so order stops mattering
print(describe("Dave", 28, city="Berlin"))      # override the default

# print(describe(name="Eve", 31))
# SyntaxError: positional argument follows keyword argument
```

**Output:**
```
Alice, 30, from Unknown
Bob, 25, from Unknown
Carol, 40, from Unknown
Dave, 28, from Berlin
```

**Analysis.** *Positional* arguments bind by order, *keyword* arguments bind by name, and *defaults* fill in for anything the caller omits. The two ordering rules — positional before keyword at the call, non-defaulted before defaulted in the definition — are not style preferences; they are what makes the matching unambiguous. Break the first one and you get the commented-out `SyntaxError` above, refused at compile time rather than guessed at.

**Intuition.**

*Mechanism.* Python matches arguments to parameters in one pass: positional values are consumed left to right, keyword values are then dropped into the parameters they name, and any parameter still empty falls back to its default. A parameter that ends up with nothing at all is a `TypeError`. Because keywords carry their own destination, they are order-free — the price is that once you start naming, you cannot go back to relying on position.

*Concrete bite.* Bare positional values are not just hard to read; they fail *silently*, which is worse:

```python run
def create_user(name, admin=False, active=True, verified=False):
    return f"{name}: admin={admin} active={active} verified={verified}"


print(create_user("Ada", True, False, True))                          # what are these three?
print(create_user("Ada", admin=True, active=False, verified=True))    # identical, and legible
print(create_user("Ada", False, True, True))                          # two flags swapped — no error at all
```

**Output:**
```
Ada: admin=True active=False verified=True
Ada: admin=True active=False verified=True
Ada: admin=False active=True verified=True
```

The first two calls are the same call written two ways. The third has two booleans transposed — a plausible typo — and Python accepts it without a murmur, quietly creating a non-admin user where you asked for an admin. There is no error to catch, no traceback to read; only wrong data, discovered later. Keyword arguments make that class of mistake impossible to write.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Pass positionally only when the meaning is obvious from context and the order is conventional (`point(x, y)`, `replace(old, new)`); switch to keywords the moment a bare value would be cryptic — above all for booleans and option flags, where a transposition costs you nothing at the call site and everything at runtime. Encode "what most callers want" as a default so callers only spell out the unusual. And when you want to *force* that clarity on everyone calling your function, make the parameters keyword-only (§14).

</div>

---

## 4. The mutable default argument trap

This is the single most famous Python footgun, and it is a direct consequence of §1: `def` is a statement that **executes**, and it executes *once*. Anything you write after an `=` in the parameter list is evaluated right there, as part of that one execution. Predict the output before reading it.

```python run viz=array:bucket
def add_item(x, bucket=[]):
    bucket.append(x)
    return bucket

print(add_item(1))
print(add_item(2))
print(add_item(3))
```

**Output:**
```
[1]
[1, 2]
[1, 2, 3]
```

**Analysis.** You almost certainly expected `[1]`, `[2]`, `[3]`. But `bucket=[]` did not mean "start each call with a fresh empty list" — it created **one** list while the `def` ran, and stored it on the function object. Every call that omits `bucket` gets handed that same list, and `.append` keeps growing it.

You can watch the timing happen rather than take it on trust. Put a `print` inside the expression that produces the default:

```python run
def stamp():
    print("stamp() ran")
    return []


def f(acc=stamp()):        # stamp() runs HERE, while the def executes
    return acc


print("the def is done — and no call has happened yet")
f()
f()
f()
print("three calls later, stamp() never ran again")
```

**Output:**
```
stamp() ran
the def is done — and no call has happened yet
three calls later, stamp() never ran again
```

`stamp() ran` prints *before* the line announcing that the `def` finished, and never appears again no matter how often `f` is called. Defaults are computed once, at definition time — full stop.

Note that the trap needs **two** ingredients: a default that is mutable, *and* code that mutates it. `def greet(name, prefix="Hi")` is a mutable-looking default that is in fact a string, and immune; `def f(acc=[])` that only ever *reads* `acc` is harmless too. It is the `.append` that turns the shared object into shared state.

**The fix** — use `None` as a sentinel and build the real default inside the body, where it is evaluated on every call:

```python run
def add_item(x, bucket=None):
    if bucket is None:
        bucket = []
    bucket.append(x)
    return bucket

print(add_item(1))   # [1]
print(add_item(2))   # [2]
```

**Output:**
```
[1]
[2]
```

**Intuition.**

*Mechanism.* Default values are evaluated **once**, when the `def` statement executes, and stored on the function object itself. `bucket=[]` therefore creates exactly one list, at definition time; every call that omits the argument is handed a reference to that one list, so mutations leak from call to call. (This is the mirror image of the lambda late-binding fix in §10. There, freezing a value at definition time is precisely the cure; here, the same freezing is the disease.)

*Concrete bite.* The shared list is not a metaphor — you can read it off the function object and watch one call corrupt it for the next:

```python run
def f(acc=[]):
    return acc

print(f.__defaults__)        # ([],)  -- the one default object
f().append("leak")
print(f.__defaults__)        # (['leak'],)  -- the stored default was mutated!
```

**Output:**
```
([],)
(['leak'],)
```

Nothing was assigned and no global was touched. A caller reached the default object through an innocent-looking `f()` and mutated the function's own stored state. Every later call that omits the argument now starts from `['leak']`.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Never use a mutable object (`[]`, `{}`, `set()`, or an instance of your own class) as a default — it is one object, created once, shared forever. Use the `None`-sentinel pattern instead: `def f(x=None): if x is None: x = []`. It costs two lines and buys a fresh object per call — plus the ability to tell "caller passed nothing" apart from "caller passed an empty list", which a bare `[]` default cannot express. Immutable defaults (`0`, `""`, `None`, `()`, and other tuples) are safe precisely because there is no way to mutate them in place.

</div>

---

## 5. `*args` and `**kwargs` (and call-site unpacking)

`*` and `**` do *opposite* jobs depending on which side of the function they appear on. One symbol, two mirror-image meanings — which is exactly why they confuse people.

### In a definition: collect extras

```python run
def collect(*args, **kwargs):
    return args, kwargs


print(collect(1, 2, a=3, b=4))
print(collect())                    # both always exist — possibly empty
print(type(collect(1)[0]), type(collect(a=1)[1]))
```

**Output:**
```
((1, 2), {'a': 3, 'b': 4})
((), {})
<class 'tuple'> <class 'dict'>
```

`args` is always a tuple and `kwargs` always a dict, even when the caller passes nothing — so you can loop over them without checking for `None` first. The names are pure convention; `*a, **kw` works identically. It is the `*` and `**` that carry the meaning.

### At a call: spread out

```python run
def add3(a, b, c):
    return a + b + c

nums = [1, 2, 3]
opts = {'a': 1, 'b': 2, 'c': 3}

print(add3(*nums))    # spread list into positional args
print(add3(**opts))   # spread dict into keyword args
```

**Output:**
```
6
6
```

**Analysis.** In a *definition*, `*args` gathers leftover positional arguments into a **tuple** and `**kwargs` gathers leftover keyword arguments into a **dict**. At a *call site*, `*` and `**` do the reverse: they **unpack** one container into many separate arguments. Same symbols, opposite directions, and the side of the function you are on is what tells you which is which.

Put the two halves together and you get a wrapper that forwards *any* signature without knowing anything about it — the backbone of every decorator in §15:

```python run
def trace(fn):
    def wrapper(*args, **kwargs):     # gather whatever comes in
        print("called with", args, kwargs)
        return fn(*args, **kwargs)    # scatter it straight into fn
    return wrapper


@trace
def add3(a, b, c):
    return a + b + c


@trace
def shout(text, times=1):
    return " ".join([text.upper() + "!"] * times)


print("returned:", add3(*[1, 2, 3]))
print("returned:", shout("hi", times=2))
```

**Output:**
```
called with (1, 2, 3) {}
returned: 6
called with ('hi',) {'times': 2}
returned: HI! HI!
```

One `wrapper` handles both functions. It never mentions `a`, `b`, `c`, `text`, or `times`; `*args, **kwargs` catch whatever arrives and re-spread it on the way through. That is why the same three-line `trace` works on functions of every shape.

**Intuition.**

*Mechanism.* Think **gather** versus **scatter**. In a definition, `*`/`**` pack many arguments into one container. At a call, `*`/`**` unpack one container back into many arguments. Critically, unpacking is driven by *iteration*: `*` iterates the object and feeds the results in positionally, while `**` walks key/value pairs and feeds them in by name.

*Concrete bite.* That "`*` just iterates" detail is where it bites, because iterating a dict yields its **keys**, not its values:

```python run
def add3(a, b, c):
    return a + b + c


opts = {'a': 1, 'b': 2, 'c': 3}
print(add3(**opts))       # ** spreads the VALUES into a, b, c
print(add3(*opts))        # * spreads the KEYS — and quietly returns nonsense
```

**Output:**
```
6
abc
```

One asterisk instead of two, and `add3` received the strings `'a'`, `'b'`, `'c'`. There is no error, because `+` happily concatenates strings — you get `'abc'` where you expected `6`, and the wrong value flows onward into the rest of your program. This is the failure mode to fear: not a traceback, but a plausible-looking answer of the wrong type.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Use `*args`/`**kwargs` in a definition when a function genuinely should accept a variable number of arguments — and resist them otherwise, because they erase the signature that documents your function and lets tools check calls. At a call site, use the unpacking form to spread a container you already have. The "gather then scatter" pair (`def w(*a, **k): return fn(*a, **k)`) is the standard idiom for any transparent wrapper, proxy, or decorator. And keep the asymmetry in mind: `**` on a dict passes its values by name, `*` on a dict passes its keys.

</div>

---

## 6. Returning multiple values

```python run
def min_max(xs):
    return min(xs), max(xs)

result = min_max([4, 1, 7, 3])
print(result)             # it's a tuple
low, high = min_max([4, 1, 7, 3])   # unpack it
print(low, high)
```

**Output:**
```
(1, 7)
1 7
```

**Analysis.** Python has no "multiple return values" feature at all. `return min(xs), max(xs)` is a single `return` of a single object — the comma builds a tuple, and one tuple goes back to the caller. What makes it *feel* like several values is what happens on the other side: assigning a tuple to a comma-separated list of names unpacks it.

That the result is an ordinary tuple is not a technicality; it is usable:

```python run
def stats(xs):
    return min(xs), max(xs), sum(xs) / len(xs)

result = stats([2, 4, 6])
print(result[1])           # 6  -- indexable, because it's just a tuple
lo, hi, avg = stats([2, 4, 6])   # or unpack into names
print(lo, hi, avg)
```

**Output:**
```
6
2 6 4.0
```

You can index it, slice it, loop over it, or pass it straight into another function with `*`. No special construct is involved anywhere.

**Intuition.**

*Mechanism.* The comma is the tuple constructor, not the parentheses — `return a, b` and `return (a, b)` compile to the same thing. So "returning two values" is really "returning one tuple", and "receiving two values" is really "unpacking one tuple". It is the same machinery that powers `for i, x in enumerate(xs)` and the swap idiom `a, b = b, a`.

*Concrete bite.* Because unpacking is a structural match, the error you get when you are wrong talks about *tuples*, not about return values:

```python run
def min_max(xs):
    return min(xs), max(xs)


low, high, avg = min_max([4, 1, 7, 3])   # asked for three names, got a 2-tuple
```

**Output:**
```
Traceback (most recent call last):
  File "/w/main.py", line 5, in <module>
    low, high, avg = min_max([4, 1, 7, 3])   # asked for three names, got a 2-tuple
    ^^^^^^^^^^^^^^
ValueError: not enough values to unpack (expected 3, got 2)
```

Read that message and you can see the whole model in it: Python is not complaining that a function returned the wrong number of things — it is complaining that a 2-element tuple would not fit into 3 names. That is also why the count is rigid: add a fourth value to a function's return and every existing unpacking call site breaks loudly, which is a feature.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Lean on this freely — `return a, b, c` with `x, y, z = f(...)` is clean, idiomatic Python. Use `first, *rest = f(...)` when you want to absorb a variable tail. But watch the count: because callers unpack by position, every extra value is a breaking change, and by the time a function returns four or five things the call site has become a puzzle of positional names. At that point return a `NamedTuple` or a small dataclass instead, so callers read fields by name and new fields break nobody.

</div>

---

## 7. Scope: LEGB, `global`, `nonlocal`

Two functions can each keep a variable called `x` without ever colliding. What keeps them apart is **scope** — the region of code in which a name is visible. When you *read* a name, Python searches four scopes in a fixed order, innermost first, and stops at the first match:

| | Scope | What lives there |
| --- | --- | --- |
| **L** | Local | names assigned inside the function currently running |
| **E** | Enclosing | the locals of any function that lexically wraps it — nested `def`s only |
| **G** | Global | names at the top level of the module |
| **B** | Built-in | the names Python always provides: `print`, `len`, `list`, … |

The search **stops at the first hit**. It never looks further out, and it never merges results from two rungs. Here is the whole ladder in one program, with a name planted deliberately at each level:

```python run
x = "global x"


def outer():
    y = "enclosing y"

    def inner():
        z = "local z"
        print(z)        # L — found immediately, search stops
        print(y)        # L? no. E? yes — outer's local
        print(x)        # L? no. E? no. G? yes — module level
        print(len)      # L? E? G? no. B? yes — the builtins

    inner()


outer()
```

**Output:**
```
local z
enclosing y
global x
<built-in function len>
```

Nothing exotic happens for `y`, `x`, or `len`: `inner` has no local by those names, so the search simply keeps walking outward until something matches.

The consequence you meet most often is **shadowing**. When the same name exists at two levels, the inner one wins and the outer one becomes unreachable *by that name*:

```python run
x = "global"


def outer():
    x = "enclosing"              # shadows the global x inside outer and anything nested in it

    def inner():
        print("inner sees:", x)  # E matches first — G is never consulted

    inner()
    print("outer sees:", x)


outer()
print("module sees:", x)         # untouched by either call
```

**Output:**
```
inner sees: enclosing
outer sees: enclosing
module sees: global
```

`inner` finds `outer`'s `x` and stops; the module-level `x` is never read, and after both calls it is unchanged. That asymmetry is what the rest of this section is about: **reading can look outward, but assigning cannot write outward.**

### Reading is a search. Assigning is local.

Hold the two operations firmly apart, because they are resolved by different machinery at different times:

- **Read** a name → search L→E→G→B **at runtime**, take the first hit.
- **Assign** a name → create or update a **local** variable. Always — unless you explicitly opt out.

The second rule is settled far earlier than most people expect. Python classifies every name in a function body **when it compiles the `def`**, long before the function runs. If a name is assigned *anywhere* in the body, it is local *everywhere* in that body — including on lines that execute before the assignment ever happens.

You don't have to take that on faith. The verdict is recorded on the compiled code object, and you can read it back. These two functions differ only in whether one line assigns:

```python run
count = 0


def peek():
    return count          # only reads


def bump():
    count += 1            # reads AND assigns
    return count


print("peek locals: ", peek.__code__.co_varnames)
print("peek globals:", peek.__code__.co_names)
print("bump locals: ", bump.__code__.co_varnames)
print("bump globals:", bump.__code__.co_names)
```

**Output:**
```
peek locals:  ()
peek globals: ('count',)
bump locals:  ('count',)
bump globals: ()
```

`peek` has `count` filed as a global lookup; `bump` has it filed as a local slot. **Neither function has been called.** One `+=` reclassified the name, and it reclassified the whole body rather than that single line.

Which is exactly why calling `bump` blows up:

```python run
count = 0


def bump():
    count += 1        # the right-hand read resolves to the LOCAL count
    return count


bump()
```

**Output:**
```
Traceback (most recent call last):
  File "/w/main.py", line 9, in <module>
    bump()
    ~~~~^^
  File "/w/main.py", line 5, in bump
    count += 1        # the right-hand read resolves to the LOCAL count
    ^^^^^
UnboundLocalError: cannot access local variable 'count' where it is not associated with a value
```

Read the error literally — it is telling the exact truth. There *is* a local `count`; it just has no value yet. And `count += 1` has to read `count` before it can add to it, so that read hits the empty local slot. The module-level `count` is shadowed on every line of `bump`, so it cannot supply the starting value.

To send the assignment outward, declare where the name actually lives:

- **`global x`** — assign the module-level `x`.
- **`nonlocal x`** — assign the `x` in the nearest **enclosing function**.

```python run
count = 0


def bump():
    global count      # route the assignment to the module-level count
    count += 1
    return count


print(bump(), bump())
```

**Output:**
```
1 2
```

The two keywords are not interchangeable, and `global` is not just "`nonlocal`, but further out". From a nested function, `global` leaps past every enclosing function straight to module level:

```python run
n = "module"

def outer():
    n = "enclosing"

    def write_global():
        global n
        n = "set by write_global"

    def write_nonlocal():
        nonlocal n
        n = "set by write_nonlocal"

    print("before:", n)          # enclosing
    write_nonlocal()
    print("after nonlocal:", n)  # set by write_nonlocal
    write_global()
    print("after global:", n)    # still set by write_nonlocal — global never touches this n


outer()
print("module n: ", n)
```

**Output:**
```
before: enclosing
after nonlocal: set by write_nonlocal
after global: set by write_nonlocal
module n:  set by write_global
```

`write_global` never touched `outer`'s `n`, and `write_nonlocal` never touched the module's. `nonlocal` also refuses to reach module level at all: if no enclosing function binds the name, you get `SyntaxError: no binding for nonlocal 'n' found` at compile time rather than a surprise at runtime.

### `nonlocal`: update what a closure remembers

```python run
def make_counter():
    n = 0

    def inc():
        nonlocal n      # rebind the enclosing n; don't shadow it
        n += 1
        return n

    return inc


c1 = make_counter()
c2 = make_counter()
print(c1(), c1(), c1())
print(c2())             # a completely independent n
```

**Output:**
```
1 2 3
1
```

Every call to `make_counter()` runs the body again and creates a fresh `n`. The `inc` it returns holds a live reference to *that* `n` — a **closure** (§11) — which is why `c1` and `c2` count separately instead of sharing a tally.

`nonlocal` is the piece that lets `inc` *update* the captured name instead of shadowing it. Drop that one line and `n += 1` becomes an assignment to a brand-new local, whose read half has nothing to read: the same `UnboundLocalError` as `bump`, arriving for the same reason.

### Rebinding is not mutating

`global` and `nonlocal` are needed only when you **rebind** a name — `x = …`, `x += 1`, `del x`. Changing an object *in place* is not an assignment, and needs no declaration at all:

```python run
items = []


def add(x):
    items.append(x)   # mutates the object; never assigns to the name 'items'


add(1)
add(2)
print(items)
```

**Output:**
```
[1, 2]
```

`add` reads the name `items` (found at G) and calls a method on the object it points to. The name never appears on the left of an `=`, so nothing in `add` is local, and the one shared list is genuinely modified.

**Intuition.**

*Mechanism.* Name resolution is two systems wearing one syntax. **Reads** are a runtime search outward through L→E→G→B that stops at the first match. **Writes** are decided at compile time: the compiler scans the entire function body up front, and any name it sees assigned becomes a local slot for the whole body. `global` and `nonlocal` are the only way to overrule that verdict, which is why they must be declared before the name is used. The asymmetry is deliberate — a function may freely *use* the world around it, but it cannot quietly reassign a name it doesn't own.

*Concrete bite.* Once "mutating needs no declaration" is in hand, the trap becomes the line that looks like mutation but is really an assignment:

```python run
items = []


def add(x):
    items = items + [x]   # an assignment -> 'items' is local for all of add
    return items


add(1)
```

**Output:**
```
Traceback (most recent call last):
  File "/w/main.py", line 9, in <module>
    add(1)
    ~~~^^^
  File "/w/main.py", line 5, in add
    items = items + [x]   # an assignment -> 'items' is local for all of add
            ^^^^^
UnboundLocalError: cannot access local variable 'items' where it is not associated with a value
```

`items.append(x)` and `items = items + [x]` are interchangeable at the top level of a script and behave completely differently inside a function. The same split runs through `d[k] = v` (mutation — fine) versus `d = {**d, k: v}` (rebinding — needs a declaration). The sharpest case is `items += [x]`: on a list that *does* mutate in place, but `+=` is still an assignment statement, so the name is local and it raises anyway.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Reading outer names is automatic; *rebinding* them is not, by design — so a function can't silently clobber state it doesn't own. Prefer returning a value to mutating a `global`; it keeps a function's effects visible in its signature instead of hidden in its body. Reserve `nonlocal` for closures that genuinely carry state — counters, accumulators, caches. And run two questions over any name in a function body: is it *assigned* anywhere in this function (if so it is local **everywhere**, starting at line one), and is this line *rebinding the name* or *mutating the object*?

</div>

---

## 8. Docstrings, annotations, introspection

Because a function is an object (§1, and [The Object Model](/synapse/programming-languages/python/how-python-works/the-object-model)), it can carry attributes — and Python fills several of them in for you as it executes the `def`.

```python run
def area(width: float, height: float = 1.0) -> float:
    "Return the area of a rectangle."
    return width * height

print(area.__name__)        # the function's name
print(area.__doc__)         # the docstring
print(area.__defaults__)    # default values
print(area.__annotations__) # type hints
```

**Output:**
```
area
Return the area of a rectangle.
(1.0,)
{'width': <class 'float'>, 'height': <class 'float'>, 'return': <class 'float'>}
```

**Analysis.** The first string literal in a function body is lifted into `__doc__` — that is the whole mechanism behind docstrings, and why `help()` and every IDE tooltip can find them. Defaults land in `__defaults__` (the same tuple you watched get corrupted in §4). Annotations land in `__annotations__` and are **recorded, never enforced**.

None of this is read-only, which is the part that surprises people. A function has a `__dict__` like any other object, so you can rewrite its metadata or attach your own:

```python run
def area(width: float, height: float = 1.0) -> float:
    "Return the area of a rectangle."
    return width * height


area.__doc__ = "Rewritten at runtime."     # the metadata is writable
area.unit = "m²"                           # and you can bolt on your own
print(area.__doc__)
print(area.unit)
print(area.__dict__)
```

**Output:**
```
Rewritten at runtime.
m²
{'unit': 'm²'}
```

Only `unit` shows up in `__dict__`; `__name__` and `__doc__` have dedicated slots of their own. This writability is not a curiosity — it is exactly the machinery `functools.wraps` uses in §15 to stop decorators from erasing the identity of the functions they wrap.

**Intuition.**

*Mechanism.* A function is a data structure with metadata bolted on: `__name__`, `__doc__`, `__defaults__`, `__annotations__`, `__closure__`, `__code__`, plus anything you add. Annotations are stored and nothing more — the interpreter never checks a value against them, never coerces, and never raises on a mismatch. They exist for humans and for external tools: linters, IDEs, `mypy`.

*Concrete bite.* "Not enforced" is stronger than it sounds. An annotation cannot catch even the most blatant wrong type:

```python run
def add(a: int, b: int) -> int:
    return a + b

print(add("x", "y"))      # "xy"  -- no error; annotations don't validate anything
```

**Output:**
```
xy
```

Two strings went into a function annotated `int, int -> int`, and a string came out. No warning, no traceback. A type checker would refuse this *before* the program ran; the interpreter, running it, has no opinion at all. Annotations describe intent — they do not defend it.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Treat annotations as intent and tooling fuel, never as runtime guarantees — they only pay off if you actually run `mypy` or an IDE checker over them, so wire that into CI or you are writing comments with extra syntax. Write a one-line docstring on anything non-trivial; it costs a line and shows up in `help()`, tooltips, and generated docs. When you need real validation at the boundary — parsing user input, handling a request body — write explicit checks or reach for a library like `pydantic` that turns annotations into enforcement.

</div>

---

## 9. First-class and higher-order functions

A **higher-order** function is one that takes a function as an argument, returns a function, or both. Nothing new is required to make this work — it falls straight out of §1. If a function is a value, then of course it can be passed and returned like one.

```python run
def apply_twice(fn, x):
    return fn(fn(x))

def increment(n):
    return n + 1

print(apply_twice(increment, 10))     # increment(increment(10))
print(apply_twice(lambda s: s + "!", "hi"))
```

**Output:**
```
12
hi!!
```

**Analysis.** `apply_twice` has no idea what `fn` does and never needs to. It is *parameterized by behaviour*: the data arrives as `x`, and the "what to do with it" arrives as `fn`. A named function and a lambda work equally well, because both are just function objects.

Note what is **not** in that call: parentheses. `apply_twice(increment, 10)` passes the function; `increment(10)` would call it and pass the number `11`.

The other half of "higher-order" is returning a function, which is how you build functions to order:

```python run
def power_of(exponent):
    def raise_it(base):
        return base ** exponent
    return raise_it            # return the function object itself, uncalled


square = power_of(2)
cube = power_of(3)
print(square(5), cube(5))
print(power_of(4)(2))          # call the returned function straight away
```

**Output:**
```
25 125
16
```

`power_of` is a function factory. Each call runs the inner `def` again, producing a *new* `raise_it` that remembers its own `exponent` — the closure mechanism §11 takes apart. And `power_of(4)(2)` reads left to right: the first call returns a function, the second pair of parentheses calls it.

**Intuition.**

*Mechanism.* Passing a function passes the object itself; the parentheses are a separate operation that *invokes* it. `fn` and `fn()` are therefore completely different expressions — one is a value of type `function`, the other is whatever that function returned. Every higher-order API in Python depends on you spelling the difference correctly.

*Concrete bite.* Add the parentheses by reflex and the failure surfaces one level down, inside a function you did not write:

```python run
def apply_twice(fn, x):
    return fn(fn(x))


def increment(n):
    return n + 1


print(apply_twice(increment(10), 10))    # note the parentheses after increment
```

**Output:**
```
Traceback (most recent call last):
  File "/w/main.py", line 9, in <module>
    print(apply_twice(increment(10), 10))    # note the parentheses after increment
          ~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^
  File "/w/main.py", line 2, in apply_twice
    return fn(fn(x))
              ~~^^^
TypeError: 'int' object is not callable
```

`increment(10)` evaluated to `11` before `apply_twice` was ever entered, so `fn` was bound to an integer. The traceback points at `fn(fn(x))` — a line that is perfectly correct — because that is where the wrong *kind* of value is finally used. Whenever you see "`'int' object is not callable`" for a parameter that should hold a function, look at the call site and count the parentheses.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Use higher-order functions to parameterize **behaviour**, not just data. It is the abstraction under `sorted(key=...)`, `map`, `filter`, callbacks, retry helpers, and every decorator in §15. The trigger to reach for it: two functions that are identical except for one inner operation — lift that operation into a parameter and delete the duplicate. The trigger to stop: when the function argument is only ever called with one value at every call site, in which case you have added a layer of indirection and bought nothing.

</div>

---

## 10. Lambdas and the late-binding trap

A `lambda` is a function built by an *expression* instead of a statement. Its body must be a **single expression**, and that expression's value is returned automatically — there is no `return` keyword and no room for one.

```python run
double = lambda x: x * 2
print(double(5))
print((lambda x: x * 2)(5))     # build and call immediately
```

**Output:**
```
10
10
```

Only the *body* is restricted. The parameter list follows the same rules as `def` — zero or more parameters, defaults, `*args`, `**kwargs`:

```python run
print((lambda: "no arguments")())
print((lambda a, b=2, *rest: (a, b, rest))(1, 5, 9, 10))
```

**Output:**
```
no arguments
(1, 5, (9, 10))
```

What `lambda` produces is not a lesser kind of function. It is the same object `def` produces, differing in exactly one respect:

```python run
square = lambda x: x * x


def square_def(x):
    return x * x


print(type(square), type(square_def))
print(square.__name__, square_def.__name__)
print(square(6), square_def(6))
```

**Output:**
```
<class 'function'> <class 'function'>
<lambda> square_def
36 36
```

Same type, same behaviour — but the lambda's `__name__` is the generic `<lambda>`, because no name was ever part of its definition. That is not cosmetic: when a lambda raises deep inside a `sorted()` call, the traceback says `<lambda>`, and if you have three of them in the file you get to guess which one.

Conditionals inside a lambda use the **ternary expression** (`A if cond else B`), since `if` as a *statement* would not be an expression and cannot appear here:

```python run
parity = lambda n: "even" if n % 2 == 0 else "odd"
print(parity(4), parity(7))
```

**Output:**
```
even odd
```

## The late-binding trap

```python run
funcs = [lambda: i for i in range(3)]
print([f() for f in funcs])
```

**Output:**
```
[2, 2, 2]
```

**Analysis.** Three separate lambdas were built, and all three print `2`. The reason is that none of them stored a value. Each one stored a *reference to the variable* `i`, and the comprehension used a single `i` that it advanced to `2` before any lambda was ever called. By the time `f()` runs, there is one `i` and its value is `2` — so all three agree.

Before reaching for a fix, it is worth pinning down what is actually causing this, because the loop and the `lambda` are both innocent bystanders.

### It is not about loops

Strip the loop away entirely and the behaviour survives:

```python run
i = 0
f = lambda: i
i = 99
print(f())
```

**Output:**
```
99
```

The `i` in the body was never resolved when the lambda was built. It is resolved when `f()` *runs*, by the ordinary scope-lookup rules — the same machinery that makes `global` and `nonlocal` bind a name to a **scope** rather than to a value. The lambda stored the *question* "what is `i`?", not the answer. Rebinding `i` afterwards changes the answer, and the lambda has no say in it.

A loop is simply the fastest way to rebind the same name several times before anyone calls anything.

### It is not about `lambda` either

`def` closes over variables by exactly the same rules:

```python run
funcs = []
for i in range(3):
    def f():
        return i
    funcs.append(f)

print([g() for g in funcs])
```

**Output:**
```
[2, 2, 2]
```

Nothing about `lambda` is special here. What is special is *deferring the call* until after the variable has moved on.

### Proving they share one variable

The shared variable is a real object you can inspect. A free variable captured by a nested function lives in a **cell**, and every closure over that variable holds the *same* cell:

```python run
def make_all():
    funcs = []
    for i in range(3):
        funcs.append(lambda: i)
    return funcs


fs = make_all()
print(fs[0].__closure__[0].cell_contents)
print(fs[0].__closure__[0] is fs[1].__closure__[0])
```

**Output:**
```
2
True
```

One cell, three lambdas pointing at it. `is` returning `True` is the whole bug in one line — there was never anything per-iteration to disagree about.

### When it does *not* bite

If the call happens before the variable moves on, there is no trap:

```python run
results = []
for i in range(3):
    f = lambda: i
    results.append(f())      # called now, while i still holds this iteration's value
print(results)
```

**Output:**
```
[0, 1, 2]
```

Same shared variable, but each `f()` runs while `i` still holds that iteration's value. The bug needs *deferral* — storing the function now and calling it later.

### A comprehension's private scope will not save you

In Python 3 a comprehension does get its own scope, which is why the loop variable does not leak:

```python run
funcs = [lambda: i for i in range(3)]
print([f() for f in funcs])
print("i" in dir())          # False -- i never escaped the comprehension
```

**Output:**
```
[2, 2, 2]
False
```

But that scope is **one frame for the whole comprehension**, not one frame per iteration. The isolation protects the code *outside* the comprehension from the loop variable; it does nothing for the closures built *inside* it. Reading "comprehensions have their own scope" as "comprehensions are safe here" is a common and expensive mistake.

### Forcing an early snapshot

Every fix does the same thing: it makes each function get its *own* variable, filled in at build time.

**1. Default argument** — evaluated at definition time (as §4 showed), so the value is frozen into the lambda's own parameter:

```python run
funcs = [lambda i=i: i for i in range(3)]
print([f() for f in funcs])
```

**Output:**
```
[0, 1, 2]
```

Each lambda now has its own parameter `i`, filled in with the loop's current value at the moment that lambda was built. Nothing is shared, so nothing changes underneath them. The cost is that the snapshot is now part of the signature — `funcs[0](99)` returns `99` — which matters if a framework calls your callback with arguments.

**2. Factory function** — a fresh call means a fresh local variable, and therefore a fresh cell:

```python run
def bind(i):
    return lambda: i


funcs = [bind(i) for i in range(3)]
print([f() for f in funcs])
```

**Output:**
```
[0, 1, 2]
```

**3. `functools.partial`** — binds the argument when `partial()` runs, not when the result is called:

```python run
from functools import partial


def show(i):
    return i


funcs = [partial(show, i) for i in range(3)]
print([f() for f in funcs])
```

**Output:**
```
[0, 1, 2]
```

| Technique | Snapshot taken | Trade-off |
|-----------|----------------|-----------|
| `lambda i=i: ...` | at definition | shortest; adds an overridable parameter to the signature |
| factory `def bind(i): return lambda: i` | at each `bind()` call | signature stays clean; costs one extra function |
| `partial(f, i)` | at the `partial()` call | only fits when you already have a named function |

**Intuition.**

*Mechanism.* Two mirror-image timing rules govern every function you write. A function or lambda **body** is evaluated at **call** time and captures *variables*, not values — so a lambda closing over `i` reads whatever `i` holds at the moment it runs. A **default argument** is evaluated at **definition** time — so `i=i` copies the current value into the lambda's own parameter, one frozen copy per lambda.

| What | Evaluated when | Consequence |
|------|----------------|-------------|
| Function/lambda **body** | at **call** time | sees the latest value of free variables |
| **Default argument** value | at **definition** time | frozen once, per function object |

*Concrete bite.* The version that reaches production is wiring up callbacks in a loop, where the symptom appears far from the cause:

```python run
handlers = []
for name in ["save", "load", "quit"]:
    handlers.append(lambda: print(f"running {name}"))
handlers[0]()      # "running quit"  -- all three print "quit"!
```

**Output:**
```
running quit
```

Click "save", get "quit". All three handlers close over the same `name`, and the loop left it at `"quit"` — so the button you press is irrelevant. Worse, the loop that built the handlers has long since finished by the time anything goes wrong, so nothing in the traceback points at it. `lambda name=name: print(f"running {name}")` fixes it by freezing each value as its handler is created.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** A function remembers *where to look* (the variable), not *what it found* (the value) — unless you force an early snapshot with a default argument. So whenever you build functions inside a loop that mention the loop variable, capture it with `var=var`; reach for a factory function instead when the callback's signature has to stay clean. This is not a `lambda` quirk and not a loop quirk — `def` behaves identically, and a comprehension's private scope does not help, because it is one frame for the whole comprehension rather than one per iteration. As for lambdas themselves: keep them to short throwaway callables passed to a higher-order function (`key=`, `map`, a callback). The moment one needs a statement, wants a docstring, gets reused, or grows past a line, write a `def` — you gain a real name in tracebacks and lose nothing. Assigning a lambda to a variable (`f = lambda x: ...`) is the one clearly pointless case: that is a `def` with worse debugging. Note this is the *same* definition-time-versus-call-time rule as the mutable-default trap in §4 — there it bites you, here you wield it on purpose.

</div>
---

## 11. Closures

A **closure** is a function that carries variables from the scope where it was defined, and keeps them alive even after that scope has finished executing. Three things have to line up: a function nested inside another, a reference from the inner one to the outer one's variables, and the inner function outliving the call that created it.

```python run
def multiplier(factor):
    def multiply(n):
        return n * factor      # 'factor' is captured from the enclosing scope
    return multiply

times3 = multiplier(3)
times5 = multiplier(5)
print(times3(10))
print(times5(10))
print(times3.__closure__[0].cell_contents)   # peek at the captured value
```

**Output:**
```
30
50
3
```

**Analysis.** `multiplier(3)` has returned; its frame is gone. Yet `times3` still reads `factor` and gets `3`. The captured variable survived in a **cell**, which you can open directly through `__closure__` — that last line is the mechanism made visible, not a metaphor. `times3` and `times5` hold different cells, which is why they don't interfere.

Because the cell belongs to the *call*, two functions created by the same call share one piece of state — a whole object's worth of behaviour without writing a class:

```python run
def make_account(balance):
    def deposit(n):
        nonlocal balance
        balance += n
        return balance

    def peek():
        return balance

    return deposit, peek


dep, look = make_account(100)
print(look())
dep(50)
print(look())          # the SAME cell — two functions, one shared state
```

**Output:**
```
100
150
```

`deposit` writes and `peek` reads the same `balance`, and nothing outside can touch it — there is no attribute to reach for. That is genuine encapsulation, built from nothing but scope.

**Intuition.**

*Mechanism.* When an inner function references a name from its enclosing function, the compiler promotes that name from an ordinary local into a **cell**: a small box shared between the outer frame and every inner function that mentions it. The outer frame can disappear; the cell survives as long as some function holds a reference to it. So a closure is a function plus a set of live boxes — emphasis on *live*, because a box holds a variable, not a copy of its value.

*Concrete bite.* That distinction falsifies the natural assumption that a closure snapshots what it saw:

```python run
def make():
    msg = "first"

    def show():
        print("show sees:", msg)

    show()
    msg = "second"        # rebound AFTER show was created
    show()                # ...and the closure sees the change


make()
```

**Output:**
```
show sees: first
show sees: second
```

`show` was created while `msg` was `"first"` and captured nothing of the sort. It captured the box, and reads it fresh on every call — so rebinding `msg` afterwards changes what an already-built function prints. Run the same logic inside a loop and you have the late-binding trap of §10, which is this exact behaviour with the rebinding done by the loop.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** A closure is a lightweight stateful object — one function plus private state — and the functional alternative to a small class for configured functions ("multiply by 3"), counters, accumulators, and caches. Use `nonlocal` (§7) when the closure must *update* what it captured. Prefer a real class once the state grows past a couple of variables or more than two or three functions need it, because closure state has no `repr`, cannot be inspected in a debugger without digging into `__closure__`, and cannot be pickled. And remember the captured variable is live, not frozen: if you need a snapshot, take one explicitly with a default argument.

</div>

---

## 12. `map`, `filter`, `reduce`, and `key=`

These higher-order built-ins apply a function across an iterable — §9's idea, packaged.

```python run viz=array:squares
from functools import reduce

squares = list(map(lambda x: x * x, [1, 2, 3, 4]))
evens   = list(filter(lambda x: x % 2 == 0, range(10)))
total   = reduce(lambda a, b: a + b, [1, 2, 3, 4], 0)

print(squares)
print(evens)
print(total)
```

**Output:**
```
[1, 4, 9, 16]
[0, 2, 4, 6, 8]
10
```

`map` applies a function to each element; `filter` keeps the elements for which a predicate is truthy; `reduce` folds the whole iterable down to one value, carrying an accumulator. That trailing `0` in the `reduce` call is the accumulator's starting value, and it is worth passing even when it looks redundant — without it, `reduce` on an empty iterable has nothing to return and raises `TypeError: reduce() of empty iterable with no initial value`.

Notice the `list(...)` around `map` and `filter`. It is not decoration:

```python run
nums = [1, 2, 3]
doubled = map(lambda x: x * 2, nums)

print(type(doubled).__name__)  # not a list — a lazy iterator
print(list(doubled))           # [2, 4, 6] — consuming it
print(list(doubled))           # [] — and it is now exhausted
```

**Output:**
```
map
[2, 4, 6]
[]
```

`map` and `filter` return **lazy iterators** that compute nothing until something pulls on them, and that can be pulled only once. The second `list()` gets an empty list — not an error, just silently nothing, which is how this usually reaches production. If you need the results more than once, materialise them with `list()` immediately. (This is the same laziness that makes generators worth having in §16; here it is mostly a hazard.)

### `key=` in `sorted`, `min`, `max`

```python run
people = [("Alice", 30), ("Bob", 25), ("Carol", 30), ("Dave", 25)]

print(sorted(people, key=lambda p: (p[1], p[0])))   # age asc, then name asc
print(max(people, key=lambda p: p[1]))              # oldest
```

**Output:**
```
[('Bob', 25), ('Dave', 25), ('Alice', 30), ('Carol', 30)]
('Alice', 30)
```

**Analysis.** `key=` is an **extractor**, not a comparator: Python calls `key(element)` once per element and orders by whatever comes back. Returning a **tuple** gives you multi-level sorting for free, because tuples compare lexicographically — `(25, "Bob")` beats `(25, "Dave")` on the second field only after tying on the first.

**Intuition.**

*Mechanism.* `key` is called once per element — n calls for n elements — and the results are what actually get compared. It never sees two elements at once. This is a deliberate departure from the comparator model of Java or C, and it buys two things: the key function runs a linear number of times rather than O(n log n), and tuple comparison gives you tie-breaking without writing any comparison logic at all.

*Concrete bite.* Reach for the comparator reflex and it fails immediately:

```python run
people = [("Alice", 30), ("Bob", 25)]
sorted(people, key=lambda a, b: a[1] - b[1])
```

**Output:**
```
Traceback (most recent call last):
  File "/w/main.py", line 2, in <module>
    sorted(people, key=lambda a, b: a[1] - b[1])
    ~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
TypeError: <lambda>() missing 1 required positional argument: 'b'
```

The error is oddly worded but exact: `sorted` called the lambda with one element, and the lambda wanted two. Extract instead of compare — `key=lambda p: p[1]` — and for the rare case that genuinely needs pairwise comparison, `functools.cmp_to_key` adapts an old-style comparator into a key function.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Prefer comprehensions to `map`/`filter` for readability — `[x*x for x in xs]` reads better than `list(map(lambda x: x*x, xs))` and skips the wrapper entirely. Keep `map` for the case where you already have a named function to apply (`map(str.strip, lines)`), and treat its laziness as a fact to plan around, not a feature to enjoy. But do master `key=`: it is everywhere, it has no comprehension equivalent, and the tuple tie-breaking idiom (`key=lambda p: (p[1], p[0])`) is the single most common lambda in working Python.

</div>

---

## 13. Recursion

A recursive function calls itself. Two parts are non-negotiable: a **base case** that returns without recursing, and a **recursive case** that shrinks the problem so it always moves toward that base.

```python run viz=callstack
def factorial(n):
    if n <= 1:            # base case
        return 1
    return n * factorial(n - 1)   # recursive case

print(factorial(5))
```

**Output:**
```
120
```

**Analysis.** `factorial(5)` cannot finish until `factorial(4)` does, which waits on `factorial(3)`, and so on down to `factorial(1)`. Five frames sit on the stack simultaneously, each holding its own `n`, and only when the base case returns `1` does the chain of pending multiplications collapse back up: `1 → 2 → 6 → 24 → 120`. That pile of waiting frames is the cost of recursion, and it is what makes the next part matter.

**Intuition.**

*Mechanism.* Each call pushes a frame holding its own locals, and the frame cannot be released until the call returns. Python caps how many may stack up — 1000 by default — and, unlike functional languages, does **not** optimize tail calls, so a recursion that could in principle run in constant space still consumes one frame per level. Depth is therefore a hard resource limit, not a performance detail.

*Concrete bite.* A missing base case finds that ceiling immediately:

```python run
def countdown(n):
    countdown(n - 1)      # no base case -> never stops

countdown(1000)
```

**Output:**
```
Traceback (most recent call last):
  File "/w/main.py", line 4, in <module>
    countdown(1000)
    ~~~~~~~~~^^^^^^
  File "/w/main.py", line 2, in countdown
    countdown(n - 1)      # no base case -> never stops
    ~~~~~~~~~^^^^^^^
  File "/w/main.py", line 2, in countdown
    countdown(n - 1)      # no base case -> never stops
    ~~~~~~~~~^^^^^^^
  File "/w/main.py", line 2, in countdown
    countdown(n - 1)      # no base case -> never stops
    ~~~~~~~~~^^^^^^^
  [Previous line repeated 996 more times]
RecursionError: maximum recursion depth exceeded
```

The important part is that a **correct** recursion fails the same way. The limit is on depth, not on bugs:

```python run
import sys


def fact_rec(n):
    return 1 if n <= 1 else n * fact_rec(n - 1)


def fact_iter(n):
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result


print("recursion limit:", sys.getrecursionlimit())
print("iterative 2000! is", fact_iter(2000).bit_length(), "bits long")
try:
    fact_rec(2000)
except RecursionError as exc:
    print("recursive 2000!:", type(exc).__name__)
```

**Output:**
```
recursion limit: 1000
iterative 2000! is 19053 bits long
recursive 2000!: RecursionError
```

Two implementations of the same mathematics. The loop computes a 19,053-bit answer without breaking a sweat; the recursion — flawless, base case and all — dies at 1000 because it needs 2000 frames. Raising the limit with `sys.setrecursionlimit` is available and is usually the wrong answer: the interpreter stack is a real, finite resource, and pushing the limit past what it can hold trades a clean `RecursionError` for a hard crash.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Recurse when the *data* is self-similar — trees, nested structures, divide-and-conquer, backtracking — because there the recursion mirrors the shape of the problem and depth stays proportional to the log of the input or the height of the tree. Use a loop for linear problems: it is faster, it never overflows, and it is usually no harder to read. The question to ask before recursing is not "can I?" but "how deep can this get on real input?" — if the honest answer is "as deep as there are elements", write the loop.

</div>

---

## 14. Keyword-only and positional-only parameters

§3 showed that callers *may* use keywords. Two markers in a signature let the author decide that they **must** — or must not. This is how you make a function hard to misuse instead of merely hoping.

```python run
def connect(host, *, timeout):     # everything after * is keyword-ONLY
    return f"{host} t={timeout}"

print(connect("db", timeout=30))   # OK
```

**Output:**
```
db t=30
```

Passing it positionally is now an error:

```python run
def connect(host, *, timeout):
    return f"{host} t={timeout}"

connect("db", 30)
```

**Output:**
```
Traceback (most recent call last):
  File "/w/main.py", line 4, in <module>
    connect("db", 30)
    ~~~~~~~^^^^^^^^^^
TypeError: connect() takes 1 positional argument but 2 were given
```

The mirror marker is `/`, which makes the parameters before it positional-only:

```python run
def divide(a, b, /):               # everything before / is positional-ONLY
    return a / b

print(divide(10, 2))               # OK
```

**Output:**
```
5.0
```

```python run
def divide(a, b, /):
    return a / b

divide(a=10, b=2)
```

**Output:**
```
Traceback (most recent call last):
  File "/w/main.py", line 4, in <module>
    divide(a=10, b=2)
    ~~~~~~^^^^^^^^^^^
TypeError: divide() got some positional-only arguments passed as keyword arguments: 'a, b'
```

**Analysis.** A bare `*` marks the start of the **keyword-only** parameters: callers must name them. A `/` marks the end of the **positional-only** parameters: callers cannot name them. Both markers can appear in the same signature, carving it into three zones:

```python run
def report(data, /, fmt="text", *, verbose=False):
    return f"{data} as {fmt}, verbose={verbose}"


print(report([1, 2]))                             # data: positional-only
print(report([1, 2], "json"))                     # fmt: either way
print(report([1, 2], fmt="json", verbose=True))   # verbose: keyword-only
```

**Output:**
```
[1, 2] as text, verbose=False
[1, 2] as json, verbose=False
[1, 2] as json, verbose=True
```

Read left to right: everything before `/` is positional-only, everything after `*` is keyword-only, and whatever sits between them is flexible. Most signatures need neither marker — but when you reach for one, that is the grammar.

**Intuition.**

*Mechanism.* These markers move a decision from the caller to the author. Without them, every parameter name is part of your public API whether you meant it to be or not: the moment someone writes `divide(a=10, b=2)`, renaming `a` becomes a breaking change. `/` takes those names back, which is why so much of the standard library uses it (`len(obj, /)`). `*` does the opposite — it makes a name mandatory at the call site, so the meaning of a value can never be left implicit.

*Concrete bite.* The problem keyword-only solves is the anonymous boolean, and it solves it by refusing to run at all:

```python run
def split_file(path, *, in_place):
    return f"splitting {path} (in_place={in_place})"


print(split_file("data.csv", in_place=True))   # unmistakable at the call site
split_file("data.csv", True)                   # refused before it can confuse anyone
```

**Output:**
```
splitting data.csv (in_place=True)
Traceback (most recent call last):
  File "/w/main.py", line 6, in <module>
    split_file("data.csv", True)                   # refused before it can confuse anyone
    ~~~~~~~~~~^^^^^^^^^^^^^^^^^^
TypeError: split_file() takes 1 positional argument but 2 were given
```

Compare this with §3, where transposing two positional booleans produced a wrong answer and no error at all. Here the same class of mistake cannot even be expressed: `split_file("data.csv", True)` fails loudly at the call, on the line that is actually wrong. That is the whole argument for the marker — it converts a silent data bug into a `TypeError`. It is also why you can't write `sorted(xs, True)`.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Reach for keyword-only (`*`) whenever a bare argument would be cryptic at the call site — booleans and option flags above all, and anything a reader would have to open your source to decode. Reach for positional-only (`/`) when the parameter names are implementation detail you refuse to freeze into your API, or when the argument's role is so obvious that naming it adds nothing (`len(obj)`, `abs(x)`). The cost in both cases is flexibility you are taking away from callers, so apply them where misuse is plausible rather than everywhere on principle.

</div>

---

## 15. Decorators

A decorator is a higher-order function (§9) that **takes a function and returns a replacement**, usually one that wraps the original in extra behaviour. The `@` is pure syntax:

```python run
def logged(fn):
    def wrapper(*args, **kwargs):
        print(f"calling {fn.__name__}")
        return fn(*args, **kwargs)
    return wrapper


def add(a, b):
    return a + b


add = logged(add)      # exactly what @logged does — no syntax required
print(add(2, 3))
```

**Output:**
```
calling add
5
```

That is the whole idea. `@logged` above a `def` means precisely `add = logged(add)`, run immediately after the definition. Everything below is that one line plus bookkeeping.

### Basic decorator

```python run
import functools

def logged(fn):
    @functools.wraps(fn)              # preserves fn's name/docstring
    def wrapper(*args, **kwargs):
        print(f"calling {fn.__name__}")
        result = fn(*args, **kwargs)
        print(f"{fn.__name__} returned {result!r}")
        return result
    return wrapper

@logged
def add(a, b):
    "Add two numbers."
    return a + b

print(add(2, 3))
print(add.__name__)      # thanks to functools.wraps
print(add.__doc__)
```

**Output:**
```
calling add
add returned 5
5
add
Add two numbers.
```

The `*args, **kwargs` forwarding from §5 is what makes this work on *any* function, and `functools.wraps` is what keeps the replacement from looking like a stranger.

### Decorator that takes arguments

This needs *three* nested layers, for a simple reason: `@repeat(3)` contains a call, so `repeat(3)` runs first and whatever it returns is used as the decorator.

```python run
import functools

def repeat(n):                        # takes the decorator's argument
    def decorator(fn):                # takes the function
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            return [fn(*args, **kwargs) for _ in range(n)]
        return wrapper
    return decorator

@repeat(3)
def hello():
    return "hi"

print(hello())
```

**Output:**
```
['hi', 'hi', 'hi']
```

Desugared, `@repeat(3)` on `hello` is `hello = repeat(3)(hello)`. Read the layers outside-in and each has exactly one job: `repeat` captures `n`, `decorator` captures `fn`, `wrapper` is the thing that finally replaces the name.

### Stacking

Decorators stack, and the order is the part everyone gets wrong once:

```python run
def outer(fn):
    def w(*a, **k):
        print("outer before")
        result = fn(*a, **k)
        print("outer after")
        return result
    return w


def inner(fn):
    def w(*a, **k):
        print("  inner before")
        result = fn(*a, **k)
        print("  inner after")
        return result
    return w


@outer
@inner
def job():
    print("    job body")


job()
```

**Output:**
```
outer before
  inner before
    job body
  inner after
outer after
```

They **apply** bottom-up — `job = outer(inner(job))` — so the one nearest the `def` wraps first and ends up innermost. But they **execute** top-down, because the outermost wrapper is the one your call reaches first. Both readings are visible in that output.

**Intuition.**

*Mechanism.* `@deco` is syntax for `fn = deco(fn)`, evaluated once at definition time. The decorator receives the original function object and returns whatever should now own the name — typically a closure (§11) that has captured `fn` and calls it via `*args, **kwargs`. Nothing is special-cased: the reason a decorator can add timing, caching or logging to any function is just that it is a function taking a function and returning a function.

*Concrete bite.* Skip `functools.wraps` and the replacement quietly keeps its own identity:

```python run
def logged(fn):
    def wrapper(*a, **k):     # no @functools.wraps(fn)
        return fn(*a, **k)
    return wrapper

@logged
def compute(): ...
print(compute.__name__)       # 'wrapper'  -- not 'compute'!
```

**Output:**
```
wrapper
```

The name `compute` now refers to a function called `wrapper`, and it is not only `__name__` that is lost — the docstring, the annotations, and the signature that `help()` and IDEs display all belong to the wrapper. Anything keyed on function identity misreports: log lines, metrics labels, `pytest` test names, registry decorators that index by `__name__`. `@functools.wraps(fn)` copies the metadata across and sets `__wrapped__` so the original stays reachable.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Use decorators for **cross-cutting concerns** — timing, caching, logging, retries, access control — anything you want to bolt onto many functions uniformly without editing each one. **Always** put `@functools.wraps(fn)` on the wrapper; the cost is one line and the alternative is losing every function's identity. Keep the wrapper's forwarding fully general (`*args, **kwargs`) so it survives signature changes in what it wraps. And be aware of what a decorator costs the reader: the code that runs is no longer the code under the `def`, so a stack of four decorators is four places to look when behaviour surprises you.

</div>

---

## 16. Generators and `yield`

A generator function uses `yield` instead of `return`. Calling it does not run the body at all — it hands back a **generator object** that produces values lazily, one at a time, only when something asks. (These are the same lazy iterators introduced as generator expressions in [Comprehensions](/synapse/programming-languages/python/working-with-data/comprehensions) and developed fully in [Iterators & Generators](/synapse/programming-languages/python/how-python-works/iterators-and-generators).)

```python run
def countdown(n):
    while n > 0:
        yield n
        n -= 1

print(list(countdown(3)))     # force all values

gen = countdown(3)
print(next(gen), next(gen))   # pull one at a time
```

**Output:**
```
[3, 2, 1]
3 2
```

**Analysis.** Each `yield` *pauses* the function and hands a value out, freezing every local exactly where it stands. The next `next()` *resumes* on the line after that `yield`, with `n` still holding whatever it held. `list(...)` simply pulls until there is nothing left.

"Nothing left" has a specific meaning: the generator's body runs off the end and the iterator signals exhaustion by raising:

```python run
def countdown(n):
    while n > 0:
        yield n
        n -= 1


gen = countdown(2)
print(next(gen))
print(next(gen))
next(gen)          # nothing left to yield
```

**Output:**
```
2
1
Traceback (most recent call last):
  File "/w/main.py", line 10, in <module>
    next(gen)          # nothing left to yield
    ~~~~^^^^^
StopIteration
```

You rarely see `StopIteration` in practice because `for` loops and `list()` catch it for you — that is precisely how a `for` loop knows when to stop. It surfaces only when you drive the iterator by hand.

### Why it matters: laziness and memory

Because a generator computes on demand, it can describe a sequence that could never exist all at once:

```python run
def naturals():
    n = 1
    while True:               # infinite — you could never build this as a list
        yield n
        n += 1


first_five = []
for value in naturals():
    if value > 5:
        break                 # we simply stop pulling
    first_five.append(value)

print(first_five)
```

**Output:**
```
[1, 2, 3, 4, 5]
```

`while True` with no exit would hang any ordinary function. Here it is fine, because nothing runs until someone pulls, and the consumer decides when to stop pulling.

**Intuition.**

*Mechanism.* A generator is a **pausable function**. `yield` suspends execution, hands out a value, and preserves the frame — locals, instruction pointer and all — instead of destroying it the way `return` does. The next `next()` restores that frame and carries on. So the object holds one frozen frame's worth of state, no matter how many values it will eventually produce.

*Concrete bite.* The memory consequence is not a rounding difference:

```python run
import sys

big_list = [x for x in range(1_000_000)]
big_gen = (x for x in range(1_000_000))

print("list over 8 MB:         ", sys.getsizeof(big_list) > 8_000_000)
print("generator under 1 KB:   ", sys.getsizeof(big_gen) < 1_024)
print("both sum to the same:   ", sum(big_list) == sum(big_gen))
```

**Output:**
```
list over 8 MB:          True
generator under 1 KB:    True
both sum to the same:    True
```

The list comprehension allocates a million integers up front — over 8 MB of pointers before you do anything with them. The generator expression is a few hundred bytes, and stays that size whether the range is a million or a billion, because it stores the recipe rather than the results. Both produce the identical sum. Swap `[` for `(` in a `sum(...)`, `any(...)` or `max(...)` call and you get that saving for free.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Use a generator when the sequence is large, infinite, or expensive to produce and you will consume it once, in order. `yield` gives you a full iterator with no class and no boilerplate, and inside a `sum`/`any`/`max` call the parenthesised form `(...)` costs nothing over `[...]` and saves everything. The price is real, though: a generator cannot be indexed, cannot be measured with `len()`, and is empty the second time you touch it — so the moment you need the values twice, materialise with `list()` and pay the memory deliberately.

</div>

---

## 17. The `functools` toolkit

The standard library's higher-order-function utilities — where "a function is a value" stops being a slogan and starts saving you code.

### `partial` — pre-fill arguments

```python run
from functools import partial

def power(base, exp):
    return base ** exp

square = partial(power, exp=2)    # fix exp=2, leave base open
cube   = partial(power, exp=3)

print(square(5))
print(cube(2))
```

**Output:**
```
25
8
```

`partial(fn, ...)` returns a new callable with some arguments already bound, waiting for the rest. It is the same job a lambda would do (`lambda b: power(b, 2)`), but the result keeps a reference to the original function and its fixed arguments, so it stays introspectable and picklable where a lambda is neither.

### `lru_cache` — memoization for free

```python run viz=callstack
import functools

@functools.lru_cache(maxsize=None)
def fib(n):
    return n if n < 2 else fib(n - 1) + fib(n - 2)

print(fib(30))
print(fib.cache_info())
```

**Output:**
```
832040
CacheInfo(hits=28, misses=31, maxsize=None, currsize=31)
```

**Analysis.** `cache_info()` tells the whole story. The 31 **misses** are the only real computations — one for each distinct `n` from 0 to 30 — and the 28 **hits** were served from the cache without re-entering the function. Undecorated, `fib(30)` makes over 2.7 million calls, because each branch re-derives the same subproblems from scratch; the cache collapses that `O(2ⁿ)` tree to `O(n)` by ensuring no input is ever computed twice.

**Intuition.**

*Mechanism.* `lru_cache` wraps the function in a dict keyed by the call's arguments. On each call it builds that key, returns the stored value on a hit, and otherwise runs the real function and stores the result. Two requirements follow directly from that design, and both bite in practice: the arguments must be **hashable** (a list argument raises `TypeError: unhashable type: 'list'`), and the function must be **pure** — because the key is built from the arguments alone, anything else the function depends on is invisible to the cache.

*Concrete bite.* That second requirement is the one that silently produces wrong answers:

```python run
import functools

RATE = 2


@functools.lru_cache(maxsize=None)
def scaled(n):
    return n * RATE          # depends on state the cache cannot see


print(scaled(10))
RATE = 10                    # the world changes
print(scaled(10))            # ...the cache does not
print(scaled(11))            # but a fresh input sees the new rate
```

**Output:**
```
20
20
110
```

Look at the last two lines together. With `RATE` at 10, `scaled(10)` returns 20 and `scaled(11)` returns 110 — the function is now answering from two different versions of the world at once, and it will keep doing so until the process restarts. No error is raised, and the older the cache entry the more plausible its stale value looks. `lru_cache` is safe exactly to the degree the function it decorates is pure, which is what §18 is about.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** `functools` is where "functions as values" pays rent: `partial` for specialization, `lru_cache` for one-line memoization, `reduce` for folding, `wraps` for decorators that do not lie about their identity. Reach for `lru_cache` when a **pure** function with hashable arguments recomputes the same inputs — overlapping-subproblem recursion is the textbook case, and a repeated expensive lookup is the everyday one. Do not reach for it when the function touches a file, a clock, a database, or a global, because you will cache an answer that was only true once. Bound it with `maxsize` whenever the space of inputs is unbounded; `maxsize=None` on user-supplied keys is a memory leak with good manners.

</div>

---

## 18. Pure functions and side effects

A **pure** function makes two promises: the same input always produces the same output, and calling it changes nothing observable outside itself. Break either one and you have a side effect.

```python run viz=array:data
# Pure: depends only on inputs, changes nothing outside
def pure_add(a, b):
    return a + b

# Impure: mutates its argument (a side effect)
def impure_append(lst, x):
    lst.append(x)        # caller's list is changed
    return lst

data = [1, 2]
impure_append(data, 3)
print(data)              # the original list was mutated
```

**Output:**
```
[1, 2, 3]
```

**Analysis.** `pure_add` cannot surprise you: nothing outside it can change its answer, and nothing it does can change anything outside. `impure_append` returns a value *and* reaches back through its parameter to modify the caller's list — note that the caller never assigned anything, yet `data` is different afterwards. That is the defining shape of a side effect: an observable change that the call site does not look like it made.

**Intuition.**

*Mechanism.* A function's real inputs are everything it reads — parameters, yes, but also globals, files, the clock, a database, the random number generator. Its real outputs are everything it changes: the returned value, plus any mutation of arguments, globals, or the outside world. Purity is simply the case where those two lists contain nothing but the parameters and the return value. When they contain more, the function is coupled to state and timing, so the *same call* can legitimately give different answers.

*Concrete bite.* Coupling to state means results depend on call history — the "works the first time" class of bug:

```python run viz=array:cart
def add_tax(prices, rate):
    for i in range(len(prices)):
        prices[i] *= (1 + rate)   # mutates the caller's list in place
    return prices

cart = [100, 200]
print(add_tax(cart, 0.1))        # taxed once
print(add_tax(cart, 0.1))        # same call, taxed AGAIN
```

**Output:**
```
[110.00000000000001, 220.00000000000003]
[121.00000000000003, 242.00000000000006]
```

The same expression, evaluated twice in a row, produces two different answers — because the first call left the cart changed and the second one taxed the tax. (The ragged decimals are ordinary [float rounding](/synapse/programming-languages/python/first-steps/numbers-and-arithmetic), unrelated to the bug.) Now the pure version, which differs by one line:

```python run
def add_tax(prices, rate):
    return [p * (1 + rate) for p in prices]   # builds a NEW list


cart = [100, 200]
print(add_tax(cart, 0.1))    # taxed once
print(add_tax(cart, 0.1))    # same call, same answer
print(cart)                  # and the original is untouched
```

**Output:**
```
[110.00000000000001, 220.00000000000003]
[110.00000000000001, 220.00000000000003]
[100, 200]
```

Twice-called, twice the same result, and `cart` still holds the numbers you put in it. Nothing about the impure version was faster or simpler; it was merely careless about where its output went.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Purity buys predictability: a pure function can be tested with nothing but a table of inputs and expected outputs, cached (`lru_cache` in §17 is only correct on pure functions), reordered, and run in parallel — all without reading its body. You cannot make everything pure, because a program that changes nothing is a program that does nothing. The workable discipline is to push side effects to the **edges** — read input, write output, and talk to the database at the boundary — and keep the logic in between pure. When you hit a bug that "only happens sometimes" or "goes away when I rerun it", suspect shared mutable state before you suspect anything else.

</div>

---

## 19. Mental-model summary

The whole lesson compressed into the ideas that generate the rest:

| Principle | Consequence |
|-----------|-------------|
| A function **is a value** (first-class object) | Pass them, return them, store them → higher-order functions, lambdas, decorators, closures |
| `def` is a **statement that executes** | Nothing exists before its line runs; defaults are computed there, once |
| **Body** runs at **call** time; captures *variables*, not values | Late-binding trap; closures see the latest value of free variables |
| **Default arguments** evaluated **once** at definition time | Mutable-default trap (§4) *and* the `i=i` lambda fix (§10) — one rule, both directions |
| `return a, b` builds **one tuple** | "Multiple returns" and unpacking are ordinary tuple mechanics |
| `*`/`**` **gather** in a definition, **scatter** at a call | Transparent argument forwarding in wrappers and decorators |
| Reads search **LEGB**; assignment defaults to **local** | Decided at compile time — `global`/`nonlocal` are the explicit opt-outs |
| `key=` is an **extractor** (one element in), not a comparator | Return a tuple for multi-level sorting |
| `@deco` means `fn = deco(fn)` | Decorators are function wrapping; `functools.wraps` keeps the identity |
| `yield` makes a **pausable function** | Lazy, memory-light streams instead of materialized lists |
| Lazy iterators are **single-use** | `map`, `filter`, and generators are empty the second time you read them |
| **Purity** = same input → same output, no side effects | Predictable, testable, cacheable, parallelizable |

### Gotcha checklist

<div style="border-left:4px solid #da5233;background:rgba(218,82,51,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

- **Mutable default argument** (`def f(x, acc=[])`) → use the `None` sentinel (§4).
- **Lambda/closure in a loop** all returning the last value → capture with `var=var` (§10).
- **Passing `fn()` where `fn` was wanted** → `'int' object is not callable`, thrown one level down (§9).
- **`*` on a dict at a call site** → spreads the *keys*, often with no error at all (§5).
- **`key=` given a two-argument lambda** (the Java reflex) → `key` receives *one* element (§12).
- **Lambda body ending at a comma in a call** → parenthesize tuples: `key=lambda p: (p[1], p[0])`.
- **`nonlocal`/`global` forgotten when rebinding an outer name** → `UnboundLocalError`, on the first line of the function (§7).
- **Rebinding where you meant to mutate** (`items = items + [x]` vs `items.append(x)`) → same error, but only inside a function (§7).
- **Forgetting `functools.wraps` in a decorator** → the wrapped function loses its `__name__` and `__doc__` (§15).
- **Re-reading an exhausted `map`/`filter`/generator** → silently empty, not an error (§12, §16).
- **`lru_cache` on an impure function** → stale answers forever, no warning (§17).
- **Deep recursion** (Python has no tail-call optimization) → `RecursionError` even when the logic is correct (§13).
- **Printing instead of returning** a value you need to compute with → `TypeError` on `None`, one line later (§2).

</div>

---

<div style="border-left:4px solid #6d28d9;background:rgba(109,40,217,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

🧪 **Predict, then check.** Retype the two famous traps — the mutable default (§4) and the lambda late-binding loop (§10) — from memory, and predict each output before you run it. When you can explain why *both* come down to a single rule — defaults and closures are decided at definition time, while bodies run at call time — you have understood the deepest thing this lesson teaches, and you are ready for [Errors & Exceptions](/synapse/programming-languages/python/how-python-works/errors-and-exceptions).

</div>

## Your Turn

Before you move on, check your understanding with the coach — explain the idea, apply it, weigh the trade-offs, then defend your reasoning.

<div class="concept-coach"></div>
