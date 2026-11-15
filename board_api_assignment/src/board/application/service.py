import uuid

from board.domain.board import Authority, Board
from board.domain.enums import PostSearchType, Role
from board.domain.post import Author, Comment, Post
from board.domain.repository.board_repository import BoardRepository
from board.domain.repository.comment_repository import CommentRepository
from board.domain.repository.post_repository import PostRepository
from board.domain.service import PasswordHasher
from shared.core.exceptions import (
    ConflictException,
    ForbiddenException,
    NotFoundException,
)


class BoardService:
    """게시판 설정 서비스"""

    def __init__(self, board_repo: BoardRepository):
        self._board_repo = board_repo

    async def create_board(
        self,
        board_id: str,
        board_name: str,
        authority: Authority | None = None,
        page_size: int = 20,
    ) -> Board:
        board = Board.create(
            board_id=board_id,
            board_name=board_name,
            authority=authority,
            page_size=page_size,
        )
        if await self._board_repo.exists_by_id(board.board_id):
            raise ConflictException(
                f"이미 존재하는 게시판 ID입니다 ('{board.board_id}')."
            )
        return await self._board_repo.create(board)

    async def get_board(self, board_id: str) -> Board:
        board = await self._board_repo.find_by_id(board_id)
        if not board:
            raise NotFoundException("존재하지 않거나 삭제된 게시판입니다.")
        return board

    async def get_all_boards(self, include_deleted: bool = False) -> list[Board]:
        return await self._board_repo.find_all(include_deleted=include_deleted)

    async def update_board_config(
        self,
        board_id: str,
        board_name: str,
        page_size: int,
        authority: Authority | None = None,
    ) -> Board:
        board = await self.get_board(board_id)
        board.update_config(
            board_name=board_name, page_size=page_size, authority=authority
        )
        return await self._board_repo.save(board)

    async def delete_board(self, board_id: str) -> None:
        board = await self.get_board(board_id)
        board.delete()
        await self._board_repo.save(board)


class PostService:
    """게시글 서비스"""

    def __init__(
        self,
        post_repo: PostRepository,
        board_repo: BoardRepository,
        password_hasher: PasswordHasher,
    ):
        self._post_repo = post_repo
        self._board_repo = board_repo
        self._hasher = password_hasher

    async def write_post(
        self,
        board_id: str,
        title: str,
        content: str,
        author: Author,
        raw_guest_password: str | None = None,
        user_role: Role | None = None,  # 비회원은 None
    ) -> Post:
        board = await self._get_active_board(board_id)
        if not board.authority.can_edit(user_role):
            raise ForbiddenException("해당 게시판에 글을 작성할 권한이 없습니다.")

        post = Post.create(
            board_id=board.board_id,
            board_name=board.board_name,
            title=title,
            content=content,
            author=author,
            raw_guest_password=raw_guest_password,
            hasher=self._hasher,
        )
        return await self._post_repo.save(post)

    async def get_post_detail(
        self,
        post_id: int,
        user_role: Role | None = None,
    ) -> Post:
        post = await self._get_active_post(post_id)
        board = await self._get_active_board(post.board_info.board_id)

        if not board.authority.can_view(user_role):
            raise ForbiddenException("게시글 상세 열람 권한이 없습니다.")

        return post

    async def list_posts(
        self,
        board_id: str,
        user_role: Role | None = None,
        page: int = 1,
        page_size: int | None = None,
        search_type: PostSearchType | str | None = None,
        keyword: str | None = None,
    ) -> tuple[list[Post], int, int]:
        board = await self._get_active_board(board_id)
        if not board.authority.can_list(user_role):
            raise ForbiddenException("게시글 목록 열람 권한이 없습니다.")

        size = page_size if (page_size and page_size > 0) else board.page_size
        offset = max(0, (page - 1) * size)

        posts = await self._post_repo.find_by_board_id(
            board_id=board_id,
            limit=size,
            offset=offset,
            search_type=search_type,
            keyword=keyword,
        )
        total_count = await self._post_repo.count_by_board_id(
            board_id=board_id,
            search_type=search_type,
            keyword=keyword,
        )
        return posts, total_count, size

    async def update_post(
        self,
        post_id: int,
        title: str,
        content: str,
        requester_id: uuid.UUID | None = None,
        guest_password: str | None = None,
        user_role: Role | None = None,
    ) -> Post:
        post = await self._get_active_post(post_id)
        board = await self._get_active_board(post.board_info.board_id)

        if not board.authority.can_edit(user_role):
            raise ForbiddenException("게시글 수정 권한이 없습니다.")

        if not post.can_modify_or_delete(
            requester_id, user_role, guest_password, self._hasher
        ):
            raise ForbiddenException(
                "게시글을 수정할 권한이 없거나 비밀번호가 일치하지 않습니다."
            )

        post.update_content(title=title, content=content)
        return await self._post_repo.save(post)

    async def delete_post(
        self,
        post_id: int,
        requester_id: uuid.UUID | None = None,
        guest_password: str | None = None,
        user_role: Role | None = None,
    ) -> None:
        post = await self._get_active_post(post_id)
        board = await self._get_active_board(post.board_info.board_id)

        if not board.authority.can_edit(user_role):
            raise ForbiddenException("게시글 삭제 권한이 없습니다.")

        if not post.can_modify_or_delete(
            requester_id, user_role, guest_password, self._hasher
        ):
            raise ForbiddenException(
                "게시글을 삭제할 권한이 없거나 비밀번호가 일치하지 않습니다."
            )

        post.delete()
        await self._post_repo.save(post)

    async def _get_active_post(self, post_id: int) -> Post:
        post = await self._post_repo.find_by_id(post_id)
        if not post or post.is_deleted:
            raise NotFoundException("존재하지 않거나 삭제된 게시글입니다.")
        return post

    async def _get_active_board(self, board_id: str) -> Board:
        board = await self._board_repo.find_by_id(board_id)
        if not board or board.is_deleted:
            raise NotFoundException("해당 게시판을 찾을 수 없거나 비활성화되었습니다.")
        return board


class CommentService:
    """댓글 서비스"""

    def __init__(
        self,
        comment_repo: CommentRepository,
        post_repo: PostRepository,
        board_repo: BoardRepository,
        password_hasher: PasswordHasher,
    ):
        self._comment_repo = comment_repo
        self._post_repo = post_repo
        self._board_repo = board_repo
        self._hasher = password_hasher

    async def write_comment(
        self,
        post_id: int,
        content: str,
        author: Author,
        raw_guest_password: str | None = None,
        user_role: Role | None = None,
    ) -> Comment:
        post = await self._get_active_post(post_id)
        board = await self._get_active_board(post.board_info.board_id)

        if not board.authority.can_edit_comments(user_role):
            raise ForbiddenException("댓글을 작성할 권한이 없습니다.")

        comment = Comment.create(
            post_id=post_id,
            content=content,
            author=author,
            raw_guest_password=raw_guest_password,
            hasher=self._hasher,
        )
        return await self._comment_repo.save(comment)

    async def list_comments(
        self,
        post_id: int,
        user_role: Role | None = None,
    ) -> list[Comment]:
        post = await self._get_active_post(post_id)
        board = await self._get_active_board(post.board_info.board_id)

        if not board.authority.can_view_comments(user_role):
            raise ForbiddenException("댓글 목록을 열람할 권한이 없습니다.")

        return await self._comment_repo.find_by_post_id(post_id)

    async def update_comment(
        self,
        comment_id: int,
        content: str,
        requester_id: uuid.UUID | None = None,
        guest_password: str | None = None,
        user_role: Role | None = None,
    ) -> Comment:
        comment = await self._get_active_comment(comment_id)
        post = await self._get_active_post(comment.post_id)
        board = await self._get_active_board(post.board_info.board_id)

        if not board.authority.can_edit_comments(user_role):
            raise ForbiddenException("댓글 수정 권한이 없습니다.")

        if not comment.can_modify_or_delete(
            requester_id, user_role, guest_password, self._hasher
        ):
            raise ForbiddenException(
                "댓글을 수정할 권한이 없거나 비밀번호가 일치하지 않습니다."
            )

        comment.update_content(content=content)
        return await self._comment_repo.save(comment)

    async def delete_comment(
        self,
        comment_id: int,
        requester_id: uuid.UUID | None = None,
        guest_password: str | None = None,
        user_role: Role | None = None,
    ) -> None:
        comment = await self._get_active_comment(comment_id)
        post = await self._get_active_post(comment.post_id)
        board = await self._get_active_board(post.board_info.board_id)

        if not board.authority.can_edit_comments(user_role):
            raise ForbiddenException("댓글 삭제 권한이 없습니다.")

        if not comment.can_modify_or_delete(
            requester_id, user_role, guest_password, self._hasher
        ):
            raise ForbiddenException(
                "댓글을 삭제할 권한이 없거나 비밀번호가 일치하지 않습니다."
            )

        comment.delete()
        await self._comment_repo.save(comment)

    async def _get_active_comment(self, comment_id: int) -> Comment:
        comment = await self._comment_repo.find_by_id(comment_id)
        if not comment or comment.is_deleted:
            raise NotFoundException("존재하지 않거나 삭제된 댓글입니다.")
        return comment

    async def _get_active_post(self, post_id: int) -> Post:
        post = await self._post_repo.find_by_id(post_id)
        if not post or post.is_deleted:
            raise NotFoundException("존재하지 않거나 삭제된 게시글입니다.")
        return post

    async def _get_active_board(self, board_id: str) -> Board:
        board = await self._board_repo.find_by_id(board_id)
        if not board or board.is_deleted:
            raise NotFoundException("해당 게시판을 찾을 수 없거나 비활성화되었습니다.")
        return board
