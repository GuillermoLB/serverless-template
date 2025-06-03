import logging
from fastapi import APIRouter, HTTPException
from app.dependencies import SessionDep
from app.repos import user_repo
from app.schemas.user_schemas import UserRead, UserCreate


users_router = APIRouter(
    tags=["users"],
    prefix="/users",
)

logger = logging.getLogger(__name__)


@users_router.post("/",
                   summary="Create a new user",
                   response_model=UserRead,
                   responses={
                       400: {"description": "User already exists"},
                       201: {"description": "User created successfully"}
                   })
async def create_user(session: SessionDep, user: UserCreate):
    try:
        logger.debug(f"Creating user: {user.username}")
        user = user_repo.create_user(session, user)
        return user
    except Exception as e:
        from app.error.exceptions import BaseAppException
        if isinstance(e, BaseAppException):
            raise HTTPException(status_code=e.code, detail=e.error)
        else:
            logger.exception("Unexpected error during user creation")
            raise HTTPException(
                status_code=500, detail="Internal server error")
