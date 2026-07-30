---
title: Variables & Basic Types
summary: A variable is a name attached to a value, and every value has a type that decides what it can do. Assignment, reassignment, the four basic types (int, float, str, bool), type(), and naming rules — with the type-mismatch and use-before-assign traps shown live.
prereqs: []
---

# Variables & Basic Types — Naming Values

So far our values have been used once and forgotten. A **variable** fixes that: it is **a name attached to a value, so you can refer to that value again later.** And every value carries a **type** — whole number, decimal, text, true/false — and **the type decides what the value can do.** Those two ideas (a name points at a value; the value has a type) are the entire content of this chapter, and they quietly underpin every program you'll ever write.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **The core idea.**

- A variable is a **name attached to a value**.
- The name lets you refer to that value again later.
- Every value has a **type** that decides what it can do.

</div>

This is a gentle first pass. Much later, [The Object Model](/synapse/programming-languages/python/how-python-works/the-object-model) revisits "names point at values" with full rigour — but you won't need that depth for a long time. Every output below was produced by running the code.

<div style="border-left:4px solid #15448e;background:rgba(21,68,142,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

📘 **How to read the Intuition boxes.** Each one is built in three moves:

1. **The mechanism** — what the interpreter is *actually doing*.
2. **A concrete bite** — a specific, runnable way the naive assumption fails.
3. **The earned rule** — the decision heuristic, now justified rather than asserted, plus its cost.

</div>

---

## Table of contents

1. [A name is attached to a value](#1-a-name-is-attached-to-a-value)
2. [Reassignment: a name can change](#2-reassignment-a-name-can-change)
3. [The four basic types](#3-the-four-basic-types)
4. [Asking a value its type with `type()`](#4-asking-a-value-its-type-with-type)
5. [Naming rules and conventions](#5-naming-rules-and-conventions)
6. [Mental-model summary](#6-mental-model-summary)
7. [Gotcha checklist](#7-gotcha-checklist)

---

## 1. A name is attached to a value

You create a variable with `=`: a **name** on the left, a **value** on the right. Read `=` as "is attached to" — after it runs, the name refers to that value everywhere you use it.

```python run
age = 25
print(age)
```

**Output:**
```
25
```

**Analysis.** `age = 25` attached the name `age` to the value `25`. When we then wrote `print(age)`, Python looked up what `age` refers to — the value `25` — and printed that. We could now use `age` anywhere we wanted that number.

```d2
direction: right

name: "age  (a name)" {
  shape: oval
}

value: "25  (an int value)" {
  shape: rectangle
}

name -> value: "points at"
```

**Intuition.**
*Mechanism.* `=` is not a question or a statement of fact — it's an **action**: "make this name refer to this value." The name is created the moment you assign to it, and not before.

*Concrete bite.* Use a name before you've assigned it and Python doesn't know what you mean:

```python run
print(score)
score = 10
```
```
Traceback (most recent call last):
  File "/w/main.py", line 1, in <module>
    print(score)
          ^^^^^
NameError: name 'score' is not defined
```

The `score = 10` on line 2 would have worked fine — but line 1 ran first (top to bottom, as always), and at that moment `score` didn't refer to anything yet.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** A name exists only **after** you assign to it, so define before you use. The cost of the rule is the flip side of [Tutorial 1's halt-on-error](/synapse/programming-languages/python/first-steps/what-is-python): a name used too early is a `NameError`, not a blank or a zero — Python refuses to guess a value you never gave.

</div>

---

## 2. Reassignment: a name can change

A name isn't stuck to its first value. Assign to it again and it refers to the new value from then on. This lets one name track a changing quantity — a score, a total, a count.

```python run
count = 10
count = count + 1   # read it right-to-left: new count is old count plus 1
print(count)
```

**Output:**
```
11
```

**Analysis.** Line 1 attaches `count` to `10`. Line 2 looks confusing if you read `=` as "equals" — but Python evaluates the **right side first** (`count + 1`, which is `10 + 1`, i.e. `11`), and *then* attaches `count` to that result. So `count` goes from `10` to `11`. Line 3 prints its current value.

**Intuition.**
*Mechanism.* On every assignment Python computes the right-hand side completely, then points the left-hand name at the result. The old value the name held is simply let go.

*Concrete bite.* If `=` meant mathematical *equality*, then `count = count + 1` would be a contradiction — no number equals itself plus one. The naive "equals" reading predicts an error or an impossibility. Instead it runs and prints `11`:

```python run
count = 10
count = count + 1
print(count)
```
```
11
```

The clean `11` is the proof: `=` is assignment ("becomes"), not equality.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Read `x = expr` as "**x becomes the value of expr**," always right-side-first. The benefit is that updating a value is natural (`count = count + 1`, or its shorthand `count += 1`); the cost is that `=` looks like the maths equals sign but doesn't behave like it — a confusion worth unlearning early, because the equality *question* is a different operator (`==`, in [Tutorial 6](/synapse/programming-languages/python/control-flow/booleans-and-logic)).

</div>

---

## 3. The four basic types

Every value has a **type** — its kind. At this tier you need four:

- **`int`** — an integer, a whole number: `42`, `-7`, `0`.
- **`float`** — a "floating-point" number, one with a decimal point: `3.14`, `-0.5`, `2.0`.
- **`str`** — a "string," text inside quotes: `"Ada"`, `'hello'`.
- **`bool`** — a Boolean, one of exactly two values: `True` or `False` (always capitalised).

```python run
n = 42          # int — a whole number
pi = 3.14       # float — a number with a decimal point
name = "Ada"    # str — text in quotes
ok = True       # bool — either True or False
print(n, pi, name, ok)
```

**Output:**
```
42 3.14 Ada True
```

**Analysis.** Four names, four values, four different types. `print` showed them space-separated on one line. Notice `42` and `3.14` print as numbers (no quotes), `Ada` prints as plain text (the quotes were Python's cue that it's a string, not part of the value), and `True` is a value in its own right, not text.

**Intuition.**
*Mechanism.* The type isn't a label *you* manage — Python infers it from how you write the value (quotes → `str`, a decimal point → `float`, `True`/`False` → `bool`) and then *uses* the type to decide what operations are allowed.

*Concrete bite.* Because the type decides what's allowed, mixing incompatible types is an error. Text and a number can't be joined with `+`:

```python run
age = 25
print("Age: " + age)
```
```
Traceback (most recent call last):
  File "/w/main.py", line 2, in <module>
    print("Age: " + age)
          ~~~~~~~~^~~~~
TypeError: can only concatenate str (not "int") to str
```

`+` between two strings means "join them," and between two numbers means "add them" — but `str + int` has no agreed meaning, so Python refuses with a `TypeError` rather than guessing.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Types are not interchangeable; an operator's meaning depends on the types it's given. The cost of mixing them is a `TypeError` — which is a *good* thing, because the alternative (a silent wrong guess) would be a far worse bug. When you genuinely need to combine a number with text, convert it deliberately (`str(age)`) or use an f-string — both are in [Tutorial 4](/synapse/programming-languages/python/first-steps/strings-the-basics) and [Tutorial 5](/synapse/programming-languages/python/first-steps/input-and-output).

</div>

---

## 4. Asking a value its type with `type()`

When you're unsure what type a value is, ask. `type(x)` reports the type of `x` — invaluable when a `TypeError` has you puzzled.

```python run
print(type(42))
print(type(3.14))
print(type("Ada"))
print(type(True))
```

**Output:**
```
<class 'int'>
<class 'float'>
<class 'str'>
<class 'bool'>
```

**Analysis.** Each call reports the kind of value it was given: `42` is an `int`, `3.14` a `float`, `"Ada"` a `str`, `True` a `bool`. ("`<class '...'>`" is just Python's way of naming a type; read it as "this is an int," and so on.)

**Intuition.**
*Mechanism.* Every value carries its type with it at all times, and `type()` simply reads it back. The way you *wrote* the literal is what fixed the type.

*Concrete bite.* That means a single character — a decimal point — changes the type, even when the number looks "the same":

```python run
print(type(10))
print(type(10.0))
```
```
<class 'int'>
<class 'float'>
```

`10` is an `int`; `10.0` is a `float`. They represent the same quantity but are different types, and that difference will matter the moment you divide (next chapter, where `/` always produces a `float`).

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Reach for `type(x)` whenever behaviour surprises you — it's the fastest way to diagnose a `TypeError`. The boundary: `type()` tells you *what a value is*, not whether two values are *equal* — that's `==`, a separate idea you'll meet in [Tutorial 6](/synapse/programming-languages/python/control-flow/booleans-and-logic).

</div>

---

## 5. Naming rules and conventions

You choose variable names, but Python has a few hard **rules**, plus a strong **convention**. The rules: a name may contain letters, digits, and underscores; it must **not start with a digit**; and it can't be one of Python's reserved words (like `if` or `for`). The convention: use `snake_case` — all lowercase, words joined by underscores (`first_name`, `total_score`).

```python run
first_name = "Ada"     # snake_case: lowercase words joined by underscores
print(first_name)
```

**Output:**
```
Ada
```

**Analysis.** `first_name` is a clear, legal name: letters and an underscore, starting with a letter. It reads as plain English, which is the whole point — code is read far more often than it's written.

**Intuition.**
*Mechanism.* Python checks a name's *form* while reading your text, before running anything. A name that breaks the form isn't a runtime mistake — it's a **`SyntaxError`**, raised at parse time, so the program doesn't start at all.

*Concrete bite.* Start a name with a digit and Python can't even parse the line:

```python run
2nd_place = "silver"   # a name can't start with a digit
```
```
  File "/w/main.py", line 1
    2nd_place = "silver"   # a name can't start with a digit
    ^
SyntaxError: invalid decimal literal
```

Seeing `2n…`, Python tries to read a number, then hits letters and gives up — a `SyntaxError`. Note this is different from a `NameError`: nothing ran, because the code couldn't be understood in the first place.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Names start with a letter or underscore, then any mix of letters, digits, and underscores; write them in `snake_case` and make them descriptive. The cost of a bad name is split: an illegal *form* is a `SyntaxError` (caught instantly), but a *legal-but-vague* name like `x2` or `data` costs you every time you re-read the code and have to remember what it meant — a slower, more expensive kind of error.

</div>

---

## 6. Mental-model summary

| Principle | Consequence |
|---|---|
| `=` attaches a name to a value (an action, right-side-first) | `count = count + 1` works and means "count becomes count + 1" |
| A name exists only after it's assigned | Using it earlier is a `NameError` |
| Every value has a type, inferred from how you write it | Quotes → `str`, decimal point → `float`, `True`/`False` → `bool` |
| The type decides what operations are allowed | `str + int` is a `TypeError`, not a silent guess |
| `type(x)` reports a value's type | Your fastest tool for diagnosing a `TypeError` |
| Names follow a form (no leading digit) and a `snake_case` convention | Illegal form → `SyntaxError`; vague names cost you on every re-read |

## 7. Gotcha checklist

<div style="border-left:4px solid #da5233;background:rgba(218,82,51,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

- **`NameError: name 'X' is not defined` →** you used `X` before assigning it (or misspelled it); assign it on an earlier line.
- **`TypeError: can only concatenate str (not "int") to str` →** you joined text and a number with `+`; convert with `str(n)` or use an f-string (Tutorials 4–5).
- **`SyntaxError: invalid decimal literal` →** a name starts with a digit; rename it to start with a letter or underscore.
- **A value behaves unexpectedly →** check `type(x)`; `10` (int) and `10.0` (float) are different even though they look alike.
- **Reused a confusing one-letter name →** legal but costly; rename to a descriptive `snake_case` name.

</div>

---

<div style="border-left:4px solid #6d28d9;background:rgba(109,40,217,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

🧪 **Predict, then check.** Without running it, decide what each line of this program does — and which one fails: `temperature = 20`; then `temperature = temperature + 5`; then `print("Temp: " + temperature)`. Which line errors, what's the error's name, and how would you fix it so it prints `Temp: 25`? Then write it as a runnable block and confirm. (Hint: two different tools from this chapter can fix the last line — `str()` or, after the next two chapters, an f-string.)

</div>

## Your Turn

Before you move on, check your understanding with the coach — explain the idea, apply it, weigh the trade-offs, then defend your reasoning.

<div class="concept-coach"></div>
