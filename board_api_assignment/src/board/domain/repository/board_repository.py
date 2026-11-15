from abc import ABC, abstractmethod
from board.domain.board import Board


class BoardRepository(ABC):
    @abstractmethod
    async def find_by_id(self, board_id: str) -> Board | None:
        """게시판 ID 기준으로 단건 조회 (삭제된 게시판 제외)"""
        pass

    @abstractmethod
    async def find_all(self, include_deleted: bool = False) -> list[Board]:
        """모든 게시판 설정 목록 조회"""
        pass

    @abstractmethod
    async def exists_by_id(self, board_id: str) -> bool:
        """소프트 삭제 여부와 관계없이 게시판 ID의 중복 여부 확인"""
        pass

    @abstractmethod
    async def create(self, board: Board) -> Board:
        """새 게시판만 등록하며 기존 ID는 중복 오류로 처리"""
        pass

    @abstractmethod
    async def save(self, board: Board) -> Board:
        """기존 활성 게시판의 설정 변경 또는 소프트 삭제만 저장"""
        pass
