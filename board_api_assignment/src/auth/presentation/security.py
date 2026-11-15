from fastapi.security import HTTPBearer


optional_bearer_security = HTTPBearer(auto_error=False, bearerFormat="JWT")

# FastAPI가 생성한 Bearer 요구사항에 익명 접근 대안을 추가합니다.
OPTIONAL_BEARER_OPENAPI = {"security": [{}]}
