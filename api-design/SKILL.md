# API Design — Best Practices for REST APIs

This skill provides procedural guidance for designing consistent, production-quality REST APIs. Apply these conventions when creating new endpoints, reviewing API designs, or refactoring existing APIs.

---

## 1. URL & Resource Naming

### Procedure

- Use **nouns** for resource names, never verbs: `/users`, `/orders`, `/invoices`.
- Use **plural** forms for collection endpoints: `/users` not `/user`.
- Use **kebab-case** for multi-word resource names: `/order-items`, `/user-profiles`.
- Nest resources to express relationships, but limit to one level of depth:
  ```
  GET /users/{userId}/orders          ✅ clear relationship
  GET /users/{userId}/orders/{orderId}/items  ⚠️  consider promoting to /order-items?orderId={id}
  ```
- Use path parameters for identity (`/users/{id}`) and query parameters for filtering (`/users?role=admin`).
- Keep base URLs short and predictable: `https://api.example.com/v1/`.

### Rationale

Noun-based, plural URLs create a uniform interface that clients can predict without reading documentation. Limiting nesting depth prevents brittle, deeply coupled URL structures that break when relationships change.

---

## 2. HTTP Methods

### Procedure

| Method | Purpose | Idempotent | Safe | Request Body |
|--------|---------|-----------|------|-------------|
| `GET` | Retrieve a resource or collection | Yes | Yes | No |
| `POST` | Create a new resource | No | No | Yes |
| `PUT` | Replace an entire resource | Yes | No | Yes |
| `PATCH` | Partially update a resource | No* | No | Yes |
| `DELETE` | Remove a resource | Yes | No | Optional |

*PATCH can be made idempotent with proper design but is not required to be.

- Use `POST` for actions that don't map to CRUD — nest under the resource: `POST /orders/{id}/cancel`.
- Return `405 Method Not Allowed` for unsupported methods on a valid resource.
- Always support `HEAD` and `OPTIONS` on every endpoint.

### Rationale

Correct method semantics enable caching (GET), safe retries (PUT, DELETE), and predictable behavior for intermediaries like proxies and CDNs. Misusing methods (e.g., GET with side effects) breaks these guarantees.

---

## 3. Request & Response Design

### Procedure

- Use **JSON** (`application/json`) as the default content type.
- Use **camelCase** for JSON property names:
  ```json
  { "userId": 42, "firstName": "Ada", "createdAt": "2025-01-15T09:30:00Z" }
  ```
- Format all timestamps as **ISO 8601** in UTC: `2025-01-15T09:30:00Z`.
- Wrap collection responses in an envelope with metadata:
  ```json
  {
    "data": [ ... ],
    "pagination": { "nextCursor": "abc123", "hasMore": true },
    "meta": { "totalCount": 247 }
  }
  ```
- For single resource responses, return the object directly (no envelope) or under a `"data"` key — pick one convention and be consistent.
- Include a `Content-Type` header in all responses.
- Accept `Content-Type` and validate it — return `415 Unsupported Media Type` for unexpected formats.

### Rationale

Consistent JSON conventions reduce parsing friction for client developers. Envelopes for collections provide a stable place for pagination metadata without conflicting with the resource data. ISO 8601 eliminates timezone ambiguity.

---

## 4. Status Codes

### Procedure

**Success (2xx):**
| Code | When to Use |
|------|------------|
| `200 OK` | Successful GET, PUT, PATCH, or DELETE |
| `201 Created` | Successful POST that creates a resource (include `Location` header) |
| `202 Accepted` | Request accepted for async processing |
| `204 No Content` | Successful DELETE or PUT with no response body |

**Redirection (3xx):**
| Code | When to Use |
|------|------------|
| `301 Moved Permanently` | Resource URL has changed permanently |
| `304 Not Modified` | Conditional GET — client cache is still valid |

**Client Error (4xx):**
| Code | When to Use |
|------|------------|
| `400 Bad Request` | Malformed syntax or invalid request body |
| `401 Unauthorized` | Missing or invalid authentication |
| `403 Forbidden` | Authenticated but lacks permission |
| `404 Not Found` | Resource does not exist |
| `409 Conflict` | State conflict (e.g., duplicate creation, version mismatch) |
| `422 Unprocessable Entity` | Valid syntax but semantic errors (e.g., validation failures) |
| `429 Too Many Requests` | Rate limit exceeded |

**Server Error (5xx):**
| Code | When to Use |
|------|------------|
| `500 Internal Server Error` | Unexpected server failure |
| `502 Bad Gateway` | Upstream service failure |
| `503 Service Unavailable` | Temporary overload or maintenance (include `Retry-After`) |

- Never return `200` with an error message in the body.
- Use `404` for missing resources, not `200` with `null`.

### Rationale

HTTP status codes are machine-readable signals that clients and infrastructure (load balancers, monitoring, retries) depend on. Using them correctly enables automated error handling and accurate observability.

---

## 5. Error Handling

### Procedure

Return a consistent error response structure for all 4xx and 5xx responses:

```json
{
  "error": {
    "code": "VALIDATION_FAILED",
    "message": "The request body contains invalid fields.",
    "details": [
      {
        "field": "email",
        "reason": "Must be a valid email address.",
        "value": "not-an-email"
      }
    ],
    "requestId": "req_abc123"
  }
}
```

- **`code`**: Machine-readable error identifier (UPPER_SNAKE_CASE).
- **`message`**: Human-readable summary safe to display to end users.
- **`details`**: Optional array with field-level errors for validation failures.
- **`requestId`**: Correlation ID for debugging (also return as `X-Request-Id` header).
- Never expose stack traces, internal paths, or database details in production error responses.

### Rationale

A predictable error format lets clients programmatically handle errors, display meaningful messages to users, and correlate issues with server logs using the request ID.

---

## 6. Versioning

### Procedure

- Use **URL path versioning** as the default strategy: `/v1/users`, `/v2/users`.
- Increment the major version only for breaking changes.
- When deprecating a version:
  1. Add a `Deprecation` header: `Deprecation: true`.
  2. Add a `Sunset` header with the removal date: `Sunset: Sat, 01 Mar 2026 00:00:00 GMT`.
  3. Document the migration path.
  4. Maintain the deprecated version for at least 6 months.
- Alternative: use the `Accept` header for versioning (`Accept: application/vnd.example.v2+json`) when URL versioning is not practical.

### Rationale

URL path versioning is the most visible and debuggable approach — version is apparent in every request. Clear deprecation timelines give clients time to migrate without surprises.

---

## 7. Pagination

### Procedure

**Cursor-based pagination** (preferred for most use cases):
```
GET /users?limit=20&cursor=eyJpZCI6MTAwfQ
```
Response:
```json
{
  "data": [ ... ],
  "pagination": {
    "nextCursor": "eyJpZCI6MTIwfQ",
    "previousCursor": "eyJpZCI6ODF9",
    "hasMore": true
  }
}
```

**Offset-based pagination** (when random page access is needed):
```
GET /users?limit=20&offset=40
```
Response:
```json
{
  "data": [ ... ],
  "pagination": {
    "limit": 20,
    "offset": 40,
    "totalCount": 247
  }
}
```

- Default `limit` to a sensible value (e.g., 20). Enforce a maximum (e.g., 100).
- Include `Link` headers for discoverability:
  ```
  Link: <https://api.example.com/v1/users?cursor=abc>; rel="next",
        <https://api.example.com/v1/users?cursor=xyz>; rel="prev"
  ```

### Rationale

Cursor-based pagination is stable under concurrent writes (no skipped or duplicated items) and performs well at scale. Offset pagination is simpler but degrades with large offsets and is vulnerable to data shifting between pages.

---

## 8. Filtering, Sorting & Search

### Procedure

**Filtering** — use query parameters matching field names:
```
GET /users?status=active&role=admin
GET /orders?createdAfter=2025-01-01T00:00:00Z&totalMin=100
```

**Sorting** — use a `sort` parameter with optional `-` prefix for descending:
```
GET /users?sort=createdAt        # ascending (default)
GET /users?sort=-createdAt       # descending
GET /users?sort=-priority,createdAt  # multi-field sort
```

**Search** — use a `q` parameter for full-text search:
```
GET /users?q=ada+lovelace
```

- Document every supported filter and sort field.
- Return `400` for unsupported filter/sort fields rather than silently ignoring them.
- Combine filters with AND logic by default.

### Rationale

Consistent query parameter conventions let clients compose complex queries without learning custom DSLs. Rejecting unknown parameters prevents subtle bugs where a typo silently returns unfiltered data.

---

## 9. Authentication & Authorization

### Procedure

- Use **Bearer tokens** in the `Authorization` header as the primary auth mechanism:
  ```
  Authorization: Bearer eyJhbGciOiJSUzI1NiIs...
  ```
- Support **API keys** for server-to-server communication, passed in a custom header:
  ```
  X-API-Key: sk_live_abc123
  ```
- For user-facing applications, implement **OAuth 2.0** with PKCE for authorization code flow.
- Return `401 Unauthorized` when credentials are missing or invalid.
- Return `403 Forbidden` when credentials are valid but permissions are insufficient.
- Include a `WWW-Authenticate` header in `401` responses:
  ```
  WWW-Authenticate: Bearer realm="api", error="invalid_token"
  ```
- Never pass credentials in URL query parameters (they appear in logs and browser history).

### Rationale

The `Authorization` header is the standard mechanism supported by all HTTP clients and infrastructure. OAuth 2.0 with PKCE is the current industry standard for delegated authorization. Separating authentication (401) from authorization (403) helps clients take the correct remedial action.

---

## 10. Rate Limiting

### Procedure

- Include rate limit headers in every response:
  ```
  X-RateLimit-Limit: 1000
  X-RateLimit-Remaining: 994
  X-RateLimit-Reset: 1706140800
  ```
- When the limit is exceeded, return `429 Too Many Requests` with:
  ```
  Retry-After: 30
  ```
  ```json
  {
    "error": {
      "code": "RATE_LIMIT_EXCEEDED",
      "message": "Too many requests. Please retry after 30 seconds.",
      "retryAfter": 30
    }
  }
  ```
- Apply rate limits per API key or per authenticated user, not per IP alone.
- Use tiered rate limits: higher limits for authenticated users, lower for anonymous.
- Consider separate limits for different endpoint categories (reads vs. writes).

### Rationale

Rate limit headers let well-behaved clients self-throttle before hitting limits. The `Retry-After` header enables automatic backoff. Per-key limits prevent one client from impacting others.

---

## 11. Security Headers

### Procedure

Include these headers in all API responses:

```
Content-Type: application/json; charset=utf-8
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Strict-Transport-Security: max-age=31536000; includeSubDomains
Cache-Control: no-store
```

**CORS** (when serving browser clients):
```
Access-Control-Allow-Origin: https://app.example.com
Access-Control-Allow-Methods: GET, POST, PUT, PATCH, DELETE, OPTIONS
Access-Control-Allow-Headers: Authorization, Content-Type, X-Request-Id
Access-Control-Max-Age: 86400
```

- Never use `Access-Control-Allow-Origin: *` with credentialed requests.
- Always require HTTPS in production — redirect HTTP to HTTPS.
- Set `Content-Security-Policy: default-src 'none'` for API-only services.

### Rationale

Security headers protect against common web vulnerabilities (XSS, clickjacking, MIME sniffing, man-in-the-middle). HSTS ensures browsers always use HTTPS after the first visit. Restrictive CORS prevents unauthorized cross-origin access.

---

## 12. HATEOAS & Hypermedia

### Procedure

Include `_links` in responses to make APIs self-describing:

```json
{
  "id": 42,
  "name": "Ada Lovelace",
  "email": "ada@example.com",
  "_links": {
    "self": { "href": "/v1/users/42" },
    "orders": { "href": "/v1/users/42/orders" },
    "update": { "href": "/v1/users/42", "method": "PATCH" },
    "delete": { "href": "/v1/users/42", "method": "DELETE" }
  }
}
```

- Use standard link relations where applicable: `self`, `next`, `prev`, `first`, `last`.
- Only include links for actions the current user is authorized to perform.
- For collection responses, include navigation links in the top-level `_links`.

### Rationale

Hypermedia links decouple clients from hardcoded URL construction, making APIs evolvable. Clients discover available actions from the response itself, reducing out-of-band documentation dependency and enabling dynamic UIs that adapt to server-side permissions.

---

## 13. Idempotency

### Procedure

- Accept an `Idempotency-Key` header for non-idempotent operations (POST):
  ```
  Idempotency-Key: 7c4a8d09ca3762af
  ```
- Server behavior:
  1. On first request: process normally, store the response keyed by the idempotency key.
  2. On duplicate request (same key): return the stored response without re-processing.
  3. Key expiration: retain stored responses for at least 24 hours.
- Return `409 Conflict` if the same key is used with a different request body.
- Return `422 Unprocessable Entity` if the key format is invalid.
- `GET`, `PUT`, and `DELETE` are inherently idempotent — the header is only needed for `POST` and non-idempotent `PATCH` operations.

### Rationale

Network failures and client retries are inevitable. The idempotency key pattern prevents duplicate side effects (double charges, duplicate records) while letting clients safely retry without risk. This is critical for payment and financial APIs.

---

## 14. OpenAPI & Documentation

### Procedure

- Adopt a **spec-first design** approach: write the OpenAPI specification before implementing endpoints.
- Use **OpenAPI 3.1** (or latest stable version) as the specification format.
- Include in every operation:
  - Summary and description.
  - Request body schema with examples.
  - All possible response codes with schemas.
  - Authentication requirements (`security` field).
- Serve the spec at a well-known path: `GET /openapi.json` or `GET /openapi.yaml`.
- Generate interactive documentation (Swagger UI, Redoc) from the spec.
- Validate requests and responses against the spec in tests.
- Example operation:
  ```yaml
  /users:
    post:
      operationId: createUser
      summary: Create a new user
      tags: [Users]
      security:
        - bearerAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CreateUserRequest'
            example:
              email: "ada@example.com"
              name: "Ada Lovelace"
      responses:
        '201':
          description: User created
          headers:
            Location:
              schema:
                type: string
              example: /v1/users/42
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'
        '400':
          $ref: '#/components/responses/BadRequest'
        '409':
          $ref: '#/components/responses/Conflict'
  ```

### Rationale

Spec-first design ensures the API contract is agreed upon before implementation begins, preventing drift between documentation and behavior. OpenAPI enables automated code generation, testing, and client SDK creation, dramatically reducing integration effort.
