"""Minimal API schemas."""

from pydantic import BaseModel, field_validator


class AskRequest(BaseModel):
    question: str

    @field_validator("question")
    @classmethod
    def question_not_blank(cls, value: str) -> str:
        cleaned = (value or "").strip()
        if not cleaned:
            raise ValueError("question must not be empty")
        return cleaned


class SourceItem(BaseModel):
    page: int | None = None
    chunk_id: str | None = None
    snippet: str = ""


class AskResponse(BaseModel):
    answer: str
    sources: list[SourceItem]
