import bcrypt
from shared.core.exceptions import ValidationException
from board.domain.service import PasswordHasher


class BcryptPasswordHasher(PasswordHasher):
    def hash(self, raw_password: str) -> str:
        pwd_bytes = raw_password.encode("utf-8")
        if len(pwd_bytes) > 72:
            raise ValidationException(
                message="비밀번호는 UTF-8 기준 72바이트 이하여야 합니다.",
                error_code="PASSWORD_TOO_LONG",
                field_errors={"guest_password": ["UTF-8 기준 72바이트 이하로 입력하세요."]},
            )
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(pwd_bytes, salt)
        return hashed.decode("utf-8")

    def verify(self, raw_password: str, hashed_password: str) -> bool:
        pwd_bytes = raw_password.encode("utf-8")
        if len(pwd_bytes) > 72:
            return False
        hashed_bytes = hashed_password.encode("utf-8")
        return bcrypt.checkpw(pwd_bytes, hashed_bytes)
