from abc import ABC, abstractmethod
from board.domain.post import Post
from board.domain.enums import PostSearchType


class PostRepository(ABC):

    @abstractmethod
    async def find_by_id(self, post_id: int) -> Post | None:
        """게시글 ID 기준으로 단건 조회 (삭제된 글 제외)"""
        pass

    @abstractmethod
    async def find_by_board_id(
        self,
        board_id: str,
        limit: int,
        offset: int,
        search_type: PostSearchType | str | None = None,
        keyword: str | None = None,
    ) -> list[Post]:
        """특정 게시판의 게시글 목록을 최신순으로 페이징 조회"""
        pass

    @abstractmethod
    async def count_by_board_id(
        self,
        board_id: str,
        search_type: PostSearchType | str | None = None,
        keyword: str | None = None,
    ) -> int:
        """특정 게시판의 전체 유효 게시글 수 카운트 (페이지네이션 계산용)"""
        pass

    @abstractmethod
    async def save(self, post: Post) -> Post:
        """게시글 등록 또는 수정"""
        pass
