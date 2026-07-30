---
title: Standard-Library Tour
summary: The standard library ships high-leverage tools that replace hand-rolled code — collections (Counter, defaultdict, deque, namedtuple), itertools (lazy combinatorics), and functools (reduce, lru_cache, partial). The idioms that turn ten lines into one, with each tool's sharp edge shown.
prereqs: []
---

# The Standard-Library Tour — `collections`, `itertools`, `functools`

Python's slogan is "batteries included," and the batteries that pay off most for everyday code live in three modules. The thesis: **`collections`, `itertools`, and `functools` give you specialised containers and composable building blocks that replace whole patterns of hand-written code** — often turning a ten-line loop into a one-liner that's faster and clearer. Knowing they exist is half the battle; this chapter is a tour of the highest-leverage tools and the one gotcha each carries.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **The core idea.**

- `collections`, `itertools`, and `functools` are the highest-leverage batteries.
- They give **specialised containers** and composable building blocks.
- They replace whole patterns of hand-written code.
- Each carries **one gotcha** worth knowing.

</div>

This builds on [dicts & sets](/synapse/programming-languages/python/working-with-data/dictionaries-and-sets), [iterators](/synapse/programming-languages/python/how-python-works/iterators-and-generators), and [decorators](/synapse/programming-languages/python/how-python-works/functions-in-depth). Every output below was produced by running the code.

<div style="border-left:4px solid #15448e;background:rgba(21,68,142,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

📘 **How to read the Intuition boxes.** Each one is built in three moves:

1. **The mechanism** — what the interpreter is *actually doing*.
2. **A concrete bite** — a specific, runnable way the naive assumption fails.
3. **The earned rule** — the decision heuristic, now justified rather than asserted, plus its cost.

</div>

---

## Table of Contents

1. [`Counter` and `defaultdict`](#1-counter-and-defaultdict)
2. [`deque`](#2-deque)
3. [`itertools`](#3-itertools)
4. [`functools`](#4-functools)
5. [`namedtuple`](#5-namedtuple)
6. [Mental-model summary](#6-mental-model-summary)
7. [Gotcha checklist](#7-gotcha-checklist)

---

## 1. `Counter` and `defaultdict`

`collections.Counter` tallies occurrences; `defaultdict` supplies a default for missing keys. Both eliminate the boilerplate around the [counting idiom](/synapse/programming-languages/python/working-with-data/dictionaries-and-sets) from Tier 2.

```python run viz=hashmap:d
from collections import Counter, defaultdict
print(Counter("banana"))
print(Counter("banana").most_common(1))
d = defaultdict(list)
d["a"].append(1)
d["a"].append(2)
print(dict(d))
```

**Output:**
```
Counter({'a': 3, 'n': 2, 'b': 1})
[('a', 3)]
{'a': [1, 2]}
```

**Analysis.** `Counter("banana")` tallied every character in one call — replacing the whole `d.get(ch, 0) + 1` loop — and `.most_common(1)` returned the top entry. `defaultdict(list)` let `d["a"].append(1)` work even though `"a"` didn't exist yet: the first access auto-created an empty list. Both are dict subclasses, so everything you know about dicts still applies.

**Intuition.**
*Mechanism.* `Counter` is a dict mapping items to counts, built in C; its repr orders by descending count. `defaultdict(factory)` overrides the missing-key behaviour: on a miss it calls `factory()` (here `list()`), inserts the result, and returns it — so the key now exists.

*Concrete bite.* That auto-creation has a flip side worth knowing: a *Counter* returns `0` for a missing key without inserting it, but merely *reading* a missing key from a `defaultdict` **creates** it. With `Counter`:

```python run viz=hashmap:c
from collections import Counter
c = Counter("aaa")
print(c["z"])   # a missing key is 0, not a KeyError
```
```
0
```

`c["z"]` is `0` — convenient, and (unlike `defaultdict`) it doesn't add `"z"` to the counter. The trap is the reverse: `some_defaultdict[missing]` silently grows the dict, so checking membership with `[]` on a defaultdict pollutes it.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Reach for `Counter` to tally and rank (`most_common`), and `defaultdict(list/int/set)` to group or accumulate without pre-initialising keys. The cost is the defaultdict surprise — *reading* a missing key inserts it — so use `key in d` (not `d[key]`) to test membership on a defaultdict.

</div>

---

## 2. `deque`

`collections.deque` ("deck") is a double-ended queue: O(1) append and pop at **both** ends, unlike a list, where front operations are O(n) ([Tutorial 12](/synapse/programming-languages/python/working-with-data/sequences)).

```python run viz=deque:dq
from collections import deque
dq = deque([1, 2, 3])
dq.appendleft(0)
dq.append(4)
print(dq)
print(dq.popleft())
print(dq)
```

**Output:**
```
deque([0, 1, 2, 3, 4])
0
deque([1, 2, 3, 4])
```

**Analysis.** `appendleft`/`popleft` add and remove at the front in O(1) — the operations a list does in O(n) because it must shift every element. `deque` is the right structure for queues, sliding windows, and breadth-first search, where you push and pop at the ends.

**Intuition.**
*Mechanism.* A `deque` is a doubly-linked structure of blocks, so both ends are cheap; the trade is that **random access by index is O(n)** (it has to walk), whereas a list indexes in O(1). Different structure, different fast operations.

*Concrete bite.* A handy feature with a sharp edge: a `maxlen` deque silently **drops items from the far end** when it overflows:

```python run viz=deque:dq
from collections import deque
dq = deque([1, 2, 3], maxlen=2)
print(dq)
dq.append(4)
print(dq)
```
```
deque([2, 3], maxlen=2)
deque([3, 4], maxlen=2)
```

Creating it with `maxlen=2` immediately discarded the oldest (`1` → `deque([2, 3])`), and each `append` drops another from the left (`deque([3, 4])`). Perfect for "last N items," but if you didn't expect the dropping, data vanishes silently.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Use `deque` for FIFO queues and both-ends work (`appendleft`/`popleft`), and `maxlen` for a fixed-size rolling buffer. The cost is O(n) indexing — if you need fast random access by position, keep a list; if you need a fast front, keep a deque.

</div>

---

## 3. `itertools`

`itertools` provides lazy, composable iterators ([Tutorial 17](/synapse/programming-languages/python/how-python-works/iterators-and-generators)) for chaining, slicing, and combinatorics — building blocks you combine instead of writing loops.

```python run
import itertools
print(list(itertools.chain([1, 2], [3, 4])))
print(list(itertools.islice(itertools.count(10), 3)))
print(list(itertools.combinations("abc", 2)))
print([k + str(len(list(g))) for k, g in itertools.groupby("aabbbc")])
```

**Output:**
```
[1, 2, 3, 4]
[10, 11, 12]
[('a', 'b'), ('a', 'c'), ('b', 'c')]
['a2', 'b3', 'c1']
```

**Analysis.** `chain` flattens several iterables into one stream; `islice` takes a slice of any iterator (here the first 3 of the infinite `count(10)`); `combinations` yields all 2-element combos; `groupby` groups *consecutive* equal items. All are lazy — they yield on demand — which is why `islice` can safely slice an infinite `count`.

**Intuition.**
*Mechanism.* These return *iterators*, computing each item only when pulled. `groupby` in particular scans linearly and starts a new group whenever the key *changes* — it groups **consecutive** runs, not all equal items globally.

*Concrete bite.* That "consecutive" rule is the classic `groupby` trap — unsorted input produces split groups:

```python run
import itertools
for k, g in itertools.groupby("aabba"):
    print(k, len(list(g)))
```
```
a 2
b 2
a 1
```

The string `"aabba"` has three `a`s total, but `groupby` reports **two** `a`-groups (`a 2` and a later `a 1`) because the `a`s aren't all adjacent — the `bb` splits them. To group globally, **sort first** (`groupby(sorted(data))`).

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Compose `itertools` for lazy pipelines — `chain`/`islice`/`combinations`/`product`/`groupby` cover a huge range of loop-shaped problems. The cost/boundary: `groupby` only groups consecutive runs (sort first for global grouping), and the results are single-use iterators — wrap in `list()` if you need them twice.

</div>

---

## 4. `functools`

`functools` operates on functions. The headliners: `reduce` (fold a sequence to one value), `lru_cache` (memoise — [a decorator](/synapse/programming-languages/python/how-python-works/functions-in-depth)), and `partial` (pre-fill arguments).

```python run
import functools
print(functools.reduce(lambda a, b: a * b, [1, 2, 3, 4]))

@functools.lru_cache
def fib(n):
    return n if n < 2 else fib(n-1) + fib(n-2)
print(fib(30))
print(fib.cache_info())

double = functools.partial(lambda x, y: x * y, 2)
print(double(10))
```

**Output:**
```
24
832040
CacheInfo(hits=28, misses=31, maxsize=128, currsize=31)
20
```

**Analysis.** `reduce` folded `[1,2,3,4]` with `*` to `24`. `@lru_cache` made the naively-exponential `fib` linear by caching results — `cache_info()` shows 31 unique computations (`misses`) and 28 cache hits, so each `fib(n)` was computed once. `partial(f, 2)` produced a new function with the first argument fixed at `2`, so `double(10)` is `2 * 10`.

**Intuition.**
*Mechanism.* `reduce(f, seq)` applies `f` cumulatively: `f(f(f(1,2),3),4)`. `lru_cache` wraps the function in a memo dict keyed by the arguments (which must be hashable). `partial` returns a new callable that remembers some arguments.

*Concrete bite.* `reduce` on an **empty** sequence with no initial value has nothing to return, so it raises:

```python run
import functools
print(functools.reduce(lambda a, b: a + b, []))
```
```
Traceback (most recent call last):
  File "/w/main.py", line 2, in <module>
    print(functools.reduce(lambda a, b: a + b, []))
          ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^
TypeError: reduce() of empty iterable with no initial value
```

With no items and no seed, there's no value to produce — `TypeError`. Always pass an initial value (`reduce(f, seq, 0)`) when the sequence might be empty.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Use `lru_cache` to memoise pure functions with hashable arguments (huge wins on recursion), `partial` to specialise functions, and `reduce` *sparingly* — a plain loop or `sum`/`math.prod` is often clearer. The cost: `lru_cache` keeps results forever (memory) and needs hashable args; `reduce` with no initial value crashes on empty input.

</div>

---

## 5. `namedtuple`

`collections.namedtuple` builds a lightweight, immutable class with named fields — a tuple you can read by name, ideal for small records before reaching for a full class or `dataclass`.

```python run
from collections import namedtuple
Point = namedtuple("Point", ["x", "y"])
p = Point(1, 2)
print(p.x, p.y)
print(p)
print(p[0])         # also indexable
x, y = p            # and unpackable
print(x, y)
```

**Output:**
```
1 2
Point(x=1, y=2)
1
1 2
```

**Analysis.** `Point` is a new type with fields `x` and `y`. An instance reads by name (`p.x`), prints with a clear repr (`Point(x=1, y=2)`), and — because it *is* a tuple — also indexes (`p[0]`) and unpacks (`x, y = p`). You get readability and tuple behaviour for almost no code.

**Intuition.**
*Mechanism.* `namedtuple` generates a subclass of `tuple` with property accessors for the field names. So it has all tuple powers (indexing, unpacking, hashable, **immutable**) plus name access — and the immutability comes straight from `tuple`.

*Concrete bite.* Being a tuple, it's immutable — you cannot assign to a field:

```python run
from collections import namedtuple
P = namedtuple("P", ["x"])
p = P(1)
p.x = 2   # namedtuples are immutable
```
```
Traceback (most recent call last):
  File "/w/main.py", line 4, in <module>
    p.x = 2   # namedtuples are immutable
    ^^^
AttributeError: can't set attribute
```

`p.x = 2` raises `AttributeError` — a namedtuple is read-only, like the tuple it is. To "change" one, build a new instance (`p._replace(x=2)`).

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Use `namedtuple` for small immutable records where you want name access and tuple behaviour with zero boilerplate; reach for a `@dataclass` ([Tutorial 27](/synapse/programming-languages/python/object-oriented/advanced-oop)) when you need mutability, methods, or defaults. The cost is immutability (a feature for hashability/safety, a constraint when you need to mutate — use `_replace`).

</div>

---

## 6. Mental-model summary

| Principle | Consequence |
|-----------|-------------|
| `Counter` tallies; `defaultdict(factory)` auto-fills missing keys | `Counter[x]` is 0 (no insert); reading a `defaultdict` miss *inserts* it |
| `deque` is O(1) at both ends | Use for queues/windows; indexing is O(n); `maxlen` drops overflow silently |
| `itertools` are lazy, composable iterators | `groupby` groups only *consecutive* runs — sort first for global groups |
| `functools`: `reduce`, `lru_cache`, `partial` | `lru_cache` needs hashable args; `reduce([])` with no initial → `TypeError` |
| `namedtuple` = immutable tuple with named fields | Name access + tuple powers; can't assign fields (use `_replace`) |

## 7. Gotcha checklist

<div style="border-left:4px solid #da5233;background:rgba(218,82,51,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

- **A `defaultdict` grew keys I only read →** reading a missing key inserts it; test with `key in d`, not `d[key]`.
- **`deque` indexing felt slow →** it's O(n); use a list for random access, a deque for the ends.
- **`maxlen` deque lost data →** by design it drops the far end on overflow.
- **`groupby` split a group →** it only groups consecutive equal keys; `groupby(sorted(data))` for global grouping.
- **`reduce()` of empty iterable →** pass an initial value: `reduce(f, seq, start)`.
- **`AttributeError: can't set attribute` on a namedtuple →** it's immutable; use `p._replace(field=value)`.

</div>

---

<div style="border-left:4px solid #6d28d9;background:rgba(109,40,217,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

🧪 **Predict, then check.** Use `Counter` on `"mississippi"` and predict `.most_common(2)`. Then predict the output of `itertools.groupby("aaabbbaaa")` (how many groups, and why?) versus `groupby(sorted("aaabbbaaa"))`. Finally, memoise a recursive `factorial` with `@lru_cache` and predict `cache_info()` after calling `factorial(5)` once. The `groupby` one is the trap that catches everyone.

</div>

## Your Turn

Before you move on, check your understanding with the coach — explain the idea, apply it, weigh the trade-offs, then defend your reasoning.

<div class="concept-coach"></div>
