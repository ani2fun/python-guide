---
title: Modules, Packages & Imports
summary: A module is a .py file that runs once on first import and is then cached; import binds names from it; a package is a directory of modules. Import forms, the module cache, the __name__ == "__main__" guard, package layout, and the import search path.
prereqs: []
---

# Modules, Packages & Imports — Organizing Code Across Files

Every program past a few hundred lines spans multiple files. The thesis: **a module is just a `.py` file; `import` runs it once, caches it, and binds its names so other files can use them** — and a *package* is a directory of modules. Get the "runs once, then cached" model and imports stop being mysterious.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **The core idea.**

- A module is just a `.py` file.
- `import` **runs it once**, caches it, and binds its names.
- A package is a directory of modules.

</div>

> **A note on this chapter's runner.** The ▶ Run sandbox executes a **single file**, so it can't `import` a *custom* module you'd write in a second file. Examples that import the **standard library** (`math`, `sys`) are fully runnable; genuinely multi-file ideas (a module importing another) are shown as **static** file listings, clearly labeled, with their behavior explained. Everything testable in one file is run and verified.

Every runnable output below was produced by running the code.

<div style="border-left:4px solid #15448e;background:rgba(21,68,142,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

📘 **How to read the Intuition boxes.** Each one is built in three moves:

1. **The mechanism** — what the interpreter is *actually doing*.
2. **A concrete bite** — a specific, runnable way the naive assumption fails.
3. **The earned rule** — the decision heuristic, now justified rather than asserted, plus its cost.

</div>

---

## Table of Contents

1. [Importing modules](#1-importing-modules)
2. [A module is a cached object](#2-a-module-is-a-cached-object)
3. [`__name__` and the main guard](#3-__name__-and-the-main-guard)
4. [Packages and project structure](#4-packages-and-project-structure)
5. [The import search path and errors](#5-the-import-search-path-and-errors)
6. [Mental-model summary](#6-mental-model-summary)
7. [Gotcha checklist](#7-gotcha-checklist)

---

## 1. Importing modules

A **module** is a file of Python you can pull into another with `import`. There are three forms: `import mod` (binds the module), `from mod import name` (binds a name out of it), and `import mod as alias` (binds under a new name).

```python run
import math
from math import sqrt, pi
import math as m
print(math.sqrt(16))
print(sqrt(25))
print(m.pi)
```

**Output:**
```
4.0
5.0
3.141592653589793
```

**Analysis.** `import math` binds the module — you reach in with `math.sqrt`. `from math import sqrt, pi` binds those *names* directly, so you call `sqrt(25)` unqualified. `import math as m` binds the module under `m`. All three pull from the same underlying `math` module.

**Intuition.**
*Mechanism.* `import mod` binds the name `mod` to the module object; access its contents with `mod.thing`. `from mod import thing` instead copies `thing` into your namespace, so you use it bare. The dotted form is namespaced (no clashes); the `from` form is shorter but pollutes your namespace.

*Concrete bite.* `import math` does **not** make `sqrt` available unqualified — you must reach through `math`:

```python run
import math
print(sqrt(16))   # sqrt was not imported into this namespace
```
```
Traceback (most recent call last):
  File "/w/main.py", line 2, in <module>
    print(sqrt(16))   # sqrt was not imported into this namespace
          ^^^^
NameError: name 'sqrt' is not defined
```

`import math` bound only `math`, not `sqrt`. To call `sqrt` bare you need `from math import sqrt`; otherwise it's `math.sqrt`.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Prefer `import mod` and qualified access (`mod.func`) — it keeps origins clear and avoids name clashes; use `from mod import name` for a few frequently-used names. The cost of `from mod import *` (import everything) is namespace pollution and shadowed names — avoid it outside the interactive prompt.

</div>

---

## 2. A module is a cached object

Importing a module **runs its code once**, builds a module *object*, and caches it in `sys.modules`. Every later `import` of the same module reuses the cached object — it does **not** re-run the file.

```python run
import math
print(type(math).__name__)
print(math.__name__)
print(math.pi)
```

**Output:**
```
module
math
3.141592653589793
```

**Analysis.** `math` is an object of type `module`; its attributes (`math.pi`, `math.sqrt`) are the names defined in the module. `math.__name__` is the module's own name. A module is a first-class value — you can pass it around, inspect it with `dir(math)`, and read its `__name__`.

**Intuition.**
*Mechanism.* The first `import X` finds the file, executes it top to bottom (running its top-level code once), wraps the resulting names in a module object, and stores it in the `sys.modules` cache. Subsequent imports find it cached and skip the execution entirely.

*Concrete bite.* You can watch the cache directly — a second import is a no-op that returns the same object:

```python run
import sys
import math
print("math" in sys.modules)   # cached after first import
import math                     # second import reuses the cache
print(sys.modules["math"] is math)
```
```
True
True
```

After the first `import math`, it's in `sys.modules`. The second `import math` doesn't re-run anything — `sys.modules["math"] is math` confirms it's the very same cached object. (This is why editing a module mid-session doesn't take effect until you restart or explicitly `importlib.reload`.)

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Rely on import being cached and cheap — import freely at the top of every file that needs a module; you're not paying to re-run it. The cost/boundary: top-level code in a module runs *once at first import* (good for setup, bad for anything you expected to run each time), and a running program won't see edits to an already-imported module without a reload.

</div>

---

## 3. `__name__` and the main guard

Every module has a `__name__`. When a file is **run directly**, its `__name__` is `"__main__"`. When it's **imported**, its `__name__` is the module's name. The `if __name__ == "__main__":` guard uses this to separate "run as a script" code from "imported as a library" code.

```python run
print(__name__)
if __name__ == "__main__":
    print("running as a script")
```

**Output:**
```
__main__
running as a script
```

**Analysis.** This file was run directly, so `__name__` is `"__main__"` and the guarded block ran. The same file, if `import`ed by another, would have `__name__ == "the_module_name"` instead, and the guarded block would be skipped.

**Intuition.**
*Mechanism.* Python sets `__name__` to `"__main__"` for the file you launch, and to the module's name for any file you import. So `if __name__ == "__main__":` is "only when run as the entry point, not when imported."

*Concrete bite.* Without the guard, **all top-level code runs on import** — including the script's main logic. This needs two files, so it's shown statically (the single-file runner can't import):

```python
# greet.py
print("module-level code runs on import!")   # runs EVERY time greet is imported

def main():
    print("the real work")

main()   # NO guard -> this runs on import too, not just when run directly
```
```python
# other.py
import greet   # prints BOTH lines, because greet's main() runs on import
```

Importing `greet` from `other.py` would print `module-level code runs on import!` *and* `the real work` — the import dragged the script's work along. Wrapping `main()` in `if __name__ == "__main__":` fixes it: importing then prints only the module-level line, and `main()` runs only when `greet.py` is launched directly.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Put a module's "run as a script" code under `if __name__ == "__main__":`, and keep reusable definitions (functions, classes) at the top level. The cost of omitting the guard is import side effects — importing your file to reuse one function accidentally runs its whole main routine.

</div>

---

## 4. Packages and project structure

A **package** is a directory of modules. A real project is a tree of packages and modules; you import across it with dotted paths (`from myapp.models.user import User`). Because this is inherently multi-file, here's the layout statically:

```d2
direction: down
pkg: "myapp/  (a package)" {
  init: "__init__.py"
  main: "__main__.py"
  utils: "utils.py"
  models: "models/  (a subpackage)" {
    si: "__init__.py"
    user: "user.py"
  }
}
```

```python
# Importing across the package tree:
from myapp.utils import helper          # a function from a module
from myapp.models.user import User      # a class from a submodule
import myapp.models.user as user_mod    # the submodule itself, aliased
```

**Analysis.** A directory becomes a package; `__init__.py` (often empty) marks it and runs when the package is first imported. `__main__.py` lets you run the whole package with `python -m myapp`. Dotted paths (`myapp.models.user`) mirror the directory structure — each dot is a directory step.

**Intuition.**
*Mechanism.* A package is a directory whose modules are addressed by dotted paths matching the folder structure. `__init__.py` is the package's "module body" — code there runs once when the package (or anything inside it) is first imported, and it can curate what the package exposes.

*Concrete bite.* The most common package error is a *relative* vs *absolute* import mix-up: inside a package, `import user` (expecting a sibling) fails — the runner searches the top-level path, not the current package, so it raises `ModuleNotFoundError`. The fix is an absolute path (`from myapp.models import user`) or an explicit relative import (`from . import user`). (The mechanics of "where Python looks" are §5.)

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Structure a project as a package tree with `__init__.py` files, and use **absolute imports** (`from myapp.models.user import User`) from the project root — they're unambiguous and survive file moves better than relative ones. The cost is a bit of boilerplate (`__init__.py` files, a consistent root); the payoff is a codebase that scales past one file without import chaos. (Tier 5's [Testing & Packaging](/synapse/programming-languages/python/advanced/testing-and-packaging) covers turning a package into a distributable.)

</div>

---

## 5. The import search path and errors

When you `import X`, Python searches a list of locations — `sys.path` — in order: the script's directory, then installed-package directories, then the standard library. The first `X` found wins; if none is found, you get `ModuleNotFoundError`.

```python run
import nonexistent_module_xyz
```

**Output:**
```
Traceback (most recent call last):
  File "/w/main.py", line 1, in <module>
    import nonexistent_module_xyz
ModuleNotFoundError: No module named 'nonexistent_module_xyz'
```

**Analysis.** Python searched every directory in `sys.path` for `nonexistent_module_xyz`, found nothing, and raised `ModuleNotFoundError`. The same error appears when a third-party package isn't installed in the current environment — the cue to `pip install` it (and a strong argument for the virtual environments in Tier 5).

**Intuition.**
*Mechanism.* `import` walks `sys.path` top to bottom and uses the first match. Because the **script's own directory is first**, a local file can *shadow* a standard-library or installed module of the same name.

*Concrete bite.* Name a file after a stdlib module and you shadow it — `import random` then finds *your* file. This needs two files, so statically: a file named `random.py` in your project makes `import random` elsewhere import your file (likely missing `randint`, etc.), producing a baffling `AttributeError: module 'random' has no attribute 'randint'`. The module you wanted is masked by your same-named file sitting earlier on `sys.path`.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Never name your files after standard-library modules (`random.py`, `string.py`, `email.py`, `queue.py`) — the local file silently wins and breaks the real import. The cost of `ModuleNotFoundError` is usually a missing install (fix with `pip` inside a virtual environment) or a path issue; the cost of *shadowing* is far nastier, since the import "works" but gives the wrong module.

</div>

---

## 6. Mental-model summary

| Principle | Consequence |
|-----------|-------------|
| `import mod` binds the module; `from mod import x` binds `x` | After `import math`, `sqrt` alone is a `NameError`; use `math.sqrt` |
| Import runs a module once, then caches it in `sys.modules` | Re-imports are no-ops; top-level code runs only on first import |
| `__name__` is `"__main__"` when run directly, else the module name | Guard script code with `if __name__ == "__main__":` |
| A package is a directory of modules (`__init__.py`), addressed by dots | `from myapp.models.user import User`; prefer absolute imports |
| `import` searches `sys.path`; the script's dir is first | A local file can shadow a stdlib module — `ModuleNotFoundError` or wrong module |

## 7. Gotcha checklist

<div style="border-left:4px solid #da5233;background:rgba(218,82,51,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

- **`NameError` for an imported function →** `import mod` needs `mod.func`; use `from mod import func` for the bare name.
- **Edits to a module didn't take effect →** it's cached in `sys.modules`; restart, or `importlib.reload`.
- **Importing a file ran its whole script →** put that code under `if __name__ == "__main__":`.
- **`ModuleNotFoundError` →** typo, not installed (`pip install` in a venv), or a path/structure issue.
- **A real module behaves wrong / `AttributeError` on a stdlib import →** you have a local file with the same name shadowing it; rename your file.

</div>

---

<div style="border-left:4px solid #6d28d9;background:rgba(109,40,217,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

🧪 **Predict, then check.** In the runnable block, predict the output of `import math as m` followed by `print(m.__name__)` and `print(m is __import__("math"))`. Then reason through the static `greet.py`/`other.py` example: with `main()` called *unguarded* at module level, exactly what does `import greet` print — and what changes once you wrap it in `if __name__ == "__main__":`? That guard is the single most important convention in this chapter.

</div>

## Your Turn

Before you move on, check your understanding with the coach — explain the idea, apply it, weigh the trade-offs, then defend your reasoning.

<div class="concept-coach"></div>
