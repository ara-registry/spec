# ARA CLI — Documentation

## What is ARA?

ARA (AI Registry for Agents) is an **open-source package registry by Amazon/AWS** for sharing AI development artifacts — agents, MCP servers, skills, prompts, and more. Think of it as **npm, but for AI tools**.

## What We Built

We built the **ARA CLI** — a Python command-line tool that lets developers create, publish, discover, install, and manage AI packages from the ARA registry.

---

## Tech Stack

| Technology | Purpose |
|---|---|
| Python 3.10+ | Language |
| Click 8+ | Command-line framework |
| Pydantic 2+ | Data validation |
| httpx | Async HTTP client for registry API |
| Rich | Beautiful terminal output (tables, progress bars, colors) |
| packaging | Semantic version parsing |
| hatchling | Build system |

---

## Commands Overview

| # | Command | What it does | Needs server? |
|---|---|---|---|
| 1 | `ara init` | Create a new package (interactive wizard) | No |
| 2 | `ara validate` | Check if ara.json is correct | No |
| 3 | `ara login` | Save auth token for publishing | No |
| 4 | `ara logout` | Remove saved auth token | No |
| 5 | `ara config set/get` | Change CLI settings | No |
| 6 | `ara list` | Show locally installed packages | No |
| 7 | `ara publish --dry-run` | Test packaging without uploading | No |
| 8 | `ara search` | Search for packages in the registry | Yes |
| 9 | `ara info` | View package details | Yes |
| 10 | `ara install` | Download and install a package | Yes |
| 11 | `ara uninstall` | Remove a locally installed package | No |
| 12 | `ara update` | Update packages to latest version | Yes |
| 13 | `ara publish` | Upload package to the registry | Yes |
| 14 | `ara unpublish` | Remove a version from the registry | Yes |

---

## User Flow: End-to-End Workflow

### Step 1: Developer Creates a Package

A developer has built an AI agent that reviews code. They want to share it.

**1.1 — Initialize the package:**

```bash
$ ara init

Package name (namespace/package-name): jeevan/code-reviewer
Version (1.0.0): 1.0.0
Description: AI agent that reviews code for bugs and security issues
Author email: jeevan@example.com
Tags (comma-separated): code-review,security,python
Type (kiro-agent): kiro-agent
License (SPDX, optional): MIT

✓ Created ara.json
```

This creates an `ara.json` file:

```json
{
  "$schema": "https://raw.githubusercontent.com/aws/ara/refs/heads/main/ara.schema.json",
  "name": "jeevan/code-reviewer",
  "version": "1.0.0",
  "description": "AI agent that reviews code for bugs and security issues",
  "author": "jeevan@example.com",
  "tags": ["code-review", "security", "python"],
  "type": "kiro-agent",
  "license": "MIT"
}
```

**1.2 — Validate the package:**

```bash
$ ara validate
✓ Valid ara.json
```

If there are errors:

```bash
$ ara validate
✗ Validation failed for ara.json
  • version must be a valid semantic version
  • tags must have at least 1 item
```

---

### Step 2: Developer Publishes the Package

**2.1 — Login to the registry:**

```bash
$ ara login --token my-auth-token
✓ Login successful. Token saved.
```

**2.2 — Test with dry run first:**

```bash
$ ara publish --dry-run
Publishing jeevan/code-reviewer@1.0.0
Archive: 523 bytes, sha256:a1b2c3d4...
✓ Dry run complete. Package is valid and archive was created.
```

**2.3 — Publish for real:**

```bash
$ ara publish
Publishing jeevan/code-reviewer@1.0.0
Archive: 523 bytes, sha256:a1b2c3d4...
Uploading... ━━━━━━━━━━━━━━━━━━━━ 100%
✓ Published jeevan/code-reviewer@1.0.0
```

The package is now live on the registry.

---

### Step 3: Another Developer Discovers and Installs It

**3.1 — Search for packages:**

```bash
$ ara search "code review"
┌──────────────────────────┬─────────┬──────────┬────────────────────────────────────┐
│ Package                  │ Version │ Type     │ Description                        │
├──────────────────────────┼─────────┼──────────┼────────────────────────────────────┤
│ jeevan/code-reviewer     │ 1.0.0   │ kiro-agent│ AI agent that reviews code for ... │
└──────────────────────────┴─────────┴──────────┴────────────────────────────────────┘
Page 1 — 1 total results
```

Search supports filters:

```bash
$ ara search "weather" --type mcp-server --tags api --sort downloads
```

**3.2 — View package details:**

```bash
$ ara info jeevan/code-reviewer
╭─────────────────── Package Info ────────────────────╮
│ jeevan/code-reviewer @ 1.0.0                        │
│                                                     │
│ AI agent that reviews code for bugs and security    │
│                                                     │
│ Type:       kiro-agent                              │
│ Author:     jeevan@example.com                      │
│ Tags:       code-review, security, python           │
│ License:    MIT                                     │
│                                                     │
│ Dependencies:                                       │
│   acme/security-rules: ^1.0.0                       │
╰─────────────────────────────────────────────────────╯
```

**3.3 — Install the package:**

```bash
$ ara install jeevan/code-reviewer
Installing jeevan/code-reviewer@1.0.0... ━━━━━━━━━━━━━━━ 100%
+ 1 transitive dependency(ies)
✓ Installed jeevan/code-reviewer@1.0.0
```

What happens behind the scenes:
1. Resolves all dependencies (including transitive ones)
2. Downloads package archive from registry
3. Verifies SHA-256 checksum
4. Extracts files to `.ara/packages/jeevan/code-reviewer/1.0.0/`
5. Updates `ara.lock` for reproducible installs

**3.4 — Install from lock file (for team consistency):**

```bash
$ ara install
Installing from lock file... ━━━━━━━━━━━━━━━ 100%
✓ Installed 3 package(s) from lock file.
```

When no package name is given, it installs everything from `ara.lock` — ensuring every team member gets the exact same versions.

---

### Step 4: Managing Installed Packages

**4.1 — List installed packages:**

```bash
$ ara list
┌──────────────────────────┬─────────┐
│ Package                  │ Version │
├──────────────────────────┼─────────┤
│ jeevan/code-reviewer     │ 1.0.0   │
│ acme/security-rules      │ 1.2.0   │
└──────────────────────────┴─────────┘
```

**4.2 — Update to latest compatible version:**

```bash
$ ara update jeevan/code-reviewer
Updated jeevan/code-reviewer: 1.0.0 → 1.1.0

$ ara update
✓ Updated 2 package(s).
```

**4.3 — Uninstall a package:**

```bash
$ ara uninstall jeevan/code-reviewer
✓ Uninstalled jeevan/code-reviewer
```

---

### Step 5: Unpublishing and Cleanup

**5.1 — Remove a version from the registry:**

```bash
$ ara unpublish jeevan/code-reviewer@1.0.0
Unpublish jeevan/code-reviewer@1.0.0? This cannot be undone. [y/N]: y
✓ Unpublished jeevan/code-reviewer@1.0.0
```

**5.2 — Logout:**

```bash
$ ara logout
✓ Logged out. Token removed.
```

---

### Step 6: Configuration

**6.1 — Change registry URL:**

```bash
$ ara config set registry_url https://registry.ara.dev
✓ Set registry_url = https://registry.ara.dev

$ ara config get registry_url
registry_url = https://registry.ara.dev
```

**6.2 — Use a different registry for one command:**

```bash
$ ara --registry https://staging.ara.dev search "test"
```

---

## Package Types Supported

| Type | What it contains | Example use case |
|---|---|---|
| `kiro-agent` | Prompts, configs for AI assistants | Code review bot, writing assistant |
| `mcp-server` | Tool plugins for AI (npm/pypi/git sources) | Weather API, database tools |
| `context` | Knowledge files, reference docs | Coding guidelines, API docs |
| `skill` | Step-by-step procedures (SKILL.md) | Git workflow, deployment steps |
| `kiro-powers` | MCP tools + steering + hooks bundle | Database management power |
| `kiro-steering` | Project-specific rules | React patterns, coding conventions |
| `agents-md` | Instructions for coding agents | Monorepo guide, repo rules |

---

## Project Architecture

```
cli/
├── pyproject.toml                    # Project config + dependencies
├── src/ara_cli/
│   ├── main.py                       # CLI entry point (all commands registered here)
│   ├── models/                       # Data models (Pydantic)
│   │   ├── manifest.py               # ara.json model with validation
│   │   ├── lockfile.py               # ara.lock model
│   │   ├── config.py                 # CLI config model
│   │   └── api_responses.py          # Registry API response models
│   ├── core/                         # Business logic
│   │   ├── validation.py             # Manifest validation
│   │   ├── registry_client.py        # Async HTTP client for registry API
│   │   ├── resolver.py               # Dependency resolution + cycle detection
│   │   ├── installer.py              # Download, verify, extract packages
│   │   ├── packager.py               # Create .tgz archives for publishing
│   │   ├── lockfile_manager.py       # Read/write ara.lock (atomic writes)
│   │   ├── config_manager.py         # Read/write ~/.ara/config.json
│   │   └── security.py              # SHA-256 checksums, git URL validation
│   ├── commands/                     # One file per CLI command
│   │   ├── init.py                   # ara init
│   │   ├── validate.py               # ara validate
│   │   ├── search.py                 # ara search
│   │   ├── info.py                   # ara info
│   │   ├── install.py                # ara install
│   │   ├── uninstall.py              # ara uninstall
│   │   ├── update.py                 # ara update
│   │   ├── list_cmd.py               # ara list
│   │   ├── publish.py                # ara publish
│   │   ├── unpublish.py              # ara unpublish
│   │   ├── login.py                  # ara login
│   │   ├── logout.py                 # ara logout
│   │   └── config.py                 # ara config set/get
│   ├── output/                       # Terminal output formatting
│   │   ├── console.py                # Rich console + themed helpers
│   │   ├── tables.py                 # Table formatters for search, list, info
│   │   └── prompts.py                # Interactive prompts for init wizard
│   └── utils/                        # Shared utilities
│       ├── constants.py              # Default URLs, file names, excludes
│       ├── errors.py                 # Custom exception hierarchy
│       └── semver.py                 # Version constraint matching (^, ~, >=, *)
└── tests/                            # 75 tests, all passing
    ├── test_models.py
    ├── test_validation.py
    ├── test_semver.py
    ├── test_security.py
    ├── test_lockfile.py
    ├── test_resolver.py
    └── test_commands/
        ├── test_validate.py
        ├── test_config.py
        ├── test_login_logout.py
        ├── test_init.py
        └── test_list.py
```

---

## Key Features

### 1. Dependency Resolution
When you install a package that depends on other packages, the CLI automatically resolves and installs the entire dependency tree in the correct order. It also detects circular dependencies and reports them.

### 2. Lock File Support (ara.lock)
Records exact versions and checksums of installed packages. Ensures every team member gets identical installations. Updated automatically on install/update/uninstall.

### 3. Checksum Verification
Every downloaded package is verified using SHA-256 checksums before installation. Prevents tampered or corrupted packages from being installed.

### 4. Async Registry Client
Uses httpx for async HTTP communication with the registry. Supports streaming uploads for large packages via signed S3 URLs.

### 5. Friendly Error Handling
All errors are displayed with clear, helpful messages instead of raw stack traces. Connection errors suggest checking if the server is running.

---

## How to Install and Run

```bash
# Navigate to the CLI directory
cd cli

# Install in development mode
pip install -e ".[dev]"

# Run any command
ara --help
ara init
ara validate
ara login --token <your-token>
ara publish --dry-run
```

## How to Run Tests

```bash
cd cli
pytest tests/ -v
```

**Result: 75 tests, all passing.**

---

## What's Needed Next

| Component | Status | Notes |
|---|---|---|
| CLI tool | **Done** | 13 commands, 75 tests |
| Registry server | Not built | Backend API at localhost:3000 |
| Web UI (optional) | Not built | Browser-based package browsing |

The CLI is fully functional. Commands that interact with the registry (search, install, publish, etc.) require a running ARA registry server.

---

## Summary

| Metric | Value |
|---|---|
| Total commands | 13 |
| Source files | 55 |
| Lines of code | 2,698 |
| Tests | 75 (all passing) |
| Branch | `feature/ara-cli` |
| Offline commands | 7 (init, validate, login, logout, config, list, publish --dry-run) |
| Registry commands | 7 (search, info, install, update, publish, unpublish, uninstall) |
