---
title: Sequences & the Sequence Protocol
summary: List, tuple, and string are three implementations of one abstraction — the sequence — so a single set of operations (index, slice, len, in, +, *, iterate) serves all three, and the only axis of difference is mutability. The deep pass of Lists, with slicing, unpacking, and complexity.
prereqs: []
---

# Sequences — Lists, Tuples & Strings as One Abstraction

Lists, tuples, and strings look like three separate topics. They aren't. They're three implementations of **one abstraction — the sequence**: an ordered collection you can index, slice, and iterate. Learn the shared protocol once and three "topics" collapse into one, with the differences reducing to a single axis: *mutable or not*.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **The core idea.**

- List, tuple, and string are three implementations of **one abstraction — the sequence**.
- One shared protocol serves all three: index, slice, iterate.
- The only difference is a single axis: **mutable or not**.

</div>

This is the deep pass of [Lists, the Basics](/synapse/programming-languages/python/control-flow/lists-the-basics) and [Strings, the Basics](/synapse/programming-languages/python/first-steps/strings-the-basics) — it assumes you've met both and pushes into slicing, tuples, unpacking, and complexity. Every output below was produced by running the code.

<div style="border-left:4px solid #15448e;background:rgba(21,68,142,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

📘 **How to read the Intuition boxes.** Each one is built in three moves:

1. **The mechanism** — what the interpreter is *actually doing*.
2. **A concrete bite** — a specific, runnable way the naive assumption fails.
3. **The earned rule** — the decision heuristic, now justified rather than asserted, plus its cost.

</div>

---

## Table of Contents

1. [The sequence abstraction](#1-the-sequence-abstraction)
2. [Indexing, including negatives](#2-indexing-including-negatives)
3. [Slicing — the power tool](#3-slicing--the-power-tool)
4. [Operations every sequence shares](#4-operations-every-sequence-shares)
5. [Lists — the mutable workhorse](#5-lists--the-mutable-workhorse)
6. [Tuples — the immutable record](#6-tuples--the-immutable-record)
7. [Strings — immutable text sequences](#7-strings--immutable-text-sequences)
8. [Unpacking](#8-unpacking)
9. [Complexity: what's fast, what's slow](#9-complexity-whats-fast-whats-slow)
10. [Mental-model summary](#10-mental-model-summary)

---

## 1. The sequence abstraction

A **sequence** is any ordered collection supporting a common set of operations: get an item by integer position (`seq[i]`), take a sub-range (`seq[a:b]`), measure length (`len`), test membership (`x in seq`), concatenate (`+`), repeat (`*`), and iterate (`for x in seq`).

```python run
for seq in (['a', 'b', 'c'], ('a', 'b', 'c'), "abc"):
    print(seq[0], seq[-1], len(seq), 'b' in seq)
```

**Output:**
```
a c 3 True
a c 3 True
a c 3 True
```

**Analysis.** A list, a tuple, and a string respond *identically* to indexing, length, and membership. They share the sequence protocol. What differs is only what they hold and whether they can change.

**Intuition.**
*Mechanism.* "Sequence" isn't a vibe — it's a concrete protocol: a type is a sequence if it implements the dunder methods `__getitem__` (for `seq[i]` and slicing), `__len__`, and `__iter__`. List, tuple, and str all implement them, so the same syntax dispatches to each. The operations live in the *protocol*; each type just supplies the implementation. (You'll build these protocols yourself in [Dunder Methods](/synapse/programming-languages/python/object-oriented/dunder-methods).)

*Concrete bite.* This is why code written against "a sequence" transfers for free — one function works on all three:

```python run
def second_and_last(seq):
    return seq[1], seq[-1]

print(second_and_last([10, 20, 30]))
print(second_and_last((10, 20, 30)))
print(second_and_last("hello"))
```
```
(20, 30)
(20, 30)
('e', 'o')
```

One function, no type checks, works on a list, a tuple, and a string — because all three honor the indexing protocol.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Don't study lists, tuples, and strings as three unrelated APIs; learn the *sequence operations* once (index, slice, `len`, `in`, `+`, `*`, iterate), then treat each type as "a sequence that holds X and is (im)mutable." The payoff is that intuitions and code generalize across all three, and you only memorize the *differences* (mutability, and each type's extra methods).

</div>

---

## 2. Indexing, including negatives

Positions are **zero-based**: the first item is index `0`. **Negative** indices count from the end, with `-1` being the last item.

```python run viz=array:seq
seq = ['a', 'b', 'c', 'd', 'e']
print(seq[0])     # first
print(seq[-1])    # last
print(seq[-2])    # second from last
```

**Output:**
```
a
e
d
```

**Analysis.** `seq[0]` is the first element; `seq[-1]` is the last without needing `len(seq)-1`. Negative indexing is just `len + index` under the hood: `seq[-1]` means `seq[len(seq)-1]`.

**Intuition.**
*Mechanism.* There's one address space with two readings: a left ruler `0, 1, 2, …` and a right ruler `…, -3, -2, -1`. A negative index `i` is resolved as `len(seq) + i`, so `-1` lands on the last element with no `len` arithmetic on your part. An index outside the valid range doesn't fall back to a default — it raises.

*Concrete bite.* Python refuses to silently hand you nothing for a bad index (unlike a plain JavaScript array returning `undefined`):

```python run viz=array:seq
seq = ['a', 'b', 'c']
print(seq[5])
```
```
Traceback (most recent call last):
  File "/w/main.py", line 2, in <module>
    print(seq[5])
          ~~~^^^
IndexError: list index out of range
```

The error is a feature: it turns an off-by-one into a loud failure at the point of the bug, instead of a `None` that propagates and explodes somewhere unrelated later.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Use `-1`/`-2` for "from the end" instead of `len(seq)-1` math — it's shorter and removes a class of off-by-one mistakes. And trust that out-of-range access *raises*: don't wrap every index in defensive checks, but do guard (`seq[i] if i < len(seq) else default`) where the index genuinely might be out of bounds.

</div>

---

## 3. Slicing — the power tool

`seq[start:stop:step]` returns a **new** sub-sequence. `start` is inclusive, `stop` is **exclusive**, `step` is the stride. Any part can be omitted.

```python run viz=array:seq
seq = ['a', 'b', 'c', 'd', 'e']
print(seq[1:4])     # indices 1,2,3 (stop 4 excluded)
print(seq[:2])      # start omitted -> from beginning
print(seq[::2])     # every 2nd item
print(seq[::-1])    # reversed
print(seq[:] is seq)  # a full slice is a COPY, not the same object
```

**Output:**
```
['b', 'c', 'd']
['a', 'b']
['a', 'c', 'e']
['e', 'd', 'c', 'b', 'a']
False
```

**Analysis.** `seq[1:4]` takes positions 1, 2, 3 — `stop=4` is excluded (this half-open convention is why `len` equals `stop - start` for a simple slice). Omitting `start`/`stop` defaults to the ends. A negative step walks backward, so `seq[::-1]` reverses. Critically, `seq[:]` builds a **new** list with the same elements — `seq[:] is seq` is `False`, which is why `[:]` is a common shallow-copy idiom.

**Intuition.**
*Mechanism.* A slice never aliases — it constructs a *new* object and copies the selected element references into it (which is exactly why `seq[:] is seq` is `False`, connecting to the [object model](/synapse/programming-languages/python/how-python-works/the-object-model): a slice is a shallow copy). The half-open `[start, stop)` convention means `seq[:k]` and `seq[k:]` partition the sequence with no overlap and no gap, and `len(seq[a:b]) == b - a` for simple slices.

*Concrete bite.* Because a slice copies, it's the fix for the "never modify a collection while iterating it" trap. Mutating a list mid-loop makes the iterator skip elements:

```python run viz=array:nums
nums = [2, 4, 6]
for x in nums:
    if x % 2 == 0:
        nums.remove(x)
print(nums)        # removing while iterating skips an element

nums = [2, 4, 6]
for x in nums[:]:          # iterate a copy
    if x % 2 == 0:
        nums.remove(x)
print(nums)        # correct
```
```
[4]
[]
```

The first loop's iterator advances by index over a list that's shrinking underneath it, so it steps past `4` — leaving `[4]`. Looping over `nums[:]` iterates a fixed snapshot while you mutate the original safely, giving the correct `[]`.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Three slice idioms are worth muscle memory: `seq[::-1]` (reverse), `seq[:]` (shallow copy), `seq[a:b]` (sub-range). And remember slicing *copies* — that's what makes `for x in lst[:]` the canonical safe-removal pattern (or, often cleaner, build a new list with a [comprehension](/synapse/programming-languages/python/working-with-data/comprehensions) instead of mutating in place). The cost of `[:]` is an O(n) copy, negligible unless the sequence is huge and the loop is hot.

</div>

---

## 4. Operations every sequence shares

Concatenation, repetition, and membership work on all sequence types.

```python run
print([1, 2] + [3])       # list concatenation -> new list
print('ab' + 'cd')        # string concatenation
print([0] * 3)            # list repetition
print('ab' * 3)           # string repetition
print(3 in [1, 2, 3])     # membership
print('b' in 'abc')       # substring membership for strings
```

**Output:**
```
[1, 2, 3]
abcd
[0, 0, 0]
ababab
True
True
```

**Analysis.** `+` joins two sequences of the same type into a new one; `*` repeats. For strings, `in` tests *substring* containment (`'b' in 'abc'`), a convenient special case. All of these produce new objects.

**Intuition.**
*Mechanism.* `+` and `*` build *new* sequences and never modify their operands. But `*` on a list copies *references*, not the underlying objects — so `[obj] * 3` is three references to the same `obj`, not three independent copies.

*Concrete bite.* That reference-copying is the [aliasing trap](/synapse/programming-languages/python/control-flow/lists-the-basics) in sequence clothing:

```python run viz=grid:rows
rows = [[]] * 3            # three references to ONE inner list
rows[0].append(1)
print(rows)                # all three rows are the same list
```
```
[[1], [1], [1]]
```

You wanted three empty lists; you got one list pointed at three times, so appending to "row 0" appears in all of them. Safe for immutable elements (`[0] * 3` is genuinely fine), dangerous for mutable ones.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Use `*` freely to build repeated sequences of *immutable* elements (`[0] * n`, `"-" * 40`). For repeated *mutable* elements, never use `*` — use a comprehension that constructs a fresh object each iteration: `[[] for _ in range(3)]`. The tell is: if the element is itself a list/dict/set, reach for the comprehension.

</div>

---

## 5. Lists — the mutable workhorse

A **list** is an ordered, mutable sequence holding anything. Because it's mutable, it has in-place methods that change it and return `None`.

```python run viz=array:lst
lst = [3, 1, 2]
lst.append(4)        # add to end
lst.insert(0, 0)     # insert at index
lst.sort()           # sort in place
print(lst)
print(lst.pop())     # remove & return last
print(lst)
```

**Output:**
```
[0, 1, 2, 3, 4]
4
[0, 1, 2, 3]
```

**Analysis.** `append`, `insert`, `sort`, and `pop` mutate the list in place. Note `sort()` returns `None` (it sorts the existing list) — a classic beginner trap is `lst = lst.sort()`, which sets `lst` to `None`. Use `sorted(lst)` when you want a new sorted list and to keep the original. (Common list methods: `append`, `extend`, `insert`, `remove`, `pop`, `sort`, `reverse`, `index`, `count`, `clear`.)

**Intuition.**
*Mechanism.* In-place mutators (`sort`, `reverse`, `append`, `insert`, `extend`) change the existing object and, by deliberate convention, return `None` — so there's no return value to assign. This signals "I mutated something" versus a function that "produced a new value."

*Concrete bite.* The convention bites when you assign the result of an in-place method:

```python run
lst = [3, 1, 2].sort()     # .sort() mutates and returns None
print(lst)                 # None - the sorted list was thrown away
```
```
None
```

`[3, 1, 2].sort()` sorts an anonymous list and returns `None`, which you then bound to `lst`. The sorted data is gone.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Memorize the split: **"make a new one" vs "change this one."** `sorted(lst)` / `reversed(lst)` return new results (assign them); `lst.sort()` / `lst.reverse()` mutate in place (call them on their own line, don't assign). When in doubt, check whether a method returns the object or `None` — `None` means it mutated. Lists are your default container for ordered, growable, changeable data.

</div>

---

## 6. Tuples — the immutable record

A **tuple** is an ordered, **immutable** sequence. Same indexing/slicing as a list, but it cannot be changed after creation.

```python run viz=array:t
t = (1, 2, 3)
print(t[1])          # indexing works
try:
    t[0] = 9         # mutation does not
except TypeError as e:
    print("TypeError:", e)
```

**Output:**
```
2
TypeError: 'tuple' object does not support item assignment
```

The **single-element tuple** trap — it's the comma, not the parentheses, that makes a tuple:

```python run
print(type((5,)).__name__)   # comma -> tuple
print(type((5)).__name__)    # no comma -> just a parenthesized int
```

**Output:**
```
tuple
int
```

A tuple is immutable, but if it *contains* a mutable object, that object can still change:

```python run viz=array:tm
tm = ([1, 2], 3)
tm[0].append(99)     # the tuple's slots are fixed, but the list inside is not
print(tm)
```

**Output:**
```
([1, 2, 99], 3)
```

**Analysis.** You can't reassign a tuple's slots, but immutability is *shallow*: it fixes *which objects* the tuple holds, not the internal state of those objects. Also note `(5)` is just `5` in parentheses — you need the trailing comma `(5,)` to get a one-element tuple.

**Intuition.**
*Mechanism.* What defines a tuple is the **comma**, not the parentheses — `1, 2, 3` is already a tuple; the parens just group it. Immutability fixes the tuple's *slots* (which objects it references), but is *shallow* — it doesn't freeze the internal state of a mutable object stored in a slot.

*Concrete bite.* The shallow part means a tuple can quietly become unhashable:

```python run
key = (1, [2, 3])      # a tuple containing a list
print(hash(key))       # cannot hash a tuple that holds a mutable list
```
```
Traceback (most recent call last):
  File "/w/main.py", line 2, in <module>
    print(hash(key))       # cannot hash a tuple that holds a mutable list
          ~~~~^^^^^
TypeError: unhashable type: 'list'
```

The tuple looks immutable, but because it holds a mutable list, it can't be hashed — so it can't be a dict key or set member after all. A tuple is only *fully* immutable (and hashable) if everything inside it is — a fact [Dictionaries & Sets](/synapse/programming-languages/python/working-with-data/dictionaries-and-sets) leans on.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Reach for a tuple when a fixed group of values belongs together and shouldn't change — coordinates `(x, y)`, a DB row, a multi-value return. Immutability buys two things: **hashability** (usable as dict keys / set members, *provided the contents are hashable too*) and a clear "this won't change" signal. Watch the single-element comma (`(5,)`), and don't assume a tuple is hashable without checking its contents.

</div>

---

## 7. Strings — immutable text sequences

A **string** is an immutable sequence of characters. All sequence operations apply, plus a rich set of text methods that (being immutable) always return **new** strings.

```python run
text = "  Hello, World  "
print(text.strip())            # remove surrounding whitespace
print("aXbXc".replace("X", "-"))
print("a,b,c".split(","))      # string -> list
print("-".join(["a", "b", "c"]))  # list -> string
print("hello".find("l"))       # index of first match (-1 if absent)
print("hello".startswith("he"))
```

**Output:**
```
Hello, World
a-b-c
['a', 'b', 'c']
a-b-c
2
True
```

### Formatting with f-strings

```python run
name = "Aniket"
pi = 3.14159
print(f"{name}: {pi:.2f}")     # 2 decimal places
print(f"{42:>5}")              # right-align in width 5
print(f"{pi=}")               # debug form: shows name and value
```

**Output:**
```
Aniket: 3.14
   42
pi=3.14159
```

**Analysis.** `split`/`join` are inverses and the canonical way to move between strings and lists — note `join` is a *string* method called on the separator (`"-".join(...)`), which surprises many. f-strings embed expressions in `{}` with optional format specs after a colon (`:.2f`, `:>5`). The `{var=}` form prints both the name and value, ideal for debugging. ([Strings in Depth](/synapse/programming-languages/python/working-with-data/strings-in-depth) is the full treatment.)

**Intuition.**
*Mechanism.* Strings are immutable, so every "edit" (`upper`, `replace`, `strip`, `+`) leaves the original untouched and returns a *new* string. The crucial performance consequence: `s += chunk` can't extend `s` in place — it allocates a new string and copies all existing characters plus the new ones.

*Concrete bite.* That copy-per-step makes loop concatenation quadratic. This snippet processes `N` chunks (`pieces` stands for your data):

```python
s = ""
for chunk in pieces:      # N chunks
    s += chunk            # step k copies ~k characters already accumulated
```

Total work is `1 + 2 + ... + N` ≈ **O(N²)** character copies — fine at 1,000 chunks, a visible hang at 1,000,000. The list-based alternative does O(N) work:

```python
parts = []
for chunk in pieces:
    parts.append(chunk)   # O(1) each
result = "".join(parts)   # one pass, O(N)
```

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Build strings by accumulating pieces in a list and calling `"".join(parts)` once — never grow a string with `+=` in a loop. Master `split` / `join` / `strip` / `replace` and f-string format specs; they cover the vast majority of real text work. Commit the `"sep".join(items)` direction to memory (the *separator* owns the method) — it's the one everyone forgets.

</div>

---

## 8. Unpacking

Sequences can be **unpacked** into multiple names in one assignment — a direct consequence of their ordered structure.

```python run
first, *rest = [1, 2, 3, 4]    # starred catches the rest
print(first)
print(rest)

a, b = 1, 2
a, b = b, a                     # swap with no temp variable
print(a, b)
```

**Output:**
```
1
[2, 3, 4]
2 1
```

**Analysis.** `first, *rest = ...` binds `first` to the first element and `*rest` (a list) to everything remaining. The swap `a, b = b, a` works because the right side `b, a` first builds a tuple `(2, 1)`, which is then unpacked into `a, b` — no temporary needed, and `print(a, b)` shows `2 1`. The starred name can appear in any one position: `*init, last = seq` grabs the last; `a, *mid, z = seq` grabs the ends.

**Intuition.**
*Mechanism.* Unpacking is structural assignment: the right side is (or becomes) a sequence, and Python binds its elements positionally to the names on the left. The swap works because the right side is fully evaluated into a tuple *first*, then unpacked. A starred name greedily absorbs the leftover middle as a list.

*Concrete bite.* The shape must match, or it raises — usually what you want, but it surprises people:

```python run
a, b = [1, 2, 3]      # too many values for two names
print(a, b)
```
```
Traceback (most recent call last):
  File "/w/main.py", line 1, in <module>
    a, b = [1, 2, 3]      # too many values for two names
    ^^^^
ValueError: too many values to unpack (expected 2)
```

Three values can't bind to two names. (Use `a, b, *_ = [1, 2, 3]` to deliberately ignore extras, or `a, *rest = ...` to capture them.)

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Prefer unpacking over manual indexing (`x = pair[0]; y = pair[1]`) — it's clearer and the count-mismatch error catches bugs early. It's the same machinery behind `for i, x in enumerate(seq)` and `for k, v in d.items()` (each iteration yields a 2-tuple that unpacks). Use `*rest` for variable-length tails and `*_` to discard pieces you don't need.

</div>

---

## 9. Complexity: what's fast, what's slow

Knowing the cost of operations is essential for real performance. For lists (dynamic arrays):

| Operation | Cost | Why |
|-----------|------|-----|
| Index `lst[i]`, `len` | O(1) | Direct array access |
| Append / pop **end** | O(1) amortized | Room at the end, occasional resize |
| Insert / pop **front or middle** | O(n) | All later elements must shift |
| `x in lst` (membership) | O(n) | Linear scan |
| Slice `lst[a:b]` | O(k) | Copies k elements |
| Sort | O(n log n) | Timsort |

**Intuition.**
*Mechanism.* A list is a *contiguous array of references*: element `i` lives at a computable offset, so indexing is O(1). But inserting or deleting anywhere except the end forces every later element to shift one slot — O(n). Membership (`x in lst`) has no index to exploit, so it scans linearly.

*Concrete bite.* The headline cost is membership inside a loop, which silently becomes quadratic. Here `stream` is your input of `n` items:

```python
seen = []
for x in stream:            # n items
    if x in seen:           # each test scans up to n -> O(n) per item
        ...
    seen.append(x)
# total ~ O(n^2): instant for n=1,000, a hang for n=1,000,000
```

Swapping `seen` to a `set` makes each `in` O(1), collapsing the whole loop to O(n). (Full treatment in [Dictionaries & Sets](/synapse/programming-languages/python/working-with-data/dictionaries-and-sets).)

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Match the structure to the operation. Need fast **membership/uniqueness**? Use a `set` (O(1)), not a list (O(n)) — especially inside loops. Need fast **front** insertion/removal? Use `collections.deque`, not `list.insert(0, x)` (O(n)). Lists are ideal for ordered, index-accessed, append-at-end data; reach for the right neighbor when your hot operation is one a list does slowly. Strings and tuples share the array-access profile but, being immutable, have no in-place mutation cost (or capability).

</div>

---

## 10. Mental-model summary

| Principle | Consequence |
|-----------|-------------|
| List, tuple, string are all **sequences** | One protocol (index/slice/iterate/`in`/`+`/`*`) serves all three |
| Indices are **zero-based**; negatives count from the end | `seq[-1]` is the last item, no `len` math |
| Slicing is **half-open** `[start, stop)` and returns a **new** object | `seq[:]` copies, `seq[::-1]` reverses, slices never mutate |
| The axis of difference is **mutability** | List = mutable; tuple & string = immutable |
| In-place list methods return **`None`** | `lst.sort()` mutates; `sorted(lst)` returns new |
| Tuple immutability is **shallow** | Slots are fixed; a mutable object inside can still change |
| String "edits" make **new** strings | Build with `list` + `"".join` to avoid quadratic `+=` |
| Membership in a list is **O(n)** | Use a `set` for repeated lookups |

### Gotcha checklist

<div style="border-left:4px solid #da5233;background:rgba(218,82,51,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

- **`lst = lst.sort()` set my list to `None` →** in-place methods return `None`; use `sorted(lst)` or call `lst.sort()` alone.
- **`(5)` isn't a tuple →** use `(5,)` (the comma makes the tuple).
- **`[[]] * 3` shares one inner list →** use `[[] for _ in range(3)]`.
- **`"".join(list)` confusion →** the separator owns the method: `sep.join(items)`.
- **Repeated `s += chunk` in a loop hangs →** quadratic; accumulate in a list, join once.
- **Modifying a list while iterating skips items →** iterate over a copy (`lst[:]`) or build a new collection.
- **`x in big_list` inside a loop is slow →** O(n²); convert to a `set` first.

</div>

---

<div style="border-left:4px solid #6d28d9;background:rgba(109,40,217,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

🧪 **Predict, then check.** Retype the slicing examples (§3) and predict each output, including `seq[:] is seq`. When you can explain why a full slice is a copy but a plain assignment (`b = a`) is an alias, you've connected slicing to [the object model](/synapse/programming-languages/python/how-python-works/the-object-model) — the subject waiting in Tier 3.

</div>

## Your Turn

Before you move on, check your understanding with the coach — explain the idea, apply it, weigh the trade-offs, then defend your reasoning.

<div class="concept-coach"></div>
