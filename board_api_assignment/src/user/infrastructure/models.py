import uuid
from datetime import datetime, timezone
from sqlalchemy import Boolean, DateTime, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column
from shared.core.models import Base, DateTimeBase
from user.domain.user import User


class UserModel(Base, DateTimeBase):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), default="USER", nullable=False)
    resign: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    def to_user(self) -> User:
        """ORM Model -> Domain Entity 변환"""
        return User(
            id=self.id,
            email=self.email,
            name=self.name,
            password_hash=self.password_hash,
            role=self.role,
            resign=self.resign,
            created_at=self.created_at,
            modified_at=self.modified_at,
            deleted_at=self.deleted_at,
        )
