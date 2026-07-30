---
title: Lists, the Basics
summary: A list holds many values in order, and unlike a string it can be changed in place. Creating, indexing, membership, mutation, append/insert/remove/pop, slicing, iterating, and the aliasing trap — with the out-of-range, immutable-string, remove-missing, and shared-list traps shown live.
prereqs: []
---

# Lists, the Basics — Many Values in Order

A **list** holds many values in a single, ordered collection — `[3, 1, 4, 1, 5]`, `["red", "green"]`. You've already used lists in passing ([building one with `append`](/synapse/programming-languages/python/control-flow/loop-control-and-patterns)); now they get their own chapter. The one idea that sets lists apart from everything in Tier 0: **a list is *mutable* — you can change its contents in place, after it's created** — and that single property explains both their power (build and edit collections cheaply) and their sharpest trap (two names can point at the *same* list). This is a gentle pass; [Sequences](/synapse/programming-languages/python/working-with-data/sequences) returns in Tier 2 for the full sequence protocol and complexity.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **The core idea.**

- A list holds many values in a single, ordered collection.
- A list is **mutable** — you can change its contents in place.
- That one property explains both its power and its aliasing trap.

</div>

Every output below was produced by running the code.

<div style="border-left:4px solid #15448e;background:rgba(21,68,142,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

📘 **How to read the Intuition boxes.** Each one is built in three moves:

1. **The mechanism** — what the interpreter is *actually doing*.
2. **A concrete bite** — a specific, runnable way the naive assumption fails.
3. **The earned rule** — the decision heuristic, now justified rather than asserted, plus its cost.

</div>

---

## Table of contents

1. [Creating, indexing, and membership](#1-creating-indexing-and-membership)
2. [Lists are mutable](#2-lists-are-mutable)
3. [Growing and shrinking](#3-growing-and-shrinking)
4. [Slicing](#4-slicing)
5. [Iterating and the aliasing trap](#5-iterating-and-the-aliasing-trap)
6. [Mental-model summary](#6-mental-model-summary)
7. [Gotcha checklist](#7-gotcha-checklist)

---

## 1. Creating, indexing, and membership

Write a list with square brackets and commas. Index it exactly like a string ([Tutorial 4](/synapse/programming-languages/python/first-steps/strings-the-basics)): positions start at `0`, `-1` is the last, `len()` counts the items. `in` tests membership.

```python run viz=array:fruits
fruits = ["apple", "banana", "cherry"]
print(fruits[0])
print(fruits[-1])
print(len(fruits))
```

**Output:**
```
apple
cherry
3
```

```d2
direction: right
fruits: "fruits  (a list)" {
  grid-rows: 1
  c0: "index 0\n'apple'"
  c1: "index 1\n'banana'"
  c2: "index 2\n'cherry'"
}
```

The `in` operator ([Tutorial 6](/synapse/programming-languages/python/control-flow/booleans-and-logic)) checks whether a value is an element:

```python run viz=array:fruits
fruits = ["apple", "banana", "cherry"]
print("banana" in fruits)
print("mango" in fruits)
```

**Output:**
```
True
False
```

**Analysis.** `fruits[0]` is the first item (`apple`), `fruits[-1]` the last (`cherry`), `len(fruits)` the count (`3`). Valid indices are `0` to `len − 1`, i.e. `0`–`2`. For lists, `in` tests whole **elements** — `"banana" in fruits` is `True` because `"banana"` is an item, whereas for strings `in` tested substrings.

**Intuition.**
*Mechanism.* A list stores its items in numbered slots, `0` to `len − 1`. Indexing reads a slot; `in` scans the slots for an equal element. Same zero-based scheme as strings, so the same boundary applies.

*Concrete bite.* Indexing past the end is an error, just as with strings:

```python run
fruits = ["apple", "banana", "cherry"]
print(fruits[3])
```
```
Traceback (most recent call last):
  File "/w/main.py", line 2, in <module>
    print(fruits[3])
          ~~~~~~^^^
IndexError: list index out of range
```

Three items live at indices `0, 1, 2`; index `3` is the (nonexistent) fourth, so Python raises `IndexError`.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** The last valid index is `len(lst) - 1`; use `-1` for the end and `in` to test membership without indexing. The cost is the familiar off-by-one at the boundary — the same rule as string indexing, now reused, which is the point of learning it once.

</div>

---

## 2. Lists are mutable

Unlike strings, a list can be **changed in place**: assign to an index and that slot's value is replaced. The list object is the same; its contents differ.

```python run viz=array:fruits
fruits = ["apple", "banana", "cherry"]
fruits[1] = "blueberry"     # lists can be changed in place
print(fruits)
```

**Output:**
```
['apple', 'blueberry', 'cherry']
```

**Analysis.** `fruits[1] = "blueberry"` overwrote the item at index 1. The list still has three items in the same order; only the middle one changed. No new list was created — the existing one was edited.

**Intuition.**
*Mechanism.* Index assignment (`lst[i] = x`) mutates the list in place, replacing slot `i`. This is the defining difference from strings, which are **immutable** ([Tutorial 4](/synapse/programming-languages/python/first-steps/strings-the-basics)) and forbid it.

*Concrete bite.* Try the same on a string and it's refused:

```python run
word = "cat"
word[0] = "b"
```
```
Traceback (most recent call last):
  File "/w/main.py", line 2, in <module>
    word[0] = "b"
    ~~~~^^^
TypeError: 'str' object does not support item assignment
```

A string can't be edited in place, so `word[0] = "b"` is a `TypeError`. To "change" a string you build a new one (`"b" + word[1:]`); to change a list, you edit it directly.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Use lists when the collection needs to change (add, remove, reorder); use strings/tuples when it shouldn't. The cost of mutability is exactly §5's trap — a mutable object shared under two names can be changed through either — so mutability buys convenience at the price of aliasing surprises.

</div>

---

## 3. Growing and shrinking

Lists change size, too. `append(x)` adds to the end, `insert(i, x)` adds at a position, `remove(x)` deletes the first matching value, and `pop()` removes and **returns** the last item.

```python run viz=array:nums
nums = [1, 2, 3]
nums.append(4)
nums.insert(0, 0)
nums.remove(2)
last = nums.pop()
print(nums)
print("popped:", last)
```

**Output:**
```
[0, 1, 3]
popped: 4
```

**Analysis.** Step by step: `[1,2,3]` → `append(4)` → `[1,2,3,4]` → `insert(0,0)` puts `0` at index 0 → `[0,1,2,3,4]` → `remove(2)` deletes the value `2` → `[0,1,3,4]` → `pop()` removes the last item `4` and returns it. Final list `[0, 1, 3]`, and `last` is `4`. Note `remove` takes a *value*; `pop` works by *position* (the end, by default) and hands the item back.

**Intuition.**
*Mechanism.* `append`/`insert`/`remove` mutate in place and return `None` (their job is the side effect — [Tutorial 9](/synapse/programming-languages/python/control-flow/loop-control-and-patterns)). `pop` is the exception: it mutates *and* returns the removed item, so you can use it.

*Concrete bite.* `remove(x)` needs `x` to actually be present, or it raises:

```python run
nums = [1, 2, 3]
nums.remove(9)
```
```
Traceback (most recent call last):
  File "/w/main.py", line 2, in <module>
    nums.remove(9)
    ~~~~~~~~~~~^^^
ValueError: list.remove(x): x not in list
```

There's no `9` in the list, so `remove` can't do its job and raises `ValueError`. (Check first with `if 9 in nums:`.)

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** `append`/`pop` for stack-like ends, `insert`/`remove` for arbitrary positions/values — and guard `remove` with an `in` check, or be ready for `ValueError`. The cost/boundary: `insert(0, ...)` and `remove`/`in` scan or shift the whole list, so they're slower than `append` for big lists — a complexity point [Sequences](/synapse/programming-languages/python/working-with-data/sequences) makes precise.

</div>

---

## 4. Slicing

A **slice** copies a *range* of a list: `lst[start:stop]` gives items from `start` up to **but not including** `stop` — the same half-open rule as `range`. Omit an end to go to the edge; use negatives to count from the back.

```python run viz=array:nums
nums = [10, 20, 30, 40, 50]
print(nums[1:4])
print(nums[:2])
print(nums[3:])
print(nums[-2:])
```

**Output:**
```
[20, 30, 40]
[10, 20]
[40, 50]
[40, 50]
```

**Analysis.** `nums[1:4]` is indices 1, 2, 3 → `[20, 30, 40]` (index 4 excluded). `nums[:2]` is "from the start to index 2" → `[10, 20]`. `nums[3:]` is "from index 3 to the end" → `[40, 50]`. `nums[-2:]` is "the last two" → `[40, 50]`. Each slice is a **new list**; the original is untouched.

**Intuition.**
*Mechanism.* `lst[a:b]` builds a new list containing the items at indices `a` through `b − 1`. The `stop` is exclusive — the same half-open convention as `range(a, b)` and string slicing — so the slice length is `b − a`.

*Concrete bite.* The exclusive stop is the recurring surprise:

```python run viz=array:nums
nums = [10, 20, 30, 40, 50]
print(nums[1:3])     # indices 1 and 2, not 3
```
```
[20, 30]
```

`nums[1:3]` includes indices 1 and 2 — `[20, 30]` — but **not** index 3. Two items, not three: `stop − start = 3 − 1 = 2`.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Read `lst[a:b]` as "from `a`, stop before `b`," giving `b − a` items. The cost is the same off-by-one temptation as everywhere else in Python's zero-based, half-open world — but the upside is clean idioms: `lst[:]` copies the whole list, `lst[:n]` takes the first `n`, `lst[-n:]` takes the last `n`.

</div>

---

## 5. Iterating and the aliasing trap

You loop over a list exactly like a string ([Tutorial 8](/synapse/programming-languages/python/control-flow/loops)) — the loop variable is each **item**.

```python run viz=array:fruits
fruits = ["apple", "banana", "cherry"]
for fruit in fruits:
    print(fruit)
```

**Output:**
```
apple
banana
cherry
```

**Analysis.** The loop bound `fruit` to each element in order. No indexing needed — `for item in list` is the idiomatic way to process every element.

**Intuition.**
*Mechanism.* A variable doesn't *hold* a list — it **points at** one list object (a foreshadowing of [the object model](/synapse/programming-languages/python/how-python-works/the-object-model)). Assigning that variable to another name makes a second pointer to the *same* list, not a copy. Because lists are mutable (§2), a change through either name is visible through both.

*Concrete bite.* This is the aliasing trap — `b = a` shares one list:

```python run viz=array:a
a = [1, 2, 3]
b = a            # both names point at the SAME list
b.append(4)
print("a:", a)   # a changed too
```
```
a: [1, 2, 3, 4]
```

We only appended to `b`, yet `a` shows the `4` as well — because `a` and `b` are two names for one list. To get an independent copy, slice it (or use `list()`):

```python run viz=array:b
a = [1, 2, 3]
b = a[:]          # a copy, not an alias
b.append(4)
print("a:", a)
print("b:", b)
```
```
a: [1, 2, 3]
b: [1, 2, 3, 4]
```

Now `b` is a separate list; appending to it leaves `a` alone.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Remember `=` on a list shares, it doesn't copy; make a deliberate copy (`a[:]` or `list(a)`) when you need independence. The cost/boundary: even a copy via `[:]` is *shallow* — it copies the outer list but the two share any *inner* objects — a subtlety [The Object Model](/synapse/programming-languages/python/how-python-works/the-object-model) resolves with deep copies in Tier 3.

</div>

---

## 6. Mental-model summary

| Principle | Consequence |
|---|---|
| A list holds ordered items at indices `0 … len−1` | Index past the end → `IndexError`; `in` tests whole elements |
| Lists are mutable; `lst[i] = x` edits in place | Strings reject it (`TypeError`); pick list vs string by "will it change?" |
| `append`/`insert`/`remove` return `None`; `pop` returns the item | `remove(x)` raises `ValueError` if `x` is absent — guard with `in` |
| `lst[a:b]` is a new list, indices `a … b−1` | Stop is exclusive (`b−a` items); `lst[:]` copies the whole list |
| A list variable points at one object; `=` shares it | `b = a` aliases; mutate via either name and both see it — copy with `a[:]` |

## 7. Gotcha checklist

<div style="border-left:4px solid #da5233;background:rgba(218,82,51,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

- **`IndexError: list index out of range` →** you indexed at `len` or beyond; last valid index is `len(lst)-1`.
- **`TypeError: 'str' object does not support item assignment` →** strings are immutable; build a new string, or use a list.
- **`ValueError: list.remove(x): x not in list` →** the value isn't present; check `if x in lst` first.
- **A slice has one fewer item than expected →** `stop` is exclusive; `lst[a:b]` has `b−a` items.
- **Changing one list changed "another" →** they're the same list (`b = a` aliases); copy with `a[:]` or `list(a)`.

</div>

---

<div style="border-left:4px solid #6d28d9;background:rgba(109,40,217,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

🧪 **Predict, then check.** Start with `scores = [50, 60, 70, 80, 90]`. Predict each step's result: `scores.append(100)`, then `scores[0] = 55`, then `top3 = scores[-3:]`, then `scores.pop()`. Now the trap: predict what `top3` looks like after the `pop()` — did popping `scores` change `top3`? (Think about whether `top3` is a copy or an alias.) Build it and confirm.

</div>

## Your Turn

Before you move on, check your understanding with the coach — explain the idea, apply it, weigh the trade-offs, then defend your reasoning.

<div class="concept-coach"></div>
