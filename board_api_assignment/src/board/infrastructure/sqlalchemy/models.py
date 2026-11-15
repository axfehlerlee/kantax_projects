import uuid
from datetime import datetime
from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UUID,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from shared.core.models import Base, DateTimeBase


class BoardModel(Base, DateTimeBase):
    """게시판 설정 테이블"""

    __tablename__ = "boards"

    board_id: Mapped[str] = mapped_column("id", String(30), primary_key=True)
    board_name: Mapped[str] = mapped_column(String(100), nullable=False)
    page_size: Mapped[int] = mapped_column(Integer, default=20, nullable=False)

    # 게시판 권한
    edit_role: Mapped[str] = mapped_column(String(20), default="ALL", nullable=False)
    view_role: Mapped[str] = mapped_column(String(20), default="ALL", nullable=False)
    list_role: Mapped[str] = mapped_column(String(20), default="ALL", nullable=False)
    comment_list_role: Mapped[str] = mapped_column(
        String(20), default="ALL", nullable=False
    )
    comment_edit_role: Mapped[str] = mapped_column(
        String(20), default="ALL", nullable=False
    )


class PostModel(Base, DateTimeBase):
    """게시글 테이블"""

    __tablename__ = "posts"

    __table_args__ = (
        Index("ix_posts_id_deleted_at", "id", "deleted_at"),
        Index("ix_posts_author_id", "author_id"),
    )

    post_id: Mapped[int] = mapped_column(
        "id", BigInteger, primary_key=True, autoincrement=True
    )
    board_id: Mapped[str] = mapped_column(
        String(30), ForeignKey("boards.id"), nullable=False
    )

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)

    author_name: Mapped[str] = mapped_column(String(50), nullable=False)
    author_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    guest_password: Mapped[str | None] = mapped_column(String(65), nullable=True)

    board: Mapped["BoardModel"] = relationship("BoardModel", lazy="joined")


class CommentModel(Base, DateTimeBase):
    """댓글 테이블"""

    __tablename__ = "comments"
    __table_args__ = (Index("ix_comments_post_id_deleted_at", "post_id", "deleted_at"),)

    comment_id: Mapped[int] = mapped_column(
        "id", BigInteger, primary_key=True, autoincrement=True
    )
    post_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("posts.id"), nullable=False
    )

    content: Mapped[str] = mapped_column(Text, nullable=False)

    author_name: Mapped[str] = mapped_column(String(50), nullable=False)
    author_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    guest_password: Mapped[str | None] = mapped_column(String(65), nullable=True)

    post: Mapped[PostModel] = relationship("PostModel")
