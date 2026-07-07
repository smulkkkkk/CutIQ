from pathlib import Path
from app.core.supabase import get_supabase
from app.core.config import settings


def _bucket():
    return get_supabase().storage.from_(settings.storage_bucket)


def generate_presigned_upload_url(key: str) -> str:
    result = _bucket().create_signed_upload_url(key)
    return result.signed_url if hasattr(result, "signed_url") else result["signedURL"]


def generate_presigned_download_url(key: str, expires_in: int = 3600) -> str:
    result = _bucket().create_signed_url(key, expires_in)
    return result.signed_url if hasattr(result, "signed_url") else result["signedURL"]


def download_to_path(key: str, local_path: str) -> None:
    data = _bucket().download(key)
    Path(local_path).write_bytes(data)


def upload_from_path(local_path: str, key: str, content_type: str = "video/mp4") -> None:
    content = Path(local_path).read_bytes()
    _bucket().upload(key, content, {"content-type": content_type})


def delete_object(key: str) -> None:
    _bucket().remove([key])
