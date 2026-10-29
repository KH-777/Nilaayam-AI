import os
import uuid
import hashlib
from pathlib import Path
from typing import Optional, Tuple
from backend.config import settings
from backend.database import get_supabase
import logging

logger = logging.getLogger(__name__)

class StorageService:
    def __init__(self):
        self.bucket = settings.supabase_storage_bucket
    
    async def upload_document(self, file_content: bytes, filename: str, user_id: str) -> Tuple[str, str]:
        """Upload file to Supabase Storage. Returns (storage_path, file_hash)."""
        # compute hash
        file_hash = hashlib.sha256(file_content).hexdigest()
        # unique storage path
        ext = Path(filename).suffix.lower()
        storage_path = f"documents/{user_id}/{uuid.uuid4()}{ext}"
        
        client = get_supabase()
        if client is None:
            # demo mode: save locally
            local_dir = Path("demo_uploads")
            local_dir.mkdir(exist_ok=True)
            local_path = local_dir / Path(storage_path).name
            local_path.write_bytes(file_content)
            return str(local_path), file_hash
        
        try:
            client.storage.from_(self.bucket).upload(
                storage_path,
                file_content,
                file_options={"content-type": self._get_content_type(ext)}
            )
            return storage_path, file_hash
        except Exception as e:
            logger.error(f"Storage upload failed: {e}")
            raise
    
    async def download_document(self, storage_path: str) -> bytes:
        """Download file from Supabase Storage."""
        client = get_supabase()
        if client is None:
            # demo mode: read locally
            if os.path.exists(storage_path):
                return Path(storage_path).read_bytes()
            raise FileNotFoundError(f"Demo file not found: {storage_path}")
        
        try:
            data = client.storage.from_(self.bucket).download(storage_path)
            return data
        except Exception as e:
            logger.error(f"Storage download failed: {e}")
            raise
    
    async def delete_document(self, storage_path: str) -> bool:
        """Delete file from Supabase Storage."""
        client = get_supabase()
        if client is None:
            if os.path.exists(storage_path):
                os.remove(storage_path)
            return True
        try:
            client.storage.from_(self.bucket).remove([storage_path])
            return True
        except Exception as e:
            logger.error(f"Storage delete failed: {e}")
            return False
    
    def get_signed_url(self, storage_path: str, expires_in: int = 3600) -> Optional[str]:
        """Generate a signed URL for temporary access."""
        client = get_supabase()
        if client is None:
            return None
        try:
            result = client.storage.from_(self.bucket).create_signed_url(storage_path, expires_in)
            return result.get("signedURL")
        except Exception as e:
            logger.error(f"Signed URL generation failed: {e}")
            return None
    
    def _get_content_type(self, ext: str) -> str:
        types = {
            ".pdf": "application/pdf",
            ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".tiff": "image/tiff",
        }
        return types.get(ext, "application/octet-stream")

storage_service = StorageService()
