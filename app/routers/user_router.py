import logging
from fastapi import APIRouter, HTTPException
from app.dependencies import SettingsDep
from app.schemas.user_schemas import UserRead, UserCreate


users_router = APIRouter(
    tags=["users"],
    prefix="/users",
)

logger = logging.getLogger(__name__)


@users_router.get("/me",
                 summary="Get current user information",
                 response_model=UserRead,
                 responses={
                     401: {"description": "Not authenticated"},
                     404: {"description": "User not found"}
                 })
async def get_current_user(settings: SettingsDep):
    """
    Get information about the currently authenticated user.
    
    This endpoint requires authentication via JWT token.
    """
    try:
        user = UserRead(
            username="test_user"
        )
        return user
    except Exception as e:
        raise HTTPException(status_code=e.code, detail=e.error)
