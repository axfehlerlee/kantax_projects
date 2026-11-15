import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from user.domain.repository import UserRepository
from user.domain.user import User
from user.infrastructure.models import UserModel


class SqlAlchemyUserRepository(UserRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def find_by_id(self, user_id: uuid.UUID) -> User | None:
        stmt = select(UserModel).where(UserModel.id == user_id)
        user_model = await self.session.scalar(stmt)
        return user_model.to_user() if user_model else None

    async def find_by_email(self, email: str) -> User | None:
        stmt = select(UserModel).where(UserModel.email == email)
        user_model = await self.session.scalar(stmt)
        return user_model.to_user() if user_model else None

    async def save(self, user: User) -> User:
        if user.id is None:
            # 신규 사용자 등록(INSERT)
            user_model = UserModel(
                email=user.email,
                name=user.name,
                password_hash=user.password_hash,
                role=user.role,
                resign=user.resign,
            )
            self.session.add(user_model)
            await self.session.flush()
            await self.session.refresh(user_model)
            return user_model.to_user()

        # 기존 사용자 정보 수정(UPDATE)
        stmt = select(UserModel).where(UserModel.id == user.id)
        user_model = await self.session.scalar(stmt)

        if user_model:
            user_model.name = user.name
            user_model.password_hash = user.password_hash
            user_model.resign = user.resign
            user_model.deleted_at = user.deleted_at
            user_model.modified_at = user.modified_at

            await self.session.flush()
            await self.session.refresh(user_model)
            return user_model.to_user()

        return user
