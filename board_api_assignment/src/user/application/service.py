import uuid
from shared.core.exceptions import ConflictException, NotFoundException
from user.domain.repository import UserRepository
from user.domain.service import PasswordHasher
from user.domain.user import User


class UserService:
    def __init__(self, repository: UserRepository, hasher: PasswordHasher):
        self.repository = repository
        self.hasher = hasher

    async def register_user(self, email: str, name: str, password: str) -> User:
        # 이메일 중복 체크
        if await self.repository.find_by_email(email):
            raise ConflictException(
                message="이미 사용 중인 이메일입니다.",
                error_code="EMAIL_ALREADY_EXISTS",
            )

        # 엔티티 생성 (형식/길이/비밀번호 규칙 검증 수행)
        user = User.create(
            email=email,
            name=name,
            raw_password=password,
            hasher=self.hasher,
        )
        return await self.repository.save(user)

    async def change_password(
        self,
        user_id: uuid.UUID,
        old_password: str,
        new_password: str,
    ) -> None:
        user = await self.repository.find_by_id(user_id)
        if not user:
            raise NotFoundException(
                message="사용자를 찾을 수 없습니다.", error_code="USER_NOT_FOUND"
            )

        user.change_password(
            old_password=old_password,
            new_password=new_password,
            hasher=self.hasher,
        )

        await self.repository.save(user)
