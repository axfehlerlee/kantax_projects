from board.domain.board import Authority, Board
from board.domain.enums import Role
from board.domain.post import Author, BoardInfo, Comment, GuestPassword, Post
from board.infrastructure.sqlalchemy.models import BoardModel, CommentModel, PostModel


class BoardMapper:
    """Board 도메인 엔티티 <-> BoardModel 상호 변환기"""

    @staticmethod
    def to_domain(model: BoardModel) -> Board:
        return Board(
            board_id=model.board_id,
            board_name=model.board_name,
            authority=Authority(
                edit_role=Role(model.edit_role),
                view_role=Role(model.view_role),
                list_role=Role(model.list_role),
                comment_list_role=Role(model.comment_list_role),
                comment_edit_role=Role(model.comment_edit_role),
            ),
            page_size=model.page_size,
            created_at=model.created_at,
            modified_at=model.modified_at,
            deleted_at=model.deleted_at,
        )

    @staticmethod
    def to_model(domain: Board) -> BoardModel:
        return BoardModel(
            board_id=domain.board_id,
            board_name=domain.board_name,
            page_size=domain.page_size,
            edit_role=domain.authority.edit_role.value,
            view_role=domain.authority.view_role.value,
            list_role=domain.authority.list_role.value,
            comment_list_role=domain.authority.comment_list_role.value,
            comment_edit_role=domain.authority.comment_edit_role.value,
            created_at=domain.created_at,
            modified_at=domain.modified_at,
            deleted_at=domain.deleted_at,
        )


class PostMapper:
    """Post 도메인 엔티티 <-> PostModel 상호 변환기"""

    def to_domain(model: PostModel) -> Post:
        guest_pw = (
            GuestPassword.from_hash(model.guest_password)
            if model.guest_password
            else None
        )

        return Post(
            post_id=model.post_id,
            board_info=BoardInfo(
                board_id=model.board_id, board_name=model.board.board_name
            ),
            title=model.title,
            content=model.content,
            author=Author(author_name=model.author_name, author_id=model.author_id),
            guest_password=guest_pw,
            created_at=model.created_at,
            modified_at=model.modified_at,
            deleted_at=model.deleted_at,
        )

    @staticmethod
    def to_model(domain: Post) -> PostModel:
        return PostModel(
            post_id=domain.post_id,
            board_id=domain.board_info.board_id,
            title=domain.title,
            content=domain.content,
            author_name=domain.author.author_name,
            author_id=domain.author.author_id,
            guest_password=(
                domain.guest_password.hashed_value if domain.guest_password else None
            ),
            created_at=domain.created_at,
            modified_at=domain.modified_at,
            deleted_at=domain.deleted_at,
        )


class CommentMapper:
    """Comment 도메인 엔티티 <-> CommentModel 상호 변환기"""

    @staticmethod
    def to_domain(model: CommentModel) -> Comment:

        return Comment(
            comment_id=model.comment_id,
            post_id=model.post_id,
            content=model.content,
            author=Author(author_name=model.author_name, author_id=model.author_id),
            guest_password=(
                GuestPassword.from_hash(model.guest_password)
                if model.guest_password
                else None
            ),
            created_at=model.created_at,
            modified_at=model.modified_at,
            deleted_at=model.deleted_at,
        )

    @staticmethod
    def to_model(domain: Comment) -> CommentModel:
        return CommentModel(
            comment_id=domain.comment_id,
            post_id=domain.post_id,
            content=domain.content,
            author_name=domain.author.author_name,
            author_id=domain.author.author_id,
            guest_password=(
                domain.guest_password.hashed_value if domain.guest_password else None
            ),
            created_at=domain.created_at,
            modified_at=domain.modified_at,
            deleted_at=domain.deleted_at,
        )
