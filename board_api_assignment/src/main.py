from pathlib import Path
from fastapi.staticfiles import StaticFiles

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from auth.presentation.routers.v1.router import router as auth_router
from user.presentation.routers.v1.router import router as user_router
from board.presentation.routers.v1.router import router as board_router
from board.presentation.ui_router import router as board_ui_router
from wiring import wire_dependencies
from shared.middleware.exception_handler import (
    ExceptionHandlerMiddleware,
    request_validation_handler,
)

app = FastAPI(
    title="Board API Assignment",
    version="0.1.0",
)

app.add_middleware(ExceptionHandlerMiddleware)
app.add_exception_handler(RequestValidationError, request_validation_handler)

app.include_router(user_router)
app.include_router(auth_router)
app.include_router(board_router)

app.mount(
    "/static",
    StaticFiles(directory=str(Path(__file__).resolve().parent.parent / "static")),
    name="board_static",
)
app.include_router(board_ui_router)

wire_dependencies(app)


@app.get("/health")
async def health():
    return {"status": "ok"}
