"""API router for asset uploads, downloads, and deletion via S3."""

from typing import Literal

from fastapi import APIRouter, HTTPException, UploadFile

from ..services.asset_storage import (
    AssetCategory,
    delete_asset,
    get_asset_url,
    upload_asset,
)

router = APIRouter(prefix="/assets", tags=["assets"])


@router.post("/upload")
async def upload_file(
    file: UploadFile,
    category: Literal["audio", "icons", "avatars"] = "icons",
) -> dict[str, str]:
    """Upload a file (audio prompt, icon, or avatar) to S3.

    - **file**: The file to upload.
    - **category**: Asset category — ``audio``, ``icons``, or ``avatars``.

    Returns the S3 object key for later retrieval or deletion.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required.")

    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    try:
        key = upload_asset(
            file_bytes=contents,
            filename=file.filename,
            content_type=file.content_type or "application/octet-stream",
            category=category,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Upload failed: {exc}") from exc

    return {"key": key, "message": "Asset uploaded successfully."}


@router.get("/{key:path}")
async def get_file_url(key: str) -> dict[str, str]:
    """Get a presigned download URL for an asset.

    - **key**: The S3 object key (e.g. ``icons/abc123_task.png``).
    """
    try:
        url = get_asset_url(key)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Asset not found.")
    except Exception as exc:
        raise HTTPException(
            status_code=500, detail=f"Failed to generate URL: {exc}"
        ) from exc

    return {"url": url}


@router.delete("/{key:path}")
async def delete_file(key: str) -> dict[str, str]:
    """Delete an asset from S3.

    - **key**: The S3 object key to delete.
    """
    try:
        delete_asset(key)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Asset not found.")
    except Exception as exc:
        raise HTTPException(
            status_code=500, detail=f"Delete failed: {exc}"
        ) from exc

    return {"message": "Asset deleted successfully."}
