---
title: Performance, Profiling & Memory
summary: The first rule of optimisation is measure, don't guess — intuition about what's slow is usually wrong. timeit for microbenchmarks, why algorithmic complexity dominates everything, cProfile to find the real hotspot, and __slots__ for memory. Optimise what the numbers point at, not what you assume.
prereqs: []
---

# Performance, Profiling & Memory — Measure, Don't Guess

Making code fast is mostly about *not optimising the wrong thing*. The thesis: **measure before you optimise, because intuition about what's slow is usually wrong — and when something genuinely is slow, the cause is almost always algorithmic complexity, not the micro-details people fixate on.** This chapter gives you the measuring tools (`timeit`, `cProfile`), shows why a better data structure beats a hundred micro-tweaks, and covers `__slots__` for memory.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **The core idea.**

- **Measure before you optimise** — intuition about what's slow is usually wrong.
- When something genuinely is slow, the cause is almost always **algorithmic complexity**.
- Not the micro-details people fixate on.

</div>

This draws on [complexity](/synapse/programming-languages/python/working-with-data/sequences) and [sets](/synapse/programming-languages/python/working-with-data/dictionaries-and-sets). Every output below was produced by running the code; timing figures are marked illustrative because they vary run to run, but the *relationships* between them are the point.

<div style="border-left:4px solid #15448e;background:rgba(21,68,142,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

📘 **How to read the Intuition boxes.** Each one is built in three moves:

1. **The mechanism** — what the interpreter is *actually doing*.
2. **A concrete bite** — a specific, runnable way the naive assumption fails.
3. **The earned rule** — the decision heuristic, now justified rather than asserted, plus its cost.

</div>

---

## Table of Contents

1. [Measure with `timeit`](#1-measure-with-timeit)
2. [Complexity dominates everything](#2-complexity-dominates-everything)
3. [Memory and `__slots__`](#3-memory-and-__slots__)
4. [Profiling to find the hotspot](#4-profiling-to-find-the-hotspot)
5. [Don't guess: intuition misleads](#5-dont-guess-intuition-misleads)
6. [Mental-model summary](#6-mental-model-summary)
7. [Gotcha checklist](#7-gotcha-checklist)

---

## 1. Measure with `timeit`

`timeit` runs a snippet many times and reports the total — the right way to microbenchmark, because a single run is dominated by noise.

```python run
import timeit
t = timeit.timeit("sum(range(100))", number=10000)
print(f"10000 runs took {t:.4f}s")
```

**Output (illustrative — your exact time will differ):**
```
10000 runs took 0.0058s
```

**Analysis.** `timeit.timeit(stmt, number=N)` runs `stmt` `N` times and returns the **total** seconds for all `N`. Running many times and aggregating smooths out the jitter (OS scheduling, caches) that makes a single `time.perf_counter()` measurement unreliable for fast code.

**Intuition.**
*Mechanism.* `timeit` executes the statement in a tight loop `number` times, timing the whole loop with a high-resolution clock and disabling the garbage collector for stability. The result is the *sum* over all runs, not the per-call time.

*Concrete bite.* The classic misread is treating the result as per-call. The `0.0058s` above is for **10,000** runs — per call it's `0.0058 / 10000 ≈ 0.6 microseconds`. Report a snippet as "0.0058 seconds" without dividing and you'll overstate it by 10,000×. Always divide by `number` for a per-call figure.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Use `timeit` for small, fast snippets (with a large `number`), and divide by `number` for per-call time; for whole programs use a profiler (§4) instead. The cost/boundary: microbenchmarks are notoriously misleading out of context — a snippet's speed in isolation rarely reflects its impact in the real program, which is why profiling the actual workload (§4) matters more than benchmarking fragments.

</div>

---

## 2. Complexity dominates everything

The single biggest performance lever is **algorithmic complexity** — O(n) vs O(1) — not micro-optimisation. The list-vs-set membership gap from Tier 2 makes it vivid.

```python run
import timeit
L = list(range(100000))
S = set(L)
tl = timeit.timeit(lambda: 99999 in L, number=1000)
ts = timeit.timeit(lambda: 99999 in S, number=1000)
print(f"list: {tl:.4f}s   set: {ts:.6f}s   ratio: {tl/ts:.0f}x")
```

**Output (illustrative — exact times vary, the ratio is the point):**
```
list: 0.4454s   set: 0.000031s   ratio: 14377x
```

**Analysis.** Membership in a 100,000-element list (`O(n)` — scans every element) versus a set (`O(1)` — hashes and jumps) differs by *four orders of magnitude*. No amount of micro-tuning the list version could close that gap; the set is faster because of its *complexity class*, not its constant factors. This is the lever that matters.

**Intuition.**
*Mechanism.* `x in list` compares against each element (up to `n` checks); `x in set` hashes `x` once and probes one bucket. As `n` grows, the list cost grows linearly while the set cost stays flat — so the ratio *widens* with size. Complexity beats constants at scale, always.

*Concrete bite.* The numbers are the bite: **14,000×** from one data-structure change. Programmers routinely spend hours shaving constant factors (a faster loop, a `+=` tweak — [Tutorial 15](/synapse/programming-languages/python/working-with-data/strings-in-depth)) while an `O(n²)` algorithm hides in plain sight. The hours-long micro-optimisation is dwarfed by a one-line `list` → `set`.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Before optimising anything, ask "what's the complexity?" — fix `O(n²)`/`O(n)` hot paths (right data structure, right algorithm) before touching constants. The cost of the wrong structure is unbounded as data grows; the cost of fixing it is usually a one-line change to the right container. Micro-optimisation is the *last* resort, not the first.

</div>

---

## 3. Memory and `__slots__`

By default every instance stores its attributes in a per-instance `__dict__`, which is flexible but memory-heavy. Declaring `__slots__` replaces it with a fixed, compact layout — a big saving when you have millions of objects.

```python run
import sys

class WithDict:
    def __init__(self):
        self.x = 1
        self.y = 2

class WithSlots:
    __slots__ = ('x', 'y')
    def __init__(self):
        self.x = 1
        self.y = 2

a = WithDict()
b = WithSlots()
print('plain (instance + __dict__):', sys.getsizeof(a) + sys.getsizeof(a.__dict__), 'bytes')
print('slots:', sys.getsizeof(b), 'bytes')
```

**Output (illustrative — exact sizes are CPython-specific):**
```
plain (instance + __dict__): 344 bytes
slots: 48 bytes
```

**Analysis.** The plain instance plus its `__dict__` is ~344 bytes; the `__slots__` instance is ~48 bytes — roughly **7× smaller**, because `__slots__` stores the two attributes in fixed slots instead of a hash table. Multiply by millions of instances and that's the difference between fitting in memory and not.

**Intuition.**
*Mechanism.* Without `__slots__`, each instance owns a `__dict__` (a hash table) so you can add arbitrary attributes. `__slots__` tells Python the exact attribute names up front, so it allocates a small fixed array and **no `__dict__`** — saving the dict's overhead per instance.

*Concrete bite.* The trade-off is rigidity: with `__slots__` you can't add attributes that aren't declared:

```python run
class Point:
    __slots__ = ('x', 'y')
    def __init__(self, x, y):
        self.x = x
        self.y = y

p = Point(1, 2)
p.z = 3   # not in __slots__
```
```
Traceback (most recent call last):
  File "/w/main.py", line 8, in <module>
    p.z = 3   # not in __slots__
    ^^^
AttributeError: 'Point' object has no attribute 'z' and no __dict__ for setting new attributes
```

`p.z = 3` raises because there's no `__dict__` to hold an undeclared attribute. That rigidity is exactly what saves the memory — but it also means no dynamic attributes, and it interacts awkwardly with multiple inheritance.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Reach for `__slots__` when you have *many* instances of a small class and memory matters (data points, graph nodes, ORM rows); skip it otherwise — the flexibility of `__dict__` is worth more than bytes for ordinary objects. The cost is rigidity (no new attributes, `__slots__` must be coordinated across a class hierarchy), so it's a targeted optimisation, not a default. (Measure first — `sys.getsizeof` and a memory profiler tell you if it's worth it.)

</div>

---

## 4. Profiling to find the hotspot

For a whole program, don't guess where the time goes — **profile** it. `cProfile` runs your code and reports, per function, how many times it was called and how long it took.

```python run
import cProfile

def slow():
    return sum(i * i for i in range(100000))

def main():
    for _ in range(10):
        slow()

cProfile.run("main()")
```

**Output (illustrative — times vary; the call counts and ranking are the signal):**
```
         1000034 function calls in 0.126 seconds

   Ordered by: standard name

   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
        1    0.000    0.000    0.126    0.126 <string>:1(<module>)
       10    0.000    0.000    0.126    0.013 main.py:3(slow)
  1000010    0.055    0.000    0.055    0.000 main.py:4(<genexpr>)
        1    0.000    0.000    0.126    0.126 main.py:6(main)
        1    0.000    0.000    0.126    0.126 {built-in method builtins.exec}
       10    0.071    0.007    0.126    0.013 {built-in method builtins.sum}
        1    0.000    0.000    0.000    0.000 {method 'disable' ...}
```

**Analysis.** The profile shows the truth: time is split between `sum` (`0.071s`) and the generator expression (`0.055s`, called **1,000,010** times). The `tottime` column (time *in* that function, excluding sub-calls) is where to look first; `cumtime` includes sub-calls. The hotspot is the inner squaring loop — which a profiler tells you precisely, instead of you guessing.

**Intuition.**
*Mechanism.* `cProfile` instruments every function call, recording counts and timings, then prints a table you sort by `tottime` (self time) or `cumtime` (total including callees). The highest-`tottime` rows are your hotspots — the only places optimisation will move the needle.

*Concrete bite.* The bite is what the profile reveals vs. what you'd assume: people optimise the function they *think* is slow, but the profiler often fingers a different one — here, a tiny `<genexpr>` called a million times dominates, not the visually "big" `main`. Optimising anything *not* near the top of the `tottime` list is wasted effort, because it's not where the time is.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Profile the real workload with `cProfile` (or `python -m cProfile script.py`) and optimise the top `tottime` entries first; ignore everything below them. The cost is profiling overhead (so profile representative inputs, not toy ones) — but it's the only way to know where time actually goes, which is the whole game.

</div>

---

## 5. Don't guess: intuition misleads

Even seasoned programmers guess wrong about micro-performance. The discipline: when two approaches seem close, **measure** — don't argue from intuition or folklore.

```python run
import timeit
# Sum of squares two ways. Which is faster? Predict, then measure.
loop = timeit.timeit("s=0\nfor i in range(1000): s+=i*i", number=1000)
comp = timeit.timeit("sum(i*i for i in range(1000))", number=1000)
print(f"loop: {loop:.4f}s   genexpr-sum: {comp:.4f}s")
```

**Output (illustrative — exact times vary):**
```
loop: 0.0264s   genexpr-sum: 0.0318s
```

**Analysis.** Conventional wisdom says the "Pythonic" `sum(generator)` should beat the explicit loop — but here the **plain loop is actually faster** (the generator's per-item function-call overhead outweighs `sum`'s C-level speed at this size). The point isn't that loops are always faster (they often aren't); it's that the *answer was not obvious*, and only measurement settled it.

**Intuition.**
*Mechanism.* Performance depends on details that defy intuition — interpreter version, data size, C-level shortcuts, call overhead, cache effects. Two reasonable-looking approaches can flip in ranking with size or Python version, so any confident claim about "X is faster than Y" without a measurement is a guess.

*Concrete bite.* The output is the bite: the supposedly-slower explicit loop beat the idiomatic `sum(genexpr)`. Anyone who "optimised" by blindly converting the loop to a comprehension here would have made it *slower* — and felt clever doing it. Folklore ("comprehensions are always faster," "`+=` is always quadratic" — [Tutorial 15](/synapse/programming-languages/python/working-with-data/strings-in-depth)) is how you optimise in the wrong direction.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Write for **clarity first**, then measure if it's actually too slow, then optimise the measured hotspot — in that order. The cost of premature optimisation is real: complex, "fast" code that's harder to read and often no faster (or slower). "Measure, don't guess" is the whole chapter; the profiler and `timeit` are how you obey it.

</div>

---

## 6. Mental-model summary

| Principle | Consequence |
|-----------|-------------|
| `timeit` runs a snippet `number` times, returns the **total** | Divide by `number` for per-call; one run is just noise |
| Algorithmic complexity dominates constant factors | `list`→`set` membership is ~10⁴× faster; fix `O(n²)` first |
| `__slots__` removes the per-instance `__dict__` | ~7× less memory per object, but no dynamic attributes |
| `cProfile` shows where time *actually* goes | Optimise the top `tottime` rows; ignore the rest |
| Intuition about micro-performance is unreliable | Measure before optimising; clarity first, speed only where it's needed |

## 7. Gotcha checklist

<div style="border-left:4px solid #da5233;background:rgba(218,82,51,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

- **Reported a snippet as too slow →** `timeit` returns total for `number` runs; divide for per-call.
- **Optimised for hours with little gain →** you tuned constants; find and fix the `O(n²)`/`O(n)` hotspot instead.
- **`AttributeError: ... no __dict__` →** the class has `__slots__`; declare the attribute in `__slots__` or drop it.
- **Optimised the wrong function →** profile with `cProfile` and target the highest `tottime`.
- **"Pythonic = faster" assumption →** not always; measure two approaches before rewriting, and prefer clarity.

</div>

---

<div style="border-left:4px solid #6d28d9;background:rgba(109,40,217,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

🧪 **Predict, then check.** Predict the ratio between `x in a_list` and `x in a_set` for 1,000,000 elements (bigger or smaller than the 100k case?). Then predict whether `sum(i*i for i in range(N))` beats a plain loop at `N = 1_000_000` (does the ranking hold at larger sizes?). Build both with `timeit` and check — the goal is to *stop predicting and start measuring*, which is the entire discipline of performance work.

</div>

## Your Turn

Before you move on, check your understanding with the coach — explain the idea, apply it, weigh the trade-offs, then defend your reasoning.

<div class="concept-coach"></div>
