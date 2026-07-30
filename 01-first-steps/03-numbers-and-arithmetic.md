---
title: Numbers & Arithmetic
summary: Python's arithmetic mostly matches school maths, but a handful of rules — true vs floor division, the remainder, exponent precedence, and binary floating-point — decide the result. Learn them and you can predict any expression's value before running it.
prereqs: []
---

# Numbers & Arithmetic — Predicting the Result

Python does arithmetic the way you'd expect from school — mostly. The thesis of this chapter is the "mostly": **a few specific rules — the two kinds of division, operator precedence, and how decimals are stored — explain every arithmetic result that looks surprising.** Learn those rules and you can predict what any expression evaluates to before you run it, which is exactly the skill that prevents silent wrong answers later.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **The core idea.**

- A few specific rules explain every surprising result.
- Those rules: the two kinds of division, operator precedence, and how decimals are stored.
- Learn them and you can **predict any expression before running it**.

</div>

Every output below was produced by running the code. As you read, change the numbers and predict the new result before clicking Run.

<div style="border-left:4px solid #15448e;background:rgba(21,68,142,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

📘 **How to read the Intuition boxes.** Each one is built in three moves:

1. **The mechanism** — what the interpreter is *actually doing*.
2. **A concrete bite** — a specific, runnable way the naive assumption fails.
3. **The earned rule** — the decision heuristic, now justified rather than asserted, plus its cost.

</div>

---

## Table of contents

1. [The four basic operators](#1-the-four-basic-operators)
2. [Integer division and remainder](#2-integer-division-and-remainder)
3. [Exponentiation](#3-exponentiation)
4. [Precedence and parentheses](#4-precedence-and-parentheses)
5. [Integers, floats, and the precision trap](#5-integers-floats-and-the-precision-trap)
6. [Mental-model summary](#6-mental-model-summary)
7. [Gotcha checklist](#7-gotcha-checklist)

---

## 1. The four basic operators

Addition, subtraction, and multiplication are written `+`, `-`, `*`, and division is `/`. They work on the `int` and `float` numbers from the last chapter.

```python run
print(7 + 3)
print(7 - 3)
print(7 * 3)
print(7 / 3)
```

**Output:**
```
10
4
21
2.3333333333333335
```

**Analysis.** The first three are unsurprising: `10`, `4`, `21`, all whole numbers. The fourth, `7 / 3`, is `2.3333333333333335` — a decimal. Division produced a `float` even though we divided two `int`s, and the long tail of digits is a preview of §5.

**Intuition.**
*Mechanism.* `/` is **true division**: it always produces a `float`, because the mathematically correct answer to "a divided by b" is generally not a whole number, and Python picks the type that can represent fractions.

*Concrete bite.* This holds even when the division comes out even:

```python run
print(6 / 2)         # not 3 — it is 3.0
print(type(6 / 2))
```
```
3.0
<class 'float'>
```

`6 / 2` is `3.0`, a `float`, not `3` the `int` — the result type is decided by the *operator*, not by whether the answer happens to be whole.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** `+`, `-`, `*` keep `int`s as `int`s, but `/` always gives a `float`. The cost surfaces later: some operations (like picking an item at a position) demand an `int` and reject `3.0`, so when you want whole-number division you need a different operator — the next section's `//`.

</div>

---

## 2. Integer division and remainder

Two operators handle whole-number division. `//` (floor division) gives the whole-number part of a division; `%` (modulo) gives the remainder left over. Together they answer "how many whole times does b fit into a, and what's left?"

```python run
print(17 // 5)    # how many whole 5s fit in 17
print(17 % 5)     # what is left over
```

**Output:**
```
3
2
```

**Analysis.** Five fits into seventeen three whole times (`17 // 5` is `3`), with two left over (`17 % 5` is `2`). Check: `3 * 5 + 2 == 17`. These two operators are how you test "is this number even?" (`n % 2`), wrap values around a range, or split a total into groups.

**Intuition.**
*Mechanism.* `//` doesn't "chop off the decimal" — it **floors**, meaning it rounds *down* toward negative infinity to the nearest whole number. For positive results, flooring and chopping look identical, which hides the difference.

*Concrete bite.* Make the result negative and the two ideas part ways:

```python run
print(7 // 2)     # 3, as expected
print(-7 // 2)    # NOT -3 — it rounds down to -4
```
```
3
-4
```

`7 // 2` is `3` (chopping and flooring agree). But `-7 // 2` is `-4`, not `-3`: true division gives `-3.5`, and flooring rounds *down* to `-4`. "Chopping the decimal" would have given `-3` — the wrong answer. The remainder follows the same rule, so `%` with negatives can surprise too: `-7 % 2` is `1`, not `-1`.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Use `//` for whole-number division and `%` for remainders, but remember `//` floors toward −∞ — for negative numbers it is *not* the same as discarding the decimal. The cost of forgetting is an off-by-one bug that only appears once a value goes negative, which is exactly when it's hardest to notice.

</div>

---

## 3. Exponentiation

Raising a number to a power is `**` (two asterisks). `2 ** 10` is "2 to the power 10." A fractional exponent gives roots: `x ** 0.5` is the square root of `x`.

```python run
print(2 ** 10)    # 2 to the power of 10
print(2 ** 0.5)   # a fractional exponent: the square root of 2
```

**Output:**
```
1024
1.4142135623730951
```

**Analysis.** `2 ** 10` is `1024` (an `int`, since both operands are `int`s and the result is whole). `2 ** 0.5` is `1.4142135623730951` — the square root of 2, a `float` because the exponent is a `float`.

**Intuition.**
*Mechanism.* `**` binds **more tightly** than the other arithmetic operators — and, surprisingly, more tightly than a leading minus sign. So Python applies the power *before* it applies a negation in front of it.

*Concrete bite.* That precedence makes a negative-looking expression come out negative:

```python run
print(-2 ** 2)    # is this 4, or -4?
```
```
-4
```

You might read `-2 ** 2` as "(−2) squared = 4." Python reads it as `-(2 ** 2)` = `-(4)` = `-4`, because `**` runs before the minus. To square negative two, you must group it: `(-2) ** 2` gives `4`.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** `**` is exponentiation and has very high precedence — higher than unary minus — so parenthesise when a negative base is involved. The cost of the default is silent sign errors: `-2 ** 2` gives a perfectly valid number, just not the one you meant, so nothing flags the mistake.

</div>

---

## 4. Precedence and parentheses

When several operators appear in one expression, Python applies them in a fixed **precedence** order — the same "times before plus" rule as school maths: `*`, `/`, `//`, `%` bind tighter than `+` and `-`. Parentheses override the order.

```python run
print(2 + 3 * 4)      # multiplication happens before addition
print((2 + 3) * 4)    # parentheses force the addition first
```

**Output:**
```
14
20
```

**Analysis.** `2 + 3 * 4` is `14`: `3 * 4` happens first (`12`), then `+ 2`. Add parentheses — `(2 + 3) * 4` — and the addition goes first (`5`), then `* 4`, giving `20`. Same numbers, same operators, different grouping, different answer.

**Intuition.**
*Mechanism.* Python evaluates higher-precedence operators before lower ones regardless of left-to-right reading order, and parentheses force a sub-expression to be computed first.

*Concrete bite.* Precedence quietly ruins a hand-written average:

```python run
print(1 + 2 + 3 / 3)      # not 2 — the division happens first
print((1 + 2 + 3) / 3)    # the average you actually meant
```
```
4.0
2.0
```

`1 + 2 + 3 / 3` looks like "average of 1, 2, 3 = 2," but `/` binds tighter than `+`, so Python computes `3 / 3 = 1.0` first, then `1 + 2 + 1.0 = 4.0`. The average you intended needs parentheses around the sum: `(1 + 2 + 3) / 3` is `2.0`.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Memorise the core order — `**` first, then `* / // %`, then `+ -` — but **parenthesise anything non-obvious** rather than trusting the reader (often future-you) to recall it. The cost of getting precedence wrong is the worst kind: no error at all, just a confidently wrong number.

</div>

---

## 5. Integers, floats, and the precision trap

`int`s are exact whole numbers of any size. `float`s represent numbers with a decimal point — but they store them in **binary**, and most decimal fractions have no exact binary form, so a `float` is often a very close *approximation*, not the exact value.

```python run
print(10 / 3)
print(10 // 3)
```

**Output:**
```
3.3333333333333335
3
```

**Analysis.** `10 / 3` is a `float` approximation of one-third-times-ten, accurate to ~16 digits — note it even ends in `...35`, not an endless run of 3s, because that's the closest value the binary `float` can hold. `10 // 3` sidesteps fractions entirely and gives the exact `int` `3`.

**Intuition.**
*Mechanism.* A `float` is stored as the nearest representable binary fraction. For values like `0.1` that have no exact binary form, "nearest" means *slightly off*, and those tiny errors can add up visibly.

*Concrete bite.* The most famous example in all of programming:

```python run
total = 0.1 + 0.2
print(total)              # not exactly 0.3
```
```
0.30000000000000004
```

`0.1` and `0.2` are each stored a hair off, and their errors combine to `0.30000000000000004` — not `0.3`. This is not a Python bug; it's how binary floating-point works in every mainstream language. The fix when you need a clean decimal is to **round** to the precision you care about (`round(value, ndigits)`):

```python run
total = 0.1 + 0.2
print(round(total, 2))    # 0.3, rounded to 2 decimal places
```
```
0.3
```

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Treat `float` results as accurate-but-approximate: round for display, and never assume two floats are *exactly* equal (a trap you'll meet head-on with `==` in [Tutorial 6](/synapse/programming-languages/python/control-flow/booleans-and-logic)). The cost of the approximation is the whole reason it exists — floats trade exactness for the ability to represent a vast range of magnitudes efficiently; when you need exact decimals (money, especially), work in integer units like cents, or reach for the `decimal` module much later.

</div>

---

## 6. Mental-model summary

| Principle | Consequence |
|---|---|
| `/` is true division — always a `float` | `6 / 2` is `3.0`, not `3`; use `//` for a whole-number result |
| `//` floors toward −∞; `%` is the remainder | `-7 // 2` is `-4` (not `-3`); `-7 % 2` is `1` |
| `**` is exponentiation with very high precedence | `-2 ** 2` is `-4`; write `(-2) ** 2` for `4` |
| Operators follow precedence: `**` → `* / // %` → `+ -` | `1 + 2 + 3 / 3` is `4.0`; parenthesise to force order |
| `float`s are binary approximations of decimals | `0.1 + 0.2` is `0.30000000000000004`; round for display |

## 7. Gotcha checklist

<div style="border-left:4px solid #da5233;background:rgba(218,82,51,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

- **Got a `float` where you wanted a whole number →** you used `/`; switch to `//` for floor division.
- **Negative `//` or `%` looks off by one →** `//` floors toward −∞; for `-7 // 2` that's `-4`, by design.
- **`-x ** 2` came out negative →** `**` binds tighter than the minus; write `(-x) ** 2`.
- **A formula gives the wrong number with no error →** precedence bit you; add parentheses around the part that must go first.
- **`0.1 + 0.2` isn't `0.3` / decimals look slightly wrong →** binary float approximation; `round(value, n)` for display, integer cents for money.

</div>

---

<div style="border-left:4px solid #6d28d9;background:rgba(109,40,217,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

🧪 **Predict, then check.** Without running them, write down the value **and the type** of each: `9 / 3`, `9 // 2`, `-9 // 2`, `2 + 2 ** 3`, and `(0.1 + 0.1 + 0.1)`. Two of these have results that surprise most beginners — predict all five, then build a runnable block to check. Being able to do this reliably is the entire goal of the chapter.

</div>

## Your Turn

Before you move on, check your understanding with the coach — explain the idea, apply it, weigh the trade-offs, then defend your reasoning.

<div class="concept-coach"></div>
