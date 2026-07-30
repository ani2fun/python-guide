---
title: Booleans, Comparisons & Logic
summary: Comparisons produce a bool, and/or/not combine them, and Python can judge the truth of ANY value — the machinery every if and while relies on. Comparison operators, boolean logic, truthiness, short-circuit evaluation, and membership, with the float-equality and or-default traps shown live.
prereqs: []
---

# Booleans, Comparisons & Logic — Asking Yes/No Questions

Every decision a program makes comes down to a **bool** — `True` or `False` (the type you met in [Tutorial 2](/synapse/programming-languages/python/first-steps/variables-and-types)). This chapter is about producing and combining those values, because the `if` and `while` of the next chapters do nothing more than check a bool and act on it. The thesis: **comparisons and logic operators turn data into `True`/`False`, and Python can judge the "truth" of *any* value at all** — which is the machinery every decision in the rest of the book runs on.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **The core idea.**

- Comparisons and logic operators turn data into `True`/`False`.
- Python can judge the **truth of any value at all**.
- This is the machinery every decision in the book runs on.

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

1. [Comparisons produce booleans](#1-comparisons-produce-booleans)
2. [Combining conditions: `and`, `or`, `not`](#2-combining-conditions-and-or-not)
3. [Truthiness: every value is true-ish or false-ish](#3-truthiness-every-value-is-true-ish-or-false-ish)
4. [Short-circuit evaluation](#4-short-circuit-evaluation)
5. [Membership with `in`](#5-membership-with-in)
6. [Mental-model summary](#6-mental-model-summary)
7. [Gotcha checklist](#7-gotcha-checklist)

---

## 1. Comparisons produce booleans

A **comparison** asks a yes/no question about two values and answers with a bool. The six operators: `==` (equal), `!=` (not equal), `<`, `>`, `<=`, `>=`.

```python run
print(5 > 3)
print(5 == 5)
print(5 != 3)
print(2 <= 2)
print(10 < 9)
```

**Output:**
```
True
True
True
True
False
```

**Analysis.** Each line evaluated a comparison to a single bool. Note `==` (two equals signs) asks "are these equal?" — distinct from `=` (one equals sign), which *assigns* ([Tutorial 2](/synapse/programming-languages/python/first-steps/variables-and-types)). Mixing them up is one of the most common beginner errors, and the next chapter shows the `SyntaxError` it causes.

**Intuition.**
*Mechanism.* A comparison operator takes two values and returns `True` or `False` by examining them — for numbers, by their magnitude. The result is an ordinary bool you can store, print, or feed to an `if`.

*Concrete bite.* Comparing floats with `==` is treacherous, because (from [Tutorial 3](/synapse/programming-languages/python/first-steps/numbers-and-arithmetic)) floats are approximations:

```python run
print(0.1 + 0.2 == 0.3)
print(0.1 + 0.2)
```
```
False
0.30000000000000004
```

`0.1 + 0.2` is `0.30000000000000004`, not exactly `0.3`, so the `==` is `False` — a comparison that "should" be true isn't.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Use `==`/`!=`/`<`/`>` freely on integers, strings, and bools, but **never compare floats with `==`** — test closeness instead (`abs(a - b) < 1e-9`, or `math.isclose(a, b)`). The cost of forgetting is a condition that silently never fires; the boundary is that exact equality is only safe for values stored exactly, which floats usually aren't.

</div>

---

## 2. Combining conditions: `and`, `or`, `not`

Real decisions combine several yes/no questions. `and` is True only if **both** sides are; `or` is True if **either** side is; `not` flips a bool.

```python run
age = 25
print(age > 18 and age < 65)
print(age < 13 or age > 60)
print(not age > 18)
```

**Output:**
```
True
False
False
```

**Analysis.** `age > 18 and age < 65` is `True and True` → `True`. `age < 13 or age > 60` is `False or False` → `False`. `not age > 18` is `not True` → `False` (`not` binds looser than the comparison, so it negates the whole `age > 18`).

**Intuition.**
*Mechanism.* `and`/`or` look at the truth of each side to decide the result. Crucially, they must be given **complete conditions** on both sides — each side is judged on its own.

*Concrete bite.* The classic mistake is "factoring out" a comparison the way you would in English — "is color red or blue?":

```python run
color = "green"
print(color == "red" or "blue")
```
```
blue
```

You meant "is `color` red, or is `color` blue?" But Python reads it as `(color == "red") or ("blue")` — that's `False or "blue"`, and `or` hands back `"blue"` (a non-empty, truthy string). The condition is *always* truthy regardless of `color`, so a test you thought was selective accepts everything.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Spell out **both** sides of each `and`/`or`: `color == "red" or color == "blue"` (or, more cleanly, `color in ("red", "blue")` — see §5). The cost of the shortcut is a condition that looks right in English but is always true, and never warns you.

</div>

---

## 3. Truthiness: every value is true-ish or false-ish

Python can treat **any** value as a condition, not just bools. When it needs a yes/no — in an `if`, a `while`, or with `and`/`or` — it asks the value whether it is "truthy" or "falsy." The **falsy** values are few: `False`, `0`, `0.0`, `""` (empty string), `None`, and empty containers (like `[]`). Everything else is **truthy**. `bool(x)` shows you which.

```python run
print(bool(0))
print(bool(42))
print(bool(""))
print(bool("hi"))
print(bool(0.0))
```

**Output:**
```
False
True
False
True
False
```

**Analysis.** Zero (`0` and `0.0`) and the empty string are falsy; a non-zero number and a non-empty string are truthy. This is what lets you write `if name:` to mean "if name is non-empty" instead of the longer `if name != ""`.

**Intuition.**
*Mechanism.* "Falsy" means "empty or zero or nothing"; "truthy" means "has something." Python maps each value to one or the other when a boolean is needed, so a value can stand in for a condition.

*Concrete bite.* The trap is assuming the *contents* are inspected. They aren't — only emptiness is:

```python run
print(bool("0"))
print(bool(0))
```
```
True
False
```

The string `"0"` is **truthy** — it's a one-character string, and non-empty strings are always truthy, regardless of what that character is. Only the *number* `0` is falsy. So `if user_input:` accepts the text `"0"` as "present," which may not be what you want.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Use truthiness for "is this empty/missing?" checks (`if items:`, `if name:`), but when the literal value matters — especially text that might be `"0"` or `"False"` — compare explicitly. The cost of truthiness is exactly this: it collapses every non-empty value to `True`, hiding the difference between `"0"` and `"yes"`.

</div>

---

## 4. Short-circuit evaluation

`and`/`or` are lazy: they evaluate left to right and **stop as soon as the answer is decided**. For `and`, a falsy left side settles it (False) — the right side is never looked at. For `or`, a truthy left side settles it. And what they hand back is the deciding *operand*, not necessarily a bare bool.

```python run
x = 0
print(x != 0 and 10 / x > 1)   # second test is skipped, so no division by zero
```

**Output:**
```
False
```

**Analysis.** `x != 0` is `False`. For `and`, a false left side decides the whole thing, so Python never evaluates `10 / x > 1` — which is lucky, because `10 / 0` would crash with `ZeroDivisionError`. The short-circuit acted as a guard.

**Intuition.**
*Mechanism.* `and`/`or` return the operand that decided the result, not a converted `True`/`False`. `a and b` gives `a` if `a` is falsy, otherwise `b`; `a or b` gives `a` if `a` is truthy, otherwise `b`.

*Concrete bite.* So their results aren't always `True`/`False`:

```python run
print(1 and 2)
print(0 or 3)
print("" or "fallback")
```
```
2
3
fallback
```

`1 and 2` → `2` (1 is truthy, so the result is the second operand). `0 or 3` → `3` (0 is falsy, fall through to `3`). `"" or "fallback"` → `"fallback"`. That last one is the useful **default-value idiom**: `name or "Anonymous"` yields `name` when it's non-empty, else the fallback.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Lean on short-circuiting to guard risky operations (`x != 0 and 10/x`) and to supply defaults (`value or default`). The cost/boundary: `value or default` replaces *every* falsy value — `0`, `0.0`, `""`, `False` — with the default, so if `0` is a legitimate input, use an explicit `if value is None` instead (a distinction [Tutorial 16](/synapse/programming-languages/python/how-python-works/the-object-model) sharpens).

</div>

---

## 5. Membership with `in`

`in` asks "does this contain that?" and returns a bool. For a string, it tests whether one string is a **substring** of another.

```python run
print("ell" in "hello")
print("z" in "hello")
print("H" in "hello")
```

**Output:**
```
True
False
False
```

**Analysis.** `"ell"` appears inside `"hello"`, so the first is `True`. `"z"` doesn't appear, so `False`. `"H"` (capital) doesn't appear in lowercase `"hello"` — string membership is case-sensitive, like `==`.

**Intuition.**
*Mechanism.* `x in s` scans `s` for an occurrence of `x` and returns a bool. For strings it's a substring search; for lists (next chapters) it tests element membership. It compares with `==`, so it inherits case sensitivity and exactness.

*Concrete bite.* `in` matches a substring *anywhere*, and is case-sensitive — both of which surprise people:

```python run
print("Cat" in "cat")
print("cat" in "concatenate")
```
```
False
True
```

`"Cat" in "cat"` is `False` (capital C ≠ lowercase c). `"cat" in "concatenate"` is `True` — `cat` appears inside `con·cat·enate`, even though "cat" isn't a *word* there. `in` finds substrings, not words.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Use `in` for quick "contains?" checks, but normalise case first when you mean a case-insensitive match (`"cat" in text.lower()`), and remember it's a substring test, not a word test. The cost is false positives like `"cat" in "concatenate"`; for whole-word matching you need more than `in` (string methods or, later, splitting into words).

</div>

---

## 6. Mental-model summary

| Principle | Consequence |
|---|---|
| Comparisons (`== != < > <= >=`) return a bool | `==` is a question; `=` is assignment — don't swap them |
| `==` on floats compares exact (approximate) values | `0.1 + 0.2 == 0.3` is `False`; test closeness instead |
| `and`/`or` need a full condition on each side | `x == "a" or "b"` is always truthy; write `x == "a" or x == "b"` |
| Any value is truthy/falsy (empty/zero/None = falsy) | `if name:` means "non-empty"; but `"0"` is truthy |
| `and`/`or` short-circuit and return an operand | `x != 0 and 10/x` is safe; `value or default` fills blanks (and zeros!) |
| `in` tests substring (strings), case-sensitively | `"cat" in "concatenate"` is `True`; lowercase first for case-insensitive |

## 7. Gotcha checklist

<div style="border-left:4px solid #da5233;background:rgba(218,82,51,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

- **A float comparison never matches →** don't use `==` on floats; test `abs(a-b) < 1e-9`.
- **A condition is always true →** you wrote `x == a or b`; both sides of `or` need a full comparison, or use `x in (a, b)`.
- **`"0"` or `"False"` treated as present →** truthiness only checks emptiness; non-empty strings are truthy, so compare the value explicitly.
- **`value or default` ignored a real `0` →** `or` treats `0`/`""`/`False` as missing; use `if value is None` when zero is valid.
- **A "contains" check matched the wrong thing →** `in` is a case-sensitive substring test; normalise case and remember it's not word-aware.

</div>

---

<div style="border-left:4px solid #6d28d9;background:rgba(109,40,217,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

🧪 **Predict, then check.** Set `stock = 0`. Predict each: `print(stock > 0)`, `print(bool(stock))`, `print(stock or "out of stock")`, and `print(stock == False)`. The last one surprises almost everyone — and explaining *why* `0 == False` behaves as it does is a perfect warm-up for the object model in Tier 3. Build a runnable block and confirm.

</div>

## Your Turn

Before you move on, check your understanding with the coach — explain the idea, apply it, weigh the trade-offs, then defend your reasoning.

<div class="concept-coach"></div>
