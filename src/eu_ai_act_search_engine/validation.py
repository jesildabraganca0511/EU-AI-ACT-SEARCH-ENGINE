from pydantic import BaseModel, Field, ValidationError,ConfigDict, field_validator

class Article(BaseModel):
    model_config=ConfigDict(
        extra="forbid")

    article_number: str = Field(..., min_length=1, max_length=20)
    article_title: str = Field(..., min_length=1, max_length=200)
    text: str = Field(..., min_length=1)

    @field_validator("article_number", "article_title", "text")
    @classmethod
    def must_not_be_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError(f"{cls.__name__}: {value} must not be blank")
        return value


class Chunk(BaseModel):
    model_config=ConfigDict(
        extra="forbid")

    text: str = Field(..., min_length=1)
    article_number: str = Field(..., min_length=1, max_length=20)
    article_title: str = Field(..., min_length=1, max_length=200)
    chunk_index: int = Field(..., ge=0)
    total_chunks_in_article: int = Field(..., ge=1)

    @field_validator("text", "article_number", "article_title")
    @classmethod
    def must_not_be_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError(f"{cls.__name__}: {value} must not be blank")
        return value


class SearchQuery(BaseModel):
    model_config=ConfigDict(
        extra="forbid")

    query: str = Field(..., min_length=1, max_length=2000)
    top_k: int = Field(..., ge=1, le=50)

    @field_validator("query")
    @classmethod
    def must_not_be_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError(f"{cls.__name__}: {value} must not be blank")
        return value