import uuid
from dataclasses import dataclass
from datetime import datetime, timezone

from shared.core.exceptions import BadRequestException, ValidationException
from board.domain.service import PasswordHasher
from board.domain.enums import Role

"""
1. 게시판은 무한대로 생성 가능하다. 게시판 설정 하나가 게시판 하나가 된다.
2. 게시판은 비회원, 회원, 관리자 모두 사용 가능하다.
3. 비회원, 회원, 관리자의 역할에 따라서 이용 제한을 설정할 수 있다.
4. 권한은 다음과 같다.
    - 게시글 수정 가능 권한(edit_role, editable): 글 쓰기, 글 수정, 글 삭제 가능
    - 게시글 상세 보기 가능 권한(view_role, viewable): 글 상세 열람 가능
    - 게시글 목록 보기 가능 권한(list_role, listable): 글 목록 열람 가능
    - 댓글 목록 보기 가능 권한(comment_list_role, comment_listable): 댓글 목록 열람 가능하다
    - 댓글 수정 가능 권한(comment_edit_role, comment_editable): 댓글 쓰기, 댓글 수정, 댓글 삭제 권한
5. 비회원으로 글 또는 댓글 작성시에는 비밀번호(6자리 이상)를 등록해야 하며, 글 또는 댓글 수정, 삭제시에 작성시에 등록한 비밀번호를 검증해야 한다.
6. 회원 게시글의 경우 직접 글 또는 댓글을 등록한 회원만 수정이 가능하며, 관리자는 상관없이 가능하다.
7. 게시글 목록에서 노출될 게시글 갯수는 설정 가능해야 하며 기본값은 20이다.
8. 게시판 ID는 영문 소문자로 시작, 영문 소문자/숫자/하이픈/언더스코어 허용 (2~30자)
9. 게시판 설정은 소프트 삭제를 하며 삭제된 게시판은 수정할 수 없다.
"""


# Value Object 정의 S
@dataclass(frozen=True)
class BoardInfo:
    """게시판 정보 값 객체"""

    board_id: str
    board_name: str


@dataclass(frozen=True)
class Author:
    """작성자 정보 값 객체"""

    author_name: str
    author_id: uuid.UUID | None = None  # None이면 비회원

    def __post_init__(self):
        field_errors: dict[str, list[str]] = {}

        if not self.author_name or not self.author_name.strip():
            field_errors.setdefault("author_name", []).append(
                "작성자 이름은 필수 입력값입니다."
            )
        elif not (1 <= len(self.author_name.strip()) <= 20):
            field_errors.setdefault("author_name", []).append(
                "작성자 이름은 1자 이상 20자 이하여야 합니다."
            )

        if field_errors:
            raise ValidationException(
                message="작성자 정보 유효성 검사에 실패했습니다.",
                field_errors=field_errors,
            )

    @property
    def is_guest(self) -> bool:
        """비회원 여부"""
        return self.author_id is None

    @classmethod
    def member(cls, user_id: uuid.UUID, username: str) -> "Author":
        """회원 작성자 생성"""
        return cls(author_id=user_id, author_name=username.strip())

    @classmethod
    def guest(cls, guest_name: str) -> "Author":
        """비회원 작성자 생성"""
        return cls(author_id=None, author_name=guest_name.strip())

    def is_owner(self, user_id: uuid.UUID | None) -> bool:
        """로그인 사용자가 작성자 본인인지 검증 (비회원은 False)"""
        if self.is_guest or user_id is None:
            return False
        return self.author_id == user_id


@dataclass(frozen=True)
class GuestPassword:
    """비회원 비밀번호 값 객체 (해시 문자열만 보관)"""

    hashed_value: str

    def __post_init__(self):
        if not self.hashed_value or not self.hashed_value.strip():
            raise ValidationException(
                message="비회원 비밀번호 해시값은 필수입니다.",
                field_errors={"guest_password": ["유효하지 않은 비밀번호 해시입니다."]},
            )

    @classmethod
    def create(cls, raw_password: str, hasher: PasswordHasher) -> "GuestPassword":
        """평문 6자리 이상 검증 후 해시화"""
        if not raw_password or len(raw_password) < 6:
            raise ValidationException(
                message="비회원 비밀번호 유효성 검사에 실패했습니다.",
                field_errors={
                    "guest_password": ["비회원 비밀번호는 6자리 이상이어야 합니다."]
                },
            )
        return cls(hashed_value=hasher.hash(raw_password))

    @classmethod
    def from_hash(cls, hashed_password: str) -> "GuestPassword":
        return cls(hashed_value=hashed_password)

    def verify(self, raw_password: str, hasher: PasswordHasher) -> bool:
        """평문 비밀번호 검증 위임"""
        if not raw_password:
            return False
        return hasher.verify(raw_password, self.hashed_value)


# Value Object 정의 E


# Entities 정의 S
@dataclass
class Post:
    """게시글 엔티티"""

    board_info: BoardInfo  # 게시판 정보
    title: str
    content: str
    author: Author
    guest_password: GuestPassword | None = None
    post_id: int | None = None  # 게시글 ID

    created_at: datetime | None = None
    modified_at: datetime | None = None
    deleted_at: datetime | None = None

    def __post_init__(self):
        field_errors: dict[str, list[str]] = {}

        if not self.title or not self.title.strip():
            field_errors.setdefault("title", []).append("제목은 필수 입력값입니다.")

        if not self.content or not self.content.strip():
            field_errors.setdefault("content", []).append("내용은 필수 입력값입니다.")

        if self.author.is_guest and self.guest_password is None:
            field_errors.setdefault("guest_password", []).append(
                "비회원 작성 시 비밀번호 등록은 필수입니다."
            )

        if self.post_id is not None and self.post_id < 1:
            field_errors.setdefault("post_id", []).append(
                "게시글 ID는 1 이상의 정수여야 합니다."
            )

        if field_errors:
            raise ValidationException(
                message="게시글 유효성 검사에 실패했습니다.",
                field_errors=field_errors,
            )

    @classmethod
    def create(
        cls,
        board_id: str,
        board_name: str,
        title: str,
        content: str,
        author: Author,
        raw_guest_password: str | None = None,
        hasher: PasswordHasher | None = None,
    ) -> "Post":
        """신규 게시글 생성 도메인 팩토리"""
        guest_pw = None
        if author.is_guest:
            if not raw_guest_password or hasher is None:
                raise ValidationException(
                    message="비회원 글 작성 시 비밀번호와 PasswordHasher가 필요합니다.",
                    field_errors={"guest_password": ["비회원 비밀번호는 필수입니다."]},
                )
            guest_pw = GuestPassword.create(raw_guest_password, hasher)

        return cls(
            board_info=BoardInfo(board_id=board_id, board_name=board_name),
            title=title,
            content=content,
            author=author,
            guest_password=guest_pw,
            post_id=None,
        )

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None

    def verify_guest_password(self, raw_password: str, hasher: PasswordHasher) -> bool:
        """비회원 비밀번호 검증"""
        if not self.author.is_guest or self.guest_password is None:
            return False
        return self.guest_password.verify(raw_password, hasher)

    def update_content(self, title: str, content: str) -> None:
        if self.is_deleted:
            raise BadRequestException(message="삭제된 게시글은 수정할 수 없습니다.")

        field_errors: dict[str, list[str]] = {}
        if not title or not title.strip():
            field_errors.setdefault("title", []).append("제목은 공백일 수 없습니다.")
        if not content or not content.strip():
            field_errors.setdefault("content", []).append("내용은 공백일 수 없습니다.")

        if field_errors:
            raise ValidationException(
                message="게시글 수정 유효성 검사에 실패했습니다.",
                field_errors=field_errors,
            )

        self.title = title.strip()
        self.content = content.strip()
        self.modified_at = datetime.now(timezone.utc)

    def delete(self) -> None:
        if self.is_deleted:
            raise BadRequestException("이미 삭제된 게시글입니다.")
        self.deleted_at = datetime.now(timezone.utc)

    def can_modify_or_delete(
        self,
        requester_id: uuid.UUID | None,
        user_role: Role,
        raw_guest_password: str | None,
        hasher: PasswordHasher,
    ) -> bool:
        """수정/삭제 권한 확인 (관리자 -> 회원 본인 -> 비회원 비밀번호 일치 순)"""
        if user_role == Role.ADMIN:
            return True

        if not self.author.is_guest:
            return self.author.is_owner(requester_id)

        if not raw_guest_password:
            return False
        return self.verify_guest_password(raw_guest_password, hasher)


@dataclass
class Comment:
    """댓글 엔티티"""

    post_id: int  # 게시글 ID
    content: str
    author: Author
    guest_password: GuestPassword | None = None
    comment_id: int | None = None  # 댓글 ID

    created_at: datetime | None = None
    modified_at: datetime | None = None
    deleted_at: datetime | None = None

    def __post_init__(self):
        field_errors: dict[str, list[str]] = {}

        if self.post_id < 1:
            field_errors.setdefault("post_id", []).append(
                "유효한 게시글 ID여야 합니다."
            )

        if not self.content or not self.content.strip():
            field_errors.setdefault("content", []).append(
                "댓글 내용은 필수 입력값입니다."
            )

        if self.author.is_guest and self.guest_password is None:
            field_errors.setdefault("guest_password", []).append(
                "비회원 댓글 작성 시 비밀번호 등록은 필수입니다."
            )

        if self.comment_id is not None and self.comment_id < 1:
            field_errors.setdefault("comment_id", []).append(
                "댓글 ID는 1 이상의 정수여야 합니다."
            )

        if field_errors:
            raise ValidationException(
                message="댓글 유효성 검사에 실패했습니다.",
                field_errors=field_errors,
            )

    @classmethod
    def create(
        cls,
        post_id: int,
        content: str,
        author: Author,
        raw_guest_password: str | None = None,
        hasher: PasswordHasher | None = None,
    ) -> "Comment":
        """신규 댓글 생성 도메인 팩토리"""
        guest_pw = None
        if author.is_guest:
            if not raw_guest_password or hasher is None:
                raise ValidationException(
                    message="비회원 댓글 작성 시 비밀번호와 PasswordHasher가 필요합니다.",
                    field_errors={"guest_password": ["비회원 비밀번호는 필수입니다."]},
                )
            guest_pw = GuestPassword.create(raw_guest_password, hasher)

        return cls(
            post_id=post_id,
            content=content,
            author=author,
            guest_password=guest_pw,
            comment_id=None,
        )

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None

    def verify_guest_password(self, raw_password: str, hasher: PasswordHasher) -> bool:
        if not self.author.is_guest or self.guest_password is None:
            return False
        return self.guest_password.verify(raw_password, hasher)

    def update_content(self, content: str) -> None:
        if self.is_deleted:
            raise BadRequestException(message="삭제된 댓글은 수정할 수 없습니다.")

        if not content or not content.strip():
            raise ValidationException(
                message="댓글 수정 유효성 검사에 실패했습니다.",
                field_errors={"content": ["댓글 내용은 공백일 수 없습니다."]},
            )

        self.content = content.strip()
        self.modified_at = datetime.now(timezone.utc)

    def delete(self) -> None:
        if self.is_deleted:
            raise BadRequestException(message="이미 삭제된 댓글입니다.")
        self.deleted_at = datetime.now(timezone.utc)

    def can_modify_or_delete(
        self,
        requester_id: uuid.UUID | None,
        user_role: Role,
        raw_guest_password: str | None,
        hasher: PasswordHasher,
    ) -> bool:
        """수정/삭제 권한 확인 (관리자 -> 회원 본인 -> 비회원 비밀번호 일치 순)"""
        if user_role == Role.ADMIN:
            return True

        if not self.author.is_guest:
            return self.author.is_owner(requester_id)

        if not raw_guest_password:
            return False
        return self.verify_guest_password(raw_guest_password, hasher)


# Entities 정의 E
