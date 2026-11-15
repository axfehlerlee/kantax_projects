from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from board.domain.enums import PostSearchType
from board.domain.post import Post
from board.domain.repository.post_repository import PostRepository
from board.infrastructure.sqlalchemy.mappers import PostMapper
from board.infrastructure.sqlalchemy.models import PostModel
from user.infrastructure.models import UserModel


class SqlAlchemyPostRepository(PostRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def _build_search_filter(
        self,
        search_type: PostSearchType | str | None,
        keyword: str | None,
    ):
        """검색 조건에 따른 필터 표현식 생성"""
        if not keyword or not keyword.strip():
            return None

        clean_keyword = keyword.strip()

        if isinstance(search_type, str):
            try:
                search_type = PostSearchType(search_type.upper())
            except ValueError:
                search_type = PostSearchType.ALL
        elif search_type is None:
            search_type = PostSearchType.ALL

        author_email_expr = UserModel.email.icontains(clean_keyword)
        author_name_expr = PostModel.author_name.icontains(clean_keyword)
        title_expr = PostModel.title.icontains(clean_keyword)
        content_expr = PostModel.content.icontains(
            clean_keyword
        )  # 오타 수정 (clearn_keyword -> clean_keyword)

        match search_type:
            case PostSearchType.TITLE:
                return title_expr
            case PostSearchType.CONTENT:
                return content_expr
            case PostSearchType.TITLE_CONTENT:
                return or_(title_expr, content_expr)
            case PostSearchType.AUTHOR_EMAIL:
                return author_email_expr
            case PostSearchType.AUTHOR_NAME:
                return author_name_expr
            case PostSearchType.ALL:
                return or_(
                    title_expr,
                    content_expr,
                    author_name_expr,
                    author_email_expr,
                )

    def _should_join_user(
        self, search_type: PostSearchType | str | None, keyword: str | None
    ) -> bool:
        """UserModel 조인이 필요한 검색 조건인지 확인"""
        if not keyword or not keyword.strip():
            return False
        st = (
            PostSearchType(search_type.upper())
            if isinstance(search_type, str)
            else search_type
        )
        return st in (PostSearchType.AUTHOR_EMAIL, PostSearchType.ALL, None)

    async def find_by_id(self, post_id: int) -> Post | None:
        stmt = select(PostModel).where(
            PostModel.post_id == post_id,
            PostModel.deleted_at.is_(None),
        )
        model = await self.session.scalar(stmt)
        return PostMapper.to_domain(model) if model else None

    async def find_by_board_id(
        self,
        board_id: str,
        limit: int,
        offset: int,
        search_type: PostSearchType | str | None = None,
        keyword: str | None = None,
    ) -> list[Post]:
        stmt = select(PostModel).where(
            PostModel.board_id == board_id,
            PostModel.deleted_at.is_(None),
        )

        if self._should_join_user(search_type, keyword):
            stmt = stmt.outerjoin(UserModel, PostModel.author_id == UserModel.id)

        search_condition = self._build_search_filter(search_type, keyword)
        if search_condition is not None:
            stmt = stmt.where(search_condition)

        stmt = stmt.order_by(PostModel.post_id.desc()).offset(offset).limit(limit)

        models = (await self.session.scalars(stmt)).all()
        return [PostMapper.to_domain(model) for model in models]

    async def count_by_board_id(
        self,
        board_id: str,
        search_type: PostSearchType | str | None = None,
        keyword: str | None = None,
    ) -> int:
        stmt = select(func.count(PostModel.post_id)).where(
            PostModel.board_id == board_id,
            PostModel.deleted_at.is_(None),
        )

        if self._should_join_user(search_type, keyword):
            stmt = stmt.outerjoin(UserModel, PostModel.author_id == UserModel.id)

        search_condition = self._build_search_filter(search_type, keyword)
        if search_condition is not None:
            stmt = stmt.where(search_condition)

        count = await self.session.scalar(stmt)
        return count or 0

    async def save(self, post: Post) -> Post:
        if post.post_id:
            db_model = await self.session.get(PostModel, post.post_id)
            if db_model:
                db_model.title = post.title
                db_model.content = post.content
                db_model.deleted_at = post.deleted_at
                db_model.modified_at = post.modified_at
                await self.session.flush()
                await self.session.refresh(db_model)
                return PostMapper.to_domain(db_model)

        new_model = PostMapper.to_model(post)
        self.session.add(new_model)
        await self.session.flush()
        await self.session.refresh(new_model)
        return PostMapper.to_domain(new_model)
