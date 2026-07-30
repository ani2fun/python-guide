---
title: Inheritance & super
summary: A subclass IS-A superclass — it inherits the parent's attributes and methods, may override them, and uses `super()` to extend rather than replace the parent's behaviour. This tutorial covers subclassing, overriding, `super().__init__`, the `isinstance`-vs-`type() is` distinction, and when to prefer composition over inheritance.
prereqs: []
---

# Inheritance & super — Reusing and Extending Behaviour

You can build a new class on top of an existing one. A `Cat` is an `Animal`, so it should get everything an animal has — for free — plus whatever is cat-specific. The thesis: **a subclass IS-A superclass: it *inherits* the parent's attributes and methods, can *override* them to specialise behaviour, and uses `super()` to *extend* the parent rather than replace it.** Inheritance is reuse plus the freedom to differ where it matters.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **The core idea.**

- A subclass **IS-A** superclass.
- It **inherits** the parent's attributes and methods.
- It can **override** them to specialise.
- `super()` **extends** the parent rather than replacing it.

</div>

This builds on [Classes & Objects](/synapse/programming-languages/python/object-oriented/classes-and-objects) and the [class-vs-instance](/synapse/programming-languages/python/object-oriented/class-vs-instance) lookup rule — inheritance simply extends that lookup up a chain of classes. Every output below was produced by running the code — including the deliberate traceback.

<div style="border-left:4px solid #15448e;background:rgba(21,68,142,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

📘 **How to read the Intuition boxes.** Each one is built in three moves:

1. **The mechanism** — what the interpreter is *actually doing*.
2. **A concrete bite** — a specific, runnable way the naive assumption fails.
3. **The earned rule** — the decision heuristic, now justified rather than asserted, plus its cost.

</div>

---

## Table of Contents

1. [Subclassing](#1-subclassing)
2. [Overriding methods](#2-overriding-methods)
3. [`super()` to extend](#3-super-to-extend)
4. [`isinstance` and the is-a test](#4-isinstance-and-the-is-a-test)
5. [Composition vs inheritance](#5-composition-vs-inheritance)
6. [Mental-model summary](#6-mental-model-summary)
7. [Gotcha checklist](#7-gotcha-checklist)

---

## 1. Subclassing

You declare a subclass by naming its parent in parentheses: `class Cat(Animal):`. The subclass automatically gains every attribute and method of the parent, even with an empty body.

```python run
class Animal:
    def __init__(self, name):
        self.name = name

    def describe(self):
        return f"{self.name} is an animal"

class Cat(Animal):
    pass

c = Cat("Whiskers")
print(c.name)
print(c.describe())
print(isinstance(c, Animal))
print(issubclass(Cat, Animal))
```

**Output:**
```
Whiskers
Whiskers is an animal
True
True
```

**Analysis.** `Cat` has an empty body (`pass`), yet `Cat("Whiskers")` ran `Animal.__init__` (setting `name`) and `c.describe()` ran `Animal.describe` — both inherited. `isinstance(c, Animal)` is `True`: a cat *is* an animal. `issubclass(Cat, Animal)` is `True`: the *class* `Cat` is a kind of `Animal`. With zero cat-specific code, `Cat` already behaves like a fully functional animal.

**Intuition.**
*Mechanism.* `class Cat(Animal)` records `Animal` as `Cat`'s *base class*. When you look up `c.describe`, Python checks `c`'s instance dict, then `Cat`, then `Animal` — walking *up* the chain of classes (the MRO, "method resolution order") until it finds the name. Inheritance is that fallback chain extended one level higher.

*Concrete bite.* Inheritance is not copying — the subclass *defers* to the parent at lookup time. `isinstance` and `issubclass` ask the relationship directly: `isinstance(c, Animal)` is `True` because `Cat`'s chain includes `Animal`, and `issubclass(Cat, Animal)` is `True` for the same structural reason. A `Cat` satisfies "is an `Animal`" everywhere that test is made, with no duplicated code to keep in sync.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Subclass when the new type genuinely *is a kind of* the base — the "is-a" test — so it can stand in wherever the base is expected. The cost of inheriting without a true is-a relationship is a subclass that drags along methods that make no sense for it; the benefit, when the relationship holds, is reuse the language keeps consistent automatically.

</div>

---

## 2. Overriding methods

A subclass can *override* an inherited method by defining one with the same name. Lookup finds the subclass's version first, so the specialised behaviour wins.

```python run
class Animal:
    def speak(self):
        return "some sound"

class Cat(Animal):
    def speak(self):
        return "meow"

class Dog(Animal):
    def speak(self):
        return "woof"

print(Cat().speak())
print(Dog().speak())
print(Animal().speak())
```

**Output:**
```
meow
woof
some sound
```

**Analysis.** `Animal.speak` returns a generic `"some sound"`. `Cat` and `Dog` each define their own `speak`, so `Cat().speak()` finds `Cat.speak` *before* reaching `Animal` and returns `"meow"`; `Dog().speak()` returns `"woof"`. A bare `Animal()` has no override, so it falls through to the generic version. Same method name, three behaviours — selected by the object's actual class.

**Intuition.**
*Mechanism.* Overriding is just the lookup rule resolving in the subclass's favour: `Cat.speak` sits *earlier* in the chain than `Animal.speak`, so it shadows it for cats. Nothing is deleted — `Animal.speak` still exists and still serves any `Animal` (or subclass that did not override it).

*Concrete bite.* Because the *object's class* drives the choice, the same call site produces different results depending on what it is given — this is polymorphism. A loop calling `.speak()` over `[Cat(), Dog(), Animal()]` would print `meow`, `woof`, `some sound` in turn, with no `if`/`else` on the type; each object brings its own version of the method. The caller writes one line; the objects supply the behaviour.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Override a method when the subclass needs different behaviour for the *same operation*, and keep the signature compatible so callers cannot tell which subclass they hold. The cost of an incompatible override (different parameters, different return shape) is that polymorphism breaks — a caller that works for the base will fail for the subclass; the benefit of a compatible one is branch-free code that handles every subtype uniformly.

</div>

---

## 3. `super()` to extend

Often a subclass wants to *add* to the parent's behaviour, not discard it. `super()` gives you the parent's version of a method, so you can call it and then do more. The most common case is `__init__`: run the parent's setup, then add subclass-specific attributes.

```python run
class Animal:
    def __init__(self, name):
        self.name = name

class Dog(Animal):
    def __init__(self, name, breed):
        super().__init__(name)     # run Animal's setup first
        self.breed = breed         # then add Dog-specific state

d = Dog("Rex", "Labrador")
print(d.name)
print(d.breed)
print(d.__dict__)
```

**Output:**
```
Rex
Labrador
{'name': 'Rex', 'breed': 'Labrador'}
```

**Analysis.** `Dog.__init__` overrides `Animal.__init__`, so without help it would *replace* it and `name` would never get set. Instead, `super().__init__(name)` calls `Animal.__init__` with this same instance, which sets `self.name`. Then `self.breed = breed` adds the dog-specific attribute. The final `__dict__` proves both ran: `name` from the parent, `breed` from the child. `super()` is "extend, don't replace."

**Intuition.**
*Mechanism.* `super()` returns a proxy that dispatches to the *next class up* the chain — here, `Animal`. So `super().__init__(name)` is `Animal.__init__(self, name)`, with `self` threaded through automatically. Your override runs, *and* the parent's setup runs, because you explicitly invited it.

*Concrete bite.* Forget the `super().__init__()` call and the parent's setup simply never happens — the attributes it would have set are missing, and the failure surfaces later, wherever you first read one:

```python run
class Animal:
    def __init__(self, name):
        self.name = name

class Dog(Animal):
    def __init__(self, breed):
        self.breed = breed         # forgot super().__init__(name)

d = Dog("Labrador")
print(d.breed)
print(d.name)
```

**Output:**
```
Labrador
Traceback (most recent call last):
  File "/w/main.py", line 11, in <module>
    print(d.name)
          ^^^^^^
AttributeError: 'Dog' object has no attribute 'name'
```

`Dog.__init__` sets `breed` but never calls `super().__init__`, so `Animal.__init__` *never runs* and `name` is never set. `d.breed` works (`Labrador`), masking the problem — then `d.name` raises `AttributeError`. The error fires far from the real cause: the bug is the missing `super()` call in `__init__`, not the line that reads `name`.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** When a subclass overrides `__init__` (or any method) but still wants the parent's work done, call `super().__init__(...)` — almost always *first*, before adding subclass state. The cost of omitting it is the trap above: a half-initialised object whose `AttributeError` points at the innocent reader, not the guilty constructor — so when an inherited attribute goes missing, suspect a forgotten `super()`.

</div>

---

## 4. `isinstance` and the is-a test

Two ways to ask "what is this object?" behave differently under inheritance. `isinstance(x, Cls)` is `True` if `x` is a `Cls` *or any subclass*. `type(x) is Cls` is `True` only if `x`'s class is *exactly* `Cls`. The difference is the whole point of inheritance.

```python run
class Animal:
    pass

class Cat(Animal):
    pass

c = Cat()
print(isinstance(c, Animal))
print(isinstance(c, Cat))
print(type(c) is Cat)
print(type(c) is Animal)
```

**Output:**
```
True
True
True
False
```

**Analysis.** `isinstance(c, Animal)` is `True` — a `Cat` is an `Animal`, so it passes the is-a test against the parent. `isinstance(c, Cat)` is `True` too. But `type(c) is Cat` is `True` while `type(c) is Animal` is `False`: `type(c)` is *exactly* `Cat`, and `Cat is Animal` is false because they are different class objects. `isinstance` respects the inheritance chain; `type() is` checks for an exact class match and ignores it.

**Intuition.**
*Mechanism.* `isinstance(x, Cls)` walks `x`'s class chain and returns `True` if `Cls` appears anywhere in it. `type(x)` returns the single, *most-derived* class of `x` and nothing else; `is` then tests that one class for object identity. So `type(c) is Animal` asks "is `c`'s exact class the *same object* as `Animal`?" — and `Cat` is not `Animal`.

*Concrete bite.* This is exactly why `type() is` is the wrong tool for "is this usable as an `Animal`?":

```python run
class Animal:
    pass

class Cat(Animal):
    pass

c = Cat()
print(type(c) is Animal)        # exact-class check: ignores inheritance
print(isinstance(c, Animal))    # is-a check: respects inheritance
```

**Output:**
```
False
True
```

A `Cat` *is* an `Animal` in every behavioural sense, yet `type(c) is Animal` reports `False` because it demands an exact class match. Code that gates on `type(x) is Animal` silently rejects every subclass — so a perfectly valid `Cat` is turned away. `isinstance` gets it right.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Use `isinstance(x, Cls)` for "can I treat this as a `Cls`?" — the question you almost always mean — and reserve `type(x) is Cls` for the rare case where subclasses must be *excluded* deliberately. The cost of reaching for `type() is` by habit is code that breaks the moment someone subclasses your type; `isinstance` is the inheritance-aware default for a reason.

</div>

---

## 5. Composition vs inheritance

Inheritance models "is-a." But many relationships are "has-a": a car *has* an engine; it is not a *kind of* engine. For those, *composition* — holding another object as an attribute — is the right tool, and usually the better default.

```python run
class Engine:
    def __init__(self, horsepower):
        self.horsepower = horsepower

    def start(self):
        return f"engine ({self.horsepower}hp) starting"

class Car:
    def __init__(self, model, horsepower):
        self.model = model
        self.engine = Engine(horsepower)   # Car HAS-A Engine

    def start(self):
        return f"{self.model}: {self.engine.start()}"

c = Car("Sedan", 180)
print(c.start())
print(isinstance(c, Engine))
```

**Output:**
```
Sedan: engine (180hp) starting
False
```

**Analysis.** `Car` does *not* inherit from `Engine`. Instead it *holds* one as `self.engine` and delegates to it inside `start()`. The output shows the car starting its engine, and `isinstance(c, Engine)` is `False` — correctly, because a car is not a kind of engine. The car uses the engine's behaviour without claiming to *be* an engine. That is composition: assemble behaviour from parts rather than inherit it.

We can picture the small inheritance hierarchy this tutorial built — a true "is-a" tree — alongside the "has-a" relationship above:

```d2
direction: down
Animal: "Animal\nspeak()  __init__(name)" {
  shape: rectangle
}
Dog: "Dog\nspeak()  (overrides)" {
  shape: rectangle
}
Cat: "Cat\nspeak()  (overrides)" {
  shape: rectangle
}
Dog -> Animal: "is-a"
Cat -> Animal: "is-a"
```

**Intuition.**
*Mechanism.* Inheritance fuses two classes into one identity chain — a `Dog` literally *is* an `Animal`, sharing its methods through lookup. Composition keeps them separate: `Car` and `Engine` are unrelated types; the car merely *references* an engine and forwards calls to it. The coupling is a single attribute, not a shared class hierarchy.

*Concrete bite.* Inheritance leaks: a subclass is exposed to *all* of the parent's methods and internals, so a change to the parent can silently alter — or break — the child. Composition limits the surface to the methods you *choose* to call: `Car.start` uses only `engine.start()`, so the rest of `Engine` can change freely without touching `Car`. Swapping in an `ElectricEngine` with the same `start()` needs no change to `Car` at all — whereas re-parenting in an inheritance tree ripples through every subclass.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Prefer composition (has-a) unless there is a genuine is-a relationship that you want to expose through the type system; reach for inheritance when subtypes must be *substitutable* for the base (§4's `isinstance`). The cost of deep inheritance is fragility — long chains where a parent change breaks distant descendants and behaviour is scattered across levels; composition trades a little forwarding boilerplate for parts you can reason about, test, and replace in isolation.

</div>

---

## 6. Mental-model summary

| Principle | Consequence |
|-----------|-------------|
| `class Sub(Base)` inherits Base's methods via the lookup chain | An empty subclass already works; `issubclass(Sub, Base)` is `True` |
| A same-named method in the subclass overrides the parent's | The object's actual class picks the version — one call, many behaviours |
| `super().method(...)` runs the parent's version | Extend with `super().__init__(...)`; forgetting it leaves attributes unset |
| `isinstance` respects subclasses; `type(x) is C` demands exact match | `isinstance(cat, Animal)` is `True`; `type(cat) is Animal` is `False` |
| Inheritance is is-a; composition is has-a | Prefer composition unless subtypes must substitute for the base |

## 7. Gotcha checklist

<div style="border-left:4px solid #da5233;background:rgba(218,82,51,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

- **An inherited attribute is missing (`AttributeError`) →** the override of `__init__` forgot `super().__init__(...)`; call it (usually first).
- **A subclass instance fails a `type(x) is Base` check →** that demands an *exact* class; use `isinstance(x, Base)` to accept subclasses.
- **A `type()`-based gate rejects valid subclasses →** swap `type(x) is C` for `isinstance(x, C)` — the inheritance-aware test.
- **An override "doesn't take effect" →** the method name or signature differs from the parent's; match the name exactly (and keep the signature compatible).
- **A subclass breaks when the parent changes →** the inheritance coupling is too deep; model the relationship as has-a (composition) unless it is truly is-a.

</div>

---

<div style="border-left:4px solid #6d28d9;background:rgba(109,40,217,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

🧪 **Predict, then check.** Define `class Vehicle:` with `__init__(self, wheels)` setting `self.wheels`, then `class Motorcycle(Vehicle):` whose `__init__(self)` sets `self.wheels = 2` *without* calling `super().__init__`. Predict whether `Motorcycle()` works and what `m.wheels` prints (does skipping `super()` matter when the child sets the attribute itself?). Then predict `isinstance(Motorcycle(), Vehicle)` versus `type(Motorcycle()) is Vehicle`. Two predictions that capture when `super()` is optional and the isinstance-vs-`type() is` split.

</div>

## Your Turn

Before you move on, check your understanding with the coach — explain the idea, apply it, weigh the trade-offs, then defend your reasoning.

<div class="concept-coach"></div>
