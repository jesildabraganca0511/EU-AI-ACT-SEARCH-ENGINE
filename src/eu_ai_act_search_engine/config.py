from pathlib import Path
from typing import Literal

from pydantic import Field,SecretStr,field_validator
from pydantic_settings import BaseSettings,SettingsConfigDict

PROJECT_ROOT=Path(__file__).resolve().parents[2]

class Settings(BaseSettings):
    model_config=SettingsConfigDict(

        env_file=".env",
        env_file_encoding="utf-8",  
        extra="ignore",
        case_sensitive=False,
    )

    environment:Literal["development","test","production"]="development"
    gemini_api_key:SecretStr=Field(min_length=1)
    gemini_model:Literal["gemini-3.6-flash","gemini-2.0-flash"]="gemini-3.6-flash"

    embedding_model_name:str="all-MiniLM-L6-v2"

    chroma_path:Path=PROJECT_ROOT / "src" / "eu_ai_act_search_engine" / "results" / "chroma_db"

    collection_name:str="eu_ai_act_articles"

    top_k: int = Field(default=5, ge=1, le=50)
    max_query_length: int = Field(default=2_000, ge=1)
    max_prompt_characters: int = Field(default=30_000, ge=1)
    request_timeout_seconds: float = Field(default=30.0, gt=0)
    embedding_batch_size: int = Field(default=32, ge=1)

    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"

    @field_validator(
        "gemini_model",
        "embedding_model_name",
        "collection_name",
    )

    @classmethod
    def must_not_be_blank(cls, value:str)-> str:
        value=value.strip()
        if not value:
            raise ValueError(f"{cls.__name__}: {value} must not be blank") 
        return value

    

