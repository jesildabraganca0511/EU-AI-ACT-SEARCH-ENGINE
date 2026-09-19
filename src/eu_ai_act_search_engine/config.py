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
    

