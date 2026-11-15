from enum import StrEnum


class Role(StrEnum):
    ALL = "ALL"  # 비회원 포함 모두
    USER = "USER"  # 회원 + 관리자
    ADMIN = "ADMIN"  # 관리자만

    @property
    def level(self) -> int:
        """권한 가중치 (상위 권한 포함 여부 판별 목적)"""
        _levels = {
            Role.ALL: 0,
            Role.USER: 1,
            Role.ADMIN: 2,
        }
        return _levels[self]

    def satisfies(self, required_role: "Role | str") -> bool:
        """현재 역할이 요구 권한 이상을 보유하고 있는지 검증"""
        if isinstance(required_role, str):
            required_role = Role(required_role)

        return self.level >= required_role.level


# 게시글 검색 타입
class PostSearchType(StrEnum):
    ALL = "ALL"
    TITLE = "TITLE"
    CONTENT = "CONTENT"
    TITLE_CONTENT = "TITLE_CONTENT"
    AUTHOR_NAME = "AUTHOR_NAME"
    AUTHOR_EMAIL = "AUTHOR_EMAIL"
