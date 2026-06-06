# Idiomatic Patterns and Performance in Python

This guide defines excellence standards for writing robust, efficient, and maintainable Python code, integrated into the high-performance **UV** workflow.

---

## 1. Fundamental Principles (The Zen of Python)

### Readability First
Code should be obvious and easy to understand. If the code is hard to explain, it's a bad idea.

```python
# ✅ GOOD: Clear and readable
def get_active_users(users: list[User]) -> list[User]:
    """Returns only active users from the provided list."""
    return [u for u in users if u.is_active]

# ❌ BAD: "Clever" but confusing
def get_act_u(u):
    return [x for x in u if x.a]
```

### Explicit is better than Implicit
Avoid "magic" and hidden side effects. Be clear about what your code does.

```python
# ✅ GOOD: Explicit configuration
import logging
logging.basicConfig(level=logging.INFO)

# ❌ BAD: Hidden side effects
import magic_module # Configures logging internally without warning
```

---

## 2. EAFP vs LBYL

Python prefers the **EAFP** (*Easier to Ask Forgiveness than Permission*) style over **LBYL** (*Look Before You Leap*).

```python
# ✅ GOOD (EAFP): Try and handle the exception
try:
    value = dictionary["key"]
except KeyError:
    value = default

# ❌ BAD (LBYL): Check before acting
if "key" in dictionary:
    value = dictionary["key"]
else:
    value = default
```

---

## 3. Modern Type Hints (Python 3.9+)

Use static typing to improve maintenance and allow tools like `mypy` (via `uv run mypy`) to detect errors early.

```python
# Python 3.9+ - Use built-in types directly
def process_items(items: list[str]) -> dict[str, int]:
    return {item: len(item) for item in items}

# Generic Types and Union (3.10+)
def first_element[T](items_list: list[T]) -> T | None:
    return items_list[0] if items_list else None
```

### Protocol-Based Duck Typing (Interfaces)
Use `Protocol` to define contracts without rigid inheritance.

```python
from typing import Protocol

class Renderable(Protocol):
    def render(self) -> str: ...

def display_all(items: list[Renderable]) -> None:
    for item in items:
        print(item.render())
```

---

## 4. Advanced Exception Management

### Exception Chaining
Always use `from e` when re-raising exceptions to preserve the original traceback.

```python
def process_data(data: str):
    try:
        result = json.loads(data)
    except json.JSONDecodeError as e:
        raise ValueError("Invalid JSON data") from e
```

### Customized Exception Hierarchy
Create a base for your application to facilitate global handling.

```python
class AppError(Exception): """Base for all app errors"""
class ValidationError(AppError): """Input validation error"""
```

---

## 5. Performance and Memory Efficiency

### Optimization with `__slots__`
For classes with millions of instances, use `__slots__` to drastically reduce memory usage (avoids `__dict__` creation).

```python
class Point:
    __slots__ = ['x', 'y']
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
```

### Generators for Large Data Volumes
Never return giant lists if you can use generators (Lazy Evaluation).

```python
# ✅ GOOD: Processes line by line
def read_giant_file(path: str):
    with open(path) as f:
        for line in f:
            yield line.strip()

# ❌ BAD: Loads everything into RAM
def read_everything(path: str):
    with open(path) as f:
        return f.readlines()
```

### String Manipulation
Avoid concatenation with `+` in loops (O(n²)). Use `.join()` or `io.StringIO` (O(n)).

```python
# ✅ GOOD
result = "".join(string_list)
```

---

## 6. Data Classes with Validation

Use `dataclasses` for data containers, and `__post_init__` for simple validations. For complex validations, consider `Pydantic` (integrated via `uv add pydantic`).

```python
from dataclasses import dataclass

@dataclass
class User:
    email: str
    age: int

    def __post_init__(self):
        if "@" not in self.email:
            raise ValueError("Invalid email")
        if self.age < 0:
            raise ValueError("Age cannot be negative")
```

---

## 7. Anti-Patterns to Avoid

1. **Mutable Default Arguments**: Never use `list` or `dict` as a default. Use `None`.
   ```python
   # ❌ BAD
   def add_item(item, items_list=[]): ...
   # ✅ GOOD
   def add_item(item, items_list=None):
       if items_list is None: items_list = []
   ```
2. **Bare Except**: Never use `except:`. Catch specific exceptions or `Exception`.
3. **Type Checking with `type()`**: Use `isinstance(obj, class)`.
4. **Comparison with `None`**: Use `is None` instead of `== None`.
---

<!-- @sdd-state -->
```yaml
version: "2.3.0"
feature_id: "python-uv-alignment"
phase: "VERIFY"
status: "COMPLETED"
last_update: "2026-05-06T13:12:14.665217Z"
evidence_checksum: "8e52f6a"
```
