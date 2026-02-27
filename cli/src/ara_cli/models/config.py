"""CLI configuration model."""

from typing import Optional
from pydantic import BaseModel, Field

from ..utils.constants import DEFAULT_REGISTRY_URL, TRUSTED_GIT_DOMAINS


class CLIConfig(BaseModel):
    registry_url: str = DEFAULT_REGISTRY_URL
    auth_token: Optional[str] = None
    default_author: Optional[str] = None
    trusted_git_domains: list[str] = Field(default_factory=lambda: list(TRUSTED_GIT_DOMAINS))
