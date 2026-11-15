from datetime import datetime, timezone
from typing import Any, Generic, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    success: bool = Field(description="처리 성공/실패 여부")
    code: str | None = Field(
        None, description="비즈니스 식별 코드 (성공 시 OK, 실패 시 에러 코드)"
    )
    message: str | None = Field(None, description="성공 또는 실패시 설명")
    errors: dict[str, list[str]] | list[str] | Any | None = Field(
        None, description="실패 시 세부 오류 내용"
    )
    data: T | None = Field(None, description="성공시 응답 데이터")
    responded_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="응답 날짜시간(UTC)",
    )

    @classmethod
    def ok(
        cls,
        data: T | None = None,
        message: str = "요청이 성공적으로 처리되었습니다.",
        code: str = "OK",
    ) -> "APIResponse[T]":
        return cls(
            success=True,
            code=code,
            message=message,
            errors=None,
            data=data,
        )

    @classmethod
    def fail(
        cls,
        message: str,
        code: str = "BAD_REQUEST",
        errors: dict[str, list[str]] | list[str] | Any | None = None,
    ) -> "APIResponse[None]":
        return cls(
            success=False,
            code=code,
            message=message,
            errors=errors,
            data=None,
        )
