from typing import Any


def create_minio_client(
    endpoint: str,
    access_key: str,
    secret_key: str,
    *,
    secure: bool = True,
) -> Any:
    """Create a MinIO client for artifact repository adapters."""
    from minio import Minio

    return Minio(
        endpoint,
        access_key=access_key,
        secret_key=secret_key,
        secure=secure,
    )

