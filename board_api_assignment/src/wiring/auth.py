from fastapi import Depends, FastAPI
from sqlalchemy.ext.asyncio import AsyncSession

from auth.application.service import AuthService
from auth.domain.repository import TokenBlacklistRepository
from auth.domain.service import TokenProvider
from auth.infrastructure.credentials_verifier import UserCredentialVerifierImpl
from auth.infrastructure.repositories import SqlAlchemyTokenBlacklistRepository
from auth.infrastructure.security import JwtTokenProvider
from auth.presentation.dependencies import provide_auth_service
from shared.core.database import get_db
from user.domain.repository import UserRepository
from wiring.user import create_user_repository, password_hasher

token_provider: TokenProvider = JwtTokenProvider()


def create_token_blacklist_repository(
    session: AsyncSession = Depends(get_db, scope="function"),
) -> TokenBlacklistRepository:
    return SqlAlchemyTokenBlacklistRepository(session)


def create_auth_service(
    session: AsyncSession = Depends(get_db, scope="function"),
    user_repository: UserRepository = Depends(create_user_repository),
) -> AuthService:
    return AuthService(
        credential_verifier=UserCredentialVerifierImpl(
            user_repo=user_repository,
            password_hasher=password_hasher,
        ),
        token_blacklist_repo=SqlAlchemyTokenBlacklistRepository(session),
        token_provider=token_provider,
    )


def wire_auth_dependencies(app: FastAPI) -> None:
    app.dependency_overrides.update(
        {
            provide_auth_service: create_auth_service,
        }
    )
