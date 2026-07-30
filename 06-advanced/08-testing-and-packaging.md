---
title: Testing, Debugging & Packaging
summary: Tests pin behaviour so you can change code without fear, pytest makes them ergonomic, logging beats print for debugging, and virtual environments plus a pyproject.toml let you ship. assert and test functions, the assert-tuple trap, logging levels, venvs, and packaging.
prereqs: []
---

# Testing, Debugging & Packaging — Shipping Code You Trust

The last step of real Python is making code you (and others) can rely on and run. The thesis: **tests pin behaviour so you can change code without fear, and packaging plus virtual environments make that code reproducible on someone else's machine** — the two disciplines that turn a script into software. Along the way, `logging` replaces `print` for debugging you can leave in.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **The core idea.**

- Tests **pin behaviour** so you can change code without fear.
- Packaging plus virtual environments make code **reproducible** on another machine.
- `logging` replaces `print` for debugging you can leave in.

</div>

This is the capstone; it builds on [errors](/synapse/programming-languages/python/how-python-works/errors-and-exceptions) and [modules](/synapse/programming-languages/python/how-python-works/modules-and-packages). Every runnable output below was produced by running the code; the `pytest`, virtual-environment, and packaging examples are shown statically (they're external tools / shell commands the sandbox doesn't run), clearly marked.

<div style="border-left:4px solid #15448e;background:rgba(21,68,142,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

📘 **How to read the Intuition boxes.** Each one is built in three moves:

1. **The mechanism** — what the interpreter is *actually doing*.
2. **A concrete bite** — a specific, runnable way the naive assumption fails.
3. **The earned rule** — the decision heuristic, now justified rather than asserted, plus its cost.

</div>

---

## Table of Contents

1. [`assert`: the simplest test](#1-assert-the-simplest-test)
2. [Tests as functions](#2-tests-as-functions)
3. [`pytest`](#3-pytest)
4. [Debugging: logging over print](#4-debugging-logging-over-print)
5. [Virtual environments and packaging](#5-virtual-environments-and-packaging)
6. [Mental-model summary](#6-mental-model-summary)
7. [Gotcha checklist](#7-gotcha-checklist)

---

## 1. `assert`: the simplest test

A test checks that code does what you claim. The most basic tool is `assert`: it does nothing if the condition is true and raises `AssertionError` if it's false.

```python run
def add(a, b):
    return a + b

assert add(2, 3) == 5
print("test passed")
assert add(2, 3) == 6, "add is broken"
```

**Output:**
```
test passed
```
```
Traceback (most recent call last):
  File "/w/main.py", line 6, in <module>
    assert add(2, 3) == 6, "add is broken"
           ^^^^^^^^^^^^^^
AssertionError: add is broken
```

The first `assert` passed silently (so `test passed` printed), and the second failed, raising `AssertionError: add is broken` — the message after the comma.

**Analysis.** `assert condition, message` is "fail loudly if this isn't true." The passing assert produced no output (silence = success); the failing one raised `AssertionError` with our message and halted. That's the essence of a test: state an expected result, and let a mismatch stop the program.

**Intuition.**
*Mechanism.* `assert expr, msg` is equivalent to `if not expr: raise AssertionError(msg)`. A true (truthy) `expr` is a no-op; a false one raises. The optional message after the comma is the error text.

*Concrete bite.* Wrapping the whole thing in parentheses is a notorious trap — it becomes a **tuple**, which is always truthy, so the assert never fails:

```python run
assert (1 == 2, "this should fail")   # parentheses make it a TUPLE
print("the assertion did NOT fail - bug!")
```
```
the assertion did NOT fail - bug!
```

`assert (1 == 2, "msg")` asserts a two-element *tuple*, and a non-empty tuple is always truthy ([Tutorial 6](/synapse/programming-languages/python/control-flow/booleans-and-logic)) — so the check is silently disabled and the next line runs. (Python prints a `SyntaxWarning: assertion is always true, perhaps remove parentheses?` to stderr — heed it.) Write `assert cond, "msg"` with **no** parentheses around the pair.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Use `assert` for tests and internal sanity checks, with the `cond, "message"` form (never parenthesised). The cost/boundary: `assert` statements are **stripped** when Python runs with `-O` (optimised) mode, so never use `assert` for runtime validation that must always happen (input checks, security) — raise a real exception there; reserve `assert` for tests and "this can't happen" invariants.

</div>

---

## 2. Tests as functions

Real test suites group assertions into functions named `test_*`, each checking one behaviour. Plain functions with `assert` already work; a runner (next section) just automates finding and running them.

```python run
def add(a, b):
    return a + b

def test_add():
    assert add(2, 3) == 5
    assert add(-1, 1) == 0
    assert add(0, 0) == 0

test_add()
print("all assertions passed")
```

**Output:**
```
all assertions passed
```

**Analysis.** `test_add` bundles several assertions about `add` — typical, edge (negatives), and boundary (zero) cases. Calling it runs them all; reaching the end means every assertion held. Grouping by behaviour makes failures easy to locate: a failing `test_add` points straight at addition.

**Intuition.**
*Mechanism.* A test function is just a function full of `assert`s. It "passes" by returning normally and "fails" by raising `AssertionError` at the first bad assertion. Independent test functions isolate concerns, so one failure doesn't mask others.

*Concrete bite.* A test that doesn't actually `assert` anything passes vacuously — giving false confidence while testing nothing:

```python run
def add(a, b):
    return a - b          # BUG: subtracts instead of adds

def test_add():
    add(2, 3)             # calls it but never asserts - checks nothing

test_add()
print("test 'passed' - but it never verified the result")
```
```
test 'passed' - but it never verified the result
```

`add` is clearly broken (it subtracts), yet `test_add` "passes" — because it only *calls* `add` without checking the result. A test without an assertion is theatre: it runs, it's green, and it catches nothing.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Every test must assert an expected *result*, and should cover typical, edge, and error cases (use `pytest.raises` for the error ones). The cost of a test is writing and maintaining it; the cost of a *fake* test (no assertion, or asserting something trivially true) is worse than none — it's false confidence that hides real bugs.

</div>

---

## 3. `pytest`

Writing your own runner gets old. `pytest` is the standard tool: it auto-discovers `test_*` functions in `test_*.py` files, runs them, and gives rich failure output — showing the actual values in a failed `assert`. (It's a third-party tool, not on this runner, so this section is illustrative.)

```python
# test_math.py  — pytest discovers files named test_*.py and functions named test_*
def add(a, b):
    return a + b

def test_add():
    assert add(2, 3) == 5

def test_add_negatives():
    assert add(-1, -1) == -2

import pytest
def test_divide_by_zero_raises():
    with pytest.raises(ZeroDivisionError):
        1 / 0
```

Running `pytest` on a passing suite prints something like (illustrative):

```
$ pytest
========================= test session starts =========================
collected 3 items

test_math.py ...                                                [100%]

========================== 3 passed in 0.01s ==========================
```

And on a *failing* assert, pytest's introspection shows the values:

```
    def test_add():
>       assert add(2, 3) == 6
E       assert 5 == 6
E        +  where 5 = add(2, 3)

test_math.py:5: AssertionError
```

**Analysis.** Two things make `pytest` worth adopting: **discovery** (it finds `test_*` functions automatically — no manual runner) and **assert introspection** (a plain `assert add(2,3)==6` failure shows `assert 5 == 6` and `5 = add(2, 3)`, so you see the actual values without writing messages). `pytest.raises` asserts that a block *does* raise — the way to test error paths.

**Intuition.**
*Mechanism.* `pytest` rewrites the bytecode of your `assert` statements at import so it can report the operands on failure (plain `assert` would only say "AssertionError"). It collects every `test_*` function across `test_*.py` files and runs them in isolation, reporting pass/fail per test.

*Concrete bite.* The discovery rules are strict, and silently skip what doesn't match: a test function not named `test_*` (e.g. `check_add`), or in a file not named `test_*.py`, is **never collected** — it doesn't run, and pytest reports success as if all is well. People add a test, see "passed," and don't notice their misnamed test never executed. Follow the `test_` naming convention exactly.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Use `pytest` for any real project — install it (`pip install pytest`), name files `test_*.py` and functions `test_*`, write plain `assert`s, and use `pytest.raises` for errors. The cost is a dependency and the naming discipline; the payoff is automatic discovery, readable failures, fixtures, and parametrisation — the difference between tests you write once and tests you actually maintain.

</div>

---

## 4. Debugging: logging over print

When something misbehaves, the instinct is `print`. For anything beyond a quick check, `logging` is better: it has severity **levels** you can filter, timestamps, and it writes to stderr — and you can leave it in the code.

```python run
import logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logging.info("starting up")
logging.warning("low disk space")
print("normal stdout still works")
```

**Output:**
```
normal stdout still works
```
```
INFO: starting up
WARNING: low disk space
```

**Analysis.** `print` went to stdout; the log messages went to **stderr** (shown here as a separate stream). `logging` tags each message with its level (`INFO`, `WARNING`) and is configured once with `basicConfig`. Unlike scattered `print`s you must delete, logging stays in the code — you control how much shows by setting the level.

**Intuition.**
*Mechanism.* Each log call has a severity (`DEBUG < INFO < WARNING < ERROR < CRITICAL`). `basicConfig(level=...)` sets a threshold; only messages *at or above* it are emitted. So you can leave detailed `logging.debug(...)` calls in place and they stay silent in production (level `INFO`+), then turn them on by lowering the level — no code edits.

*Concrete bite.* That filtering surprises people: a `debug` message below the configured level simply doesn't appear:

```python run
import logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logging.debug("detailed trace")   # below INFO - filtered out
logging.info("running")
logging.error("something failed")
```
```
INFO: running
ERROR: something failed
```

The `debug` line produced **nothing** — it's below the `INFO` threshold, so it was filtered. That's the feature (verbose logs off by default), but it confuses anyone who expects every log call to print. Lower the level to `logging.DEBUG` to see it.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Use `logging` (not `print`) for diagnostics you want to keep — pick a level per message and configure the threshold per environment (DEBUG in dev, INFO/WARNING in prod). For *interactive* stepping through a live bug, reach for the debugger: `breakpoint()` drops into `pdb` (`n` next, `s` step, `p var` print, `c` continue). The cost of `print`-debugging is the cleanup (and the noise you forget to remove); logging and `breakpoint()` are the tools that scale past a one-off.

</div>

---

## 5. Virtual environments and packaging

To ship code, it must run on machines other than yours — which means isolating dependencies and declaring them. A **virtual environment** isolates a project's packages; a **`pyproject.toml`** declares the project so it can be built and installed. (These are shell/tooling steps, shown statically.)

A virtual environment, per project:

```bash
python -m venv .venv            # create an isolated environment
source .venv/bin/activate       # activate it (Windows: .venv\Scripts\activate)
pip install requests pytest     # installs INTO .venv, not system Python
pip freeze > requirements.txt   # record exact versions for reproducibility
```

A minimal `pyproject.toml` to make your code an installable package:

```toml
[project]
name = "mytool"
version = "0.1.0"
dependencies = ["requests>=2.31"]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

With that, `pip install .` installs your project, and `python -m build` produces distributable artifacts you can publish to PyPI.

**Analysis.** A venv gives each project its *own* `site-packages`, so Project A's `requests==2.31` can't collide with Project B's `requests==2.20`. `pyproject.toml` is the modern, standard project descriptor (replacing the old `setup.py`): it names the project, pins dependencies, and tells build tools how to package it. Together they make "works on my machine" become "works on any machine."

**Intuition.**
*Mechanism.* A venv is a directory with its own Python and `site-packages`; activating it puts that Python first on your `PATH`, so `pip install` and `import` use the project's isolated packages, not the system's. `pyproject.toml` is read by `pip`/`build` to resolve dependencies and assemble a wheel.

*Concrete bite.* Skipping the venv and `pip install`-ing globally is the classic mess: two projects needing different versions of the same library **can't coexist** — installing one breaks the other (and on system Python you can break OS tools). It surfaces as `ImportError`/version-mismatch bugs that depend on *which project you installed last* — irreproducible and maddening, and exactly what a per-project venv prevents.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** One virtual environment per project, always; declare dependencies in `pyproject.toml` (and/or pin a `requirements.txt`) so anyone can recreate the environment. The cost is a little ceremony per project (create, activate, install); the payoff is reproducibility — the difference between code that runs only on your laptop and code you can actually ship. (Tools like `uv`, `poetry`, and `pipenv` automate this further.)

</div>

---

## 6. Mental-model summary

| Principle | Consequence |
|-----------|-------------|
| `assert cond, "msg"` raises `AssertionError` when false | Pins behaviour; `assert (cond, "msg")` is an always-true tuple — never parenthesise |
| Tests are `test_*` functions full of assertions | A test with no assertion passes vacuously and catches nothing |
| `pytest` auto-discovers `test_*` in `test_*.py` and shows values | Misnamed tests are silently skipped; follow the convention |
| `logging` has filterable levels and goes to stderr | `debug` below the threshold is hidden; leave logs in, tune the level |
| A venv isolates deps; `pyproject.toml` declares them | One env per project, or versions collide irreproducibly |

## 7. Gotcha checklist

<div style="border-left:4px solid #da5233;background:rgba(218,82,51,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

- **An `assert` never fails →** you parenthesised it into a tuple; write `assert cond, "msg"` (heed the `SyntaxWarning`).
- **Validation vanished in production →** `assert` is stripped under `-O`; use real exceptions for runtime checks.
- **A test is green but the code is broken →** the test doesn't assert a result; add a real assertion.
- **A new test never runs →** it's misnamed; pytest only collects `test_*` functions in `test_*.py`.
- **A `logging.debug` didn't print →** it's below the configured level; set `level=logging.DEBUG`.
- **"Works on my machine" / version conflicts →** you installed globally; use a per-project virtual environment and declare deps in `pyproject.toml`.

</div>

---

<div style="border-left:4px solid #6d28d9;background:rgba(109,40,217,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

🧪 **Predict, then check.** Write `def test_clamp():` with three assertions for a `clamp(x, lo, hi)` function (one in-range, one below, one above), then run it. Predict what happens if you accidentally write `assert (clamp(5, 0, 10) == 5,)` with a trailing comma. Then predict which of `logging.debug`/`info`/`warning` appear at the default `INFO` level. The assert-tuple and the logging-level filters are the two traps that quietly disable your safety nets.

</div>

## Your Turn

Before you move on, check your understanding with the coach — explain the idea, apply it, weigh the trade-offs, then defend your reasoning.

<div class="concept-coach"></div>
