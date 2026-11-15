from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from shared.core.exceptions import ConflictException, NotFoundException

from board.domain.board import Board
from board.domain.repository.board_repository import BoardRepository
from board.infrastructure.sqlalchemy.mappers import BoardMapper
from board.infrastructure.sqlalchemy.models import BoardModel


class SqlAlchemyBoardRepository(BoardRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def find_by_id(self, board_id: str) -> Board | None:
        """게시판 ID 기준으로 단건 조회 (삭제된 게시판 제외)"""
        stmt = select(BoardModel).where(
            BoardModel.board_id == board_id,
            BoardModel.deleted_at.is_(None),
        )
        model = await self.session.scalar(stmt)

        return BoardMapper.to_domain(model) if model else None

    async def find_all(self, include_deleted: bool = False) -> list[Board]:
        """모든 게시판 설정 목록 조회"""

        stmt = select(BoardModel)
        if not include_deleted:  # 삭제 게시글 미포함
            stmt = stmt.where(BoardModel.deleted_at.is_(None))

        models = (await self.session.scalars(stmt)).all()

        return [BoardMapper.to_domain(model) for model in models]

    async def exists_by_id(self, board_id: str) -> bool:
        """소프트 삭제된 게시판을 포함하여 ID 중복 여부를 확인합니다."""
        stmt = select(func.count(BoardModel.board_id)).where(
            BoardModel.board_id == board_id,
        )
        count = await self.session.scalar(stmt)
        return (count or 0) > 0

    async def create(self, board: Board) -> Board:
        """INSERT 전용 경로: 기존 게시판을 수정하거나 복구하지 않습니다."""
        new_model = BoardMapper.to_model(board)
        self.session.add(new_model)
        try:
            await self.session.flush()
        except IntegrityError as exc:
            # 사전 중복 검사 이후 동시 INSERT가 발생해도 PK가 덮어쓰기를 막습니다.
            # rollback은 기존 요청 트랜잭션(get_db)에 맡깁니다.
            if getattr(exc.orig, "sqlstate", None) == "23505":
                raise ConflictException(
                    f"이미 존재하는 게시판 ID입니다 ('{board.board_id}')."
                ) from exc
            raise

        await self.session.refresh(new_model)
        return BoardMapper.to_domain(new_model)

    async def save(self, board: Board) -> Board:
        """UPDATE 전용 경로: 없는 게시판을 생성하거나 삭제된 행을 복구하지 않습니다."""
        model = await self.session.get(BoardModel, board.board_id)
        if model is None or model.deleted_at is not None:
            raise NotFoundException("존재하지 않거나 삭제된 게시판입니다.")

        model.board_name = board.board_name
        model.page_size = board.page_size
        model.edit_role = board.authority.edit_role.value
        model.view_role = board.authority.view_role.value
        model.list_role = board.authority.list_role.value
        model.comment_list_role = board.authority.comment_list_role.value
        model.comment_edit_role = board.authority.comment_edit_role.value
        model.deleted_at = board.deleted_at

        await self.session.flush()
        await self.session.refresh(model)
        return BoardMapper.to_domain(model)
