---
title: Classes & Objects
summary: A class is a blueprint that bundles data (attributes) with behaviour (methods), and an instance is one concrete object built from it. The `self` parameter is how a method refers to the particular instance it was called on; everything else in this tutorial follows from those two ideas.
prereqs: []
---

# Classes & Objects — Blueprints and the Things Built From Them

You have used objects since [Tutorial 1](/synapse/programming-languages/python/first-steps/what-is-python) — a `list`, a `dict`, a `str` are all objects, and you have called their methods (`.append`, `.get`, `.upper`). Now you build your own. The thesis: **a class is a blueprint that bundles *data* (attributes) with *behaviour* (methods); an instance is one concrete thing made from that blueprint; and `self` is how a method names the particular instance it was called on.** A `Dog` class describes what every dog has and can do; `Dog("Rex")` makes one specific dog.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **The core idea.**

- A class is a **blueprint** bundling data (attributes) with behaviour (methods).
- An instance is one concrete thing built from it.
- `self` names the **particular instance** a method was called on.

</div>

Classes are not a new kind of value — they sit squarely on top of the [object model](/synapse/programming-languages/python/how-python-works/the-object-model) you already know, and methods are just [functions](/synapse/programming-languages/python/control-flow/functions-the-basics) that live on a class. Every output below was produced by running the code — including the deliberate tracebacks.

<div style="border-left:4px solid #15448e;background:rgba(21,68,142,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

📘 **How to read the Intuition boxes.** Each one is built in three moves:

1. **The mechanism** — what the interpreter is *actually doing*.
2. **A concrete bite** — a specific, runnable way the naive assumption fails.
3. **The earned rule** — the decision heuristic, now justified rather than asserted, plus its cost.

</div>

---

## Table of Contents

1. [Defining a class and creating instances](#1-defining-a-class-and-creating-instances)
2. [`__init__` and instance attributes](#2-__init__-and-instance-attributes)
3. [Methods and `self`](#3-methods-and-self)
4. [Instances carry their own attributes](#4-instances-carry-their-own-attributes)
5. [`__repr__` for a useful display](#5-__repr__-for-a-useful-display)
6. [Mental-model summary](#6-mental-model-summary)
7. [Gotcha checklist](#7-gotcha-checklist)

---

## 1. Defining a class and creating instances

The `class` keyword defines a new type. The simplest possible class has no body of its own — `pass` is a placeholder statement that does nothing. *Calling* the class like a function builds an instance.

```python run
class Dog:
    pass

d = Dog()
print(type(d))
print(isinstance(d, Dog))
```

**Output:**
```
<class '__main__.Dog'>
True
```

**Analysis.** `class Dog: pass` created a brand-new type. `Dog()` — calling the class — produced an *instance*, which we bound to `d`. `type(d)` reports `Dog` (qualified by the module it lives in, `__main__`), and `isinstance(d, Dog)` confirms `d` is a `Dog`. The class is the blueprint; `d` is one thing built from it.

**Intuition.**
*Mechanism.* `class Dog: ...` does not build a dog — it builds the *type object* `Dog` and binds the name `Dog` to it. Each time you call `Dog()`, Python allocates a fresh object, tags it with `Dog` as its class, and hands it back. The blueprint is reusable; every call stamps out a new, independent product.

*Concrete bite.* Because each call makes a *distinct* object, two instances are never the same object — even with identical (here, empty) contents:

```python run
class Dog:
    pass

print(Dog() is Dog())
a = Dog()
b = Dog()
print(a is b)
print(id(a) == id(b))
```

**Output:**
```
False
False
False
```

`Dog() is Dog()` is `False`: two separate calls, two separate objects, two separate identities. `a is b` is `False` for the same reason, and `id(a) == id(b)` confirms they live at different addresses. `is` tests *identity* — "the same object" — not contents (see [the object model](/synapse/programming-languages/python/how-python-works/the-object-model)).

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Use the class name to *make* instances and `isinstance(x, Cls)` to *ask* whether something is one; reach for `is` only when you genuinely mean "the very same object," not "looks equal." The cost of confusing them is real bugs: two freshly built objects compare unequal under `is` even when they should be interchangeable, so identity checks on fresh instances almost always surprise you.

</div>

---

## 2. `__init__` and instance attributes

A blank dog is not useful — a dog has a name. The `__init__` method runs automatically right after an instance is built, and its job is to set up that instance's starting attributes. The first parameter, `self`, is the instance being initialised; `self.name = name` stores data *on that instance*.

```python run
class Dog:
    def __init__(self, name):
        self.name = name

d = Dog("Rex")
print(d.name)
```

**Output:**
```
Rex
```

**Analysis.** When we wrote `Dog("Rex")`, Python built a new instance and immediately called `__init__` with that instance as `self` and `"Rex"` as `name`. The line `self.name = name` attached a `name` attribute to *this* dog. Afterwards, `d.name` reads it back. Note the asymmetry: you pass *one* argument (`"Rex"`) even though `__init__` lists *two* parameters — `self` is supplied for you.

**Intuition.**
*Mechanism.* `Dog("Rex")` is two steps fused: allocate a blank instance, then call `__init__(that_instance, "Rex")`. `__init__` does not *create* the object (that already happened); it *configures* it. Anything you assign to `self.something` becomes an attribute living on that specific instance.

*Concrete bite.* An attribute exists only if something set it. Read one that `__init__` never assigned and Python raises `AttributeError`:

```python run
class Dog:
    def __init__(self, name):
        self.name = name

d = Dog("Rex")
print(d.age)
```

**Output:**
```
Traceback (most recent call last):
  File "/w/main.py", line 6, in <module>
    print(d.age)
          ^^^^^
AttributeError: 'Dog' object has no attribute 'age'
```

`__init__` set `name` but never `age`, so `d.age` has nothing to read and raises `AttributeError`. Attributes are not declared up front the way fields are in some languages — they spring into existence the moment they are assigned, and not a moment sooner.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Set *every* attribute an instance is meant to have inside `__init__`, even ones that start empty or `None`, so the object is fully formed the instant it exists. The cost of skipping one is the error above — an `AttributeError` that fires far from `__init__`, at the unrelated line that happened to read the missing attribute first.

</div>

---

## 3. Methods and `self`

A method is a function defined inside a class. It almost always takes `self` as its first parameter, which lets it reach the instance's own data. Here `bark` reads `self.name`.

```python run
class Dog:
    def __init__(self, name):
        self.name = name

    def bark(self):
        return f"{self.name} says woof"

d = Dog("Rex")
print(d.bark())
```

**Output:**
```
Rex says woof
```

**Analysis.** `d.bark()` called the `bark` method on `d`. Inside it, `self` *is* `d`, so `self.name` reads `"Rex"`. Crucially, you wrote `d.bark()` with no arguments, yet `bark` has a `self` parameter — Python passed `d` as `self` automatically. That automatic pass is the whole trick of methods.

**Intuition.**
*Mechanism.* `d.bark()` is *syntactic sugar* for `Dog.bark(d)`. The instance to the left of the dot becomes the first argument. So `self` is not magic — it is an ordinary parameter that receives "the object this method was called on." The name `self` is convention; the *position* (first parameter) is what matters.

*Concrete bite.* If you forget `self`, the automatic pass has nowhere to land, and the call fails with an argument-count error:

```python run
class Dog:
    def __init__(self, name):
        self.name = name

    def bark():
        return "woof"

d = Dog("Rex")
print(d.bark())
```

**Output:**
```
Traceback (most recent call last):
  File "/w/main.py", line 9, in <module>
    print(d.bark())
          ~~~~~~^^
TypeError: Dog.bark() takes 0 positional arguments but 1 was given
```

`bark()` declares *zero* parameters, but `d.bark()` still desugars to `Dog.bark(d)` — Python tries to pass `d` as the first argument, and there is no slot for it. The error says it plainly: "takes 0 positional arguments but 1 was given." The "1" is the instance you never asked to pass but always do.

To see the sugar directly, both forms are identical:

```python run
class Dog:
    def __init__(self, name):
        self.name = name

    def bark(self):
        return f"{self.name} says woof"

d = Dog("Rex")
print(d.bark())
print(Dog.bark(d))
```

**Output:**
```
Rex says woof
Rex says woof
```

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Give every instance method a first parameter named `self`, and read `instance.method(args)` mentally as `Class.method(instance, args)`. The cost of dropping `self` is the `TypeError` above — and because the count is off by exactly one, the message can look baffling until you remember the instance is an invisible argument.

</div>

---

## 4. Instances carry their own attributes

Each instance keeps its own attributes in a private namespace exposed as `__dict__` — a plain dictionary mapping attribute names to values. Two dogs built from the same class have *separate* `__dict__`s, so they do not share per-instance data.

```python run
class Dog:
    def __init__(self, name):
        self.name = name

a = Dog("Rex")
b = Dog("Fido")
print(a.__dict__)
print(b.__dict__)
a.age = 3
print(a.__dict__)
print(b.__dict__)
```

**Output:**
```
{'name': 'Rex'}
{'name': 'Fido'}
{'name': 'Rex', 'age': 3}
{'name': 'Fido'}
```

**Analysis.** `a.__dict__` and `b.__dict__` are different dictionaries: `a` holds `name='Rex'`, `b` holds `name='Fido'`. Then `a.age = 3` added a new attribute to `a` *after* construction — instances are *open*, you can attach attributes to them any time. The last two lines prove it stayed local: `a` now has `age`, but `b` is untouched. Setting `self.x` in a method is just writing to that instance's `__dict__`.

**Intuition.**
*Mechanism.* An instance attribute is an entry in *that instance's* `__dict__`. `a.age = 3` inserts the key `'age'` into `a.__dict__` only; `b` has its own dictionary and never hears about it. There is no shared per-instance storage — each object is its own bag of attributes.

*Concrete bite.* This openness has a sharp edge: a misspelled attribute name on the *left* of `=` does not raise — it silently creates a brand-new attribute:

```python run
class Dog:
    def __init__(self, name):
        self.name = name

d = Dog("Rex")
d.naem = "Buddy"
print(d.__dict__)
print(d.name)
```

**Output:**
```
{'name': 'Rex', 'naem': 'Buddy'}
Rex
```

You meant `d.name = "Buddy"` but typed `d.naem`. Python obliges — it cannot know `naem` is a typo, because adding attributes freely is a *feature* (it is exactly what `a.age = 3` relied on). So `d.__dict__` now carries a stray `naem`, while `d.name` is still the original `"Rex"`. No error fires; your "rename" simply did not take. (This is the same permissiveness explored in [the object model](/synapse/programming-languages/python/how-python-works/the-object-model).)

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Lean on open instances for legitimate per-object state, but treat attribute *assignment* as the place typos hide — when a value you "set" mysteriously fails to change behaviour, print `obj.__dict__` and look for an extra, misspelled key. The cost of Python's freedom is that no spell-checker guards attribute names; the benefit is that you never have to declare them in advance.

</div>

---

## 5. `__repr__` for a useful display

By default, printing an instance shows something like `<__main__.Dog object at 0x...>` — the class name and a memory address, which tells you almost nothing about the dog. Defining `__repr__` lets you control that string.

```python run
class Dog:
    def __init__(self, name):
        self.name = name

d = Dog("Rex")
print(d)
print(repr(d))
```

**Output (illustrative — addresses vary per run):**
```
<__main__.Dog object at 0x7b7b1bafe900>
<__main__.Dog object at 0x7b7b1bafe900>
```

**Analysis.** With no `__repr__` defined, Python falls back to a generic representation: the type and the object's address in memory. The hex address changes every run (and is different on your machine), so it is useless for telling two dogs apart by *name*. Both `print(d)` and `repr(d)` reach for this default here.

Define `__repr__` and the display becomes informative:

```python run
class Dog:
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"Dog({self.name!r})"

d = Dog("Rex")
print(d)
print(repr(d))
```

**Output:**
```
Dog('Rex')
Dog('Rex')
```

**Analysis.** `__repr__` returns the string Python uses to represent the object. We made it `Dog('Rex')` — the `!r` in the f-string applies `repr` to `self.name`, which is why the name shows with quotes. Now both `print` and `repr` give a self-describing result. A good `__repr__` reads like the call that would recreate the object. Full coverage of `__repr__`, `__str__`, and the other dunder methods is in [Dunder Methods](/synapse/programming-languages/python/object-oriented/dunder-methods).

**Intuition.**
*Mechanism.* When Python needs a string for an object and you have not defined `__repr__`, it uses the inherited default: `<ClassName object at 0xADDR>`. Defining `__repr__` overrides that — `print`, `repr`, and the interactive prompt all route through it. The default is honest (it identifies the object precisely) but unreadable.

*Concrete bite.* The default bites hardest inside a container — a list of objects shows a row of opaque addresses, not data:

```python run
class Dog:
    def __init__(self, name):
        self.name = name

dogs = [Dog("Rex"), Dog("Fido")]
print(dogs)
```

**Output (illustrative — addresses vary per run):**
```
[<__main__.Dog object at 0x7db189856900>, <__main__.Dog object at 0x7db189728a50>]
```

Printing a list calls `repr` on each element. Without `__repr__`, you get two anonymous addresses — you cannot even tell which dog is Rex. Add the `Dog({self.name!r})` repr from above and the same list prints as `[Dog('Rex'), Dog('Fido')]`, which is the difference between a debuggable program and a frustrating one.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Define `__repr__` on every class you expect to inspect, log, or store in a collection, and make it unambiguous (ideally resembling the constructor call). The cost is one short method; the payoff is that error messages, debugger views, and `print` of a list all become legible instead of a wall of hex addresses.

</div>

---

## 6. Mental-model summary

| Principle | Consequence |
|-----------|-------------|
| A class is a blueprint; calling it builds an instance | `Dog()` makes a new object each time — `Dog() is Dog()` is `False` |
| `__init__` configures a freshly built instance via `self` | Pass one fewer argument than parameters listed; `self` is supplied automatically |
| `instance.method()` desugars to `Class.method(instance)` | A method without `self` raises `TypeError` — the instance has no slot |
| Each instance owns its attributes in its own `__dict__` | `a.age = 3` never touches `b`; instances are open, so typos create new attributes |
| `__repr__` controls how an object displays | Without it, `print`/lists show `<Dog object at 0x...>` — addresses, not data |

## 7. Gotcha checklist

<div style="border-left:4px solid #da5233;background:rgba(218,82,51,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

- **Two fresh instances compare unequal under `is` →** `is` tests identity, and each call makes a distinct object; use `==`/`isinstance`, not `is`, unless you mean the *same* object.
- **`AttributeError: 'X' object has no attribute 'y'` →** nothing assigned `y`; set every attribute in `__init__`, even to `None`.
- **`TypeError: ... takes 0 positional arguments but 1 was given` →** the method is missing `self`; the instance is always passed as the first argument.
- **A "rename" silently did nothing →** you assigned a misspelled attribute (`d.naem`), which created a new one; print `obj.__dict__` to spot the stray key.
- **`print(obj)` shows `<... object at 0x...>` →** no `__repr__`; define one (e.g. `return f"Dog({self.name!r})"`) so objects display their data.

</div>

---

<div style="border-left:4px solid #6d28d9;background:rgba(109,40,217,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

🧪 **Predict, then check.** Write a `Cat` class whose `__init__` takes a `name`, with a `meow(self)` method returning `f"{self.name} says meow"` and a `__repr__` returning `f"Cat({self.name!r})"`. Predict the exact output of `print([Cat("Tom"), Cat("Felix")])`. Then predict what `Cat("Tom") is Cat("Tom")` returns, and — without running it — predict the precise error you get if you rewrite `meow` as `def meow():` and call `c.meow()`. Three predictions that capture instances, identity, and the invisible `self`.

</div>

## Your Turn

Before you move on, check your understanding with the coach — explain the idea, apply it, weigh the trade-offs, then defend your reasoning.

<div class="concept-coach"></div>
