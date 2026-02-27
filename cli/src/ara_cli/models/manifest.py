"""ARA manifest model — enhanced from reference lib."""

import json
import re
from enum import Enum
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field, EmailStr, AnyUrl, field_validator, model_validator

SEMVER_PATTERN = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)"
    r"(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?"
    r"(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$"
)

TAG_PATTERN = re.compile(r"^[a-zA-Z0-9_-]+$")
NAME_PATTERN = re.compile(r"^[a-zA-Z0-9_-]+/[a-zA-Z0-9_-]+$")


class PackageType(str, Enum):
    KIRO_AGENT = "kiro-agent"
    MCP_SERVER = "mcp-server"
    CONTEXT = "context"
    SKILL = "skill"
    KIRO_POWERS = "kiro-powers"
    KIRO_STEERING = "kiro-steering"
    AGENTS_MD = "agents-md"


class SourceType(str, Enum):
    NPM = "npm"
    PYPI = "pypi"
    GIT = "git"
    MCP_REGISTRY = "mcp-registry"


class PackageSource(BaseModel):
    type: SourceType
    package: Optional[str] = None
    version: Optional[str] = None
    registry: Optional[AnyUrl] = None
    repository: Optional[AnyUrl] = None
    ref: Optional[str] = None
    subfolder: Optional[str] = None
    install_command: Optional[str] = Field(None, alias="installCommand")
    executable: Optional[str] = None
    preferred: Optional[bool] = None

    model_config = {"populate_by_name": True}

    @model_validator(mode="after")
    def validate_conditional_fields(self):
        if self.type in (SourceType.NPM, SourceType.PYPI, SourceType.MCP_REGISTRY):
            if self.package is None:
                raise ValueError(f"'package' is required for {self.type.value} source type")
        elif self.type == SourceType.GIT:
            if self.repository is None:
                raise ValueError("'repository' is required for git source type")
        return self


class ARAManifest(BaseModel):
    schema_url: Optional[str] = Field(None, alias="$schema")
    name: str = Field(..., pattern=r"^[a-zA-Z0-9_-]+/[a-zA-Z0-9_-]+$", min_length=3, max_length=200)
    version: str
    description: str = Field(..., min_length=1, max_length=500)
    author: EmailStr
    tags: list[str] = Field(..., min_length=1)
    type: PackageType = PackageType.KIRO_AGENT
    files: Optional[list[str]] = None
    license: Optional[str] = Field(None, max_length=100)
    homepage: Optional[AnyUrl] = None
    repository: Optional[AnyUrl] = None
    dependencies: Optional[dict[str, str]] = None
    sources: Optional[list[PackageSource]] = None

    model_config = {"populate_by_name": True}

    @field_validator("version")
    @classmethod
    def validate_version(cls, v: str) -> str:
        if not SEMVER_PATTERN.match(v):
            raise ValueError(f"version must be a valid semantic version (e.g., '1.0.0'), got: {v}")
        return v

    @field_validator("sources")
    @classmethod
    def sources_only_for_mcp_server(cls, v, info):
        if v is not None and info.data.get("type") != PackageType.MCP_SERVER:
            raise ValueError("sources field is only allowed for mcp-server type")
        return v

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v: list[str]) -> list[str]:
        for tag in v:
            if not tag or len(tag) > 50:
                raise ValueError(f"Invalid tag length: '{tag}' (must be 1-50 characters)")
            if not TAG_PATTERN.match(tag):
                raise ValueError(f"Invalid tag format: '{tag}' (must match ^[a-zA-Z0-9_-]+$)")
        return v

    @field_validator("files")
    @classmethod
    def validate_files(cls, v: list[str] | None) -> list[str] | None:
        if v is None:
            return v
        for f in v:
            if ".." in f or f.startswith("/"):
                raise ValueError(f"Invalid file path: '{f}' (no absolute paths or '..' traversal)")
        return v

    def parse_name(self) -> tuple[str, str]:
        """Return (namespace, package_name) from the name field."""
        namespace, package_name = self.name.split("/", 1)
        return namespace, package_name

    def to_file(self, path: Path) -> None:
        """Write manifest to an ara.json file."""
        data = self.model_dump(by_alias=True, exclude_none=True)
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
            f.write("\n")
