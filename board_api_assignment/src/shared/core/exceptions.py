class ValidationException(Exception):
    def __init__(
        self,
        message: str,
        error_code: str = "VALIDATION_ERROR",
        field_errors: dict | None = None,
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.field_errors = field_errors


class BadRequestException(Exception):
    def __init__(
        self,
        message: str,
        error_code: str = "BAD_REQUEST",
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code


class ForbiddenException(Exception):
    def __init__(
        self,
        message: str,
        error_code: str = "FORBIDDEN",
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code


class UnauthorizedException(Exception):
    def __init__(
        self,
        message: str,
        error_code: str = "UNAUTHORIZED",
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code


class ConflictException(Exception):
    def __init__(
        self,
        message: str,
        error_code: str = "CONFLICT",
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code


class NotFoundException(Exception):
    def __init__(
        self,
        message: str,
        error_code: str = "NOT_FOUND",
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
