# REST API Design Guide

Design patterns to ensure the API is intuitive and scalable.

## 1. Resource Naming
- Use **Plural Nouns**: `/users`, `/items`, `/orders`.
- NEVER use verbs in the path: `/getUsers` (Wrong) -> `/users` (Right).

## 2. Versioning
- Always use versioning in the path: `/v1/users`, `/v2/items`.
- This allows evolving the API without breaking old clients.

## 3. Mandatory Status Codes
| Code | Meaning | When to use |
|------|-------------|-------------|
| 200 | OK | Success in GET or PUT. |
| 201 | Created | Success in POST (Creation). |
| 204 | No Content | Success in DELETE (No body). |
| 400 | Bad Request | Client logic error. |
| 401 | Unauthorized | Lack of authentication. |
| 403 | Forbidden | Authenticated, but without permission (Scopes). |
| 404 | Not Found | Non-existent resource. |

## 4. Filtering and Pagination
Use Query Parameters for search and pagination:
- `GET /users?limit=10&offset=20`
- `GET /items?status=active`


---

<!-- @sdd-state -->
```yaml
version: "2.3.0"
feature_id: "HUB-ALIGNMENT"
phase: "VERIFY"
status: "COMPLETED"
last_update: "2026-05-06T13:16:19.360611Z"
evidence_checksum: "8e52f6a"
```
