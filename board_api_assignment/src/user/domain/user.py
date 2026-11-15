import re
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Literal

from shared.core.exceptions import (
    BadRequestException,
    ForbiddenException,
    ValidationException,
)
from user.domain.service import PasswordHasher

EMAIL_REGEX = re.compile(r"^[\w\.-]+@[\w\.-]+\.\w+$")
PASSWORD_REGEX = re.compile(
    r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$"
)
"""
1. 비밀번호는 8자리 이상으로 구성되어야 하며, 특수문자, 숫자, 영어로만 구성되어야 한다.
2. 이메일은 유효한 형식이어야 하며 로그인시에 사용되므로 중복되서는 안된다.
3. 이름은 최소 2자 ~ 20자 이내로 구성되어야 한다.
4. 탈퇴는 소프트 삭제를 기본으로 하며 deleted_at컬럼에 탈퇴한 날짜를 기록하고, 그 여부로 resign 컬럼의 값을 결정한다.
5. 탈퇴는 본인 또는 관리자 권한(탈퇴를 시킬수 있는)을 가진 사용자만 가능하다.
"""

EMAIL_REGEX = re.compile(r"^[\w\.-]+@[\w\.-]+\.\w+$")
PASSWORD_REGEX = re.compile(
    r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$"
)


@dataclass
class User:

    email: str
    name: str
    password_hash: str
    role: Literal["USER", "ADMIN"]
    resign: bool  # 탈퇴 여부

    # 기본값이 있는 필드는 아래쪽 위치
    id: uuid.UUID | None = None
    created_at: datetime | None = None
    modified_at: datetime | None = None
    deleted_at: datetime | None = None

    def __post_init__(self):
        self._validate_email(self.email)
        self._validate_name(self.name)

    @classmethod
    def create(
        cls,
        email: str,
        name: str,
        raw_password: str,
        hasher: PasswordHasher,
        role: Literal["USER", "ADMIN"] = "USER",
    ) -> "User":
        cls._validate_password(raw_password)
        password_hash = hasher.hash(raw_password)

        return cls(
            email=email,
            name=name,
            password_hash=password_hash,
            role=role,
            resign=False,
        )

    def change_password(
        self,
        old_password: str,
        new_password: str,
        hasher: PasswordHasher,
    ) -> None:
        """비밀번호 변경"""
        if self.resign:
            raise ForbiddenException(
                message="탈퇴한 회원은 비밀번호를 변경할 수 없습니다.",
                error_code="USER_ALREADY_WITHDRAWN",
            )

        # 기존 비밀번호 일치 여부 확인
        if not hasher.verify(old_password, self.password_hash):
            raise BadRequestException(
                message="기존 비밀번호가 일치하지 않습니다.",
                error_code="INVALID_OLD_PASSWORD",
            )

        # 동일 비밀번호 변경 방지
        if old_password == new_password:
            raise BadRequestException(
                message="새 비밀번호는 이전 비밀번호와 동일할 수 없습니다.",
                error_code="SAME_PASSWORD",
            )

        # 새 비밀번호 제약 규칙 검증
        self._validate_password(new_password)

        # 해싱 및 상태 갱신
        self.password_hash = hasher.hash(new_password)
        self.modified_at = datetime.now(timezone.utc)

    def withdraw(self, requester: "User") -> None:
        """회원 탈퇴 처리 비즈니스 로직"""
        if self.resign:
            raise ValidationException(
                message="이미 탈퇴 처리된 사용자입니다.",
                error_code="ALREADY_WITHDRAWN",
            )

        is_owner = self.id is not None and self.id == requester.id
        is_admin = requester.role == "ADMIN"
        if not (is_owner or is_admin):
            raise ForbiddenException(
                message="탈퇴 처리는 본인 또는 관리자 권한만 가능합니다.",
                error_code="WITHDRAW_PERMISSION_DENIED",
            )

        now = datetime.now(timezone.utc)
        self.resign = True
        self.deleted_at = now
        self.modified_at = now

    @staticmethod
    def _validate_email(email: str) -> None:
        if not EMAIL_REGEX.match(email):
            raise ValidationException(
                message="유효하지 않은 이메일 형식입니다.",
                field_errors={"email": ["올바른 이메일 형식을 입력하세요."]},
            )

    @staticmethod
    def _validate_name(name: str) -> None:
        if not (2 <= len(name) <= 20):
            raise ValidationException(
                message="이름은 2자 이상 20자 이하여야 합니다.",
                field_errors={"name": ["이름 길이는 2자 이상 20자 이하여야 합니다."]},
            )

    @staticmethod
    def _validate_password(raw_password: str) -> None:
        if not PASSWORD_REGEX.match(raw_password):
            raise ValidationException(
                message="비밀번호 제약 조건을 만족하지 못했습니다.",
                field_errors={
                    "password": [
                        "비밀번호는 8자 이상이어야 하며 영문, 숫자, 특수문자를 포함해야 합니다."
                    ]
                },
            )
