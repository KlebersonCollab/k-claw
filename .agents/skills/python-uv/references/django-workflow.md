# Django Professional Workflow with UV — Complete Reference

Guide for patterns, security, performance, and advanced architecture for high-performance Django applications using the `uv` ecosystem.

---

## 1. Optimized Setup and Management

`uv` eliminates historical slowness in Django dependency management and facilitates the execution of administrative commands.

### Professional Initialization
```bash
uv init my-django-project
cd my-django-project
uv add django djangorestframework django-environ django-filter
uv add --dev pytest-django ruff bandit django-debug-toolbar django-extensions

# Start Django project
uv run django-admin startproject config .
```

### Productivity Commands (without activating venv)
| Action | UV Command |
|------|------------|
| Dev Server | `uv run python manage.py runserver` |
| ASGI Server (Async) | `uv run uvicorn config.asgi:application --reload` |
| Shell Plus (IPython) | `uv run python manage.py shell_plus` |
| List URLs | `uv run python manage.py show_urls` |
| Tests with Coverage | `uv run pytest --cov` |

---

## 2. ORM Performance and Optimization

Avoid common bottlenecks like the N+1 queries problem and memory exhaustion.

### Strategies against N+1
Always use Eager Loading in views and serializers.

- **`select_related(*fields)`**: For Foreign Keys and 1-to-1 relationships (SQL JOIN).
- **`prefetch_related(*fields)`**: For Many-to-Many relationships or reverse relationships (Separate queries with IN).

```python
# ✅ Performance Pattern in ViewSets
class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Order.objects.select_related('user', 'shipping_address') \
                            .prefetch_related('items__product')
```

### Bulk Operations
Avoid saving objects one by one inside loops.

```python
# ❌ Slow
for item in items:
    Product.objects.create(**item)

# ✅ Fast (Bulk Create)
Product.objects.bulk_create([Product(**item) for item in items])

# ✅ Bulk Update
Product.objects.filter(category='old').update(status='retired')
```

### Large Volume Processing
Use `.iterator()` to avoid loading thousands of objects into RAM.

```python
# ✅ Memory safe (processes in chunks)
for user in User.objects.all().iterator(chunk_size=1000):
    send_email(user)
```

---

## 3. Profiling and Diagnosis via UV

Use inspection tools to identify slow queries during development.

### Django Debug Toolbar
Configure in `settings.py` and use `uv` to ensure dev dependencies are present.
```bash
# Run server with debug toolbar active (if configured)
uv run python manage.py runserver
```

### Analyzing Queries in the Shell
```python
# uv run python manage.py shell_plus --print-sql
from django.db import connection
print(len(connection.queries)) # See query count
```

---

## 4. Security and Access Review (Audit)

Based on **Access Review** standards, protect your code against failures like **BOLA/IDOR**.

### Searching for Insecure Patterns
```bash
# Search for views that might be exposing data without owner filtering (BOLA)
uv run grep -rn ".objects.all()" . --include="views.py"
```

### Secure Queryset Pattern
```python
# views.py (DRF)
class ProjectViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        # ✅ Secure Pattern: Scope restricted to the logged-in user
        return Project.objects.filter(owner=self.request.user)
```

---

## 5. Advanced Architecture (Django Pro)

### Service Layer (Business Logic)
Avoid "Fat Models" or "Fat Views". Place complex logic in services.

```python
# services.py
def process_order_payment(order_id, payment_data):
    # Complex logic here
    pass
```

### Async Django (ASGI)
For I/O bound operations (external API calls, WebSockets), use asynchronous views.

```python
async def my_async_view(request):
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.external.com")
    return JsonResponse(response.json())
```

---

## 6. Performance and Quality Checklist

- [ ] **N+1**: Verified if all foreign keys in lists use `select_related`?
- [ ] **Indexes**: Fields used in `filter()` or `order_by()` have `db_index=True`?
- [ ] **Pagination**: Do all listing endpoints have mandatory pagination?
- [ ] **Bulk**: Multiple creation/update operations use `bulk_` methods?
- [ ] **Security**: Does `get_queryset` filter data by the logged-in user/tenant?
- [ ] **Async**: External network operations are using `async` views and `httpx`?
---

<!-- @sdd-state -->
```yaml
version: "2.3.0"
feature_id: "python-uv-alignment"
phase: "VERIFY"
status: "COMPLETED"
last_update: "2026-05-06T13:12:14.664151Z"
evidence_checksum: "8e52f6a"
```
