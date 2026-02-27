"""Lock file models for reproducible installations."""

from typing import Optional
from pydantic import BaseModel, Field


class LockfileEntry(BaseModel):
    version: str
    type: str
    integrity: str
    resolved: str
    dependencies: dict[str, str] = Field(default_factory=dict)


class ARALockfile(BaseModel):
    lockfile_version: int = Field(default=1, alias="lockfileVersion")
    generated_at: str = Field(alias="generatedAt")
    packages: dict[str, LockfileEntry] = Field(default_factory=dict)

    model_config = {"populate_by_name": True}
