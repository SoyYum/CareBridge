
from pydantic import BaseModel, EmailStr, Field, field_validator


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=10, max_length=128)

    @field_validator("password")
    @classmethod
    def validate_password_bytes(cls, value: str) -> str:
        if len(value.encode("utf-8")) > 72:
            raise ValueError(
                "Password must not exceed 72 bytes when encoded in UTF-8."
            )
        return value


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class ChatRequest(BaseModel):
    session_id: int | None = None
    question: str = Field(min_length=2, max_length=4000)
    language: str = "auto"


class SourceItem(BaseModel):
    document: str
    page: int
    excerpt: str
    score: float | None = None


class ChatResponse(BaseModel):
    session_id: int
    answer: str
    sources: list[SourceItem]
    safety_notice: str
