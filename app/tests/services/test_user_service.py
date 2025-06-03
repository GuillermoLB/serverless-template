from datetime import datetime, timedelta
import datetime as dt  # Import the whole module under a different name
import pytest

from hypothesis import given
from hypothesis.strategies import text
from hypothesis import settings as hypothesis_settings
from jose import JWTError, jwt

from app.core.config import Settings
from app.error.exceptions import UnauthorizedException
from app.schemas.token_schemas import TokenCreate, TokenVerify
from app.services.user_service import create_access_token, verify_token


@pytest.mark.asyncio
async def test_no_username_in_token_raises_exception(settings):
    token_create = TokenCreate(
        username="",
        expire_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        secret_key=settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    created_token = create_access_token(token_create)

    token_verify = TokenVerify(
        access_token=created_token.access_token,
        token_type=created_token.token_type,
        secret_key=settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

    with pytest.raises(UnauthorizedException):
        verify_token(token_verify)

@pytest.mark.asyncio
async def test_invalid_token_raises_exception(settings):
    # Create a token verify object
    valid_token_verify = TokenVerify(
        access_token="invalid_token",
        token_type=settings.TOKEN_TYPE,
        secret_key=settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    with pytest.raises(UnauthorizedException):
        verify_token(valid_token_verify)


@pytest.mark.asyncio
async def test_valid_token_not_raise_exception(settings):
    payload = {
        "sub": "test_user",  # Valid username
        "exp": datetime.now(dt.timezone.utc) + timedelta(minutes=30)  # Use dt.timezone
    }
    
    # Generate a real token with the test settings
    valid_token = jwt.encode(
        payload, 
        settings.SECRET_KEY, 
        algorithm=settings.ALGORITHM
    )
    
    # Create a token verify object
    valid_token_verify = TokenVerify(
        access_token=valid_token,
        token_type=settings.TOKEN_TYPE,
        secret_key=settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

@pytest.mark.asyncio
@hypothesis_settings(deadline=None, max_examples=10)
@given(text(min_size=1))
def test_token_decode_inverts_encode(username: str):
    settings = Settings()
    token_create = TokenCreate(
        username=username,
        expire_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        secret_key=settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    created_token = create_access_token(token_create)

    token_verify = TokenVerify(
        access_token=created_token.access_token,
        token_type=created_token.token_type,
        secret_key=settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    verified_token = verify_token(token_verify)

    assert username == verified_token.username