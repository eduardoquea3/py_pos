from fastapi import APIRouter, status
from src.auth.model import LoginRequest
from src.auth.service import find_user


router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


@router.post("/login", status_code=status.HTTP_201_CREATED)
async def login(body: LoginRequest):
    user = find_user(body.username)
    return user
