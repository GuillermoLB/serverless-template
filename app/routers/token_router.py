import logging
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.db.session import get_session
from app.dependencies import UserDep
from app.schemas.token_schemas import TokenCreate
from app.services.user_service import authenticate_user, create_access_token
from app.core.config import settings

tokens_router = APIRouter(
    tags=["tokens"],
    prefix="/tokens",
)

logger = logging.getLogger(__name__)


@tokens_router.post("/token")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_session)
):
    try:
        user = authenticate_user(db, form_data.username, form_data.password)
        token_create = TokenCreate(
            username=user.username,
            expire_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
            secret_key=settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )
        token = create_access_token(
            token_create
        )
        return token
    except Exception as e:
        # Only use .code and .error for custom exceptions
        from app.error.exceptions import BaseAppException
        if isinstance(e, BaseAppException):
            raise HTTPException(status_code=e.code, detail=e.error)
        else:
            logger.exception("Unexpected error during login")
            raise HTTPException(
                status_code=500, detail="Internal server error")


@tokens_router.get("")
async def get_token(token: UserDep):
    return {"token": token}
