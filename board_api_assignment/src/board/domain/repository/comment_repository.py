from abc import ABC, abstractmethod
from board.domain.post import Comment


class CommentRepository(ABC):

    @abstractmethod
    async def find_by_id(self, comment_id: int) -> Comment | None:
        """댓글 ID 기준으로 단건 조회 (삭제된 댓글 제외)"""
        pass

    @abstractmethod
    async def find_by_post_id(self, post_id: int) -> list[Comment]:
        """특정 게시글에 작성된 댓글 전체 목록을 등록순(오름차순)으로 조회"""
        pass

    @abstractmethod
    async def count_by_post_id(self, post_id: int) -> int:
        """특정 게시글에 달린 유효 댓글 총 개수 카운트"""
        pass

    @abstractmethod
    async def save(self, comment: Comment) -> Comment:
        """댓글 등록 및 수정"""
        pass
