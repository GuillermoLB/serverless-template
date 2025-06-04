import logging
from fastapi import APIRouter, HTTPException
from app.schemas.user_schemas import UserRead, UserCreate


users_router = APIRouter(
    tags=["users"],
    prefix="/users",
)

logger = logging.getLogger(__name__)


@users_router.post("/",
                   summary="Create a new user",
                   responses={
                       400: {"description": "User already exists"},
                       201: {"description": "User created successfully"}
                   })
async def create_user(user: UserCreate):
    return {"status": "OK"}
