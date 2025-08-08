from fastapi import APIRouter, status
from src.features.auth.service import find_user


router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


@router.post("/login", status_code=status.HTTP_201_CREATED)
async def login(username: str, password: str):
    user = find_user(username)
    return user
