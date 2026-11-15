from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from board.domain.post import Comment
from board.domain.repository.comment_repository import CommentRepository
from board.infrastructure.sqlalchemy.mappers import CommentMapper
from board.infrastructure.sqlalchemy.models import CommentModel


class SqlAlchemyCommentRepository(CommentRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def find_by_id(self, comment_id: int) -> Comment | None:
        """댓글 ID 기준으로 단건 조회 (삭제된 댓글 제외)"""
        stmt = select(CommentModel).where(
            CommentModel.comment_id == comment_id, CommentModel.deleted_at.is_(None)
        )

        model = await self.session.scalar(stmt)
        return CommentMapper.to_domain(model) if model else None

    async def find_by_post_id(self, post_id: int) -> list[Comment]:
        """특정 게시글에 작성된 댓글 전체 목록을 등록순(오름차순)으로 조회"""
        stmt = (
            select(CommentModel)
            .where(
                CommentModel.post_id == post_id,
                CommentModel.deleted_at.is_(None),
            )
            .order_by(CommentModel.comment_id.asc())
        )
        models = (await self.session.scalars(stmt)).all()
        return [CommentMapper.to_domain(model) for model in models]

    async def count_by_post_id(self, post_id: int) -> int:
        """특정 게시글에 달린 유효 댓글 총 개수 카운트"""
        stmt = select(func.count(CommentModel.comment_id)).where(
            CommentModel.post_id == post_id,
            CommentModel.deleted_at.is_(None),
        )

        count = await self.session.scalar(stmt)
        return count or 0

    async def save(self, comment: Comment) -> Comment:
        """댓글 등록 및 수정"""
        if comment.comment_id:
            _comment = await self.session.get(CommentModel, comment.comment_id)
            if _comment:  # 댓글 수정
                _comment.content = comment.content
                _comment.deleted_at = comment.deleted_at
                await self.session.flush()
                await self.session.refresh(_comment)
                return CommentMapper.to_domain(_comment)

        # 댓글 추가
        new_model = CommentMapper.to_model(comment)
        self.session.add(new_model)
        await self.session.flush()
        await self.session.refresh(new_model)
        return CommentMapper.to_domain(new_model)
