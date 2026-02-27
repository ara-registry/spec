"""API response models matching the registry-api.md spec."""

from typing import Optional
from pydantic import BaseModel, Field


class PackageListItem(BaseModel):
    namespace: str
    name: str
    description: str
    type: str
    latest_version: str
    tags: list[str]
    total_downloads: int = 0
    created_at: str
    updated_at: str


class PackageListResponse(BaseModel):
    packages: list[PackageListItem]
    total: int
    page: int
    per_page: int
    has_next: bool
    has_prev: bool


class VersionListResponse(BaseModel):
    namespace: str
    name: str
    versions: list[str]
    latest: str


class DownloadResponse(BaseModel):
    download_url: str
    expires_at: str
    size_bytes: int
    checksum: str


class UploadInitResponse(BaseModel):
    package_upload_url: str
    manifest_upload_url: str
    upload_id: str
    expires_at: str
    max_size_bytes: int
    completion_url: str


class UploadCompleteResponse(BaseModel):
    namespace: str
    name: str
    version: str
    published_at: str
    size_bytes: int
    message: str


class ErrorResponse(BaseModel):
    detail: str
