from datetime import datetime, timedelta

from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.schemas.token_schemas import Token, TokenCreate, TokenData, TokenVerify
from app.error.codes import Errors
from app.error.exceptions import UnauthorizedException
from app.repos import user_repo


def create_access_token(
        token_create: TokenCreate
):
    to_encode = {"sub": token_create.username}

    expire = datetime.utcnow() + timedelta(minutes=token_create.expire_minutes)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        token_create.secret_key,
        algorithm=token_create.algorithm)

    token = Token(
        access_token=encoded_jwt,
        token_type="bearer"
    )
    return token


def verify_token(token: TokenVerify) -> TokenData:
    try:
        payload = jwt.decode(token.access_token, token.secret_key,
                             algorithms=[token.algorithm])
        username: str = payload.get("sub")
        if not username:
            raise UnauthorizedException(error=Errors.E010)
        token_data = TokenData(username=username)
    except JWTError:
        raise UnauthorizedException(error=Errors.E010)
    return token_data


def authenticate_user(session: Session, username: str, password: str):
    user = user_repo.read_user_by_name(session, username)
    return user
