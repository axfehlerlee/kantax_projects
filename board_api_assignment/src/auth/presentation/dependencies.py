from typing import Annotated
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from auth.application.service import AuthService
from shared.core.exceptions import ForbiddenException, UnauthorizedException
from user.domain.repository import UserRepository
from user.domain.user import User
from user.presentation.dependencies import provide_user_repository


def provide_auth_service() -> AuthService:
    raise NotImplementedError("AuthService 의존성이 주입되지 않았습니다.")
