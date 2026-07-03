import boto3
from botocore.config import Config
from app.core.config import settings

def _get_r2_client():
    return boto3.client(
        "s3",
        endpoint_url=settings.cloudflare_r2_endpoint,
        aws_access_key_id=settings.cloudflare_r2_access_key,
        aws_secret_access_key=settings.cloudflare_r2_secret_key,
        config=Config(signature_version="s3v4"),
    )

def generate_presigned_upload_url(
    key: str, content_type: str = "video/mp4", expires_in: int = 3600
) -> str:
    client = _get_r2_client()
    return client.generate_presigned_url(
        "put_object",
        Params={"Bucket": settings.cloudflare_r2_bucket, "Key": key, "ContentType": content_type},
        ExpiresIn=expires_in,
    )

def generate_presigned_download_url(key: str, expires_in: int = 3600) -> str:
    client = _get_r2_client()
    return client.generate_presigned_url(
        "get_object",
        Params={"Bucket": settings.cloudflare_r2_bucket, "Key": key},
        ExpiresIn=expires_in,
    )

def download_to_path(key: str, local_path: str) -> None:
    client = _get_r2_client()
    client.download_file(settings.cloudflare_r2_bucket, key, local_path)

def upload_from_path(local_path: str, key: str, content_type: str = "video/mp4") -> None:
    client = _get_r2_client()
    client.upload_file(local_path, settings.cloudflare_r2_bucket, key, ExtraArgs={"ContentType": content_type})

def delete_object(key: str) -> None:
    client = _get_r2_client()
    client.delete_object(Bucket=settings.cloudflare_r2_bucket, Key=key)
