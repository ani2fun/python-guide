---
title: Input & Output
summary: input() always hands you a string, so to compute with a typed number you must convert it first. Output with f-strings, reading input, int()/float() conversion, a first interactive program, and the bad-input crash — building on every earlier Tier 0 chapter.
prereqs: []
---

# Input & Output — Talking With the User

A program gets more useful the moment it can take input from a person and respond. This chapter wires together everything in Tier 0 into interactive programs, around one rule that causes more beginner bugs than any other: **`input()` always gives you a string — never a number — so before you can do arithmetic on what someone typed, you must convert it.** Output, meanwhile, is just the f-strings you already know, now filled with values that came from the user.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **The core idea.**

- `input()` always gives you a **string**, never a number.
- To do arithmetic on what was typed, you must **convert** it first.
- Output is just f-strings filled with values from the user.

</div>

Every output below was produced by running the code. One practical note about *this page's* runner, though:

> **A note on the Run button and typed input.** The sandbox behind ▶ Run executes your code but can't pause to prompt you for keyboard input. So the `input()` examples here are shown as **static** code with the exact output they produce *for a stated entry* (verified by running them with that input supplied). Where it helps, a **runnable twin** hardcodes the "typed" value so you can still click Run and experiment. When you run these for real on your own machine, `input()` will pause and wait for you to type.

<div style="border-left:4px solid #15448e;background:rgba(21,68,142,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

📘 **How to read the Intuition boxes.** Each one is built in three moves:

1. **The mechanism** — what the interpreter is *actually doing*.
2. **A concrete bite** — a specific, runnable way the naive assumption fails.
3. **The earned rule** — the decision heuristic, now justified rather than asserted, plus its cost.

</div>

---

## Table of contents

1. [Building output](#1-building-output)
2. [`input()` always gives you a string](#2-input-always-gives-you-a-string)
3. [Converting input to numbers](#3-converting-input-to-numbers)
4. [A first interactive program](#4-a-first-interactive-program)
5. [When the input is bad](#5-when-the-input-is-bad)
6. [Mental-model summary](#6-mental-model-summary)
7. [Gotcha checklist](#7-gotcha-checklist)

---

## 1. Building output

You already have the tool for output: f-strings ([Tutorial 4](/synapse/programming-languages/python/first-steps/strings-the-basics)). Building a result message is just an f-string with your values dropped in.

```python run
name = "Ada"
score = 95
print(f"{name} scored {score} points")
```

**Output:**
```
Ada scored 95 points
```

**Analysis.** The f-string pulled `name` and `score` into a sentence and `print` displayed it. This is the shape of almost all program output: compute some values, then format them into text for a human to read.

**Intuition.**
*Mechanism.* `print` ends every call with a newline by default, so consecutive `print`s stack vertically. That default lives in a setting called `end`, which you can change — for example to `""` (empty) to keep the next output on the same line.

*Concrete bite.* Two prints that you might expect to stack can be kept on one line:

```python run
print("Loading", end="")
print("...done")
```
```
Loading...done
```

The first `print` would normally end the line after `Loading`; `end=""` removed that line ending, so `...done` continued on the same line. Without `end=""`, you'd get `Loading` and `...done` on separate lines.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Use f-strings to format output and `end=""` when you need to build a line across several prints. The cost of the default newline is the occasional unwanted line break — `end` is the dial that controls it (just as `sep` controlled the gaps *between* a single print's arguments back in [Tutorial 1](/synapse/programming-languages/python/first-steps/what-is-python)).

</div>

---

## 2. `input()` always gives you a string

`input(prompt)` shows your prompt, waits for the user to type a line and press Enter, and hands that line back as a value you store in a variable. That value is **always a string** — even if the user typed digits.

```python
name = input("What's your name? ")
print(f"Hello, {name}!")
```

**Output** (when you type `Ada` and press Enter):
```
What's your name? Hello, Ada!
```

**Analysis.** `input("What's your name? ")` printed the prompt, then waited; whatever the user typed became the value of `name`. We then greeted them with an f-string. (The greeting runs straight after the prompt on the same line because the sandbox doesn't echo your keystrokes the way a terminal does — on your own machine you'd see `Ada` between them, where you typed it.)

**Intuition.**
*Mechanism.* `input()` reads raw text. It has no idea whether you *meant* a name, a number, or a date — it returns exactly the characters typed, as a `str`, every time.

*Concrete bite.* So "doing maths" on input does string operations instead, which can produce a wrong-looking answer with no error at all. Suppose the user types `5`:

```python
x = input("Enter a number: ")
print(x * 3)     # you typed 5 — but this prints 555, not 15
```

**Output** (when you type `5`):
```
Enter a number: 555
```

You typed `5` expecting `5 * 3 = 15`, but `x` is the *string* `"5"`, and `"5" * 3` is string **repetition** ([Tutorial 4](/synapse/programming-languages/python/first-steps/strings-the-basics)) — `"555"`. Here's the same trap as a runnable twin, with the "typed" value hardcoded so you can run it:

```python run
x = "5"          # imagine the user typed 5 — input() always returns a string
print(x * 3)     # 555, not 15 — that is string repetition, not arithmetic
```
```
555
```

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Treat every `input()` result as text until you deliberately convert it. The cost of forgetting is the nastiest kind of bug — no crash, just `"555"` where you expected `15` — which is exactly why the next section exists.

</div>

---

## 3. Converting input to numbers

To do arithmetic on typed digits, convert the string to a number first: `int(text)` for a whole number, `float(text)` for a decimal. These are the same conversion functions you'd use anywhere.

```python run
text = "42"          # a string of digits
number = int(text)   # convert it to an int
print(number + 8)    # now arithmetic works
```

**Output:**
```
50
```

**Analysis.** `int("42")` turned the string `"42"` into the integer `42`, and `42 + 8` is the real arithmetic `50` — not the string concatenation that `+` would have done on `"42"`. `float` does the same for decimals:

```python run
price = float("3.50")
print(price * 2)
```

**Output:**
```
7.0
```

**Intuition.**
*Mechanism.* `int()` and `float()` **parse** a string — read its characters and build the corresponding number. They're the bridge from "text the user typed" to "a number you can compute with," and they're the missing step in the §2 trap.

*Concrete bite.* The fix for the `555` bug is one conversion: wrap the input in `int()` before the maths. `int("5") * 3` is `15`, the answer you wanted — string-times-number was the bug, number-times-number is the fix.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Convert input at the boundary: read it as text, `int()`/`float()` it immediately, then work with the number. The cost is that conversion can *fail* if the text isn't a valid number — which is the subject of §5.

</div>

---

## 4. A first interactive program

Putting it together: read two numbers, convert both, add them, and report the result. Here's the runnable version, with the inputs hardcoded so you can run it on this page:

```python run
a = "7"      # imagine these two came from input()
b = "5"
total = int(a) + int(b)
print(f"{a} + {b} = {total}")
```

**Output:**
```
7 + 5 = 12
```

**Analysis.** We converted both strings with `int()` *before* adding, so `+` did arithmetic (`12`), not concatenation (which would have given `"75"`). The f-string then reported the result. The real, interactive version uses `input()` in place of the hardcoded strings:

```python
a = input("First number: ")
b = input("Second number: ")
total = int(a) + int(b)
print(f"{a} + {b} = {total}")
```

**Output** (when you type `7`, then `5`):
```
First number: Second number: 7 + 5 = 12
```

Both prompts appear before the answer because, again, the sandbox doesn't echo your typed input between them; on your own machine you'd type `7` after the first prompt and `5` after the second.

**Intuition.**
*Mechanism.* The structure here — **read input → convert → compute → output** — is the skeleton of countless programs. Each stage uses exactly one Tier 0 idea: `input()` for reading, `int()` for converting, `+` for computing, an f-string for output.

*Concrete bite.* Drop the conversions and the same program silently changes meaning: `input("...") + input("...")` with `7` and `5` gives `"75"` (two strings joined), not `12`. The `int()` calls are what make `+` mean addition.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Lay interactive programs out as read → convert → compute → output, and do the conversion as early as possible. The cost of skipping or delaying it is that `+` quietly flips from addition to concatenation — the single most common bug in beginner input code.

</div>

---

## 5. When the input is bad

Conversion isn't guaranteed to succeed. `int()` only accepts a string that *is* a whole number; anything else raises a `ValueError` and — per [Tutorial 1](/synapse/programming-languages/python/first-steps/what-is-python) — stops the program.

```python run
print(int("42"))     # fine — a whole number
print(int("3.5"))    # ValueError — "3.5" is not a whole number
```

**Output** (then an error):
```
42
```
```
Traceback (most recent call last):
  File "/w/main.py", line 2, in <module>
    print(int("3.5"))    # ValueError — "3.5" is not a whole number
          ~~~^^^^^^^
ValueError: invalid literal for int() with base 10: '3.5'
```

**Analysis.** `int("42")` worked and printed `42`. But `int("3.5")` failed: `"3.5"` is a valid *float* string, not an *int* string, so `int()` rejected it with a `ValueError` and the program halted before anything after it could run. (`int("abc")` fails the same way — `int()` wants digits.) A user who types `3.5` into our adder, or `seven` instead of `7`, will crash it exactly here.

**Intuition.**
*Mechanism.* `int()` validates as it parses: if the characters don't form a whole number, there's no sensible value to return, so it raises `ValueError` rather than guessing.

*Concrete bite.* The output above is the demonstration: `42` prints, then `int("3.5")` throws and execution stops. Real user input is unpredictable, so this isn't an edge case — it's Tuesday.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Convert at the boundary and assume conversion *can* fail on real input. The cost of unhandled bad input is a crash; for now, know that it happens and where. Handling it gracefully — letting the program recover and re-prompt instead of crashing — needs `try`/`except`, which is [Errors & Exceptions](/synapse/programming-languages/python/how-python-works/errors-and-exceptions). (One quick trick worth knowing: `int(float("3.5"))` succeeds by converting to `3.0` first, then to the integer `3` — at the cost of silently discarding the `.5`.)

</div>

---

## 6. Mental-model summary

| Principle | Consequence |
|---|---|
| `input()` always returns a `str` | Typed digits are text; `"5" * 3` is `"555"`, not `15` |
| Convert input with `int()` / `float()` before computing | `int("5") * 3` is `15`; conversion is the bridge to arithmetic |
| `+` on strings concatenates; on numbers it adds | Forgetting to convert flips addition into joining (`"7"+"5"` → `"75"`) |
| Output is f-strings; `end=""` controls the line ending | Build a line across prints with `print(..., end="")` |
| `int()`/`float()` raise `ValueError` on non-numbers | Bad input crashes at the conversion; recover with `try`/`except` (Tutorial 19) |

## 7. Gotcha checklist

<div style="border-left:4px solid #da5233;background:rgba(218,82,51,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

- **Maths on input gives a too-long or joined result (`555`, `75`) →** you computed on strings; wrap inputs in `int()`/`float()` first.
- **`TypeError` adding input to a number →** `input()` returned a `str`; convert it before the arithmetic.
- **`ValueError: invalid literal for int() …` →** the text isn't a whole number; check it, or use `try`/`except` (Tutorial 19); `int(float(s))` if you can accept dropping the decimals.
- **Prompts and answers run together on this page →** the sandbox doesn't echo typed input; on your own machine they appear where you type.
- **Two prints land on separate lines and you wanted one →** add `end=""` to the first.

</div>

---

<div style="border-left:4px solid #6d28d9;background:rgba(109,40,217,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

🧪 **Predict, then check.** Imagine a user runs the §4 adder and types `10` then `20`. Predict the exact output. Now suppose they type `10` then `twenty` — predict what happens and name the error. Finally, rewrite the runnable twin so it computes the *average* of `a` and `b` (hint: convert, add, divide by 2 — and recall from [Tutorial 3](/synapse/programming-languages/python/first-steps/numbers-and-arithmetic) which division operator and which precedence you need). Build it and confirm.

</div>

## Your Turn

Before you move on, check your understanding with the coach — explain the idea, apply it, weigh the trade-offs, then defend your reasoning.

<div class="concept-coach"></div>
