"""S3 asset storage service for audio prompts, task icons, and avatars."""

import uuid
from typing import Literal

import boto3
from botocore.exceptions import ClientError

from ..config import settings

AssetCategory = Literal["audio", "icons", "avatars"]

# Prefix mapping for S3 object organization
CATEGORY_PREFIXES: dict[AssetCategory, str] = {
    "audio": "audio/",   # Zelda mode voice prompts
    "icons": "icons/",   # Task icons
    "avatars": "avatars/",  # Family member avatars
}

PRESIGNED_URL_EXPIRY_SECONDS = 3600  # 1 hour


def _get_s3_client() -> boto3.client:
    """Create an S3 client using settings or IAM role (on EC2)."""
    kwargs: dict = {"region_name": settings.aws_s3_region}
    if settings.aws_access_key_id and settings.aws_secret_access_key:
        kwargs["aws_access_key_id"] = settings.aws_access_key_id
        kwargs["aws_secret_access_key"] = settings.aws_secret_access_key
    return boto3.client("s3", **kwargs)


def _build_key(filename: str, category: AssetCategory) -> str:
    """Build a unique S3 object key with the appropriate prefix."""
    prefix = CATEGORY_PREFIXES[category]
    unique_name = f"{uuid.uuid4().hex}_{filename}"
    return f"{prefix}{unique_name}"


def upload_asset(
    file_bytes: bytes,
    filename: str,
    content_type: str,
    category: AssetCategory = "icons",
) -> str:
    """Upload a file to S3 and return the object key.

    Args:
        file_bytes: Raw file content.
        filename: Original filename (used for key generation).
        content_type: MIME type (e.g. ``image/png``, ``audio/mpeg``).
        category: One of ``audio``, ``icons``, or ``avatars``.

    Returns:
        The S3 object key for the uploaded asset.
    """
    s3 = _get_s3_client()
    key = _build_key(filename, category)

    s3.put_object(
        Bucket=settings.aws_s3_bucket,
        Key=key,
        Body=file_bytes,
        ContentType=content_type,
    )
    return key


def get_asset_url(key: str) -> str:
    """Generate a presigned URL to download an asset.

    Args:
        key: The S3 object key.

    Returns:
        A time-limited presigned download URL.

    Raises:
        FileNotFoundError: If the object does not exist.
    """
    s3 = _get_s3_client()

    # Verify the object exists
    try:
        s3.head_object(Bucket=settings.aws_s3_bucket, Key=key)
    except ClientError as exc:
        if exc.response["Error"]["Code"] == "404":
            raise FileNotFoundError(f"Asset not found: {key}") from exc
        raise

    presigned_url: str = s3.generate_presigned_url(
        "get_object",
        Params={"Bucket": settings.aws_s3_bucket, "Key": key},
        ExpiresIn=PRESIGNED_URL_EXPIRY_SECONDS,
    )
    return presigned_url


def delete_asset(key: str) -> None:
    """Delete an asset from S3.

    Args:
        key: The S3 object key to delete.

    Raises:
        FileNotFoundError: If the object does not exist.
    """
    s3 = _get_s3_client()

    # Verify the object exists before deleting
    try:
        s3.head_object(Bucket=settings.aws_s3_bucket, Key=key)
    except ClientError as exc:
        if exc.response["Error"]["Code"] == "404":
            raise FileNotFoundError(f"Asset not found: {key}") from exc
        raise

    s3.delete_object(Bucket=settings.aws_s3_bucket, Key=key)
