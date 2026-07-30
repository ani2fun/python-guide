---
title: Comprehensions
summary: A comprehension compresses a build-a-collection loop into one expression — [expr for x in it if cond] — and the same shape makes lists, sets, dicts, and lazy generators. The loop translation, filter vs transform, generator expressions and laziness, flattening, and when a comprehension hurts readability.
prereqs: []
---

# Comprehensions — Building Collections in One Expression

A **comprehension** is a loop that builds a collection, compressed into a single expression. The thesis: **one shape — `[expr for item in iterable if condition]` — replaces the "create empty, loop, append" pattern** ([Tutorial 9](/synapse/programming-languages/python/control-flow/loop-control-and-patterns)), and the *same* shape with different brackets builds lists, sets, dicts, and even lazy generators. Learn the shape once and you've learned four constructors.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **The core idea.**

- One shape — `[expr for item in iterable if condition]` — replaces "create empty, loop, append".
- The **same shape** with different brackets builds lists, sets, dicts, and lazy generators.
- Learn the shape once and you've learned four constructors.

</div>

This builds on [loops](/synapse/programming-languages/python/control-flow/loops) and [dicts & sets](/synapse/programming-languages/python/working-with-data/dictionaries-and-sets), and the generator expressions here feed straight into [Iterators & Generators](/synapse/programming-languages/python/how-python-works/iterators-and-generators). Every output below was produced by running the code.

<div style="border-left:4px solid #15448e;background:rgba(21,68,142,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

📘 **How to read the Intuition boxes.** Each one is built in three moves:

1. **The mechanism** — what the interpreter is *actually doing*.
2. **A concrete bite** — a specific, runnable way the naive assumption fails.
3. **The earned rule** — the decision heuristic, now justified rather than asserted, plus its cost.

</div>

---

## Table of Contents

1. [List comprehensions](#1-list-comprehensions)
2. [The loop translation](#2-the-loop-translation)
3. [Dict and set comprehensions](#3-dict-and-set-comprehensions)
4. [Generator expressions](#4-generator-expressions)
5. [Nesting, flattening, and when not to](#5-nesting-flattening-and-when-not-to)
6. [Mental-model summary](#6-mental-model-summary)
7. [Gotcha checklist](#7-gotcha-checklist)

---

## 1. List comprehensions

A list comprehension builds a list from an iterable: `[expr for item in iterable]` transforms each item; add `if condition` to keep only some.

```python run viz=array:squares
squares = [n * n for n in range(1, 6)]
evens = [n for n in range(10) if n % 2 == 0]
print(squares)
print(evens)
```

**Output:**
```
[1, 4, 9, 16, 25]
[0, 2, 4, 6, 8]
```

**Analysis.** The first comprehension applies `n * n` to each `n` in `1..5` — a **transform** (map). The second keeps only the `n` where `n % 2 == 0` — a **filter**. Together, `[expr for item in iterable if cond]` does "transform the items that pass the filter," the two most common collection operations in one line.

**Intuition.**
*Mechanism.* A comprehension runs its `for` (and optional `if`) just like a loop, evaluating `expr` for each surviving item and collecting the results into a new list. Critically, it runs in its **own scope** — the loop variable is local to the comprehension and does not leak into the surrounding code (a deliberate change from Python 2).

*Concrete bite.* So you can't read the loop variable afterward:

```python run
[n for n in range(3)]
print(n)        # the comprehension variable does not leak
```
```
Traceback (most recent call last):
  File "/w/main.py", line 2, in <module>
    print(n)        # the comprehension variable does not leak
          ^
NameError: name 'n' is not defined
```

The `n` lived only inside the comprehension; once it finished, `n` is gone, so `print(n)` is a `NameError`. (A plain `for` loop *does* leak its variable; a comprehension does not.)

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Use a comprehension to build a list by transforming and/or filtering an iterable — it's more concise and usually faster than the equivalent append loop. The boundary: it doesn't leak its variable (good — no accidental shadowing) and it always builds the *whole* list in memory, so for huge or infinite sources reach for a generator (§4) instead.

</div>

---

## 2. The loop translation

Every comprehension has an exactly equivalent `for` loop. Knowing the translation both ways is the key to reading and writing them fluently.

```python run
result = [x.upper() for x in ["a", "b"]]
print(result)

result2 = []
for x in ["a", "b"]:
    result2.append(x.upper())
print(result2)
```

**Output:**
```
['A', 'B']
['A', 'B']
```

**Analysis.** The comprehension `[x.upper() for x in ...]` and the three-line loop produce the identical list. Read a comprehension by mentally expanding it: `[EXPR for VAR in ITER if COND]` becomes "make an empty list; for each VAR in ITER, if COND, append EXPR."

**Intuition.**
*Mechanism.* The two parts of a comprehension occupy different positions and mean different things. A **filter** `if` goes at the *end* and selects which items survive (no `else` allowed — an item either passes or doesn't). A **conditional expression** `a if cond else b` goes at the *front*, in the `expr` slot, and chooses the value for every item.

*Concrete bite.* Putting a filter-`if` with an `else` at the end is a syntax error, because a filter can't have an "otherwise":

```python run
nums = [1, 2, 3, 4]
print([x for x in nums if x % 2 == 0 else 0])   # filter-if cannot take an else
```
```
  File "/w/main.py", line 2
    print([x for x in nums if x % 2 == 0 else 0])   # filter-if cannot take an else
                                         ^^^^
SyntaxError: invalid syntax
```

The two correct forms are distinct — filter at the end (no `else`), transform at the front (with `else`):

```python run
nums = [1, 2, 3, 4]
print([x for x in nums if x % 2 == 0])         # filter: if at the END (no else)
print([x if x % 2 == 0 else 0 for x in nums])   # transform: if/else at the FRONT
```
```
[2, 4]
[0, 2, 0, 4]
```

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Position tells you the role: `if` at the **end** filters (keeps fewer items); `if/else` at the **front** transforms (same count, different values). The cost of mixing them up is a `SyntaxError` (for filter-with-else) or a wrong-length result — so decide first whether you're *selecting* items or *mapping* them.

</div>

---

## 3. Dict and set comprehensions

The same shape with `{}` builds a **dict** (`{k: v for ...}`) or a **set** (`{expr for ...}`).

```python run viz=hashmap:lengths
words = ["apple", "banana", "cherry"]
lengths = {w: len(w) for w in words}
first_letters = {w[0] for w in words}
print(lengths)
print(first_letters)
```

**Output (illustrative — the set's order is arbitrary and may differ for you):**
```
{'apple': 5, 'banana': 6, 'cherry': 6}
{'b', 'a', 'c'}
```

**Analysis.** `{w: len(w) for w in words}` builds a dict mapping each word to its length. `{w[0] for w in words}` builds a set of first letters (duplicates would collapse, and order is unspecified — [sets have no order](/synapse/programming-languages/python/working-with-data/dictionaries-and-sets)). The presence of a colon (`k: v`) is what makes it a *dict* comprehension rather than a *set* one.

**Intuition.**
*Mechanism.* Brackets choose the result type: `[]` → list, `{k: v ...}` → dict (colon present), `{expr ...}` → set (no colon). All four (including the generator in §4) share the identical `for`/`if` machinery; only the collector differs.

*Concrete bite.* The ambiguity of `{}` catches everyone — empty braces are a **dict**, not a set:

```python run
print(type({}).__name__)        # empty {} is a dict, not a set
print(type({1, 2}).__name__)    # braces with elements is a set
print(type(set()).__name__)     # the empty set
```
```
dict
set
set
```

`{}` is the empty dict (dicts predate sets in the syntax), so the empty *set* must be written `set()`. With elements, `{1, 2}` is unambiguously a set.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Reach for a dict comprehension to build mappings (`{obj.id: obj for obj in objs}`, invert with `{v: k for k, v in d.items()}`) and a set comprehension for unique results. Just remember the empty-set gotcha: `set()`, never `{}`. The cost is the same as any comprehension — the whole collection is built eagerly in memory.

</div>

---

## 4. Generator expressions

Swap the brackets for **parentheses** and you get a **generator expression** — same syntax, but it produces items **lazily**, one at a time, instead of building the whole collection. This is the memory-efficient choice for large or streamed data.

```python run
import sys
list_comp = [n * n for n in range(10000)]
gen_exp = (n * n for n in range(10000))
print(type(gen_exp).__name__)
print(sys.getsizeof(list_comp), "bytes (list)")
print(sys.getsizeof(gen_exp), "bytes (generator)")
print(sum(n * n for n in range(10000)))   # consumed lazily, no list built
```

**Output (exact byte sizes are CPython-specific):**
```
generator
85176 bytes (list)
200 bytes (generator)
333283335000
```

**Analysis.** The list comprehension built all 10,000 squares up front — ~85 KB. The generator expression stored almost nothing (~200 bytes); it computes each square only when asked. Passing a generator straight to `sum(...)` (note: no extra parentheses needed) computes the total without ever materializing the list — constant memory regardless of size.

**Intuition.**
*Mechanism.* A list comprehension is **eager**: it computes and stores every element immediately. A generator expression is **lazy**: it yields one element per request and forgets it, so memory stays flat no matter how many elements flow through. (This is the iterator protocol, the subject of [Tutorial 17](/synapse/programming-languages/python/how-python-works/iterators-and-generators).)

*Concrete bite.* Laziness has a cost: a generator is **single-use** — once consumed, it's empty:

```python run
gen = (n for n in range(3))
print(list(gen))    # first pass
print(list(gen))    # already exhausted
```
```
[0, 1, 2]
[]
```

The first `list(gen)` pulled all three values; the second finds the generator exhausted and gets `[]`. A list can be iterated again and again; a generator flows past once and is gone.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Use a generator expression when you'll consume the items **once** and want to avoid building a big list — `sum(...)`, `any(...)`, `max(...)`, or feeding a loop over millions of rows. Use a list comprehension when you need the result **more than once**, need its length, or need indexing. The cost of laziness is single-use and no `len()`; the cost of a list is the memory.

</div>

---

## 5. Nesting, flattening, and when not to

Comprehensions can contain multiple `for` clauses — most usefully to **flatten** a nested structure.

```python run viz=grid:matrix
matrix = [[1, 2], [3, 4], [5, 6]]
flat = [x for row in matrix for x in row]
print(flat)
```

**Output:**
```
[1, 2, 3, 4, 5, 6]
```

**Analysis.** Two `for` clauses flatten the matrix: for each `row` in `matrix`, for each `x` in `row`, collect `x`. The clauses read **left to right in the same order as nested loops** — outer (`for row in matrix`) first, inner (`for x in row`) second.

**Intuition.**
*Mechanism.* Multiple `for` clauses nest left-to-right exactly like written-out loops: the leftmost is the outermost. Each later clause can use the variables bound by earlier ones — but not the reverse.

*Concrete bite.* Write them in the "natural-looking" but wrong order — inner expression first — and the later-defined name isn't available yet:

```python run viz=grid:matrix
matrix = [[1, 2], [3, 4]]
flat = [x for x in row for row in matrix]   # wrong order: row used before its loop
```
```
Traceback (most recent call last):
  File "/w/main.py", line 2, in <module>
    flat = [x for x in row for row in matrix]   # wrong order: row used before its loop
                       ^^^
NameError: name 'row' is not defined. Did you mean: 'pow'?
```

`for x in row` comes first but `row` isn't defined until the *second* clause — so it's a `NameError`. The clause order must match nested-loop order: outer source first.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Use a multi-`for` comprehension to flatten one level (`[x for row in M for x in row]`), keeping clause order = outer-to-inner. But stop there: a comprehension with two `for`s and an `if`, or any you can't read at a glance, is *less* clear than a plain loop. The cost of cleverness is unreadability — when a comprehension needs a comment to explain it, write the loop instead.

</div>

---

## 6. Mental-model summary

| Principle | Consequence |
|-----------|-------------|
| `[expr for x in it if cond]` = transform + filter in one expression | Replaces the create-empty / loop / append pattern |
| `if` at the **end** filters; `a if c else b` at the **front** transforms | Filter-if with `else` is a `SyntaxError` |
| Brackets pick the type: `[]` list, `{k:v}` dict, `{e}` set, `()` generator | `{}` is an empty **dict**; the empty set is `set()` |
| List comp is **eager**; generator expression is **lazy** | Generator uses ~constant memory but is **single-use** |
| Multiple `for` clauses nest **outer-to-inner, left to right** | Wrong order → `NameError`; matches written-out loops |
| A comprehension runs in its **own scope** | The loop variable does not leak (unlike a `for` loop) |

## 7. Gotcha checklist

<div style="border-left:4px solid #da5233;background:rgba(218,82,51,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

- **`SyntaxError` near `else` in a comprehension →** you put a filter-`if` with `else` at the end; move `a if c else b` to the front, or drop the `else`.
- **`{}` gave me a dict, not a set →** empty braces are a dict; use `set()` for an empty set.
- **My generator is empty the second time →** generators are single-use; rebuild it, or use a list comp if you need it twice.
- **`NameError` for the inner variable in a nested comp →** clause order is outer-to-inner; put the source loop first.
- **Comprehension is unreadable →** if it has multiple `for`s/`if`s and needs a comment, write a plain loop instead.

</div>

---

<div style="border-left:4px solid #6d28d9;background:rgba(109,40,217,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

🧪 **Predict, then check.** Given `nums = [1, -2, 3, -4, 5]`, predict the output of three comprehensions: `[n for n in nums if n > 0]`, `[n if n > 0 else 0 for n in nums]`, and `{abs(n) for n in nums}` (will it have 5 elements?). Then predict what `g = (n for n in nums)` followed by `sum(g)` then `sum(g)` prints for each `sum`. The double-`sum` is the one that catches people — and it's the seed of the iterator protocol in Tier 3.

</div>

## Your Turn

Before you move on, check your understanding with the coach — explain the idea, apply it, weigh the trade-offs, then defend your reasoning.

<div class="concept-coach"></div>
