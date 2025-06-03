from functools import lru_cache
from typing import Annotated, Any
from app.error.codes import Errors
from app.error.exceptions import UnauthorizedException
from sqlalchemy.orm import Session

from fastapi import Depends, Header
from fastapi.security import OAuth2PasswordBearer

from app.core.config import settings, Settings
from app.db.session import get_session


from app.repos import user_repo
from app.schemas.bedrock_session_schemas import BedrockSession
from app.schemas.token_schemas import TokenVerify
from app.schemas.user_schemas import User
from app.services.user_service import verify_token
import boto3

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="tokens/token")


@lru_cache
def get_settings():
    return settings


def get_current_user(
    db: Session = Depends(get_session),
    token: str = Depends(oauth2_scheme)
):
    token_verify = TokenVerify(
        access_token=token,
        token_type="bearer",
        secret_key=get_settings().SECRET_KEY,
        algorithm=get_settings().ALGORITHM
    )
    token_data = verify_token(token_verify)
    user = user_repo.read_user_by_name(db, token_data.username)
    return user


def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise UnauthorizedException(error=Errors.E003, code=400)
    return current_user


region_name = get_settings().AWS_REGION


@lru_cache()
def get_bedrock():
    return boto3.client('bedrock-agent-runtime', region_name=region_name)


@lru_cache()
def get_cloudwatch():
    return boto3.client('logs', region_name=region_name)


def get_bedrock_session(session_id: Annotated[str | None, Header()] = None):
    """
    Get the Bedrock agent session from the request.
    """
    return BedrockSession(session_id=session_id)


def get_bedrock_invocation(bedrock: "BedrockDep", bedrock_session: "BedrockSessionDep"):
    """
    Create and get the bedrock message invocation.
    """
    # Create the invocation (represents the message)
    invocation = bedrock.create_invocation(
        description="Test invocation",
        sessionIdentifier=bedrock_session.session_id
    )
    return invocation["invocationId"]


SessionDep = Annotated[Session, Depends(get_session)]
BedrockSessionDep = Annotated[BedrockSession, Depends(get_bedrock_session)]
SettingsDep = Annotated[Settings, Depends(get_settings)]
# NOTE: So in routes we can use current_user: UserDep instead of current_user: User = Depends(get_current_active_user) -> DRY principle
UserDep = Annotated[User, Depends(get_current_active_user)]
BedrockDep = Annotated[Any, Depends(get_bedrock)]
BedrockInvocationDep = Annotated[str, Depends(get_bedrock_invocation)]
CloudwatchDep = Annotated[Any, Depends(get_cloudwatch)]
