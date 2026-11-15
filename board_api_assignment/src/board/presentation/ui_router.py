from pathlib import Path

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from user.presentation.dependencies import get_optional_user
from user.domain.user import User

PROJECT_ROOT = Path(__file__).resolve().parents[3]
templates = Jinja2Templates(directory=str(PROJECT_ROOT / "templates"))
router = APIRouter(include_in_schema=False)


@router.get("/")
async def home():
    return RedirectResponse(url="/boards")


@router.get("/boards", response_class=HTMLResponse)
async def board_list_page(request: Request):
    return templates.TemplateResponse(request=request, name="boards.html")


@router.get("/boards/{board_id}", response_class=HTMLResponse)
async def post_list_page(request: Request, board_id: str):
    return templates.TemplateResponse(
        request=request, name="posts.html", context={"board_id": board_id}
    )


@router.get("/posts/{post_id}", response_class=HTMLResponse)
async def post_detail_page(request: Request, post_id: int):
    return templates.TemplateResponse(
        request=request, name="post_detail.html", context={"post_id": post_id}
    )


@router.get("/boards/{board_id}/write", response_class=HTMLResponse)
async def post_write_page(request: Request, board_id: str):
    return templates.TemplateResponse(request=request, name="post_form.html", context={"board_id": board_id})


@router.get("/posts/{post_id}/edit", response_class=HTMLResponse)
async def post_edit_page(request: Request, post_id: int):
    return templates.TemplateResponse(request=request, name="post_form.html", context={"post_id": post_id})


@router.get("/signup", response_class=HTMLResponse)
async def signup_page(request: Request):
    return templates.TemplateResponse(request=request, name="signup.html")


@router.get("/account", response_class=HTMLResponse)
async def account_page(request: Request):
    return templates.TemplateResponse(request=request, name="account.html")


@router.get("/manage/boards", response_class=HTMLResponse)
async def manage_boards_page(request: Request):
    return templates.TemplateResponse(request=request, name="manage_boards.html")


@router.get("/ui/session")
async def ui_session(user: User | None = Depends(get_optional_user)):
    """UI visibility uses the same verified identity as the existing API."""
    return {
        "authenticated": user is not None,
        "user_id": str(user.id) if user else None,
        "role": user.role if user else None,
    }
