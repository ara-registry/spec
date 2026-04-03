# ara.json Format Specification

A `ara.json` file is a standardized way to describe packages for registry publishing, client discovery, and package management.

> **Note on schema URL:** Examples in this spec use `refs/heads/main`. Production consumers SHOULD pin to a tagged release URL (e.g., `refs/tags/v1.0`) once v1.0 is cut, to avoid unexpected breakage from schema updates to the main branch.

See also:
- [Ecosystem Vision](vision.md) for design principles and architecture
- [JSON Schema](ara.schema.json) for machine-readable validation

## Table of Contents

- [Normative Language](#normative-language)
- [For Implementers](#for-implementers)
- [Required Fields](#required-fields)
  - [name](#name)
  - [version](#version)
  - [description](#description)
  - [author](#author)
  - [tags](#tags)
- [Optional Fields](#optional-fields)
  - [specVersion](#specversion)
  - [type](#type)
  - [platform](#platform)
  - [files](#files)
  - [license](#license)
  - [homepage](#homepage)
  - [repository](#repository)
  - [private](#private)
  - [dependencies](#dependencies)
  - [sources](#sources)
- [Package Types](#package-types)
- [Installation Routing](#installation-routing)
- [Lock File](#lock-file-aralock)
- [Complete Example](#complete-example)

## Normative Language

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD",
"SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be
interpreted as described in [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119).

## For Implementers

This specification defines the `ara.json` format for package manifests. All normative requirements use RFC 2119 language (MUST, SHOULD, MAY) as defined in the [Normative Language](#normative-language) section above.

---

## Required Fields

### name

Package name in `namespace/package-name` format.

| Property | Value |
|----------|-------|
| Type | `string` |
| Pattern | `^[a-zA-Z0-9_-]+/[a-zA-Z0-9_-]+$` |
| Min length | 3 |
| Max length | 200 |

The namespace groups packages by author or organization. Both namespace and package name may contain letters, numbers, hyphens, and underscores.

```json
{
  "name": "acme/code-reviewer"
}
```

### version

Semantic version string.

| Property | Value |
|----------|-------|
| Type | `string` |
| Format | [Semantic Versioning 2.0.0](https://semver.org/) |

Supports prerelease tags (`1.0.0-alpha`) and build metadata (`1.0.0+build.123`).

```json
{
  "version": "2.1.0"
}
```

### description

Human-readable explanation of package functionality.

| Property | Value |
|----------|-------|
| Type | `string` |
| Min length | 1 |
| Max length | 500 |

Focus on capabilities and use cases, not implementation details.

```json
{
  "description": "AI agent for automated code review with multi-language support"
}
```

### author

Author contact information for attribution.

| Property | Value |
|----------|-------|
| Type | `string` (email) or `object` |

Accepts either a plain email string (backwards-compatible) or an object for richer attribution:

```json
// String form (backwards compatible)
"author": "team@acme.com"

// Object form
"author": {
  "name": "ACME Corp",
  "email": "team@acme.com",
  "url": "https://acme.com"
}
```

### tags

Discovery tags for search and categorization.

| Property | Value |
|----------|-------|
| Type | `array` of `string` |
| Min items | 1 |
| Item pattern | `^[a-zA-Z0-9_-]+$` |
| Item max length | 50 |

Use lowercase, hyphen-separated terms. Tags improve discoverability in registry searches.

```json
{
  "tags": ["code-review", "automation", "typescript"]
}
```

---

## Optional Fields

### specVersion

Version of the ARA spec this manifest targets.

| Property | Value |
|----------|-------|
| Type | `string` |
| Pattern | `^[0-9]+\.[0-9]+$` |
| Default | `1.0` |

```json
{
  "specVersion": "1.0"
}
```

Clients MUST reject manifests with an unrecognized `specVersion` value and report an error to the user. Clients MAY use `specVersion` to apply forward-compatible parsing between known versions.

### type

Package type determining installation and usage behavior.

| Property | Value |
|----------|-------|
| Type | `string` |
| Enum | `agent`, `mcp-server`, `powers`, `steering`, `skill`, `context`, `agents-md` |

| Type | Description |
|------|-------------|
| `agent` | AI assistant configurations with prompts, tools, and behaviors |
| `mcp-server` | Model Context Protocol servers that extend AI capabilities |
| `powers` | Kiro-specific bundles of MCP tools, steering files, and hooks that give agents specialized capabilities |
| `steering` | Kiro-specific persistent knowledge files automatically included in the agent context window |
| `skill` | Reusable procedural knowledge via the [SKILL.md open standard](https://skillmd.org) that agents load on demand — platform-agnostic |
| `context` | Generic knowledge assets (files, prompt templates, reference docs) injected into the agent context window — platform-agnostic |
| `agents-md` | Agent instruction files following the [AGENTS.md open standard](https://agents.md/) — platform-agnostic |

```json
{
  "type": "agent"
}
```

### platform

Optional vendor-specific platform identifier.

| Property | Value |
|----------|-------|
| Type | `string` |

The `platform` field allows tool vendors to declare platform-specific installation behavior while remaining interoperable at the registry level. The registry routes the archive; the client uses `platform` to determine where to unpack it.

```json
{
  "type": "agent",
  "platform": "kiro"
}
```

Example values: `kiro`, `claude-code`, `opencode`, `codex`. Tool vendors MAY define their own platform identifiers using a consistent lowercase slug.

### files

Package files to include when publishing.

| Property | Value |
|----------|-------|
| Type | `array` of `string` |
| Default | All files (excluding common ignores) |

#### Behavior

| Scenario | Behavior |
|----------|----------|
| `files` omitted | All files included (excluding `.git`, `node_modules`, etc.) |
| `files` is `[]` | No files included - metadata-only package |
| `files` has entries | Only specified files/directories included |

#### Path Rules

- Paths are relative to the package root (where `ara.json` lives)
- Paths MUST NOT escape the package root (no `../` traversal)
- Directory paths should end with `/` to include all contents recursively
- Glob patterns are not supported - use explicit paths

```json
{
  "files": [
    "prompts/",
    "config.json",
    "README.md"
  ]
}
```

#### Implementation Notes

1. Implementations MUST resolve paths relative to the `ara.json` location
2. Implementations MUST reject paths containing `..` or absolute paths
3. When a directory path ends with `/`, implementations SHOULD recursively include all files within
4. Implementations MUST preserve directory structure in the packaged output
5. When `files` is omitted, implementations SHOULD apply sensible defaults to exclude build artifacts and version control directories

### license

SPDX license identifier.

| Property | Value |
|----------|-------|
| Type | `string` |
| Max length | 100 |

Use identifiers from the [SPDX License List](https://spdx.org/licenses/).

```json
{
  "license": "MIT"
}
```

### homepage

Project homepage or documentation URL.

| Property | Value |
|----------|-------|
| Type | `string` |
| Format | URI |

```json
{
  "homepage": "https://acme.com/code-reviewer"
}
```

### repository

Source repository URL for browsing and contributing.

| Property | Value |
|----------|-------|
| Type | `string` |
| Format | URI |

```json
{
  "repository": "https://github.com/acme/code-reviewer"
}
```

### private

Marks this package as internal-only, preventing accidental publishing to public registries.

| Property | Value |
|----------|-------|
| Type | `boolean` |
| Default | `false` |

```json
{
  "private": true
}
```

Registries MUST treat `private: true` packages as non-publishable to public indexes. Clients SHOULD warn users attempting to publish a private package.

### dependencies

Package dependencies with version constraints.

| Property | Value |
|----------|-------|
| Type | `object` |
| Keys | Package names in `namespace/package-name` format |
| Values | Version constraint strings |

Version constraints follow semantic versioning:

| Constraint | Meaning |
|------------|---------|
| `1.0.0` | Exact version |
| `^1.0.0` | Compatible with 1.x.x (>=1.0.0 <2.0.0) |
| `~1.0.0` | Compatible with 1.0.x (>=1.0.0 <1.1.0) |
| `>=1.0.0` | Version 1.0.0 or higher |
| `*` | Any version |

```json
{
  "dependencies": {
    "acme/base-prompts": "^1.0.0",
    "acme/common-tools": ">=2.0.0"
  }
}
```

#### Implementation Notes

Implementations resolving dependencies SHOULD:

1. Parse version constraints using semver semantics
2. Resolve the dependency graph before installation
3. Detect and report circular dependencies
4. Support lock files for reproducible installs

### sources

Installation sources for MCP server packages.

| Property | Value |
|----------|-------|
| Type | `array` of `PackageSource` |
| Applies to | `mcp-server` type only |

Only valid when `type` is `mcp-server`. Clients attempt sources in order, preferring those marked with `preferred: true`.

#### Source Types

**npm** - Install from npm registry:
```json
{
  "type": "npm",
  "package": "@acme/weather-mcp",
  "version": "1.0.0",
  "registry": "https://registry.npmjs.org"
}
```

| Field | Required | Description |
|-------|----------|-------------|
| `type` | Yes | `"npm"` |
| `package` | Yes | npm package name |
| `version` | No | Specific version |
| `registry` | No | Registry URL (defaults to npmjs.org) |

**pypi** - Install from PyPI:
```json
{
  "type": "pypi",
  "package": "weather-mcp-server",
  "version": "0.5.0",
  "registry": "https://pypi.org"
}
```

| Field | Required | Description |
|-------|----------|-------------|
| `type` | Yes | `"pypi"` |
| `package` | Yes | PyPI package name |
| `version` | No | Specific version |
| `registry` | No | Registry URL (defaults to pypi.org) |

**git** - Build from source:

> ⚠️ **Security Warning:** The `installCommand` field executes arbitrary shell commands
> during installation. Clients MUST display the full command to the user and require
> explicit confirmation before execution. Clients SHOULD sandbox execution where
> possible. Registries SHOULD flag packages using `installCommand` for additional
> security review. Never execute `installCommand` in automated or non-interactive
> environments without explicit user opt-in.

```json
{
  "type": "git",
  "repository": "https://github.com/example/mcp-server",
  "ref": "v1.0.0",
  "subfolder": "packages/server",
  "installCommand": "npm install && npm run build",
  "executable": "dist/index.js"
}
```

| Field | Required | Description |
|-------|----------|-------------|
| `type` | Yes | `"git"` |
| `repository` | Yes | Git repository URL |
| `ref` | No | Tag, branch, or commit hash |
| `subfolder` | No | Subdirectory for monorepos |
| `installCommand` | No | Build command after clone |
| `executable` | No | Path to executable after build |

Clients implementing `installCommand` support SHOULD maintain a configurable allowlist of permitted commands and patterns.

**mcp-registry** - Install from MCP Registry:
```json
{
  "type": "mcp-registry",
  "package": "@modelcontextprotocol/server-brave-search"
}
```

| Field | Required | Description |
|-------|----------|-------------|
| `type` | Yes | `"mcp-registry"` |
| `package` | Yes | MCP Registry package name |

**oci** - Pull from an OCI/container registry:
```json
{
  "type": "oci",
  "image": "ghcr.io/acme/weather-mcp",
  "tag": "2.0.0",
  "digest": "sha256:abc123...",
  "registry": "ghcr.io"
}
```

| Field | Required | Description |
|-------|----------|-------------|
| `type` | Yes | `"oci"` |
| `image` | Yes | Full image name |
| `tag` | No | Image tag (defaults to `latest`) |
| `digest` | No | Content-addressable digest (preferred over tag for reproducibility) |
| `registry` | No | Registry host (inferred from image if omitted) |

#### Multiple Sources

Packages can specify multiple sources for redundancy:

```json
{
  "sources": [
    {
      "type": "npm",
      "package": "@acme/server",
      "version": "1.0.0",
      "preferred": true
    },
    {
      "type": "pypi",
      "package": "acme-server",
      "version": "1.0.0"
    }
  ]
}
```

#### Implementation Notes

Implementations SHOULD:

1. Attempt the source marked `preferred: true` first
2. Fall back to other sources in array order on failure
3. Validate git repositories against an allowlist of trusted domains
4. Cache installed packages to avoid redundant downloads

---

## Package Types

### Agent Packages

Agent packages contain AI assistant configurations including prompts, tool definitions, and behavioral settings. Use `platform` to declare tool-specific installation targets.

```json
{
  "$schema": "https://raw.githubusercontent.com/ara-registry/spec/refs/heads/main/ara.schema.json",
  "name": "acme/code-reviewer",
  "version": "1.0.0",
  "description": "AI agent for automated code review",
  "author": "developer@example.com",
  "tags": ["code-review", "automation", "quality"],
  "type": "agent",
  "files": [
    "prompts/system.md",
    "prompts/review.md",
    "config.json"
  ]
}
```

### MCP Server Packages

MCP server packages describe Model Context Protocol servers with installation sources.

```json
{
  "$schema": "https://raw.githubusercontent.com/ara-registry/spec/refs/heads/main/ara.schema.json",
  "name": "acme/weather-server",
  "version": "2.0.0",
  "description": "MCP server for weather data access",
  "author": "developer@example.com",
  "tags": ["weather", "api", "mcp"],
  "type": "mcp-server",
  "sources": [
    {
      "type": "npm",
      "package": "@acme/weather-mcp",
      "version": "2.0.0"
    }
  ]
}
```

### Context Packages

Context packages contain knowledge files, prompt templates, and reference materials.

```json
{
  "$schema": "https://raw.githubusercontent.com/ara-registry/spec/refs/heads/main/ara.schema.json",
  "name": "acme/rust-guidelines",
  "version": "1.0.0",
  "description": "Rust coding guidelines and best practices",
  "author": "developer@example.com",
  "tags": ["rust", "guidelines", "best-practices"],
  "type": "context",
  "files": [
    "guidelines.md",
    "examples/"
  ]
}
```

### Skill Packages

Skill packages contain procedural knowledge that agents load dynamically via SKILL.md files. Unlike agents which configure AI assistant identity, skills provide on-demand instructions for specific tasks.

```json
{
  "$schema": "https://raw.githubusercontent.com/ara-registry/spec/refs/heads/main/ara.schema.json",
  "name": "acme/git-workflow",
  "version": "1.0.0",
  "description": "Git workflow procedures for branching and merging",
  "author": "developer@example.com",
  "tags": ["git", "workflow", "procedures"],
  "type": "skill",
  "files": [
    "SKILL.md"
  ]
}
```

### AGENTS.md Packages

AGENTS.md packages use the open format for guiding coding agents.

```json
{
  "$schema": "https://raw.githubusercontent.com/ara-registry/spec/refs/heads/main/ara.schema.json",
  "name": "acme/monorepo-guide",
  "version": "1.0.0",
  "description": "AGENTS.md guide for monorepo development",
  "author": "developer@example.com",
  "tags": ["monorepo", "agents", "guide"],
  "type": "agents-md",
  "files": [
    "AGENTS.md"
  ]
}
```

### Powers Packages

Powers packages bundle MCP tools with steering files and hooks that give agents specialized capabilities.

```json
{
  "$schema": "https://raw.githubusercontent.com/ara-registry/spec/refs/heads/main/ara.schema.json",
  "name": "acme/database-power",
  "version": "1.0.0",
  "description": "Database management power with SQL tools and best practices",
  "author": "developer@example.com",
  "tags": ["database", "sql", "tools"],
  "type": "powers",
  "platform": "kiro",
  "files": [
    "tools/",
    "steering/",
    "hooks/"
  ]
}
```

### Steering Packages

Steering packages contain persistent project knowledge that guides agent behavior.

```json
{
  "$schema": "https://raw.githubusercontent.com/ara-registry/spec/refs/heads/main/ara.schema.json",
  "name": "acme/react-patterns",
  "version": "1.0.0",
  "description": "React development patterns and conventions",
  "author": "developer@example.com",
  "tags": ["react", "patterns", "conventions"],
  "type": "steering",
  "platform": "kiro",
  "files": [
    "steering.md"
  ]
}
```

---

## Installation Routing

An **ARA-compatible client** is any tool or CLI that implements this specification to install ARA packages. A developer may have multiple ARA-compatible tools active in the same project simultaneously. Clients SHOULD detect which other tools are present and install packages to all compatible locations in a single operation.

### ARA-compatible Tool Contract

Every ARA-compatible tool MUST publish the following as part of its ARA integration documentation:

1. **Platform identifier** — the string used as the `platform` field value (e.g., the tool's canonical lowercase name)
2. **Detection marker** — how other clients detect whether this tool is active in a project (typically a well-known directory at the project root or in the user's home directory)
3. **Routing table** — a mapping of package `type` → installation path for all types the tool supports

Clients SHOULD detect active tools by inspecting the project for the detection markers published by known ARA-compatible tools. Clients MAY also support an explicit configuration where users declare their active tools, for cases where detection is ambiguous.

### The `platform` Field as a Restriction

When `platform` is absent, a client SHOULD install to **all detected compatible tools**. When `platform` is set, installation is restricted to that tool only — all other detected tools MUST skip the package.

| Manifest | Tools detected | Result |
|----------|---------------|--------|
| `"type": "skill"` | Tool A, Tool B | Installs for both |
| `"type": "skill", "platform": "tool-a"` | Tool A, Tool B | Installs for Tool A only |
| `"type": "agent", "platform": "tool-b"` | Tool A only | Skipped — Tool B not present |

### Special Case: `agents-md`

`agents-md` packages follow the [AGENTS.md open standard](https://agents.md/) — a single Markdown file placed at the project root, natively supported by a large number of AI coding tools. Clients SHOULD install `agents-md` packages to the project root as `AGENTS.md`.

Tools that use a proprietary instruction file format instead of or in addition to `AGENTS.md` SHOULD document how their ARA client handles `agents-md` installation (e.g., creating an import or symlink from their proprietary format to `AGENTS.md`).

### Special Case: `mcp-server`

MCP server installation is driven by the `sources` field and is inherently tool-specific. Each ARA-compatible tool SHOULD document its MCP routing behavior as part of its integration documentation.

---

## Lock File (ara.lock)

The `ara.lock` file records exact versions and integrity hashes for reproducible installations. It is generated automatically when installing packages locally.

### Purpose

- **Reproducibility**: Ensures all team members install identical versions
- **Integrity**: SHA-256 hashes verify package contents haven't changed
- **Speed**: Skips resolution when lock file is present and valid

### Format

```json
{
  "lockfileVersion": 1,
  "generatedAt": "2025-12-30T15:30:00+00:00",
  "packages": {
    "acme/code-review": {
      "version": "1.2.0",
      "type": "skill",
      "integrity": "sha256-abc123...",
      "resolved": "https://...",
      "dependencies": {}
    },
    "acme/test-generator": {
      "version": "2.0.1",
      "type": "skill",
      "integrity": "sha256-def456...",
      "resolved": "https://...",
      "dependencies": {
        "acme/code-review": "^1.0.0"
      }
    },
    "myteam/my-agent": {
      "version": "0.5.0",
      "type": "agent",
      "integrity": "sha256-ghi789...",
      "resolved": "https://...",
      "dependencies": {}
    }
  }
}
```

### Fields

| Field | Description |
|-------|-------------|
| `lockfileVersion` | Lock file format version (currently `1`) |
| `generatedAt` | ISO 8601 timestamp when lock file was generated |
| `packages` | Map of package names to locked metadata |
| `version` | Exact installed version |
| `type` | Package type |
| `integrity` | SHA-256 hash of package contents |
| `resolved` | URL where package was downloaded from |
| `dependencies` | Map of dependency names to version ranges |

### Behavior

| Command | Lock file behavior |
|---------|-------------------|
| `install <package>` | Add to lock file |
| `install` (no args) | Install from lock file |
| `update <package>` | Update entry in lock file |
| `uninstall <package>` | Remove from lock file |

### Implementation Notes

Implementations supporting lock files SHOULD:

1. Generate lock file on first install or when dependencies change
2. Verify integrity hash before using cached packages
3. Re-resolve if lock file is missing or corrupted
4. Commit lock file to version control for team reproducibility

> **Note:** A JSON Schema for `ara.lock` is out of scope for this version of the spec.

---

## Complete Example

```json
{
  "$schema": "https://raw.githubusercontent.com/ara-registry/spec/refs/heads/main/ara.schema.json",
  "specVersion": "1.0",
  "name": "acme/full-stack-assistant",
  "version": "2.1.0",
  "description": "AI assistant for full-stack development with code review and testing",
  "author": {
    "name": "ACME Corp",
    "email": "team@acme.com",
    "url": "https://acme.com"
  },
  "tags": ["development", "code-review", "testing", "full-stack"],
  "type": "agent",
  "platform": "claude-code",
  "license": "MIT",
  "homepage": "https://acme.com/full-stack-assistant",
  "repository": "https://github.com/acme/full-stack-assistant",
  "private": false,
  "files": [
    "prompts/system.md",
    "prompts/review.md",
    "prompts/test.md",
    "config.json"
  ],
  "dependencies": {
    "acme/code-standards": "^1.0.0"
  }
}
```

---

## Reference Libraries

Demo implementations for parsing and validating `ara.json` files:

- [Python Reference Library](lib/python/) using Pydantic
- [Rust Reference Library](lib/rust/) using Serde

These libraries are provided as examples for implementers and are not production-ready.
