---
title: Strings, the Basics
summary: A string is a sequence of characters, and its methods return brand-new strings rather than changing the original. Quotes and escaping, joining and repeating, f-strings, the everyday methods, and indexing — with the discard-the-result and out-of-range traps shown live.
prereqs: []
---

# Strings, the Basics — Building and Reshaping Text

Text in Python is a **string** (`str`), and the one idea that explains almost all of its behaviour is this: **a string is a fixed sequence of characters, and every operation that "changes" a string actually builds and returns a new one — the original is never modified.** Concatenation, the methods, slicing — all of them produce fresh strings. Hold that idea and the chapter's central trap (calling a method and seeing "nothing happen") becomes obvious.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **The core idea.**

- A string is a **fixed sequence of characters**.
- Every operation that "changes" it builds and returns a **new** string.
- The original is **never modified**.

</div>

This is the gentle pass; [Strings in Depth](/synapse/programming-languages/python/working-with-data/strings-in-depth) returns later for the format mini-language and text algorithms, and [The Object Model](/synapse/programming-languages/python/how-python-works/the-object-model) explains *why* strings can't be changed in place. Every output below was produced by running the code.

<div style="border-left:4px solid #15448e;background:rgba(21,68,142,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

📘 **How to read the Intuition boxes.** Each one is built in three moves:

1. **The mechanism** — what the interpreter is *actually doing*.
2. **A concrete bite** — a specific, runnable way the naive assumption fails.
3. **The earned rule** — the decision heuristic, now justified rather than asserted, plus its cost.

</div>

---

## Table of contents

1. [String literals and quotes](#1-string-literals-and-quotes)
2. [Joining and repeating](#2-joining-and-repeating)
3. [f-strings](#3-f-strings)
4. [Everyday string methods](#4-everyday-string-methods)
5. [Reading individual characters](#5-reading-individual-characters)
6. [Mental-model summary](#6-mental-model-summary)
7. [Gotcha checklist](#7-gotcha-checklist)

---

## 1. String literals and quotes

You write a string by wrapping text in quotes — single (`'…'`) or double (`"…"`); Python treats them identically. Having both lets you put one kind of quote *inside* a string delimited by the other.

```python run
single = 'hello'
double = "hello"
print(single)
print(double)
quote = "She said \"hi\""   # escape inner double quotes with a backslash...
apostrophe = "it's fine"     # ...or just use the other quote style
print(quote)
print(apostrophe)
```

**Output:**
```
hello
hello
She said "hi"
it's fine
```

**Analysis.** `'hello'` and `"hello"` are the same string. To include a double quote inside a double-quoted string, we put a backslash before it (`\"`) — that's an **escape**, telling Python "this quote is part of the text, not the end of the string." The apostrophe in `"it's fine"` needs no escape because the string is delimited by double quotes, so the `'` is unambiguous.

**Intuition.**
*Mechanism.* The opening quote starts a string and the **next matching quote ends it** — that's how Python finds the boundaries while reading your text. A quote of the same kind inside the text looks exactly like the closing quote unless you escape it.

*Concrete bite.* Put an apostrophe inside a single-quoted string and the string ends early:

```python run
text = 'it's broken'
```
```
  File "/w/main.py", line 1
    text = 'it's broken'
                       ^
SyntaxError: unterminated string literal (detected at line 1)
```

Python read `'it'` as the whole string, then found `s broken'` — junk it can't parse — and reported an *unterminated* string. The apostrophe closed the string prematurely.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Choose the quote style that *isn't* in your text (use `"..."` for text with apostrophes), or escape the clashing quote with a backslash. The cost of getting it wrong is a `SyntaxError` at parse time — the program won't even start — but it's an easy fix once you recognise the "unterminated string literal" message.

</div>

---

## 2. Joining and repeating

Two operators you already know from numbers do something different with strings. `+` **concatenates** — joins strings end to end. `*` with a number **repeats** a string.

```python run
first = "Ada"
last = "Lovelace"
print(first + " " + last)   # concatenation with +
print("ab" * 3)              # repetition with *
print("-" * 10)              # a quick separator line
```

**Output:**
```
Ada Lovelace
ababab
----------
```

**Analysis.** `first + " " + last` glued three strings — the names and a literal space — into `Ada Lovelace`. `"ab" * 3` produced `ababab`, and `"-" * 10` a ten-dash line (a handy trick for separators). The operators are the same symbols as arithmetic; the *types* decide they mean "join" and "repeat" here, exactly as [Tutorial 2](/synapse/programming-languages/python/first-steps/variables-and-types) warned.

**Intuition.**
*Mechanism.* `+` requires **both sides to be strings** (it has no meaning for "string plus number"), and `*` repeats a string a **whole number** of times — so the count must be an `int`.

*Concrete bite.* A non-integer repeat count is an error, because "repeat something 2.0 times" is undefined:

```python run
print("ab" * 2.0)    # you can repeat a string by an int, but not by a float
```
```
Traceback (most recent call last):
  File "/w/main.py", line 1, in <module>
    print("ab" * 2.0)    # you can repeat a string by an int, but not by a float
          ~~~~~^~~~~
TypeError: can't multiply sequence by non-int of type 'float'
```

`2.0` is a `float`, and there's no such thing as repeating text a fractional number of times, so Python refuses. (The same strictness is why `"Age: " + 25` failed back in Tutorial 2 — `+` won't mix a string with a number.)

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Use `+` to join strings (both operands must be strings) and `* n` to repeat one (`n` must be an `int`). The cost of `+`'s strictness is that you can't drop a number straight into text with it — which is precisely the problem f-strings solve, next.

</div>

---

## 3. f-strings

The clean way to build text out of values is an **f-string**: put `f` immediately before the opening quote, then write `{…}` wherever you want a value inserted. Whatever's inside the braces is evaluated and converted to text automatically.

```python run
name = "Ada"
age = 36
print(f"{name} is {age} years old")
print(f"{name} will be {age + 1} next year")   # expressions work inside { }
```

**Output:**
```
Ada is 36 years old
Ada will be 37 next year
```

**Analysis.** `{name}` was replaced by `Ada` and `{age}` by `36` — and crucially, the number `36` was turned into text for us, no `str()` needed. Inside the braces you can write expressions too: `{age + 1}` computed `37`. This is why f-strings are the everyday tool for mixing values into messages.

**Intuition.**
*Mechanism.* The `f` prefix switches on substitution: Python scans the string for `{…}`, evaluates each one, converts the result to text, and splices it in. Without the `f`, the braces are just ordinary characters.

*Concrete bite.* Forget the `f` and the braces print literally — a silent mistake with no error:

```python run
name = "Ada"
print("{name} is here")    # no f — the braces print literally
print(f"{name} is here")   # with f — the value is substituted
```
```
{name} is here
Ada is here
```

The first line had no `f`, so Python printed the characters `{name}` verbatim. The second, with `f`, substituted the value. Nothing crashed — you just get the wrong text.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Prefix with `f` whenever you want values inside a string, and let it handle the type conversion `+` won't. The cost is the quietest kind of bug: a missing `f` produces no error, only literal `{...}` in your output — so when you see braces in your text, suspect a forgotten `f` first.

</div>

---

## 4. Everyday string methods

A **method** is a function attached to a value, called with a dot: `value.method(...)`. Strings come with many. The everyday ones: `upper()` / `lower()` change case, `strip()` removes surrounding whitespace, `replace(old, new)` swaps text, and `split(sep)` breaks a string apart.

```python run
s = "  Hello, World  "
print(s.upper())
print(s.lower())
print(s.strip())            # remove the surrounding spaces
print(s.replace("World", "Python"))
print("a,b,c".split(","))   # break apart on commas
```

**Output:**
```
  HELLO, WORLD  
  hello, world  
Hello, World
  Hello, Python  
['a', 'b', 'c']
```

**Analysis.** Each method returned a reshaped copy: uppercased, lowercased, trimmed, and with `World` swapped for `Python`. Notice `upper()`, `lower()`, and `replace()` *kept* the surrounding spaces (only `strip()` removed them) — each method changes one thing and leaves the rest alone. `split(",")` returned `['a', 'b', 'c']`, a **list** — a sequence of separate strings, which you'll meet properly in [Lists](/synapse/programming-languages/python/control-flow/lists-the-basics).

**Intuition.**
*Mechanism.* String methods never modify the original string — they can't, because strings are **immutable** (unchangeable once created). Each method **returns a new string**, leaving the one you called it on untouched.

*Concrete bite.* So a method call whose result you don't capture does nothing visible:

```python run
s = "hello"
s.upper()         # this returns "HELLO" — but we throw the result away
print(s)          # still "hello"
s = s.upper()     # capture the new string by assigning it back
print(s)          # now "HELLO"
```
```
hello
HELLO
```

The first `s.upper()` *did* produce `"HELLO"` — but we didn't store it, so it vanished, and `s` was still `"hello"`. Only when we wrote `s = s.upper()`, capturing the returned string, did `s` change.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Treat string methods as "give me a new string" and **assign the result** (`s = s.strip()`); a bare `s.strip()` is almost always a bug. The cost of immutability is this extra assignment, but the payoff is large and comes later: because a string can never change under you, it's safe to share freely and to use as a dictionary key ([Tutorial 13](/synapse/programming-languages/python/working-with-data/dictionaries-and-sets)).

</div>

---

## 5. Reading individual characters

A string is a sequence, so you can pull out one character by its **index** — its position. Indexing uses square brackets, and **positions start at 0**: the first character is `[0]`, the second `[1]`. Negative indices count from the end, so `[-1]` is the last character. `len(s)` gives the number of characters.

```python run
word = "Python"
print(word[0])     # the first character — counting starts at 0
print(word[1])     # the second character
print(word[-1])    # the last character
print(len(word))   # how many characters in total
```

**Output:**
```
P
y
n
6
```

**Analysis.** `word[0]` is `P` (the *first* character — index 0, not 1), `word[1]` is `y`, and `word[-1]` is `n` (the last). `len(word)` is `6`. So the valid positions for a 6-character string are `0` through `5` — the last index is always `len - 1`, one less than the length, precisely because counting starts at 0.

**Intuition.**
*Mechanism.* Each character sits at a numbered slot from `0` to `len - 1`. Asking for a slot outside that range has no answer, so Python raises an error rather than returning something empty.

*Concrete bite.* Off-by-one past the end is the classic mistake:

```python run
word = "Python"
print(word[6])     # valid indices are 0 to 5 — 6 is past the end
```
```
Traceback (most recent call last):
  File "/w/main.py", line 2, in <module>
    print(word[6])     # valid indices are 0 to 5 — 6 is past the end
          ~~~~^^^
IndexError: string index out of range
```

`"Python"` has 6 characters at indices `0`–`5`; index `6` would be the seventh, which doesn't exist, so Python raises `IndexError`. Because counting starts at 0, "the length" is always one past the last valid index.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** The first index is `0` and the last is `len(s) - 1`; use negative indices to reach the end without computing the length. The cost of zero-based counting is the perennial off-by-one error at the boundary — when an `IndexError` fires, check whether you used the length where you meant length-minus-one. (Pulling out a whole *range* of characters — slicing — comes in [Sequences](/synapse/programming-languages/python/working-with-data/sequences).)

</div>

---

## 6. Mental-model summary

| Principle | Consequence |
|---|---|
| A string ends at the next matching quote | An un-escaped inner quote → `SyntaxError`; pick the other quote style or escape it |
| `+` joins strings (both must be `str`); `* n` repeats (`n` must be `int`) | `"ab" * 2.0` is a `TypeError`; `+` won't mix string and number |
| An f-string substitutes `{…}` and converts to text | No `f` prefix → braces print literally, with no error |
| Strings are immutable; methods return new strings | `s.upper()` alone does nothing; you must write `s = s.upper()` |
| Indices run `0` to `len(s) - 1`; `[-1]` is the last | `s[len(s)]` is one past the end → `IndexError` |

## 7. Gotcha checklist

<div style="border-left:4px solid #da5233;background:rgba(218,82,51,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

- **`SyntaxError: unterminated string literal` →** a quote inside the string matched the opening quote early; switch quote styles or escape with `\`.
- **`TypeError: can't multiply sequence by non-int` →** you repeated a string by a `float`; the count must be an `int`.
- **Your output literally shows `{name}` →** you forgot the `f` before the opening quote.
- **A method "did nothing" →** you discarded its result; assign it back, e.g. `s = s.replace(a, b)`.
- **`IndexError: string index out of range` →** you indexed at `len(s)` or beyond; the last valid index is `len(s) - 1`.

</div>

---

<div style="border-left:4px solid #6d28d9;background:rgba(109,40,217,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

🧪 **Predict, then check.** Start with `name = "ada lovelace"`. Without running it, predict the output of each line, then build a runnable block to confirm: `print(name.upper())`, then `print(name)` again (did `name` change?), then `print(name[0])`, then `print(name[-1])`, and finally `print(f"{name} has {len(name)} characters")`. The one that catches most people is the second line — and knowing *why* `name` is unchanged is the whole point of this chapter.

</div>

## Your Turn

Before you move on, check your understanding with the coach — explain the idea, apply it, weigh the trade-offs, then defend your reasoning.

<div class="concept-coach"></div>
