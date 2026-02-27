"""Async httpx client for all ARA registry API endpoints."""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any

import httpx

from ..models.api_responses import (
    DownloadResponse,
    PackageListResponse,
    UploadCompleteResponse,
    UploadInitResponse,
    VersionListResponse,
)
from ..models.manifest import ARAManifest
from ..utils.errors import (
    ARAAuthError,
    ARAConflictError,
    ARANotFoundError,
    ARARegistryError,
)


class RegistryClient:
    """Async client for the ARA registry HTTP API."""

    def __init__(self, registry_url: str, token: str | None = None):
        self.registry_url = registry_url.rstrip("/")
        self.token = token

    def _headers(self, auth: bool = False) -> dict[str, str]:
        headers: dict[str, str] = {"Content-Type": "application/json"}
        if auth and self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def _parse_detail(self, resp: httpx.Response, fallback: str) -> str:
        try:
            return resp.json().get("detail", fallback)
        except Exception:
            return fallback

    def _handle_error(self, resp: httpx.Response) -> None:
        if resp.status_code == 401:
            raise ARAAuthError("Authentication required. Run 'ara login' first.")
        if resp.status_code == 403:
            raise ARAAuthError(self._parse_detail(resp, "Permission denied"))
        if resp.status_code == 404:
            raise ARANotFoundError(self._parse_detail(resp, "Not found"))
        if resp.status_code == 409:
            raise ARAConflictError(self._parse_detail(resp, "Conflict"))
        if resp.status_code >= 400:
            raise ARARegistryError(
                self._parse_detail(resp, f"Request failed with status {resp.status_code}"),
                status_code=resp.status_code,
            )

    async def search_packages(
        self,
        query: str = "",
        tags: str = "",
        package_type: str = "",
        sort: str = "",
        page: int = 1,
        per_page: int = 20,
    ) -> PackageListResponse:
        params: dict[str, Any] = {"page": page, "per_page": per_page}
        if query:
            params["q"] = query
        if tags:
            params["tags"] = tags
        if package_type:
            params["type"] = package_type
        if sort:
            params["sort"] = sort

        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.registry_url}/packages",
                params=params,
                headers=self._headers(),
            )
        self._handle_error(resp)
        return PackageListResponse(**resp.json())

    async def list_versions(self, namespace: str, name: str) -> VersionListResponse:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.registry_url}/packages/{namespace}/{name}/versions",
                headers=self._headers(),
            )
        self._handle_error(resp)
        return VersionListResponse(**resp.json())

    async def get_manifest(self, namespace: str, name: str, version: str) -> dict:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.registry_url}/packages/{namespace}/{name}/{version}/ara.json",
                headers=self._headers(),
            )
        self._handle_error(resp)
        return resp.json()

    async def get_download_url(self, namespace: str, name: str, version: str) -> DownloadResponse:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.registry_url}/packages/{namespace}/{name}/{version}/download",
                headers=self._headers(),
            )
        self._handle_error(resp)
        return DownloadResponse(**resp.json())

    async def initiate_upload(
        self, namespace: str, name: str, version: str, manifest: dict, package_size: int
    ) -> UploadInitResponse:
        async with httpx.AsyncClient() as client:
            resp = await client.put(
                f"{self.registry_url}/packages/{namespace}/{name}/{version}",
                params={"package_size": package_size},
                json=manifest,
                headers=self._headers(auth=True),
            )
        self._handle_error(resp)
        return UploadInitResponse(**resp.json())

    async def upload_file(self, upload_url: str, file_path: Path) -> None:
        async with httpx.AsyncClient() as client:
            with open(file_path, "rb") as f:
                resp = await client.put(
                    upload_url,
                    content=f,
                    headers={"Content-Type": "application/gzip"},
                    timeout=300.0,
                )
        if resp.status_code >= 400:
            raise ARARegistryError(f"Upload failed: {resp.status_code}", status_code=resp.status_code)

    async def upload_manifest(self, upload_url: str, manifest_data: bytes) -> None:
        async with httpx.AsyncClient() as client:
            resp = await client.put(
                upload_url,
                content=manifest_data,
                headers={"Content-Type": "application/json"},
                timeout=60.0,
            )
        if resp.status_code >= 400:
            raise ARARegistryError(f"Manifest upload failed: {resp.status_code}", status_code=resp.status_code)

    async def complete_upload(
        self, namespace: str, name: str, version: str, upload_id: str
    ) -> UploadCompleteResponse:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.registry_url}/packages/{namespace}/{name}/{version}/complete-upload",
                json={"upload_id": upload_id},
                headers=self._headers(auth=True),
            )
        self._handle_error(resp)
        return UploadCompleteResponse(**resp.json())

    async def unpublish(self, namespace: str, name: str, version: str) -> dict:
        async with httpx.AsyncClient() as client:
            resp = await client.delete(
                f"{self.registry_url}/packages/{namespace}/{name}/{version}",
                headers=self._headers(auth=True),
            )
        self._handle_error(resp)
        return resp.json()

    async def download_file(self, url: str, dest: Path) -> None:
        async with httpx.AsyncClient() as client:
            async with client.stream("GET", url, timeout=300.0) as resp:
                if resp.status_code >= 400:
                    raise ARARegistryError(f"Download failed: {resp.status_code}", status_code=resp.status_code)
                dest.parent.mkdir(parents=True, exist_ok=True)
                with open(dest, "wb") as f:
                    async for chunk in resp.aiter_bytes(chunk_size=8192):
                        f.write(chunk)


def run_async(coro):
    """Bridge for calling async registry methods from sync Click commands."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as pool:
            return pool.submit(asyncio.run, coro).result()
    return asyncio.run(coro)
