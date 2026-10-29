from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # Supabase
    supabase_url: str = ""
    supabase_anon_key: str = ""
    supabase_service_role_key: str = ""
    supabase_storage_bucket: str = "nilaayam-documents"
    
    # LLM
    gemini_api_key: str = ""
    llm_model: str = "gemini-1.5-flash"
    embedding_model: str = "models/text-embedding-004"
    
    # App
    app_env: str = "development"
    max_upload_size_mb: int = 20
    allowed_extensions: list = [".pdf", ".docx", ".png", ".jpg", ".jpeg", ".tiff"]
    
    # OCR
    tesseract_cmd: str = "tesseract"
    ocr_languages: str = "tam+eng"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
