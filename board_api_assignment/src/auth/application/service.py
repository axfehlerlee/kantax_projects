from datetime import datetime, timezone
from auth.domain.entities import TokenPayload
from auth.domain.repository import TokenBlacklistRepository
from auth.domain.service import TokenProvider, UserCredentialVerifier
from shared.core.exceptions import UnauthorizedException


class AuthService:
    def __init__(
        self,
        credential_verifier: UserCredentialVerifier,
        token_blacklist_repo: TokenBlacklistRepository,
        token_provider: TokenProvider,
    ):
        self._credential_verifier = credential_verifier
        self._blacklist_repo = token_blacklist_repo
        self._token_provider = token_provider

    async def login(self, email: str, plain_password: str) -> tuple[str, str, int]:
        user_id = await self._credential_verifier.verify_credentials(
            email, plain_password
        )
        if not user_id:
            raise UnauthorizedException("이메일 또는 비밀번호가 올바르지 않습니다.")

        token, _, _, expires_in = self._token_provider.create_access_token(user_id)
        return token, "bearer", expires_in

    async def logout(self, token: str) -> None:
        payload = self._token_provider.decode_token(token)
        if not await self._blacklist_repo.is_blacklisted(payload.jti):
            await self._blacklist_repo.add(jti=payload.jti, expired_at=payload.exp)
        now = datetime.now(timezone.utc)
        await self._blacklist_repo.cleanup_expired(now)

    async def authenticate_token(self, token: str) -> TokenPayload:
        payload = self._token_provider.decode_token(token)
        if await self._blacklist_repo.is_blacklisted(payload.jti):
            raise UnauthorizedException("로그아웃된 토큰입니다.")
        return payload
