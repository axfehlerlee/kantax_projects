import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

from board.domain.board import Board
from board.domain.enums import PostSearchType, Role
from board.domain.post import Comment, Post


class AuthoritySchema(BaseModel):
    """게시판 권한 세부 설정 스키마"""

    edit_role: Role = Field(default=Role.ALL, description="게시글 작성/수정/삭제 권한")
    view_role: Role = Field(default=Role.ALL, description="게시글 상세 열람 권한")
    list_role: Role = Field(default=Role.ALL, description="게시글 목록 열람 권한")
    comment_list_role: Role = Field(default=Role.ALL, description="댓글 목록 열람 권한")
    comment_edit_role: Role = Field(
        default=Role.ALL, description="댓글 작성/수정/삭제 권한"
    )


class CreateBoardRequest(BaseModel):
    """게시판 설정 생성 요청"""

    board_id: str = Field(
        min_length=2,
        max_length=30,
        description="게시판 고유 식별자 (영문 소문자로 시작, 2~30자)",
        examples=["freetalk", "notice", "qna"],
    )
    board_name: str = Field(min_length=1, max_length=50, description="게시판 표시 이름")
    authority: AuthoritySchema = Field(
        default_factory=AuthoritySchema, description="권한 설정"
    )
    page_size: int = Field(
        default=20, ge=1, le=100, description="페이지당 노출할 게시글 수"
    )


class UpdateBoardRequest(BaseModel):
    """게시판 설정 수정 요청"""

    board_name: str = Field(min_length=1, max_length=50, description="게시판 표시 이름")
    page_size: int = Field(
        default=20, ge=1, le=100, description="페이지당 노출할 게시글 수"
    )
    authority: AuthoritySchema | None = Field(
        default=None, description="변경할 권한 설정 (생략 시 기존 유지)"
    )


class BoardResponse(BaseModel):
    """게시판 설정 정보 응답"""

    model_config = ConfigDict(from_attributes=True)

    board_id: str = Field(description="게시판 고유 식별자")
    board_name: str = Field(description="게시판 표시 이름")
    authority: AuthoritySchema = Field(description="게시판 권한 설정")
    page_size: int = Field(description="페이지당 노출 게시글 수")
    created_at: datetime | None = Field(None, description="생성일시")
    modified_at: datetime | None = Field(None, description="수정일시")

    @classmethod
    def from_domain(cls, board: Board) -> "BoardResponse":
        return cls(
            board_id=board.board_id,
            board_name=board.board_name,
            authority=AuthoritySchema(
                edit_role=board.authority.edit_role,
                view_role=board.authority.view_role,
                list_role=board.authority.list_role,
                comment_list_role=board.authority.comment_list_role,
                comment_edit_role=board.authority.comment_edit_role,
            ),
            page_size=board.page_size,
            created_at=board.created_at,
            modified_at=board.modified_at,
        )


# 게시글 관련 스키마
class CreatePostRequest(BaseModel):
    """게시글 작성 요청 (회원/비회원 공용)"""

    title: str = Field(min_length=1, max_length=200, description="게시글 제목")
    content: str = Field(min_length=1, description="게시글 본문")
    guest_name: str | None = Field(
        default=None, max_length=20, description="작성자 이름 또는 비회원 닉네임"
    )
    guest_password: str | None = Field(
        default=None, min_length=6, description="비회원 비밀번호 (6자 이상)"
    )


class UpdatePostRequest(BaseModel):
    """게시글 수정 요청"""

    title: str = Field(min_length=1, max_length=200, description="수정할 게시글 제목")
    content: str = Field(min_length=1, description="수정할 게시글 본문")
    guest_password: str | None = Field(
        default=None, description="비회원 작성글인 경우 비밀번호"
    )


class DeletePostRequest(BaseModel):
    """게시글 삭제 요청 (비회원용)"""

    guest_password: str | None = Field(
        default=None, description="비회원 작성글인 경우 비밀번호"
    )


class PostSearchQuery(BaseModel):
    """게시글 목록 페이징 및 키워드 검색 쿼리 파라미터 DTO"""

    page: int = Field(default=1, ge=1, description="페이지 번호 (기본값: 1)")
    page_size: int | None = Field(
        default=None,
        ge=1,
        le=100,
        description="페이지 크기 (미지정 시 게시판 설정 기본값 사용)",
    )
    search_type: PostSearchType = Field(
        default=PostSearchType.ALL,
        description="검색 대상 (ALL, TITLE, CONTENT, TITLE_CONTENT, AUTHOR_NAME, AUTHOR_EMAIL)",
    )
    keyword: str | None = Field(
        default=None,
        max_length=50,
        description="검색 키워드",
    )


class AuthorResponse(BaseModel):
    """작성자 정보 응답"""

    author_id: uuid.UUID | None = Field(None, description="회원 ID (비회원은 None)")
    author_name: str = Field(description="작성자 표시 이름")
    is_guest: bool = Field(description="비회원 작성글 여부")


class PostListItemResponse(BaseModel):
    """게시글 목록 항목 응답"""

    post_id: int = Field(description="게시글 고유 ID")
    board_id: str = Field(description="게시판 식별자")
    board_name: str = Field(description="게시판 이름")
    title: str = Field(description="게시글 제목")
    author: AuthorResponse = Field(description="작성자 정보")
    created_at: datetime | None = Field(None, description="작성일시")
    modified_at: datetime | None = Field(None, description="수정일시")

    @classmethod
    def from_domain(cls, post: Post) -> "PostListItemResponse":
        return cls(
            post_id=post.post_id,  # type: ignore
            board_id=post.board_info.board_id,
            board_name=post.board_info.board_name,
            title=post.title,
            author=AuthorResponse(
                author_id=post.author.author_id,
                author_name=post.author.author_name,
                is_guest=post.author.is_guest,
            ),
            created_at=post.created_at,
            modified_at=post.modified_at,
        )


class PostDetailResponse(PostListItemResponse):
    """게시글 상세 조회 응답"""

    content: str = Field(description="게시글 본문")

    @classmethod
    def from_domain(cls, post: Post) -> "PostDetailResponse":
        return cls(
            post_id=post.post_id,
            board_id=post.board_info.board_id,
            board_name=post.board_info.board_name,
            title=post.title,
            content=post.content,
            author=AuthorResponse(
                author_id=post.author.author_id,
                author_name=post.author.author_name,
                is_guest=post.author.is_guest,
            ),
            created_at=post.created_at,
            modified_at=post.modified_at,
        )


class PostPaginationResponse(BaseModel):
    """게시글 목록 페이징 및 검색 결과 응답"""

    items: list[PostListItemResponse] = Field(description="게시글 목록")
    total_count: int = Field(description="조건에 맞는 전체 게시글 수")
    page: int = Field(description="현재 페이지 번호")
    page_size: int = Field(description="페이지당 노출 개수")
    total_pages: int = Field(description="전체 페이지 수")
    search_type: PostSearchType = Field(description="적용된 검색 조건")
    keyword: str | None = Field(default=None, description="적용된 검색 키워드")


# 댓글 관련 스키마
class CreateCommentRequest(BaseModel):
    """댓글 등록 요청"""

    content: str = Field(min_length=1, description="댓글 내용")
    guest_name: str | None = Field(
        default=None, max_length=20, description="작성자 이름 또는 비회원 닉네임"
    )
    guest_password: str | None = Field(
        default=None, min_length=6, description="비회원 비밀번호 (6자 이상)"
    )


class UpdateCommentRequest(BaseModel):
    """댓글 수정 요청"""

    content: str = Field(min_length=1, description="수정할 댓글 내용")
    guest_password: str | None = Field(
        default=None, description="비회원 댓글인 경우 비밀번호"
    )


class DeleteCommentRequest(BaseModel):
    """댓글 삭제 요청 (비회원용)"""

    guest_password: str | None = Field(
        default=None, description="비회원 댓글인 경우 비밀번호"
    )


class CommentResponse(BaseModel):
    """댓글 응답"""

    comment_id: int = Field(description="댓글 고유 ID")
    post_id: int = Field(description="게시글 ID")
    content: str = Field(description="댓글 내용")
    author: AuthorResponse = Field(description="작성자 정보")
    created_at: datetime | None = Field(None, description="작성일시")
    modified_at: datetime | None = Field(None, description="수정일시")

    @classmethod
    def from_domain(cls, comment: Comment) -> "CommentResponse":
        return cls(
            comment_id=comment.comment_id,  # type: ignore
            post_id=comment.post_id,
            content=comment.content,
            author=AuthorResponse(
                author_id=comment.author.author_id,
                author_name=comment.author.author_name,
                is_guest=comment.author.is_guest,
            ),
            created_at=comment.created_at,
            modified_at=comment.modified_at,
        )
