import math
from fastapi import APIRouter, Depends, Query, status

from auth.presentation.security import OPTIONAL_BEARER_OPENAPI
from board.application.service import BoardService, CommentService, PostService
from board.domain.board import Authority
from board.domain.enums import Role
from board.domain.post import Author
from board.presentation.dependencies import (
    get_current_author,
    get_current_role,
    provide_board_service,
    provide_comment_service,
    provide_post_service,
    require_admin_role,
)

from board.presentation.schemas import (
    BoardResponse,
    CommentResponse,
    CreateBoardRequest,
    CreateCommentRequest,
    CreatePostRequest,
    DeleteCommentRequest,
    DeletePostRequest,
    PostDetailResponse,
    PostListItemResponse,
    PostPaginationResponse,
    PostSearchQuery,
    UpdateBoardRequest,
    UpdateCommentRequest,
    UpdatePostRequest,
)
from shared.core.exceptions import BadRequestException
from shared.core.logger import get_logger

logger = get_logger(__file__)


router = APIRouter(prefix="/v1", tags=["Boards"])


# 게시판 설정
@router.post(
    "/boards",
    response_model=BoardResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_board(
    req: CreateBoardRequest,
    _: Role = Depends(require_admin_role),
    board_service: BoardService = Depends(provide_board_service),
) -> BoardResponse:

    authority = Authority(
        edit_role=req.authority.edit_role,
        view_role=req.authority.view_role,
        list_role=req.authority.list_role,
        comment_list_role=req.authority.comment_list_role,
        comment_edit_role=req.authority.comment_edit_role,
    )
    board = await board_service.create_board(
        board_id=req.board_id,
        board_name=req.board_name,
        authority=authority,
        page_size=req.page_size,
    )
    return BoardResponse.from_domain(board)


@router.get(
    "/boards",
    response_model=list[BoardResponse],
    summary="게시판 전체 목록 조회",
)
async def list_boards(
    include_deleted: bool = Query(default=False, description="삭제된 게시판 포함 여부"),
    board_service: BoardService = Depends(provide_board_service),
) -> list[BoardResponse]:
    boards = await board_service.get_all_boards(include_deleted=include_deleted)
    return [BoardResponse.from_domain(board) for board in boards]


@router.get(
    "/boards/{board_id}",
    response_model=BoardResponse,
    summary="게시판 단건 상세 조회",
)
async def get_board(
    board_id: str,
    board_service: BoardService = Depends(provide_board_service),
) -> BoardResponse:
    board = await board_service.get_board(board_id)
    return BoardResponse.from_domain(board)


@router.put(
    "/boards/{board_id}",
    response_model=BoardResponse,
    summary="게시판 설정 수정 (관리자 전용)",
)
async def update_board_config(
    board_id: str,
    req: UpdateBoardRequest,
    _: Role = Depends(require_admin_role),
    board_service: BoardService = Depends(provide_board_service),
) -> BoardResponse:
    authority = None
    if req.authority is not None:
        authority = Authority(
            edit_role=req.authority.edit_role,
            view_role=req.authority.view_role,
            list_role=req.authority.list_role,
            comment_list_role=req.authority.comment_list_role,
            comment_edit_role=req.authority.comment_edit_role,
        )

    board = await board_service.update_board_config(
        board_id=board_id,
        board_name=req.board_name,
        page_size=req.page_size,
        authority=authority,
    )
    return BoardResponse.from_domain(board)


@router.delete(
    "/boards/{board_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="게시판 삭제 (관리자 전용)",
)
async def delete_board(
    board_id: str,
    _: Role = Depends(require_admin_role),
    board_service: BoardService = Depends(provide_board_service),
) -> None:
    await board_service.delete_board(board_id)


# 게시글
@router.post(
    "/boards/{board_id}/posts",
    response_model=PostDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="게시글 작성",
    openapi_extra=OPTIONAL_BEARER_OPENAPI,
)
async def write_post(
    board_id: str,
    req: CreatePostRequest,
    current_author: Author | None = Depends(get_current_author),
    current_role: Role | None = Depends(get_current_role),
    post_service: PostService = Depends(provide_post_service),
) -> PostDetailResponse:
    if current_author is not None:
        author = current_author
        raw_password = None
    else:
        if not req.guest_name or not req.guest_password:
            raise BadRequestException(
                "비회원 글 작성 시 작성자 이름과 비밀번호(6자 이상)는 필수입니다."
            )
        author = (
            Author.guest(guest_name=req.guest_name)
            if hasattr(Author, "guest")
            else Author(author_id=None, author_name=req.guest_name, is_guest=True)
        )
        raw_password = req.guest_password

    post = await post_service.write_post(
        board_id=board_id,
        title=req.title,
        content=req.content,
        author=author,
        raw_guest_password=raw_password,
        user_role=current_role,
    )
    return PostDetailResponse.from_domain(post)


@router.get(
    "/boards/{board_id}/posts",
    response_model=PostPaginationResponse,
    summary="게시글 목록 페이징 및 검색",
    openapi_extra=OPTIONAL_BEARER_OPENAPI,
)
async def list_posts(
    board_id: str,
    search_params: PostSearchQuery = Depends(),
    current_role: Role | None = Depends(get_current_role),
    post_service: PostService = Depends(provide_post_service),
) -> PostPaginationResponse:

    posts, total_count, actual_page_size = await post_service.list_posts(
        board_id=board_id,
        user_role=current_role,
        page=search_params.page,
        page_size=search_params.page_size,
        search_type=search_params.search_type,
        keyword=search_params.keyword,
    )

    total_pages = math.ceil(total_count / actual_page_size) if total_count > 0 else 0

    return PostPaginationResponse(
        items=[PostListItemResponse.from_domain(post) for post in posts],
        total_count=total_count,
        page=search_params.page,
        page_size=actual_page_size,
        total_pages=total_pages,
        search_type=search_params.search_type,
        keyword=search_params.keyword,
    )


@router.get(
    "/posts/{post_id}",
    response_model=PostDetailResponse,
    summary="게시글 상세 조회",
    openapi_extra=OPTIONAL_BEARER_OPENAPI,
)
async def get_post_detail(
    post_id: int,
    current_role: Role | None = Depends(get_current_role),
    post_service: PostService = Depends(provide_post_service),
) -> PostDetailResponse:
    post = await post_service.get_post_detail(
        post_id=post_id,
        user_role=current_role,
    )
    return PostDetailResponse.from_domain(post)


@router.put(
    "/posts/{post_id}",
    response_model=PostDetailResponse,
    summary="게시글 수정",
    openapi_extra=OPTIONAL_BEARER_OPENAPI,
)
async def update_post(
    post_id: int,
    req: UpdatePostRequest,
    current_author: Author | None = Depends(get_current_author),
    current_role: Role | None = Depends(get_current_role),
    post_service: PostService = Depends(provide_post_service),
) -> PostDetailResponse:
    requester_id = current_author.author_id if current_author else None

    post = await post_service.update_post(
        post_id=post_id,
        title=req.title,
        content=req.content,
        requester_id=requester_id,
        guest_password=req.guest_password,
        user_role=current_role,
    )
    return PostDetailResponse.from_domain(post)


@router.delete(
    "/posts/{post_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="게시글 삭제",
    openapi_extra=OPTIONAL_BEARER_OPENAPI,
)
async def delete_post(
    post_id: int,
    req: DeletePostRequest | None = None,
    current_author: Author | None = Depends(get_current_author),
    current_role: Role | None = Depends(get_current_role),
    post_service: PostService = Depends(provide_post_service),
) -> None:
    requester_id = current_author.author_id if current_author else None
    guest_password = req.guest_password if req else None

    await post_service.delete_post(
        post_id=post_id,
        requester_id=requester_id,
        guest_password=guest_password,
        user_role=current_role,
    )


# 댓글
@router.post(
    "/posts/{post_id}/comments",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="댓글 작성",
    openapi_extra=OPTIONAL_BEARER_OPENAPI,
)
async def write_comment(
    post_id: int,
    req: CreateCommentRequest,
    current_author: Author | None = Depends(get_current_author),
    current_role: Role | None = Depends(get_current_role),
    comment_service: CommentService = Depends(provide_comment_service),
) -> CommentResponse:
    if current_author is not None:
        author = current_author
        raw_password = None
    else:
        if not req.guest_name or not req.guest_password:
            raise BadRequestException(
                "비회원 댓글 작성 시 작성자 이름과 비밀번호(6자 이상)는 필수입니다."
            )
        author = (
            Author.guest(guest_name=req.guest_name)
            if hasattr(Author, "guest")
            else Author(author_id=None, author_name=req.guest_name, is_guest=True)
        )
        raw_password = req.guest_password

    comment = await comment_service.write_comment(
        post_id=post_id,
        content=req.content,
        author=author,
        raw_guest_password=raw_password,
        user_role=current_role,
    )
    return CommentResponse.from_domain(comment)


@router.get(
    "/posts/{post_id}/comments",
    response_model=list[CommentResponse],
    summary="게시글의 댓글 목록 조회",
    openapi_extra=OPTIONAL_BEARER_OPENAPI,
)
async def list_comments(
    post_id: int,
    current_role: Role | None = Depends(get_current_role),
    comment_service: CommentService = Depends(provide_comment_service),
) -> list[CommentResponse]:
    comments = await comment_service.list_comments(
        post_id=post_id,
        user_role=current_role,
    )
    return [CommentResponse.from_domain(comment) for comment in comments]


@router.put(
    "/comments/{comment_id}",
    response_model=CommentResponse,
    summary="댓글 수정",
    openapi_extra=OPTIONAL_BEARER_OPENAPI,
)
async def update_comment(
    comment_id: int,
    req: UpdateCommentRequest,
    current_author: Author | None = Depends(get_current_author),
    current_role: Role | None = Depends(get_current_role),
    comment_service: CommentService = Depends(provide_comment_service),
) -> CommentResponse:
    requester_id = current_author.author_id if current_author else None

    comment = await comment_service.update_comment(
        comment_id=comment_id,
        content=req.content,
        requester_id=requester_id,
        guest_password=req.guest_password,
        user_role=current_role,
    )
    return CommentResponse.from_domain(comment)


@router.delete(
    "/comments/{comment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="댓글 삭제",
    openapi_extra=OPTIONAL_BEARER_OPENAPI,
)
async def delete_comment(
    comment_id: int,
    req: DeleteCommentRequest | None = None,
    current_author: Author | None = Depends(get_current_author),
    current_role: Role | None = Depends(get_current_role),
    comment_service: CommentService = Depends(provide_comment_service),
) -> None:
    requester_id = current_author.author_id if current_author else None
    guest_password = req.guest_password if req else None

    await comment_service.delete_comment(
        comment_id=comment_id,
        requester_id=requester_id,
        guest_password=guest_password,
        user_role=current_role,
    )
