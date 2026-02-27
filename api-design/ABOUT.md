# API Design Skill Package — Overview

## What is the ARA Project?

ARA (AI Registry for Agents) is an open-source package registry — similar to npm or PyPI, but built for AI agents. It lets developers publish, discover, and install packages that enhance AI agent capabilities. Each package has an `ara.json` manifest file that describes what it is, who made it, and how to use it.

ARA supports 7 package types:

| Type | Purpose |
|------|---------|
| `kiro-agent` | Custom agent configurations with prompts, tools, and behaviors |
| `mcp-server` | Model Context Protocol servers extending AI capabilities |
| `context` | Knowledge files, prompt templates, and reference materials |
| `skill` | Procedural knowledge via SKILL.md that agents load dynamically |
| `kiro-powers` | Bundle MCP tools, steering files, and hooks |
| `kiro-steering` | Persistent knowledge about projects |
| `agents-md` | AGENTS.md format for guiding coding agents |

---

## What is a "Skill" Package?

A skill package delivers procedural knowledge — step-by-step instructions that an AI agent can load on-demand when it needs to perform a specific task.

The key difference from other types:

- **Agents** (`kiro-agent`) configure an AI's identity and overall behavior.
- **Skills** teach an AI how to do something specific.

A skill package contains a `SKILL.md` file with structured procedures. When an agent needs to design an API, for example, it loads the `api-design` skill and follows the procedures inside.

---

## What Was Built

This is the first example skill package for the ARA project: `ara/api-design`. It consists of two files inside the `api-design/` directory.

### File 1: `ara.json` — The Package Manifest

The metadata file that tells the ARA registry what this package is.

```json
{
  "$schema": "https://raw.githubusercontent.com/aws/ara/refs/heads/main/ara.schema.json",
  "name": "ara/api-design",
  "version": "1.0.0",
  "description": "Comprehensive REST API design best practices for AI agents building HTTP APIs",
  "author": "ara@example.com",
  "tags": ["api-design", "rest", "http", "best-practices"],
  "type": "skill",
  "license": "Apache-2.0",
  "files": ["SKILL.md"]
}
```

| Field | Value | Purpose |
|-------|-------|---------|
| `$schema` | ARA schema URL | Enables IDE validation and auto-complete |
| `name` | `ara/api-design` | Unique package identifier in `namespace/name` format |
| `version` | `1.0.0` | Semantic version following semver |
| `description` | REST API best practices... | Human-readable summary (max 500 chars) |
| `author` | `ara@example.com` | Contact email for attribution |
| `tags` | `api-design`, `rest`, `http`, `best-practices` | Discovery keywords for registry search |
| `type` | `skill` | Declares this as a skill package |
| `license` | `Apache-2.0` | SPDX open-source license identifier |
| `files` | `["SKILL.md"]` | Files included when the package is installed |

### File 2: `SKILL.md` — The Procedural Guide

The actual skill content — a comprehensive guide covering 14 sections of REST API design best practices. Each section has two parts:

- **Procedure** — concrete, actionable steps with code examples.
- **Rationale** — the reasoning behind the convention.

#### Section Breakdown

| # | Section | What It Teaches |
|---|---------|----------------|
| 1 | URL & Resource Naming | Use nouns, plurals, kebab-case, limit nesting to one level |
| 2 | HTTP Methods | Correct GET/POST/PUT/PATCH/DELETE semantics with idempotency and safety properties |
| 3 | Request & Response Design | JSON with camelCase properties, ISO 8601 timestamps, collection envelopes |
| 4 | Status Codes | When to use each 2xx, 3xx, 4xx, 5xx code with reference tables |
| 5 | Error Handling | Consistent error format with `code`, `message`, `details`, and `requestId` |
| 6 | Versioning | URL path versioning (`/v1/`), `Deprecation` and `Sunset` headers for migration |
| 7 | Pagination | Cursor-based (preferred) and offset-based patterns with `Link` headers |
| 8 | Filtering, Sorting & Search | Query parameter conventions like `?sort=-createdAt` and `?q=term` |
| 9 | Authentication & Authorization | Bearer tokens, API keys, OAuth 2.0 with PKCE, difference between 401 and 403 |
| 10 | Rate Limiting | `X-RateLimit-*` headers, `429` responses, `Retry-After` header |
| 11 | Security Headers | CORS configuration, HSTS, `X-Content-Type-Options`, Content-Security-Policy |
| 12 | HATEOAS & Hypermedia | `_links` pattern for self-describing, discoverable APIs |
| 13 | Idempotency | `Idempotency-Key` header pattern to prevent duplicate side effects |
| 14 | OpenAPI & Documentation | Spec-first design approach with OpenAPI 3.1 |

---

## Validation

The package was validated using the ARA Python reference library (`ara-ref`). The library checks the manifest against the official `ara.schema.json` schema.

```
python -c "import ara_ref; print(ara_ref.validate('api-design/ara.json'))"
# Result: []  (empty list = zero errors)
```

All fields were correctly recognized and parsed — name, version, type, tags, files, and license all conform to the schema requirements.

---

## Project Structure

```
spec/                          <-- ARA project root
├── ara.schema.json            <-- Schema that validates all packages
├── ara-json.md                <-- Full specification document
├── vision.md                  <-- Project vision and tenets
├── registry-api.md            <-- HTTP API specification
├── security.md                <-- Security guidance
├── lib/
│   ├── python/                <-- Python reference library (used for validation)
│   └── rust/                  <-- Rust reference library
└── api-design/                <-- The skill package
    ├── ara.json               <-- Package manifest (metadata)
    ├── SKILL.md               <-- Procedural knowledge (the skill content)
    └── ABOUT.md               <-- This document
```

---

## How It Works End-to-End

When an AI agent needs to design a REST API, the workflow is:

1. **Discover** — The agent searches the ARA registry using tags like `rest` or `api-design` and finds the `ara/api-design` package.
2. **Install** — The agent installs the package, which downloads `SKILL.md` to its local environment.
3. **Load** — The agent reads `SKILL.md` into its context when starting an API design task.
4. **Apply** — The agent follows the procedures in each section to produce a well-designed REST API, covering everything from URL naming to error handling to security headers.

This package serves as both a useful skill for API design and a reference example for anyone creating their own skill packages for the ARA ecosystem.
