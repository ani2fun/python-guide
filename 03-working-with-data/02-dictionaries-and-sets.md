---
title: Dictionaries & Sets
summary: Dicts and sets share one engine — hashing — which buys O(1) average lookup. A dict maps keys to values; a set is keys with no values. Hashing, safe access with get, the counting idiom, comprehensions, hashability, set algebra, O(1) membership, and frozenset — with the unhashable-key, KeyError, and merge-order traps shown live.
prereqs: []
---

# Dictionaries & Sets — Hashing as the Shared Engine

Dicts and sets are Python's **hash-based** collections, and they share one engine: **hashing**, which buys near-constant-time lookup. A dict maps keys to values; a set is a dict with keys but no values. Understand hashing once and both their power and their constraints (why keys must be hashable, why sets have no order) follow directly.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **The core idea.**

- Dicts and sets share one engine: **hashing**.
- Hashing buys near-constant-time lookup.
- A dict maps keys to values; a set is keys with no values.

</div>

This builds on [Sequences](/synapse/programming-languages/python/working-with-data/sequences) — especially the tuple-hashability discussion — and on [list membership being O(n)](/synapse/programming-languages/python/control-flow/lists-the-basics). Every output below was produced by running the code.

<div style="border-left:4px solid #15448e;background:rgba(21,68,142,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

📘 **How to read the Intuition boxes.** Each one is built in three moves:

1. **The mechanism** — what the interpreter is *actually doing*.
2. **A concrete bite** — a specific, runnable way the naive assumption fails.
3. **The earned rule** — the decision heuristic, now justified rather than asserted, plus its cost.

</div>

---

## Table of Contents

1. [The core idea: hashing](#1-the-core-idea-hashing)
2. [Dictionaries: the mapping](#2-dictionaries-the-mapping)
3. [Safe access: `get` and `setdefault`](#3-safe-access-get-and-setdefault)
4. [Iterating and comprehensions](#4-iterating-and-comprehensions)
5. [What can be a key: hashability](#5-what-can-be-a-key-hashability)
6. [Merging dicts](#6-merging-dicts)
7. [Sets: membership and algebra](#7-sets-membership-and-algebra)
8. [The killer feature: O(1) membership](#8-the-killer-feature-o1-membership)
9. [`frozenset` and deduplication](#9-frozenset-and-deduplication)
10. [Mental-model summary](#10-mental-model-summary)

---

## 1. The core idea: hashing

A **hash function** turns an object into an integer. A hash table uses that integer to decide *where* to store the object, so finding it later is a direct jump rather than a search.

```python run
print(hash("hello"))      # varies per run for strings
print(hash(42))           # ints hash to themselves
print(hash((1, 2)))       # tuples are hashable
```

**Output (illustrative — the string hash changes every run):**
```
6479512370364792116
42
-3550055125485641917
```

**Analysis.** Hashing maps an object to a bucket index. To look up a key, Python hashes it, jumps to the bucket, and checks — **O(1) on average**, regardless of how many items are stored. This is the whole reason dicts and sets are fast. (Run the block yourself: `hash(42)` is always `42`, but the string's hash differs each run — Python randomizes string hashing for security.) The catch: only **immutable** (hashable) objects can be keys.

**Intuition.**
*Mechanism.* The hash of a key determines *which bucket* it goes in. Lookup re-hashes the key, jumps straight to that bucket, and checks — so cost is roughly constant no matter how many entries exist. This only works if a key's hash never changes while it's stored; a key whose value (and thus hash) could change mid-storage would become unfindable. That's why keys must be **immutable**, and Python enforces it up front.

*Concrete bite.* The enforcement is a hard error, not a silent misfile:

```python run
d = {}
d[[1, 2]] = "x"      # a list cannot be a key
```
```
Traceback (most recent call last):
  File "/w/main.py", line 2, in <module>
    d[[1, 2]] = "x"      # a list cannot be a key
    ~^^^^^^^^
TypeError: unhashable type: 'list'
```

Python refuses a list key rather than let you create an entry that could later be lost in the wrong bucket. (Contrast a tuple key, which is allowed — it can't change.)

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** "Can X be a dict key or set element?" reduces to "is X immutable/hashable?" Strings, numbers, bools, and tuples-of-hashables: yes. Lists, dicts, sets: no — convert (`tuple(my_list)`, `frozenset(my_set)`) first. The single hashing mechanism explains *everything* downstream: the O(1) speed, the key constraint, and the lack of set ordering.

</div>

---

## 2. Dictionaries: the mapping

A **dict** maps **keys → values**. Access, insertion, and deletion by key are all O(1) average.

```python run viz=hashmap:d
d = {"a": 1, "b": 2}
print(d["a"])         # access by key
d["c"] = 3            # insert (or update if key exists)
print(d)
print(list(d.keys()))
print(list(d.values()))
print(list(d.items()))
```

**Output:**
```
1
{'a': 1, 'b': 2, 'c': 3}
['a', 'b', 'c']
[1, 2, 3]
[('a', 1), ('b', 2), ('c', 3)]
```

**Insertion order is preserved (Python 3.7+):**

```python run viz=hashmap:od
od = {}
for k in ["z", "a", "m"]:
    od[k] = 1
print(list(od.keys()))
```

**Output:**
```
['z', 'a', 'm']
```

**Analysis.** `d[key]` retrieves a value; `d[key] = v` inserts or overwrites. `.keys()`, `.values()`, `.items()` are *live views* onto the dict (they reflect later changes and are iterable), and `.items()` yields `(key, value)` tuples — perfect for unpacking ([Sequences §8](/synapse/programming-languages/python/working-with-data/sequences)). Since Python 3.7, iteration yields keys in **insertion order** (`z, a, m`, not sorted). Sets still do **not** guarantee order.

**Intuition.**
*Mechanism.* A dict is a lookup table keyed by hash (§1), so `d[key]` is O(1) average whether the dict holds ten or ten million entries. The views aren't snapshots — they're *live*, tied to the dict.

*Concrete bite.* Because views are live, mutating a dict's *size* while iterating raises mid-loop:

```python run viz=hashmap:d
d = {1: 'a', 2: 'b', 3: 'c'}
for k in d:
    d[k * 10] = 'x'      # adding keys during iteration
```
```
Traceback (most recent call last):
  File "/w/main.py", line 2, in <module>
    for k in d:
             ^
RuntimeError: dictionary changed size during iteration
```

Adding keys during iteration would invalidate the view's cursor, so Python stops you. (Iterate over `list(d)` if you must add/remove while looping.)

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Use a dict whenever you have a *lookup* relationship (name → record, word → count, id → object) — access stays fast at any size. Iterate pairs with `.items()`, and rely on insertion-order being preserved (handy for the dedup trick in §9). When you need to modify a dict's size during a loop, iterate a *materialized snapshot* (`list(d)`), not the live view.

</div>

---

## 3. Safe access: `get` and `setdefault`

Indexing a missing key raises `KeyError`. `get` handles absence gracefully.

```python run viz=hashmap:counts
d = {"a": 1}
print(d.get("z", 0))     # missing key -> default, no error

counts = {}
for ch in "banana":
    counts[ch] = counts.get(ch, 0) + 1
print(counts)
```

**Output:**
```
0
{'b': 1, 'a': 3, 'n': 2}
```

**Analysis.** `d.get(key, default)` returns the value if present, else `default` (default `None`) — never raises. The counting idiom `counts.get(ch, 0) + 1` reads as "current count or zero, plus one," the canonical way to tally without pre-initializing every key. Note the result is in **insertion order** of first appearance: `b, a, n`. (`collections.Counter` and `defaultdict` automate this — see the [stdlib tour](/synapse/programming-languages/python/advanced/standard-library-tour).)

**Intuition.**
*Mechanism.* `d[key]` demands the key exist and raises `KeyError` if not. `d.get(key, default)` instead returns `default` on a miss — folding "check if present, else use a fallback" into one expression with no branch.

*Concrete bite.* Without `get`, the natural first attempt at counting crashes on the very first character:

```python run
counts = {}
for ch in "banana":
    counts[ch] = counts[ch] + 1   # read before the key exists
```
```
Traceback (most recent call last):
  File "/w/main.py", line 3, in <module>
    counts[ch] = counts[ch] + 1   # read before the key exists
                 ~~~~~~^^^^
KeyError: 'b'
```

`counts['b']` is read before it's ever written. `counts.get(ch, 0) + 1` supplies the implicit zero, so the first occurrence starts at one cleanly.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Reach for `get` whenever a key might be absent and you have a sensible fallback — it replaces the clumsy `if key in d: ... else: ...`. Burn the frequency-count idiom (`d.get(k, 0) + 1`) into muscle memory; counting occurrences is one of the most common patterns in all of programming. (For accumulating into lists, `d.setdefault(k, []).append(x)` is the analog.)

</div>

---

## 4. Iterating and comprehensions

Iterating a dict yields its **keys**. To build dicts concisely, use a **dict comprehension** (the full toolkit is the [next chapter](/synapse/programming-languages/python/working-with-data/comprehensions)).

```python run viz=hashmap:squares
d = {"a": 1, "b": 2, "c": 3}
for k in d:                      # iterates KEYS by default
    print(k, d[k])

squares = {n: n * n for n in range(1, 5)}   # dict comprehension
print(squares)
```

**Output:**
```
a 1
b 2
c 3
{1: 1, 2: 4, 3: 9, 4: 16}
```

**Analysis.** `for k in d` walks the keys (use `d.items()` for pairs). A dict comprehension `{key_expr: val_expr for ... in ...}` builds a dict in one expression — the mapping analog of a list comprehension. You can filter too: `{k: v for k, v in d.items() if v > 1}`.

**Intuition.**
*Mechanism.* Iterating a dict yields its **keys** only — so `for k in d` and `for k in d.keys()` are the same. To loop over pairs you must ask explicitly with `.items()`, which yields unpackable `(key, value)` tuples.

*Concrete bite.* Assuming iteration gives pairs fails loudly with non-string keys:

```python run
d = {1: "a", 2: "b"}
for k, v in d:        # iterates int KEYS, then tries to unpack each
    print(k, v)
```
```
Traceback (most recent call last):
  File "/w/main.py", line 2, in <module>
    for k, v in d:        # iterates int KEYS, then tries to unpack each
        ^^^^
TypeError: cannot unpack non-iterable int object
```

`for k in d` hands you `1`, then `2` — single keys, not pairs — so unpacking into `k, v` blows up. The fix is `for k, v in d.items()`. (Insidiously, with 2-character string keys this *accidentally* "works" by splitting the key into two chars — masking the bug until your keys change.)

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** When you need values too, always iterate `d.items()`, never bare `d`. Use dict comprehensions to transform or filter mappings idiomatically — invert with `{v: k for k, v in d.items()}`, index objects with `{obj.id: obj for obj in objs}`, filter with a trailing `if`.

</div>

---

## 5. What can be a key: hashability

Keys must be **hashable**, which in practice means **immutable**. Lists and dicts cannot be keys; numbers, strings, and tuples (of hashables) can.

```python run
try:
    bad = {[1, 2]: "x"}      # list is mutable -> unhashable
except TypeError as e:
    print("TypeError:", e)
```

**Output:**
```
TypeError: unhashable type: 'list'
```

**Analysis.** A list's contents can change, which would change its hash and break the table, so Python forbids lists as keys (and as set members). Tuples *are* allowed — *if* everything inside them is also hashable. This connects straight to [the object model](/synapse/programming-languages/python/how-python-works/the-object-model): hashability ≈ immutability.

**Intuition.**
*Mechanism.* Hashability is the storage contract from §1: a key's hash must stay constant for its whole time in the table. Immutable objects satisfy this trivially; mutable ones can't, so they're rejected. Hashability of a container is *recursive* — a tuple is hashable only if everything inside it is.

*Concrete bite.* This is exactly why tuples beat lists for *composite* keys:

```python run viz=hashmap:grid
grid = {}
grid[(2, 3)] = "wall"     # tuple key - fine
print(grid)
grid[[2, 3]] = "wall"     # list key - error
```
```
{(2, 3): 'wall'}
Traceback (most recent call last):
  File "/w/main.py", line 4, in <module>
    grid[[2, 3]] = "wall"     # list key - error
    ~~~~^^^^^^^^
TypeError: unhashable type: 'list'
```

`grid[(row, col)] = value` is the canonical 2D-grid idiom precisely because tuples are hashable; lists can't fill that role. Convert with `tuple([2, 3])` when you have a list.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Before using something as a key or set element, ask "is it immutable?" Strings/numbers/bools/tuples-of-immutables: yes. Lists/dicts/sets: no — convert (`tuple(lst)`, `frozenset(s)`). Composite keys (coordinates, pairs) are the textbook reason tuples earn their keep.

</div>

---

## 6. Merging dicts

```python run viz=hashmap:merged
merged = {**{"a": 1}, **{"b": 2, "a": 9}}   # unpack both into a new dict
print(merged)
```

**Output:**
```
{'a': 9, 'b': 2}
```

**Analysis.** `{**d1, **d2}` builds a new dict by unpacking both; on key collisions, the **later** source wins (`a` becomes `9`, not `1`). Python 3.9+ also offers `d1 | d2` (same semantics) and `d1 |= d2` (in-place update). `d1.update(d2)` mutates `d1` with the same last-wins rule.

**Intuition.**
*Mechanism.* Merging walks the sources left to right, writing each key — so when a key appears in more than one source, the **last** write wins. `{**a, **b}` and `a | b` build a *new* dict; `a.update(b)` and `a |= b` mutate `a` in place.

*Concrete bite.* Order is the whole game, and getting it backwards silently discards user input:

```python run
defaults = {"color": "blue", "size": "M"}
user     = {"color": "red"}

print({**user, **defaults})     # defaults clobber the user
print({**defaults, **user})     # correct: user overrides
```
```
{'color': 'blue', 'size': 'M'}
{'color': 'red', 'size': 'M'}
```

Put the *lower-priority* source first and the *override* last; reverse it and your carefully chosen user settings vanish under the defaults.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** "Later wins" → place the authoritative source last: `{**defaults, **overrides}` gives overrides priority. Choose `{**a, **b}` / `a | b` for a new dict (leaving inputs intact), `a.update(b)` / `a |= b` to mutate in place. The layering pattern `{**defaults, **user_settings}` is one you'll write constantly — get the order reflexively right.

</div>

---

## 7. Sets: membership and algebra

A **set** is an unordered collection of **unique**, hashable elements. Think of it as a dict with keys and no values. Its strengths are fast membership testing and mathematical set operations.

```python run
s1 = {1, 2, 3, 4}
s2 = {3, 4, 5, 6}
print(s1 | s2)    # union: in either
print(s1 & s2)    # intersection: in both
print(s1 - s2)    # difference: in s1 not s2
print(s1 ^ s2)    # symmetric difference: in exactly one
```

**Output:**
```
{1, 2, 3, 4, 5, 6}
{3, 4}
{1, 2}
{1, 2, 5, 6}
```

**Analysis.** Sets support the algebra you'd expect: union (`|`), intersection (`&`), difference (`-`), symmetric difference (`^`). Each returns a new set. Elements are unique (duplicates collapse) and unordered (no indexing). (The display order above happens to look sorted for these small integers, but set order is *not* guaranteed — never rely on it.)

**Intuition.**
*Mechanism.* A set is a hash table storing only keys — so elements are inherently unique (a duplicate hashes to an occupied slot and is dropped) and **unordered** (storage position follows the hash, not insertion).

*Concrete bite.* Sets buy uniqueness and one-expression set logic, at the cost of order and indexing — and forgetting the latter raises:

```python run viz=hashmap:s
s = {3, 1, 2}
print(s[0])            # sets are not subscriptable
```
```
Traceback (most recent call last):
  File "/w/main.py", line 2, in <module>
    print(s[0])            # sets are not subscriptable
          ~^^^
TypeError: 'set' object is not subscriptable
```

There's no "first element" of a set — position is meaningless. In exchange, "what's common to both?" is a single `&`:

```python run
a = {1, 2, 3, 4}
b = {3, 4, 5}
print(a & b)           # elements in both, no nested loop
```
```
{3, 4}
```

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Reach for a set when you care about *presence and uniqueness*, not order or position: "in both groups?" → `a & b`; "new in the second list?" → `set(b) - set(a)`; "deduplicate" → `set(x)`. Set operations collapse nested-loop logic into one fast, readable expression. The price — no order, no indexing, hashable elements only — is usually irrelevant for these questions.

</div>

---

## 8. The killer feature: O(1) membership

The most important practical reason to use a set: **`x in set` is O(1)**, versus **`x in list` is O(n)**.

```python run
big_list = list(range(1_000_000))
big_set = set(big_list)

print(999_999 in big_set)   # O(1) - instant
print(999_999 in big_list)  # O(n) - scans up to a million items
```

**Output:**
```
True
True
```

**Analysis.** Both return `True`, but the list scans element by element (worst case, the whole million) while the set hashes the value and jumps straight to its bucket. For repeated membership tests, this is the difference between a fast program and a slow one — and in a loop it's the difference between O(n) and O(n²).

**Intuition.**
*Mechanism.* `x in list` has no structure to exploit, so it compares against each element in turn — up to `n` checks. `x in set` hashes `x` once and jumps to its bucket — ~one check, independent of size.

*Concrete bite.* Put numbers on it. Testing membership in a million-item list inside a loop over another million items is ~10¹² operations — a program that *looks* hung. Here `stream` is your input of `n` items:

```python
seen = []
for x in stream:        # n items
    if x in seen:       # O(n) scan each time
        handle_dupe(x)
    seen.append(x)
# total ~ O(n^2): fine at n=1,000; effectively frozen at n=1,000,000
```

Change `seen = []` to `seen = set()` and each `in` becomes O(1), turning the whole loop into O(n) — instant.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** This is one of the highest-leverage moves in everyday Python: **if you test membership repeatedly, put the data in a set first.** "Have I seen this?" loops, dedup, intersection — all want a set. The cost (hashable elements only, no order) is real but almost always worth it when the question is simply "is it in here?".

</div>

---

## 9. `frozenset` and deduplication

A **`frozenset`** is an immutable set — hashable, so it can be a dict key or an element of another set.

```python run
fs = {frozenset([1, 2]): "ok"}      # frozenset CAN be a dict key
print(fs[frozenset([2, 1])])        # order does not matter for sets
```

**Output:**
```
ok
```

**Deduplication** — two idioms:

```python run
print(sorted(set([3, 1, 2, 1])))            # dedup, then sort
print(list(dict.fromkeys([1, 1, 2, 3, 3, 3])))  # dedup, keep order
```

**Output:**
```
[1, 2, 3]
[1, 2, 3]
```

**Analysis.** A regular `set` is mutable and therefore unhashable; `frozenset` is the immutable version you can nest or use as a key. For deduplication, `set(x)` is fastest but unordered; `list(dict.fromkeys(x))` removes duplicates *while preserving insertion order*, leveraging the dict order guarantee from §2.

**Intuition.**
*Mechanism.* A regular `set` is mutable, hence unhashable, hence can't be a key or a member of another set; `frozenset` is the immutable counterpart that can. For dedup, `set(x)` collapses duplicates by hashing but discards order; `dict.fromkeys(x)` uses the keys-are-unique-and-ordered property (§2) to dedup *and* keep first-seen order.

*Concrete bite.* The choice matters when order carries meaning — `set()` will scramble it:

```python run
items = ["c", "a", "c", "b", "a"]
print(list(set(items)))              # order is arbitrary
print(list(dict.fromkeys(items)))    # first-seen order kept
```

**Output (illustrative — the `set()` line's order is arbitrary and may differ for you):**
```
['b', 'a', 'c']
['c', 'a', 'b']
```

Dedup a playlist or a log with `set()` and you may shuffle it; `dict.fromkeys` preserves the original sequence.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Use `frozenset` when you need a set-of-sets or a set as a key — e.g., an unordered pair as a key is `frozenset({a, b})`. For dedup, ask: *do I need order?* No → `set(x)` (fastest). Yes → `list(dict.fromkeys(x))`. The order-preserving trick surprises people who reach for `set()` reflexively.

</div>

---

## 10. Mental-model summary

| Principle | Consequence |
|-----------|-------------|
| Dicts and sets are built on **hashing** | O(1) average lookup, insertion, membership |
| Keys/elements must be **hashable** (≈ immutable) | Lists/dicts can't be keys; tuples/frozensets can |
| A **dict** maps keys → values; a **set** is keys only | Use dict for lookups, set for membership/uniqueness |
| Dicts preserve **insertion order** (3.7+); sets do **not** | Rely on dict order; never rely on set order |
| `get(k, default)` avoids `KeyError` | The `get(k, 0) + 1` counting idiom |
| Set algebra: `\|` `&` `-` `^` | Replace nested loops with one expression |
| `x in set` is **O(1)**, `x in list` is **O(n)** | Convert to a set before repeated membership tests |
| `frozenset` is the immutable, hashable set | Use it as a key or set element |

### Gotcha checklist

<div style="border-left:4px solid #da5233;background:rgba(218,82,51,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

- **`d[k]` on a missing key → `KeyError`:** use `d.get(k, default)`.
- **List/dict as a key → `unhashable type`:** convert to a tuple/frozenset.
- **`for k, v in d` → unpacking error:** that iterates keys; use `d.items()`.
- **Modifying a dict's size while iterating → `RuntimeError`:** iterate `list(d)`.
- **Relying on set iteration order:** it's unspecified; use `dict.fromkeys` if order matters.
- **Dict merge clobbered your overrides:** it's last-wins; put the priority source last (`{**defaults, **user}`).
- **`x in list` inside a loop → O(n²):** build a `set` once, then test against it.

</div>

---

<div style="border-left:4px solid #6d28d9;background:rgba(109,40,217,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

🧪 **Predict, then check.** Build the §3 frequency-counter from memory (`counts.get(ch, 0) + 1`) on the word `"mississippi"`, and predict the exact dict, **including key order**. Then rewrite the §8 membership check with `seen = set()` and reason about why it changes the loop from O(n²) to O(n). Those two patterns — counting with `get` and set membership — are the most common dict/set moves in real code.

</div>

## Your Turn

Before you move on, check your understanding with the coach — explain the idea, apply it, weigh the trade-offs, then defend your reasoning.

<div class="concept-coach"></div>
