from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class TokenPayload:
    user_id: UUID
    jti: str
    exp: datetime


@dataclass
class BlacklistToken:
    jti: str
    expired_at: datetime
