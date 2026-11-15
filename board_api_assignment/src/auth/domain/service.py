from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID

from auth.domain.entities import TokenPayload


class TokenProvider(ABC):
    @abstractmethod
    def create_access_token(self, user_id: UUID) -> tuple[str, str, datetime, int]:
        """(token, jti, expired_at, expires_in_seconds) 반환"""
        pass

    @abstractmethod
    def decode_token(self, token: str) -> TokenPayload:
        """토큰 검증 및 페이로드 추출"""
        pass


class UserCredentialVerifier(ABC):
    @abstractmethod
    async def verify_credentials(self, email: str, plain_password: str) -> UUID | None:
        """로그인 성공하면 user_id 반환, 실패 시 None 반환"""
        pass
