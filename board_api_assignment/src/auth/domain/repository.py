from abc import ABC, abstractmethod
from datetime import datetime


class TokenBlacklistRepository(ABC):
    @abstractmethod
    async def add(self, jti: str, expired_at: datetime) -> None:
        """블랙리스트에 토큰 식별자 등록"""
        pass

    @abstractmethod
    async def is_blacklisted(self, jti: str) -> bool:
        """토큰이 블랙리스트에 등록되어 있는지 확인"""
        pass

    @abstractmethod
    async def cleanup_expired(self, current_time: datetime) -> int:
        """유효기간이 지난 블랙리스트 항목 정리"""
        pass
