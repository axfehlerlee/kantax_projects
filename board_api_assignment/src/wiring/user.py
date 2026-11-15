import uuid
from typing import Annotated
from fastapi import Depends, FastAPI, Request
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from auth.application.service import AuthService
from auth.presentation.security import optional_bearer_security
from shared.core.database import get_db
from shared.core.exceptions import ForbiddenException, UnauthorizedException
from user.application.service import UserService
from user.domain.repository import UserRepository
from user.domain.service import PasswordHasher
from user.domain.user import User
from user.infrastructure.repositories import SqlAlchemyUserRepository
from user.infrastructure.security import BcryptPasswordHasher
from user.presentation.dependencies import (
    get_current_user,
    get_optional_user,
    provide_user_repository,
    provide_user_service,
    require_admin,
)
from shared.core.logger import get_logger

logger = get_logger(__file__)

password_hasher: PasswordHasher = BcryptPasswordHasher()


def create_user_repository(session: AsyncSession = Depends(get_db, scope="function")) -> UserRepository:
    return SqlAlchemyUserRepository(session)


def create_user_service(
    repository: UserRepository = Depends(create_user_repository),
) -> UserService:
    return UserService(repository=repository, hasher=password_hasher)


async def resolve_optional_user(
    request: Request,
    credentials: Annotated[
        HTTPAuthorizationCredentials | None, Depends(optional_bearer_security)
    ],
    user_repo: Annotated[UserRepository, Depends(create_user_repository)],
    session: Annotated[AsyncSession, Depends(get_db, scope="function")],
) -> User | None:
    """토큰이 없으면 None 반환, 위조/만료된 토큰이면 401 예외 발생"""
    if credentials is None:
        if request.headers.get("Authorization") is not None:
            raise UnauthorizedException("유효한 Bearer 인증 정보가 필요합니다.")
        return None

    from wiring.auth import create_auth_service

    auth_service: AuthService = create_auth_service(
        session=session, user_repository=user_repo
    )

    payload = await auth_service.authenticate_token(credentials.credentials)
    user = await user_repo.find_by_id(uuid.UUID(str(payload.user_id)))

    if not user:
        raise UnauthorizedException("존재하지 않는 사용자입니다.")
    if getattr(user, "resign", False):
        raise ForbiddenException(
            message="탈퇴한 회원은 서비스를 이용할 수 없습니다.",
            error_code="USER_ALREADY_WITHDRAWN",
        )

    return user


async def resolve_current_user(
    current_user: Annotated[User | None, Depends(resolve_optional_user)],
) -> User:
    """로그인 여부 체크 - resolve_optional_user 결과가 None이면 401 예외 발생"""
    if current_user is None:
        raise UnauthorizedException("인증 정보가 필요합니다.")
    return current_user


async def resolve_require_admin(
    current_user: Annotated[User, Depends(resolve_current_user)],
) -> User:
    if current_user.role != "ADMIN":
        raise ForbiddenException(
            message="관리자 권한이 필요합니다.",
            error_code="ADMIN_PERMISSION_DENIED",
        )
    return current_user


def wire_user_dependencies(app: FastAPI) -> None:
    app.dependency_overrides.update(
        {
            provide_user_repository: create_user_repository,
            provide_user_service: create_user_service,
            get_optional_user: resolve_optional_user,
            get_current_user: resolve_current_user,
            require_admin: resolve_require_admin,
        }
    )
