from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    email: EmailStr = Field(
        description="로그인할 사용자의 이메일 주소",
        examples=["user@example.com"],
    )
    password: str = Field(
        min_length=1,
        description="로그인할 사용자의 비밀번호",
        examples=["P@ssword1234!"],
    )


class TokenResponse(BaseModel):
    access_token: str = Field(
        description="인증 및 인가 요청 시 Authorization 헤더에 Bearer로 전달할 JWT 액세스 토큰 (HS512 서명)",
        examples=[
            "eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMmUzNDU2Ny1lODliLTEyZDMtYTR1Ni00MjY2MTQxNzQwMDAiLCJqdGkiOiJmYTQxY2U0MS02ZTc2LTRiOWUtODhjNi0wMzc2OGY5OGJkMTQiLCJleHAiOjE3OTM1MDAwMDAsImlhdCI6MTc5MzQ5NjQwMH0..."
        ],
    )
    token_type: str = Field(
        default="bearer",
        description="토큰 인증 스키마 타입",
        examples=["bearer"],
    )
    expires_in: int = Field(
        description="액세스 토큰의 유효 기간 (초 단위)",
        examples=[3600],
    )
