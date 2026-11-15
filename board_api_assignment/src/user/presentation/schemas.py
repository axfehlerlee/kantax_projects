import uuid
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class SignUpUserRequest(BaseModel):
    """회원가입 요청 스키마"""

    email: EmailStr = Field(description="로그인에 사용할 사용자 이메일")
    name: str = Field(min_length=2, max_length=20, description="사용자 이름 (2~20자)")
    password: str = Field(
        min_length=8, description="비밀번호 (8자 이상, 영문/숫자/특수문자 포함)"
    )


class ChangePasswordRequest(BaseModel):
    """비밀번호 변경 요청 스키마"""

    old_password: str = Field(description="현재 비밀번호")
    new_password: str = Field(
        min_length=8, description="새 비밀번호 (8자 이상, 영문/숫자/특수문자)"
    )


class UserResponse(BaseModel):
    """사용자 정보 응답 스키마"""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID | None = Field(None, description="사용자 식별 고유 ID")
    email: str = Field(description="이메일")
    name: str = Field(description="사용자 이름")
    role: str = Field(description="사용자 권한 (USER, ADMIN)")
