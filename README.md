# AI Registry for Agents (ARA)

ARA (pronounced: _ah-rah_) is a package registry and distribution system for AI development artifacts. It provides a standardized way to discover, share, and install reusable components that enhance AI assistants and development workflows.

ARA is a vendor-agnostic open standard — any AI coding tool can implement it, including Kiro, Claude Code, Cursor, VS Code Copilot, Windsurf, and others.

## Package Types

ARA supports the following package types:

| Type | Description |
|------|-------------|
| `agent` | AI assistant configurations with prompts, tools, and behaviors |
| `mcp-server` | Model Context Protocol servers that extend AI capabilities |
| `powers` | Bundles of MCP tools, steering files, and hooks |
| `steering` | Persistent project knowledge files that guide agent behavior |
| `skill` | Procedural knowledge via SKILL.md |
| `context` | Knowledge files, prompt templates, and reference materials |
| `agents-md` | AGENTS.md format for guiding coding agents |

Use the optional `platform` field to declare tool-specific installation targets (e.g., `"platform": "kiro"`).

## Quick Links

- [Vision](vision.md) - Understand the project goals and tenets
- [ara.json Spec](ara-json.md) - Package manifest format
- [JSON Schema](ara.schema.json) - Validate your ara.json
- [Registry API](registry-api.md) - HTTP API specification for registry implementations
- [Security](security.md) - Security guidance for implementers

## Example ara.json

```json
{
  "$schema": "https://raw.githubusercontent.com/ara-registry/spec/refs/heads/main/ara.schema.json",
  "specVersion": "1.0",
  "name": "acme/code-reviewer",
  "version": "1.0.0",
  "description": "AI agent for automated code review",
  "author": "developer@example.com",
  "tags": ["code-review", "automation"],
  "type": "agent"
}
```

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This project is licensed under the Apache-2.0 License.
