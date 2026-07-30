---
title: Type Hints & Static Typing
summary: Type hints annotate code with the types it expects, documenting intent and letting tools like mypy catch type bugs before runtime — but Python ignores them while running, so they never enforce anything by themselves. Annotations, the runtime no-op, collection and optional types, introspection, and Protocols.
prereqs: []
---

# Type Hints & Static Typing — Documentation the Tools Can Check

Python is dynamically typed, but you can *annotate* code with the types it expects. The thesis to hold firmly: **type hints are checked by external tools (a type checker like `mypy`), not by Python at runtime — the interpreter parses them, stores them, and otherwise ignores them.** So hints buy you documentation, editor autocomplete, and a static safety net, but they never change what the program *does*.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **The core idea.**

- Type hints are checked by **external tools** like `mypy`.
- Python **ignores them at runtime** — parses, stores, then moves on.
- They buy documentation, autocomplete, and a static safety net.
- They never change what the program *does*.

</div>

This builds on every type you've met and on [the object model](/synapse/programming-languages/python/how-python-works/the-object-model). Every runnable output below was produced by running the code; the one `mypy` example is marked, since the runner has no type checker installed.

<div style="border-left:4px solid #15448e;background:rgba(21,68,142,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

📘 **How to read the Intuition boxes.** Each one is built in three moves:

1. **The mechanism** — what the interpreter is *actually doing*.
2. **A concrete bite** — a specific, runnable way the naive assumption fails.
3. **The earned rule** — the decision heuristic, now justified rather than asserted, plus its cost.

</div>

---

## Table of Contents

1. [Annotating functions and variables](#1-annotating-functions-and-variables)
2. [Hints are not enforced at runtime](#2-hints-are-not-enforced-at-runtime)
3. [Collection and optional types](#3-collection-and-optional-types)
4. [Hints are introspectable](#4-hints-are-introspectable)
5. [Protocols and static checking](#5-protocols-and-static-checking)
6. [Mental-model summary](#6-mental-model-summary)
7. [Gotcha checklist](#7-gotcha-checklist)

---

## 1. Annotating functions and variables

A function annotation puts `: type` after each parameter and `-> type` before the colon. A variable annotation is `name: type = value`.

```python run
def greet(name: str, times: int = 1) -> str:
    return f"Hi {name}! " * times

print(greet("Ada", 2))
age: int = 30
print(age)
```

**Output:**
```
Hi Ada! Hi Ada! 
30
```

**Analysis.** `name: str`, `times: int = 1`, and `-> str` declare the expected types; `age: int = 30` annotates a variable. The function ran exactly as an un-annotated one would — the hints added information for *readers and tools* without changing behaviour. They're documentation that lives in the code and stays in sync with it.

**Intuition.**
*Mechanism.* When Python compiles a `def`, it records the annotations (in `__annotations__`, §4) and otherwise treats them as inert — they don't wrap, check, or convert anything. A variable annotation with no value (`x: int`) doesn't even create the variable; it only registers the intended type.

*Concrete bite.* A variable annotation with **no value** doesn't even create the variable — it only records the intended type:

```python run
x: int        # annotation only - does NOT create x
print(x)
```
```
Traceback (most recent call last):
  File "/w/main.py", line 2, in <module>
    print(x)
          ^
NameError: name 'x' is not defined
```

`x: int` registered an annotation but bound nothing, so `print(x)` is a `NameError`. The annotation is metadata, not an assignment — proof that the interpreter treats it as inert.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Annotate function signatures and tricky variables to document intent and unlock tooling; skip obvious locals (`count = 0` needs no `: int`). The cost is essentially nil at runtime, and the payoff is real only if you actually run a checker (§5) — hints you never check are just comments that look official.

</div>

---

## 2. Hints are not enforced at runtime

This is the point people most often get wrong. A hint is **not a runtime check** — passing the wrong type runs anyway, with whatever behaviour that type produces.

```python run
def double(n: int) -> int:
    return n * 2

print(double("ab"))   # a str despite the int hint - Python does not check
```

**Output:**
```
abab
```

**Analysis.** `double` is annotated for `int`, but we passed `"ab"`. Python did **not** raise — it ran `"ab" * 2`, which is string repetition, giving `"abab"`. The `-> int` return hint is equally ignored; the function returned a `str`. The annotations were pure documentation; the runtime did exactly what the values' real types dictate.

**Intuition.**
*Mechanism.* At call time Python binds arguments to parameters without consulting annotations at all. `n * 2` dispatches on the *actual* type of `n` (`str` → repeat), not the *hinted* type. There is no hidden `isinstance` check anywhere.

*Concrete bite.* The output is the bite: a function "typed" for `int` happily returned `"abab"` from a `str` input. If you rely on hints to guarantee types, you'll be surprised — the guarantee doesn't exist at runtime. Only a separate static check (or an explicit `isinstance`/validation you write) catches it.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Treat hints as *checked documentation*, not runtime contracts: to actually catch type errors, run a static checker like `mypy` (§5) in development/CI, or validate explicitly when you must enforce types at runtime (e.g. at a trust boundary). The cost of forgetting this is false confidence — annotated code is not validated code unless something checks it.

</div>

---

## 3. Collection and optional types

Annotate containers with their element types using built-in generics: `list[int]`, `dict[str, int]`, `tuple[int, ...]`. For "a value or `None`," use `X | None`.

```python run
def total(nums: list[int]) -> int:
    return sum(nums)
print(total([1, 2, 3]))

def find(d: dict[str, int], key: str) -> int | None:
    return d.get(key)
print(find({"a": 1}, "a"))
print(find({"a": 1}, "z"))
```

**Output:**
```
6
1
None
```

**Analysis.** `list[int]` documents "a list of ints"; `dict[str, int]` a string→int mapping. `int | None` (the modern spelling of `Optional[int]`) says the result is an `int` or `None` — exactly what `dict.get` returns on a hit or miss ([Tutorial 13](/synapse/programming-languages/python/working-with-data/dictionaries-and-sets)). These are still just annotations — `total` would run on a list of strings — but they tell a checker and a reader the precise shape.

**Intuition.**
*Mechanism.* `list[int]` is a *parameterized generic*: the element type lives in the brackets. `X | None` is a union of two types. A checker reads these to verify call sites; at runtime they're inert annotations like any other (the brackets do construct a small generic-alias object, but it isn't used to validate).

*Concrete bite.* The element type is documentation, not a gate — pass the wrong element type and it runs until the values themselves clash:

```python run
def total(nums: list[int]) -> int:
    return sum(nums)
print(total(["a", "b"]))   # hint says int; runtime does not check
```
```
Traceback (most recent call last):
  File "/w/main.py", line 3, in <module>
    print(total(["a", "b"]))   # hint says int; runtime does not check
          ~~~~~^^^^^^^^^^^^
  File "/w/main.py", line 2, in total
    return sum(nums)
TypeError: unsupported operand type(s) for +: 'int' and 'str'
```

`list[int]` didn't reject the list of strings; the program ran into `sum` and failed there (`sum` starts at `0`, and `0 + "a"` is the error). A checker would have flagged the *call site*; the runtime only fails once the values actually clash. The real payoff of `| None` is the same idea — a checker forces you to handle the `None` that `find` can return, before it becomes a runtime `AttributeError`.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Annotate collection element types and use `X | None` for maybe-absent values — it documents the shape and makes the checker enforce `None`-handling. The cost is a little verbosity; the payoff is the most common real bug class (forgetting something can be `None`) caught statically rather than at 3 a.m.

</div>

---

## 4. Hints are introspectable

Annotations are stored on the object in `__annotations__`, so tools (and you) can read them at runtime — the one place hints are visible to running code.

```python run
def f(x: int, y: str) -> bool:
    return True
print(f.__annotations__)
```

**Output:**
```
{'x': <class 'int'>, 'y': <class 'str'>, 'return': <class 'bool'>}
```

**Analysis.** `f.__annotations__` is a dict mapping each parameter (and `'return'`) to its annotated type. This is how frameworks like `dataclasses`, `pydantic`, and `attrs` *do* use hints at runtime — they read `__annotations__` and build behaviour from it. The hints themselves still don't check anything; libraries opt in to using them.

**Intuition.**
*Mechanism.* The compiler collects annotations into the `__annotations__` dict on the function (or class/module). Anything that wants to *act* on hints reads that dict explicitly — there's no automatic enforcement, just available metadata.

*Concrete bite.* Only *signature* (and class/module) annotations are recorded — annotations on **local** variables inside a function body are stored nowhere:

```python run
def f():
    y: int = 5     # a LOCAL annotation
    return y
print(f.__annotations__)   # local annotations are not recorded
```
```
{}
```

`f.__annotations__` is empty: the `y: int` inside the body left no trace. Python keeps annotations that describe an *interface* (parameters, return, class fields) and discards purely local ones — which is exactly why `@dataclass` ([Tutorial 27](/synapse/programming-languages/python/object-oriented/advanced-oop)) can read a class's annotated fields to build its `__init__`, but no library can act on a function-local hint.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Lean on annotation-reading libraries (`dataclasses`, `pydantic`) when you want runtime structure from types — they turn hints into validation/construction for you. The cost/boundary: that behaviour comes from the *library*, not the language, so it applies only where you opt in; plain annotated code remains unchecked.

</div>

---

## 5. Protocols and static checking

`typing.Protocol` expresses **structural typing** ("duck typing, formalized"): a type matches if it has the right methods, regardless of inheritance. And a checker like `mypy` is what turns all these hints into actual error-catching.

```python run
from typing import Protocol
class Sized(Protocol):
    def __len__(self) -> int: ...

def describe(x: Sized) -> str:
    return f"has {len(x)} items"

print(describe([1, 2, 3]))   # a list matches structurally
print(describe("hello"))      # so does a str
```

**Output:**
```
has 3 items
has 5 items
```

**Analysis.** `Sized` is a Protocol requiring a `__len__`. `describe` accepts "anything with `__len__`," so a list and a string both qualify — *without* either inheriting from `Sized`. This is structural typing: the shape matters, not the family tree. A checker verifies the argument has `__len__`; at runtime, nothing is checked.

**Intuition.**
*Mechanism.* A Protocol describes a *shape* (a set of methods/attributes). `mypy` accepts any type whose shape matches, mirroring how Python actually works (duck typing). But, like all hints, it's not enforced at runtime — pass something without `__len__` and you get the ordinary error.

*Concrete bite.* At runtime the Protocol provides no protection; you get the underlying failure:

```python run
from typing import Protocol
class Sized(Protocol):
    def __len__(self) -> int: ...
def describe(x: Sized) -> str:
    return f"has {len(x)} items"
print(describe(42))   # int has no __len__ - hints do not stop this at runtime
```
```
Traceback (most recent call last):
  File "/w/main.py", line 6, in <module>
    print(describe(42))   # int has no __len__ - hints do not stop this at runtime
          ~~~~~~~~^^^^
  File "/w/main.py", line 5, in describe
    return f"has {len(x)} items"
                  ~~~^^^
TypeError: object of type 'int' has no len()
```

`describe(42)` violates the Protocol, but Python runs it anyway and fails inside `len(42)`. A **static checker** is what would have caught `describe(42)` *before* running — that's the whole point of typing. Running `mypy` on this file would report (illustrative — `mypy` isn't installed on this runner):

```
error: Argument 1 to "describe" has incompatible type "int"; expected "Sized"  [arg-type]
```

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Use `Protocol` to type "anything shaped like this" (the Pythonic alternative to forcing inheritance), and run `mypy` (or `pyright`) in CI to convert the runtime `TypeError` above into a pre-run error. The cost is adopting a checker and keeping hints honest; the payoff is a large class of bugs caught statically — but only if you *run the checker*, since Python itself never will.

</div>

---

## 6. Mental-model summary

| Principle | Consequence |
|-----------|-------------|
| Hints annotate types but are **not checked at runtime** | `double("ab")` returns `"abab"` despite an `int` hint |
| `list[int]`, `dict[str,int]`, `X \| None` annotate shape | Documentation + checker enforcement; still inert at runtime |
| Annotations live in `__annotations__` | Libraries (`dataclasses`, `pydantic`) read them to build behaviour |
| `Protocol` = structural typing | Matches by shape (has `__len__`), not by inheritance |
| A static checker (`mypy`) is what catches type errors | Run it in dev/CI; the interpreter never enforces hints |

## 7. Gotcha checklist

<div style="border-left:4px solid #da5233;background:rgba(218,82,51,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

- **A wrong type "passed" despite hints →** hints aren't runtime checks; run `mypy`, or validate explicitly at trust boundaries.
- **`AttributeError: 'NoneType' ...` →** an `X | None` value wasn't handled; check for `None` (a checker would have flagged it).
- **Hints feel pointless →** they only pay off with a checker and an editor; add `mypy` to CI.
- **Wanted runtime validation from types →** plain hints won't; use `dataclasses`/`pydantic`, which *read* `__annotations__`.
- **Forcing inheritance just to satisfy a type →** use a `Protocol` and type by shape instead.

</div>

---

<div style="border-left:4px solid #6d28d9;background:rgba(109,40,217,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

🧪 **Predict, then check.** Annotate a function `def clamp(x: int, lo: int, hi: int) -> int:` that returns `x` bounded to `[lo, hi]`. Predict what `clamp(5, 0, 10)` returns — and what `clamp("z", "a", "m")` does at runtime (does the hint stop it?). Then predict `clamp.__annotations__`. The middle one is the lesson: hints describe intent, the runtime obeys the actual types.

</div>

## Your Turn

Before you move on, check your understanding with the coach — explain the idea, apply it, weigh the trade-offs, then defend your reasoning.

<div class="concept-coach"></div>
