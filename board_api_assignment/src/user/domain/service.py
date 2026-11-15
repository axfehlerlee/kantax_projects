# 도메인 서비스 인터페이스
from abc import ABC, abstractmethod


class PasswordHasher(ABC):
    @abstractmethod
    def hash(self, raw_password: str) -> str:
        """평문 비밀번호를 단방향 암호화하여 해시값으로 반환"""

    @abstractmethod
    def verify(self, raw_password: str, hashed_password: str) -> bool:
        """평문 비밀번호가 기존 해시값과 일치하는지 검증"""
