from fastapi.exceptions import RequestValidationError
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from shared.core.exceptions import (
    BadRequestException,
    ConflictException,
    ForbiddenException,
    NotFoundException,
    UnauthorizedException,
    ValidationException,
)
from shared.core.schemas import APIResponse


EXCEPTION_STATUS_CODES = {
    ValidationException: 400,
    BadRequestException: 400,
    UnauthorizedException: 401,
    ForbiddenException: 403,
    NotFoundException: 404,
    ConflictException: 409,
}
HANDLED_EXCEPTIONS = tuple(EXCEPTION_STATUS_CODES)


class ExceptionHandlerMiddleware:
    """공통 비즈니스 예외를 HTTP 상태 코드와 APIResponse로 변환합니다."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        response_started = False

        async def track_response(message: Message) -> None:
            nonlocal response_started
            if message["type"] == "http.response.start":
                response_started = True
            await send(message)

        try:
            await self.app(scope, receive, track_response)
        except HANDLED_EXCEPTIONS as exc:
            # 이미 전송한 응답은 교체할 수 없으므로 원래 오류를 전달합니다.
            if response_started:
                raise

            status_code = next(
                code
                for exception_type, code in EXCEPTION_STATUS_CODES.items()
                if isinstance(exc, exception_type)
            )
            payload = APIResponse.fail(
                message=exc.message,
                code=exc.error_code,
                errors=getattr(exc, "field_errors", None),
            )
            headers = {"WWW-Authenticate": "Bearer"} if status_code == 401 else None
            response = JSONResponse(
                status_code=status_code,
                content=payload.model_dump(mode="json"),
                headers=headers,
            )
            await response(scope, receive, send)


async def request_validation_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """422 응답에서 비밀번호를 포함할 수 있는 입력 원문과 컨텍스트를 제외합니다."""
    errors = [
        {"loc": error["loc"], "msg": error["msg"], "type": error["type"]}
        for error in exc.errors()
    ]
    return JSONResponse(status_code=422, content={"detail": errors})
