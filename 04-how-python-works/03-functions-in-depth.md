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

1. [What a function actually is](#1-what-a-function-actually-is)
2. [Parameters, return, and None](#2-parameters-return-and-none)
3. [Arguments: positional, keyword, defaults](#3-arguments-positional-keyword-defaults)
4. [The mutable default argument trap](#4-the-mutable-default-argument-trap)
5. [`*args` and `**kwargs` (and call-site unpacking)](#5-args-and-kwargs-and-call-site-unpacking)
6. [Returning multiple values](#6-returning-multiple-values)
7. [Scope: LEGB, `global`, `nonlocal`](#7-scope-legb-global-nonlocal)
8. [Docstrings, annotations, introspection](#8-docstrings-annotations-introspection)
9. [First-class and higher-order functions](#9-first-class-and-higher-order-functions)
10. [Lambdas and the late-binding trap](#10-lambdas-and-the-late-binding-trap)
11. [Closures](#11-closures)
12. [`map`, `filter`, `reduce`, and `key=`](#12-map-filter-reduce-and-key)
13. [Recursion](#13-recursion)
14. [Keyword-only and positional-only parameters](#14-keyword-only-and-positional-only-parameters)
15. [Decorators](#15-decorators)
16. [Generators and `yield`](#16-generators-and-yield)
17. [The `functools` toolkit](#17-the-functools-toolkit)
18. [Pure functions and side effects](#18-pure-functions-and-side-effects)
19. [Mental-model summary](#19-mental-model-summary)

---

## 1. What a function actually is

Before any syntax, the one idea everything else hangs on: **a function is a value** — a first-class object. The *name* you call it by is separate from the function object itself.

```python run
def double(x):
    return x * 2

print(double)          # the object
print(type(double))    # its type
alias = double         # bind a second name to the SAME object
print(alias(21))
```

**Output (illustrative — addresses vary per run):**
```
<function double at 0x7fc103ccf1a0>
<class 'function'>
42
```

**Analysis.** `def double(...)` does two things stapled together: (1) it builds a function *object*, and (2) it binds the name `double` to that object. `alias = double` rebinds another name to the very same object — no copy is made, which is why `alias(21)` runs `double`'s body.

**Intuition.**
*Mechanism.* `def` is not a special declaration — it's an executable statement that constructs a function object at runtime and binds a name to it. The object and the name are independent: you can bind more names to it, store it in a list, pass it as an argument, or return it, exactly as you would an `int`.

*Concrete bite.* Because functions are just values, you can build a dispatch table instead of a chain of `if`/`elif`:

```python run viz=hashmap:ops
ops = {"+": lambda a, b: a + b,
       "-": lambda a, b: a - b}
print(ops["+"](3, 4))     # the function was stored in a dict and looked up by key
```

**Output:**
```
7
```

The functions live in a dict like any other value; `ops["+"]` retrieves one and `(3, 4)` calls it. No `if op == "+"` ladder needed.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Internalize "a function is a value" and the rest of this chapter stops being a list of features and becomes *consequences*: lambdas (nameless function values), closures (functions carrying state), decorators (functions that transform functions), and higher-order functions (functions taking/returning functions) all follow from this one fact. Whenever you catch yourself writing a long `if`/`elif` over a fixed set of cases, ask whether a dict of functions is cleaner.

</div>

---

## 2. Parameters, return, and None

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

**Analysis.** `greet` *returns* a string; `shout` *prints* and falls off the end. A function with no `return` (or a bare `return`) returns `None` implicitly — that's why `b` is `None`. Note the print order: `shout("Aniket")` runs (and prints `HELLO Aniket`) on the line that assigns `b`, *before* the `print(a)` further down.

**Intuition.**
*Mechanism.* `return` hands a value back to the calling expression; `print` writes text to the console and itself evaluates to `None`. They're orthogonal. A function that ends without `return` implicitly returns `None`, so its "result" is `None` even though it may have printed plenty.

*Concrete bite.* Conflating the two means losing data you thought you had:

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

You see `6` on screen and assume `total == 6`, but `make_total` returned `None`, so the arithmetic explodes.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Keep "show a human" (`print`) and "give the caller a value" (`return`) strictly separate. If another part of your code needs the result, `return` it; printing is only for display and debugging. A function whose result you'll compute with must `return`, not `print`.

</div>

---

## 3. Arguments: positional, keyword, defaults

```python run
def describe(name, age, city="Unknown"):
    return f"{name}, {age}, from {city}"

print(describe("Alice", 30))                    # positional
print(describe("Bob", age=25))                  # keyword
print(describe(age=40, name="Carol"))           # keyword, any order
print(describe("Dave", 28, city="Berlin"))      # override default
```

**Output:**
```
Alice, 30, from Unknown
Bob, 25, from Unknown
Carol, 40, from Unknown
Dave, 28, from Berlin
```

**Analysis.** Three argument-passing styles: *positional* (matched by order), *keyword* (matched by name, order-free), and *defaults* (used when an argument is omitted).

**Intuition.**
*Mechanism.* Positional arguments bind by *position*; keyword arguments bind by *name*, so order stops mattering. A default value fills in for any parameter the caller omits. The rules — positional before keyword at the call site; defaulted parameters after non-defaulted ones in the definition — exist so binding is never ambiguous.

*Concrete bite.* Bare positional values become unreadable and easy to transpose:

```python
create_user("Ada", 1, 0, 1)     # what are 1, 0, 1?? easy to get wrong
create_user("Ada", admin=True, active=False, verified=True)   # self-explaining
```

The first call is a guessing game and a silent-bug magnet if two flags are swapped; the keyword call documents itself and resists transposition.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Pass values positionally only when their meaning is obvious from context (`point(x, y)`); use keyword arguments the moment a bare value would be cryptic, especially for booleans and option flags. Encode "the value most callers want" as a default so callers specify only the unusual. (To *force* clarity, you can make parameters keyword-only — see §14.)

</div>

---

## 4. The mutable default argument trap

This is the single most famous Python footgun. Predict the output before reading it.

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

**Analysis.** You probably expected `[1]`, `[2]`, `[3]`. The default `bucket=[]` is **evaluated exactly once — at function-definition time** — not on each call. So one single list is created and reused as the default across *every* call that omits `bucket`, accumulating.

**The fix** — use `None` as the sentinel and build a fresh list inside:

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
*Mechanism.* Default values are evaluated **once**, when the `def` executes, and stored on the function object. So `bucket=[]` creates *one* list at definition time; every call that omits `bucket` reuses that same list, and mutating it leaks state across calls. (This is the exact mirror of the lambda late-binding fix in §10: defaults are frozen at definition time — here that bites instead of helps.)

*Concrete bite.* You can see the single shared list directly, sitting on the function object:

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

The default lives on `f.__defaults__` and persists; appending through one call is visible to the next.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Never use a mutable object (`[]`, `{}`, `set()`) as a default — it's a single object reused forever. Use the `None`-sentinel pattern (`def f(x=None): if x is None: x = []`) to get a fresh object per call. Immutable defaults (`0`, `""`, `None`, `()`, tuples) are safe because you can't mutate them in place.

</div>

---

## 5. `*args` and `**kwargs` (and call-site unpacking)

`*` and `**` do *opposite* jobs depending on which side of the function they're on.

### In a definition: collect extras

```python run
def collect(*args, **kwargs):
    return args, kwargs

print(collect(1, 2, a=3, b=4))
```

**Output:**
```
((1, 2), {'a': 3, 'b': 4})
```

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

**Analysis.** In a *definition*, `*args` gathers leftover positional arguments into a **tuple** and `**kwargs` gathers leftover keyword arguments into a **dict**. At a *call site*, `*`/`**` **unpack** a container into many arguments. Same symbols, mirror-image meaning.

**Intuition.**
*Mechanism.* Think *gather* vs *scatter*. In a definition, `*`/`**` **pack** many arguments into one container (`args` tuple, `kwargs` dict). At a call, `*`/`**` **unpack** one container back into many arguments. The side of the function you're on determines the direction.

*Concrete bite.* This pair is precisely what lets a wrapper forward *any* signature transparently — the backbone of decorators (§15):

```python
def trace(fn):
    def wrapper(*args, **kwargs):     # gather whatever comes in
        print("called with", args, kwargs)
        return fn(*args, **kwargs)    # scatter it straight into fn
    return wrapper
```

`wrapper` doesn't know or care what `fn`'s parameters are; `*args, **kwargs` capture them on the way in and re-spread them on the way out, so `trace` works on functions of every shape.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Use `*args`/`**kwargs` in a definition when a function should accept a variable number of arguments, and the unpacking form at a call to spread an existing list/dict into one. The "gather then scatter" pattern (`def w(*a, **k): return fn(*a, **k)`) is the idiom for any transparent wrapper, proxy, or decorator.

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

**Analysis.** Python has no special "multiple return" feature. `return a, b` builds a **tuple** `(a, b)` and returns that one object. The caller can keep it as a tuple or *unpack* it into separate names.

**Intuition.**
*Mechanism.* "Returning multiple values" is a convenient fiction — `return a, b` builds a single tuple `(a, b)` (the comma makes the tuple — see [Sequences](/synapse/programming-languages/python/working-with-data/sequences)) and returns that one object. Tuple unpacking on the receiving end makes it *feel* like several values came back.

*Concrete bite.* Forgetting it's one tuple shows up when you handle it as a unit:

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

You can index `result` because it's genuinely a tuple, not a special multi-value construct.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Lean on this freely — `return a, b, c` then `x, y, z = f(...)` is clean and Pythonic. It's the same tuple machinery behind `for i, x in enumerate(...)` and `a, b = b, a`. If a function returns more than ~3 values, consider a small dataclass or named tuple so callers read fields by name instead of position.

</div>

---

## 7. Scope: LEGB, `global`, `nonlocal`

When you reference a name, Python searches scopes in a fixed order: **L**ocal → **E**nclosing → **G**lobal → **B**uilt-in. First match wins.

```python run
x = "global"

def outer():
    x = "enclosing"
    def inner():
        print(x)        # finds 'enclosing' (E), not 'global' (G)
    inner()

outer()
print(x)                # still 'global'
```

**Output:**
```
enclosing
global
```

To deliberately rebind an outer name, use `global` (module level) or `nonlocal` (nearest enclosing function):

```python run
def make_counter():
    n = 0
    def inc():
        nonlocal n      # rebind the enclosing n, don't shadow it
        n += 1
        return n
    return inc

c = make_counter()
print(c(), c(), c())
```

**Output:**
```
1 2 3
```

**Analysis.** Without `nonlocal`, `n += 1` would be read as "assign to a *local* `n`," and since it also reads `n` first, you'd get an `UnboundLocalError`. `nonlocal n` says "`n` lives in the enclosing scope; rebind *that* one."

**Intuition.**
*Mechanism.* *Reading* a name searches L→E→G→B and takes the first hit. *Assigning* a name, by default, creates it in the **local** scope — Python decides a function's local variables at compile time, so any name assigned anywhere in the function is local throughout it. `global`/`nonlocal` are explicit opt-outs that redirect assignment to an outer scope.

*Concrete bite.* This is why "read then assign" an outer variable fails confusingly:

```python run
count = 0

def bump():
    count += 1        # reads count first -> treated as local
    return count

bump()
```

**Output:**
```
Traceback (most recent call last):
  File "/w/main.py", line 7, in <module>
    bump()
    ~~~~^^
  File "/w/main.py", line 4, in bump
    count += 1        # reads count first -> treated as local
    ^^^^^
UnboundLocalError: cannot access local variable 'count' where it is not associated with a value
```

Because `count` is assigned in `bump`, it's treated as *local* for the whole function — so the `count` on the right-hand side has no value yet. Adding `global count` (or `nonlocal` for a nested function) fixes it.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Reading outer variables is automatic; *rebinding* them is not, by design, so functions don't silently clobber outer state. Prefer returning values over `global` mutation. Reach for `nonlocal` mainly inside closures (counters, accumulators), and remember: assigning a name *anywhere* in a function makes it local *everywhere* in that function.

</div>

---

## 8. Docstrings, annotations, introspection

Functions carry metadata you can inspect at runtime — because they're objects (the central fact from [The Object Model](/synapse/programming-languages/python/how-python-works/the-object-model)).

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

**Analysis.** The first string literal in a function body becomes its `__doc__`. Type annotations are stored in `__annotations__` but are **not enforced** at runtime. Defaults live in `__defaults__`.

**Intuition.**
*Mechanism.* A function is a data structure with attached metadata: `__name__`, `__doc__`, `__defaults__`, `__annotations__`, `__closure__`, and more. Annotations are *recorded*, not *enforced* — Python never checks or coerces them; they exist for humans and tools (linters, IDEs, `mypy`).

*Concrete bite.* "Not enforced" means an annotation can't catch a wrong type at runtime — only an external checker will:

```python run
def add(a: int, b: int) -> int:
    return a + b

print(add("x", "y"))      # "xy"  -- no error; annotations don't validate anything
```

**Output:**
```
xy
```

`add("x", "y")` happily concatenates strings; the `int` hints are documentation that a type checker would flag *before* running, but the interpreter ignores them.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Treat annotations as intent and tooling fuel, not runtime guarantees — pair them with `mypy`/IDE checks to get real value. Write a one-line docstring on anything non-trivial; it's cheap and surfaces in `help()`, IDEs, and tooling. When you need actual runtime validation, write explicit checks (or use a library like `pydantic`).

</div>

---

## 9. First-class and higher-order functions

A function that takes or returns a function is **higher-order**.

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

**Analysis.** `apply_twice` doesn't care what `fn` does — it just calls it. You can hand it a named function or a lambda; both are function-values.

**Intuition.**
*Mechanism.* Because functions are values (§1), a function can accept another function as a parameter and call it, or build and return a new one. `apply_twice` is *parameterized by behavior*: the "what to do" arrives as the argument `fn`.

*Concrete bite.* This is what lets you collapse near-duplicate code into one configurable function:

```python run
def transform_all(items, fn):
    return [fn(x) for x in items]

print(transform_all([1, 2, 3], lambda x: x * x))    # [1, 4, 9]
print(transform_all(["a", "b"], str.upper))         # ['A', 'B']
```

**Output:**
```
[1, 4, 9]
['A', 'B']
```

Without higher-order functions you'd write a separate loop for "square each" and "uppercase each"; here one function takes the operation as data.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Use higher-order functions to **parameterize behavior**, not just data — it's the abstraction behind `sorted(key=...)`, `map`, `filter`, callbacks, and decorators. When you notice two functions that differ only in one inner operation, factor that operation out as a function argument.

</div>

---

## 10. Lambdas and the late-binding trap

A `lambda` is a nameless function built by an *expression*. Its body must be a **single expression**, whose value is automatically returned.

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

Conditionals inside a lambda use the **ternary expression** (`A if cond else B`):

```python run
parity = lambda n: "even" if n % 2 == 0 else "odd"
print(parity(4), parity(7))
```

**Output:**
```
even odd
```

### The late-binding trap

```python run
funcs = [lambda: i for i in range(3)]
print([f() for f in funcs])
```

**Output:**
```
[2, 2, 2]
```

**The fix** — capture the value early via a default argument:

```python run
funcs = [lambda i=i: i for i in range(3)]
print([f() for f in funcs])
```

**Output:**
```
[0, 1, 2]
```

**Intuition.**
*Mechanism.* Two mirror-image timing rules govern functions. A function/lambda **body** is evaluated at **call** time and captures *variables*, not values — so a lambda closing over `i` reads `i` *when called*, by which point the loop has left `i` at its final value. A **default argument**, by contrast, is evaluated at **definition** time — so `i=i` snapshots `i`'s current value into the lambda's own parameter, one frozen copy per build.

| What | Evaluated when |
|------|----------------|
| Function/lambda **body** | at **call** time → sees the latest value of free variables |
| **Default argument** value | at **definition** time → frozen once |

*Concrete bite.* The classic version is wiring callbacks in a loop:

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

Every lambda closed over the *same* `name`, which ended as `"quit"`. The fix is `lambda name=name: print(f"running {name}")`, freezing each value at definition time.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** A function remembers *where* to look (the variable), not *what* it found (a value) — unless you force an early snapshot with a default argument. Reserve lambdas for short throwaway functions passed to higher-order functions (`key=`, `map`); if a lambda needs a statement, a name, or reuse, write a `def`. And whenever you build functions in a loop that reference the loop variable, capture it with `var=var`. (This is the *same* definition-time-vs-call-time rule as the mutable-default trap in §4 — there it bit, here you wield it deliberately.)

</div>

---

## 11. Closures

A **closure** is a function that "remembers" variables from the scope where it was defined, even after that scope has finished executing.

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

**Analysis.** `multiplier(3)` returns a `multiply` function that has captured `factor=3`. Even though `multiplier` has returned, `times3` still accesses its `factor`. `times3` and `times5` are independent closures over different `factor` values.

**Intuition.**
*Mechanism.* When an inner function references a variable from its enclosing function, Python keeps that variable alive in a *cell* attached to the inner function (visible in `__closure__`), even after the outer function returns. So the closure is a function bundled with a private, persistent snapshot of its surrounding variables.

*Concrete bite.* Closures capture *variables*, so they share state when they should be independent (the same late-binding mechanism as §10):

```python run
def make_adders():
    return [lambda x: x + i for i in range(3)]

add0, add1, add2 = make_adders()
print(add0(10))     # 12  -- expected 10; all three captured the same final i = 2
```

**Output:**
```
12
```

All three lambdas close over one `i` that ended at `2`. Capture per-iteration with `lambda x, i=i: x + i` to get independent adders.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** A closure is a lightweight stateful object — one function plus hidden state — and the functional alternative to a small class for things like configured functions (a "multiply-by-3" machine), counters, and accumulators. Use `nonlocal` (§7) when the closure must *update* its captured state. Beware shared-variable capture in loops; snapshot with a default argument when you need independence.

</div>

---

## 12. `map`, `filter`, `reduce`, and `key=`

These higher-order built-ins apply a function across an iterable.

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

**Analysis.** `map` applies a function to each element; `filter` keeps elements where a predicate is truthy; `reduce` folds the iterable into one value. `key=` is an **extractor**: Python calls `key(element)` and sorts by the result. Returning a **tuple** gives multi-level sorting (compare first, break ties by second).

**Intuition.**
*Mechanism.* `key=` is called once per element to produce the value to sort/compare *by* — it is **not** a comparator (it never sees two elements at once, unlike Java's `Comparator`). Tuples compare lexicographically, so returning `(age, name)` sorts by age, breaking ties by name, for free.

*Concrete bite.* The Java reflex — a two-argument comparator — fails here:

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

`key` passes *one* element, so a two-parameter lambda raises. The correct form extracts a sort value from a single element: `key=lambda p: p[1]`. (For genuine two-argument comparison, wrap it with `functools.cmp_to_key`.)

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Prefer comprehensions over `map`/`filter` for readability (`[x*x for x in xs]` beats `list(map(lambda x: x*x, xs))`), but master `key=` — it's everywhere and irreplaceable. The "return a tuple for tie-breaking" idiom (`key=lambda p: (p[1], p[0])`) is the single most common lambda use in real code and interviews.

</div>

---

## 13. Recursion

A function that calls itself. Every recursion needs a **base case** (stops it) and a **recursive case** (shrinks the problem toward the base).

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

**Analysis.** `factorial(5)` expands to `5 * 4 * 3 * 2 * 1`. Each call adds a stack frame; the stack unwinds as base cases return.

**Intuition.**
*Mechanism.* Each call pushes a frame onto the call stack holding its own locals; the base case is what eventually stops the pushing and lets the stack unwind. Python caps recursion depth (~1000 frames) and does **not** optimize tail calls, so deep recursion overflows the stack rather than running flat.

*Concrete bite.* A missing base case (or merely deep input) hits that ceiling:

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

Even a *correct* recursion fails this way if the depth exceeds the limit — e.g. naive recursion over a 100,000-element list overflows the stack long before it finishes.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Recursion shines on *self-similar* problems — trees, divide-and-conquer, backtracking — where the base case is a floor you stand on and the recursive case always moves toward it. For linear problems prefer an iterative loop: it's faster and stack-safe. Don't recurse just because you can; reach for it when the problem's structure is itself recursive.

</div>

---

## 14. Keyword-only and positional-only parameters

Two markers in a signature control *how* arguments may be passed.

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

**Analysis.** A bare `*` marks the start of **keyword-only** parameters (callers must name them). A `/` marks the end of **positional-only** parameters (callers cannot name them).

**Intuition.**
*Mechanism.* `*` in the parameter list says "everything after me can only be passed by name"; `/` says "everything before me can only be passed by position." They let an API author dictate call style rather than leaving it to the caller.

*Concrete bite.* Keyword-only parameters prevent the mystery-boolean call site:

```python
def split_file(path, *, in_place):
    ...

split_file("data.csv", True)           # TypeError: takes 1 positional arg but 2 given
split_file("data.csv", in_place=True)  # forced to be readable
```

The `*` makes `split_file("data.csv", True)` illegal, so nobody can leave a bare `True` whose meaning is unclear at the call site — exactly why `sorted(xs, reverse=True)` can't be passed positionally.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Use keyword-only (`*`) to force clarity on flags and options (anything where a bare value would be cryptic). Use positional-only (`/`) when parameter *names* are implementation details you don't want to freeze as API (common in the standard library, e.g. `len(obj, /)`). Together they let you design signatures that are hard to misuse.

</div>

---

## 15. Decorators

A decorator is a higher-order function that **takes a function and returns a replacement function** — usually one wrapping the original with extra behavior. `@deco` above a `def` is sugar for `fn = deco(fn)`.

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

### Decorator that takes arguments

This needs *three* nested layers:

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

**Analysis.** `@logged` rebinds `add` to `logged(add)` (i.e. `wrapper`). The wrapper forwards arguments with `*args, **kwargs`. `@repeat(3)` means `hello = repeat(3)(hello)` — outer layer eats the argument, middle eats the function, inner is the replacement.

**Intuition.**
*Mechanism.* `@deco` is pure syntax for `fn = deco(fn)` — the decorator receives the original function and returns whatever replaces its name (usually a wrapper that calls the original via `*args, **kwargs`). `functools.wraps(fn)` copies the original's `__name__`, `__doc__`, etc. onto the wrapper so the disguise is complete.

*Concrete bite.* Omit `wraps` and the wrapped function loses its identity, breaking introspection and tooling:

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

`compute.__name__` is now `'wrapper'`, so logs, `help()`, debuggers, and anything keyed on function names misreport it. `@functools.wraps(fn)` on `wrapper` fixes it.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** A decorator is just "wrap this function in another function"; the `*args/**kwargs` forwarding makes it work on any signature, and the three-layer structure is mechanical for parameterized decorators. **Always** put `@functools.wraps(fn)` on the wrapper so metadata survives. Use decorators for cross-cutting concerns — timing, caching, logging, access control, retries — that you want to bolt onto many functions uniformly.

</div>

---

## 16. Generators and `yield`

A generator function uses `yield` instead of `return`. Calling it doesn't run the body — it returns a **generator object** that produces values lazily, one at a time, on demand. (These are the same lazy iterators introduced as generator expressions in [Comprehensions](/synapse/programming-languages/python/working-with-data/comprehensions) and developed fully in [Iterators & Generators](/synapse/programming-languages/python/how-python-works/iterators-and-generators).)

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

**Analysis.** Each `yield` *pauses* the function and hands back a value, *freezing* local state. The next `next()` *resumes* right after the `yield` with state intact. `list(gen)` drains it; after exhaustion it raises `StopIteration`.

### Why it matters: laziness and memory

```python run
total = sum(x * x for x in range(5))      # generator expression: () not []
print(total)
```

**Output:**
```
30
```

**Intuition.**
*Mechanism.* A generator is a *pausable function*: `yield` suspends execution and returns a value, freezing all locals; the next `next()` resumes right after that `yield`. So values are produced one at a time, on demand, rather than all at once — the generator holds only its current state, not a materialized list.

*Concrete bite.* The memory difference is enormous and measurable (`sys.getsizeof` reports an object's size in bytes; it is CPython-specific):

```python run
import sys
print(sys.getsizeof([x for x in range(1_000_000)]))   # the materialized list
print(sys.getsizeof((x for x in range(1_000_000))))   # the generator
```

**Output:**
```
8448728
192
```

The list comprehension allocates all million integers up front (~8 MB); the generator expression is a fixed 192 bytes regardless of range size, computing each value only when pulled. For `sum`/`any`/`max` over large data, that's free memory savings — and the only feasible option for infinite streams.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Use a generator when the sequence is large, infinite, or expensive and you consume values once, in order, without needing them all in memory. `yield` gives you an iterator with no boilerplate. Rule of thumb: if you'll loop over results a single time, prefer a generator expression `(...)` over a list comprehension `[...]`. The cost: you can't index a generator or reuse it after exhaustion.

</div>

---

## 17. The `functools` toolkit

The standard library's higher-order-function utilities — where "functions as values" pays off in practice.

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

**Analysis.** `partial(fn, ...)` returns a new callable with some arguments pre-bound. `@lru_cache` stores results keyed by arguments, turning exponential recursion into linear.

**Intuition.**
*Mechanism.* `partial` pre-binds some of a function's arguments and returns a new callable awaiting the rest — lighter than a wrapping lambda. `@lru_cache` transparently memoizes: it stores each result keyed by the (hashable) arguments and returns the cached value on repeat calls, so each distinct input is computed once.

*Concrete bite.* For overlapping-subproblem recursion the speedup is dramatic and quantifiable. Naive `fib(30)` recomputes the same subproblems millions of times; with `@lru_cache` the `cache_info()` above tells the whole story:

```
hits=28, misses=31
```

The 31 *misses* are the only real computations — one per distinct value of `n` from 0 to 30 — and the 28 *hits* are returns straight from the cache. The exponential `O(2ⁿ)` call tree has collapsed to `O(n)`.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** `functools` is where "functions as values" pays off practically: `partial` for specialization, `lru_cache` for one-line memoization, `reduce` for folding, `wraps` for honest decorators. Reach for `lru_cache` the moment a *pure* recursive function recomputes the same inputs (memoization requires the function be effectively side-effect-free and its arguments hashable). The cost is memory for the cache (bound it with `maxsize` when inputs are unbounded).

</div>

---

## 18. Pure functions and side effects

A **pure** function: (1) returns the same output for the same input, and (2) has no side effects.

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

**Analysis.** `pure_add` can't surprise you — same inputs, same output, no ripple effects. `impure_append` mutates the caller's list; calling it changes the world outside the function.

**Intuition.**
*Mechanism.* Purity means a function's output depends *only* on its inputs and it changes *nothing* observable outside itself (no mutation of arguments or globals, no I/O). An impure function couples its behavior to external state and timing, so the same call can produce different results or visible ripples.

*Concrete bite.* Impurity makes results depend on call history — the "works the second time but not the third" class of bug:

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

Calling `add_tax` twice taxes the already-taxed list, because it mutated `cart` (the ragged decimals are ordinary [float rounding](/synapse/programming-languages/python/first-steps/numbers-and-arithmetic), a separate issue). A pure version computing `[p * (1 + rate) for p in prices]` returns a new list, leaves `cart` untouched, and gives the same answer every time.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Purity buys predictability and testability — pure functions are trivial to test, safe to cache (`lru_cache` effectively *requires* purity), and easy to parallelize and reason about. You can't make everything pure (programs must do I/O), but push side effects to the edges and keep core logic pure. When debugging "it works sometimes," suspect hidden side effects and shared mutable state first.

</div>

---

## 19. Mental-model summary

The whole chapter compressed into the ideas that generate the rest:

| Principle | Consequence |
|-----------|-------------|
| A function **is a value** (first-class object) | Pass them, return them, store them → higher-order functions, lambdas, decorators, closures |
| **Body** runs at **call** time; captures *variables*, not values | Late-binding trap; closures see the latest value of free variables |
| **Default arguments** evaluated **once** at definition time | Mutable-default trap (§4) AND the `i=i` lambda fix (§10) — same rule, both directions |
| `return a, b` builds **one tuple** | "Multiple returns" + unpacking are tuple mechanics |
| `*`/`**` **gather** in a definition, **scatter** at a call | Transparent argument forwarding in wrappers/decorators |
| Assignment defaults to **local** scope | `global`/`nonlocal` are explicit opt-ins; LEGB governs lookup |
| `key=` is an **extractor** (one element in), not a comparator | Return a tuple for multi-level sorting |
| `@deco` means `fn = deco(fn)` | Decorators are function-wrapping; `functools.wraps` keeps metadata |
| `yield` makes a **pausable function** | Lazy, memory-light streams instead of materialized lists |
| **Purity** = same input → same output, no side effects | Predictable, testable, cacheable, parallelizable |

### Gotcha checklist

<div style="border-left:4px solid #da5233;background:rgba(218,82,51,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

- **Mutable default argument** (`def f(x, acc=[])`) → use the `None` sentinel.
- **Lambda/closure in a loop** all returning the last value → capture with `var=var` default.
- **`key=` given a two-argument lambda** (Java reflex) → it takes *one* element.
- **Lambda body ending at a comma in a call** → parenthesize tuples: `key=lambda p: (p[1], p[0])`.
- **`nonlocal`/`global` forgotten when rebinding an outer name** → `UnboundLocalError`.
- **Forgetting `functools.wraps` in a decorator** → wrapped function loses its `__name__`/`__doc__`.
- **Deep recursion in Python** (no tail-call optimization) → `RecursionError`; consider iteration.
- **Printing instead of returning** a result you need to compute with → `TypeError` on `None`.

</div>

---

<div style="border-left:4px solid #6d28d9;background:rgba(109,40,217,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

🧪 **Predict, then check.** Retype the two famous traps — the mutable default (§4) and the lambda late-binding loop (§10) — from memory, and predict each output before running. When you can explain why *both* come down to one rule — "defaults and closures are decided at definition time, bodies run at call time" — you've understood the deepest thing this chapter teaches, and you're ready for [Errors & Exceptions](/synapse/programming-languages/python/how-python-works/errors-and-exceptions).

</div>

## Your Turn

Before you move on, check your understanding with the coach — explain the idea, apply it, weigh the trade-offs, then defend your reasoning.

<div class="concept-coach"></div>
