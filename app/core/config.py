from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
   app_name: str = "Production RAG Backend"
   app_version: str = "1.0.0"
   environment: str = "development"
   debug: bool = True

   host : str = "0.0.0.0"
   port : int = 8000

   document_dir: str = "Document"

   model_config = SettingsConfigDict(
      env_file=".env",
      env_file_encoding="utf-8",
      case_sensitive=False,
      extra="ignore"
      )

@lru_cache()
def get_settings() -> Settings:
    return Settings()