---
title: Strings in Depth
summary: Text work is a small set of composable tools — the format mini-language, split/join, a handful of methods, and slicing — plus one accumulation rule. The deep pass of Strings, including the truth about whether += in a loop is really quadratic (on CPython, it usually isn't).
prereqs: []
---

# Strings in Depth — The Format Language, Text Algorithms & the `+=` Question

This is the deep pass of [Strings, the Basics](/synapse/programming-languages/python/first-steps/strings-the-basics). The thesis: **almost all real text work is a small, composable toolkit** — the format mini-language, the `split`/`join` pair, a few search-and-edit methods, and slicing — and once you have those, the only remaining question is how to *accumulate* text efficiently. That last question has a famous answer ("never `+=` in a loop, it's quadratic") that turns out to be more interesting than the slogan suggests.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **The core idea.**

- Almost all real text work is a **small, composable toolkit**.
- The toolkit: the format mini-language, `split`/`join`, a few search-and-edit methods, and slicing.
- The one remaining question is how to **accumulate** text efficiently.

</div>

Every output below was produced by running the code — including the performance measurements, which are marked illustrative because exact timings vary.

<div style="border-left:4px solid #15448e;background:rgba(21,68,142,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

📘 **How to read the Intuition boxes.** Each one is built in three moves:

1. **The mechanism** — what the interpreter is *actually doing*.
2. **A concrete bite** — a specific, runnable way the naive assumption fails.
3. **The earned rule** — the decision heuristic, now justified rather than asserted, plus its cost.

</div>

---

## Table of Contents

1. [The format mini-language](#1-the-format-mini-language)
2. [`split` and `join` mastery](#2-split-and-join-mastery)
3. [Common text algorithms](#3-common-text-algorithms)
4. [Slicing patterns for text](#4-slicing-patterns-for-text)
5. [Building strings: the `+=` question](#5-building-strings-the--question)
6. [Mental-model summary](#6-mental-model-summary)
7. [Gotcha checklist](#7-gotcha-checklist)

---

## 1. The format mini-language

Inside an f-string ([Tutorial 4](/synapse/programming-languages/python/first-steps/strings-the-basics)), a colon after the value introduces a **format spec** controlling width, alignment, precision, and representation.

```python run
pi = 3.14159
print(f"{pi:.2f}")          # precision
print(f"{42:>6}")           # right-align width 6
print(f"{42:<6}|")          # left-align
print(f"{42:^6}")           # center
print(f"{255:x}")           # hex
print(f"{1000000:,}")       # thousands separator
print(f"{0.875:.1%}")       # percentage
```

**Output:**
```
3.14
    42
42    |
  42  
ff
1,000,000
87.5%
```

**Analysis.** Each spec after the `:` reshapes the value: `.2f` fixes two decimals, `>6`/`<6`/`^6` pad to width 6 (right/left/center), `x` renders hex, `,` groups thousands, `.1%` shows a fraction as a percentage. The value's *type* and the spec must agree — `.2f` means "fixed-point float."

**Intuition.**
*Mechanism.* The format spec is a tiny language: `[fill][align][width][,][.precision][type]`. Python parses it and asks the value to render itself accordingly. So the spec must match the value's type — a float type code (`f`, `%`, `e`) on a non-number is meaningless.

*Concrete bite.* Apply a numeric format to a string and it raises:

```python run
print(f"{'hi':.2f}")   # .2f is a number format, applied to a string
```
```
Traceback (most recent call last):
  File "/w/main.py", line 1, in <module>
    print(f"{'hi':.2f}")   # .2f is a number format, applied to a string
            ^^^^^^^^^^
ValueError: Unknown format code 'f' for object of type 'str'
```

`.2f` asks for fixed-point formatting, which a string can't provide, so Python raises `ValueError`. (Strings accept alignment/width specs like `:>10`, just not numeric ones.)

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Memorize the high-value specs — `.2f` (money/measurements), `,` (readable big numbers), `>`/`<`/`^` with a width (aligned columns), `.1%` (rates). The cost of a type/spec mismatch is a `ValueError` at format time — so keep numeric specs for numbers and alignment specs for either.

</div>

---

## 2. `split` and `join` mastery

`split` turns a string into a list; `join` turns a list back into a string. They're inverses, and the canonical way to move between text and structured data.

```python run viz=array:parts
csv = "a,b,c,d"
parts = csv.split(",")
print(parts)
print("|".join(parts))
print("one two three".split())     # default splits on whitespace
print("a,b,,c".split(","))         # empty fields preserved
```

**Output:**
```
['a', 'b', 'c', 'd']
a|b|c|d
['one', 'two', 'three']
['a', 'b', '', 'c']
```

**Analysis.** `split(sep)` breaks on each separator; with no argument it splits on *runs* of whitespace (and drops empties), which is what you want for words. With an explicit separator, **consecutive separators produce empty strings** (`"a,b,,c"` → `['a','b','','c']`) — important when parsing fixed-format data. `join` is called on the *separator* and takes the list.

**Intuition.**
*Mechanism.* `sep.join(items)` walks the list and concatenates with `sep` between — but it requires **every item to already be a string**, because it has nothing to convert non-strings with.

*Concrete bite.* Joining a list of numbers fails:

```python run
print("-".join([1, 2, 3]))   # join needs strings
```
```
Traceback (most recent call last):
  File "/w/main.py", line 1, in <module>
    print("-".join([1, 2, 3]))   # join needs strings
          ~~~~~~~~^^^^^^^^^^^
TypeError: sequence item 0: expected str instance, int found
```

`join` can't concatenate an `int`, so it raises. Convert first: `"-".join(str(n) for n in [1, 2, 3])` (a generator expression — [Tutorial 14](/synapse/programming-languages/python/working-with-data/comprehensions)) gives `"1-2-3"`.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** `split`/`join` are your primary text↔list bridge; reach for them over manual character loops. Remember two things: the *separator owns* `join` (`sep.join(items)`, the direction everyone forgets), and `join` needs all-string items, so map non-strings through `str()` first. The cost is nil — this is the idiomatic, fast path.

</div>

---

## 3. Common text algorithms

A handful of methods cover most text inspection and editing. They all return new strings or simple values — strings are immutable, so nothing edits in place.

```python run
s = "  Hello, World!  "
print(s.strip())
print(s.strip().lower())
print(s.count("l"))
print("hello".find("xyz"))      # -1 if not found
print("file.txt".endswith(".txt"))
print("Hello".replace("l", "L"))
```

**Output:**
```
Hello, World!
hello, world!
3
-1
True
HeLLo
```

**Analysis.** `strip` trims surrounding whitespace; methods **chain** because each returns a new string (`s.strip().lower()`). `count` tallies occurrences; `find` returns the first index *or `-1`*; `endswith`/`startswith` return bools; `replace` swaps all occurrences. None mutate `s`.

**Intuition.**
*Mechanism.* `find` reports "not found" by returning `-1` — a sentinel value, not an error — so it never raises. Its sibling `index` does the same search but **raises** when the substring is absent.

*Concrete bite.* Reaching for `index` on a possibly-absent substring crashes:

```python run
print("hello".index("z"))   # index raises when find would return -1
```
```
Traceback (most recent call last):
  File "/w/main.py", line 1, in <module>
    print("hello".index("z"))   # index raises when find would return -1
          ~~~~~~~~~~~~~^^^^^
ValueError: substring not found
```

`index("z")` can't find `z`, so unlike `find` (which would return `-1`), it raises `ValueError`.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Use `find` (or, better, `if "z" in s`) when absence is normal and expected; use `index` only when absence is a genuine error you *want* to raise. The cost of confusing them is an unhandled `ValueError` where you expected a quiet `-1` — and the `-1` itself is a trap, since `if s.find(x):` is true for index `0` too; prefer `in` for presence tests.

</div>

---

## 4. Slicing patterns for text

Slicing ([Tutorial 12](/synapse/programming-languages/python/working-with-data/sequences)) gives strings a set of one-line idioms.

```python run
s = "Python"
print(s[::-1])          # reverse
print(s[::2])           # every other
word = "racecar"
print(word == word[::-1])   # palindrome check
print("hello world"[6:])    # from index 6
```

**Output:**
```
nohtyP
Pto
True
world
```

**Analysis.** `s[::-1]` reverses (a negative step); `s[::2]` takes every second character; comparing a string to its reverse is a one-line palindrome test; `s[6:]` takes everything from index 6. Each slice produces a **new** string.

**Intuition.**
*Mechanism.* String slices follow the exact half-open, step-aware rules of any sequence — but because strings are **immutable**, slicing can only *read*. There is no slice **assignment** for strings (unlike lists, where `lst[a:b] = ...` works).

*Concrete bite.* Slice assignment on a string is rejected:

```python run
s = "hello"
s[0:2] = "HE"   # strings are immutable - no slice assignment
```
```
Traceback (most recent call last):
  File "/w/main.py", line 2, in <module>
    s[0:2] = "HE"   # strings are immutable - no slice assignment
    ~^^^^^
TypeError: 'str' object does not support item assignment
```

You can *read* `s[0:2]` but not *assign* to it — strings never change in place. To "edit," build a new string: `"HE" + s[2:]`.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Keep the three text-slice idioms handy — `s[::-1]` (reverse), `s[::2]` (stride), `s[a:b]` (substring) — and remember they only read. The cost of immutability is that every "edit" allocates a new string, which leads directly to the accumulation question below.

</div>

---

## 5. Building strings: the `+=` question

Here's a rule you'll hear stated as gospel: *"Never build a string with `+=` in a loop — it's O(N²), because each `+=` copies the whole string."* Strings are immutable, so in principle each `s += chunk` must allocate a new string and copy everything so far. Let's actually measure it on this runner.

```python run
import time
def grow_plus(n):
    s = ""
    for _ in range(n):
        s += "x"
    return len(s)
def grow_join(n):
    parts = []
    for _ in range(n):
        parts.append("x")
    return len("".join(parts))
for n in [200000, 400000, 800000]:
    t0 = time.perf_counter(); grow_plus(n); tp = time.perf_counter() - t0
    t0 = time.perf_counter(); grow_join(n); tj = time.perf_counter() - t0
    print(f"n={n:>7}  plus={tp:.4f}s  join={tj:.4f}s  ratio={tp/tj:.1f}x")
```

**Output (illustrative — exact times vary; watch the *scaling*, not the absolute numbers):**
```
n= 200000  plus=0.0054s  join=0.0040s  ratio=1.4x
n= 400000  plus=0.0119s  join=0.0092s  ratio=1.3x
n= 800000  plus=0.0245s  join=0.0176s  ratio=1.4x
```

**Analysis.** The slogan predicts disaster for `+=`, but the numbers tell a different story: as `n` *doubles*, the `+=` time also roughly *doubles* (0.005 → 0.012 → 0.025) — that's **linear**, not quadratic (quadratic would *quadruple* each step). And `+=` is only ~1.4× slower than `join`, a constant factor, not a blowup. On CPython, the famous quadratic catastrophe doesn't happen here.

**Intuition.**
*Mechanism.* Strings are immutable, so `s += chunk` should build a new string each time — that *would* be O(N²). But **CPython special-cases it**: when the string on the left has no other references, the interpreter *resizes its buffer in place* instead of copying, making the loop amortized O(n). The measurement above is that optimization at work.

*Concrete bite.* The trap is that this is a **CPython implementation detail, not a language guarantee** — and it silently evaporates. It's absent on other implementations (PyPy, Jython, IronPython), and it disappears the moment the string gains another reference: keep a snapshot each step (`history.append(s)`) and every `+=` must copy again, restoring the O(N²) behavior — and the growing copies exhaust memory fast. So code that's perfectly fast on CPython today can become a quadratic hang after an innocent refactor that holds onto the string, or when run on a different interpreter.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Build strings with `"".join(parts)`: it's **guaranteed O(n) on every implementation**, it can't be sabotaged by an extra reference, and it states the intent ("assemble these pieces") plainly. Treat CPython's `+=` optimization as a convenience you never *rely* on. The cost of `join` is a temporary list buffer and one extra pass — negligible, and a price worth paying to never depend on a fragile optimization. (The deeper "measure before you optimize" discipline is [Performance & Profiling](/synapse/programming-languages/python/advanced/performance-and-profiling) in Tier 5.)

</div>

---

## 6. Mental-model summary

| Principle | Consequence |
|-----------|-------------|
| Format spec `:[align][width][,][.prec][type]` | `.2f`, `,`, `>6`, `.1%`; type must match the value or `ValueError` |
| `split`/`join` bridge text ↔ list | `sep.join(items)`; `join` needs all-string items |
| `split()` (no arg) splits on whitespace; `split(sep)` keeps empties | `"a,,b".split(",")` → `['a','','b']` |
| `find` returns `-1`; `index` raises | Use `find`/`in` when absence is normal |
| Strings are immutable: slices read, never assign | `s[a:b] = ...` is a `TypeError`; build a new string |
| `+=` is O(n) on **CPython** (in-place opt), not guaranteed elsewhere | Use `"".join(parts)` for portable, guaranteed O(n) |

## 7. Gotcha checklist

<div style="border-left:4px solid #da5233;background:rgba(218,82,51,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

- **`ValueError: Unknown format code 'f' ...` →** a numeric format spec on a string; use alignment specs for strings, numeric for numbers.
- **`TypeError: ... expected str instance, int found` →** `join` got non-strings; `sep.join(str(x) for x in items)`.
- **`split(",")` gave empty strings →** consecutive separators produce empties; that's correct — use `split()` (no arg) for word-splitting.
- **`index` crashed on a missing substring →** use `find` (returns `-1`) or `in` when absence is expected.
- **`s[a:b] = ...` failed →** strings are immutable; rebuild (`s[:a] + new + s[b:]`).
- **Worried `+=` in a loop is quadratic →** on CPython it's usually linear, but use `"".join(parts)` for a guarantee that survives refactors and other interpreters.

</div>

---

<div style="border-left:4px solid #6d28d9;background:rgba(109,40,217,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

🧪 **Predict, then check.** Build a function that formats a price as `"$1,234.50"` from the number `1234.5` using one f-string (hint: `,` and `.2f` combine as `:,.2f`). Then take `"the quick brown fox"`, split it into words, and `join` them back with newlines — predict the output before running. Finally, re-run the §5 benchmark at `n = [100000, 200000, 400000]` and confirm the `+=` time scales *linearly* (doubles, not quadruples) on this CPython runner.

</div>

## Your Turn

Before you move on, check your understanding with the coach — explain the idea, apply it, weigh the trade-offs, then defend your reasoning.

<div class="concept-coach"></div>
