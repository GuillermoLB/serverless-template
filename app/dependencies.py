from functools import lru_cache
from typing import Annotated, Any
from app.error.codes import Errors
from app.error.exceptions import UnauthorizedException
from fastapi import Depends
from app.core.config import settings, Settings

from app.schemas.user_schemas import User
import boto3


@lru_cache
def get_settings():
    return settings


region_name = get_settings().AWS_REGION


def get_s3():
    return boto3.client("s3")


def get_sqs_client():
    return boto3.client("sqs", region_name=region_name)


SettingsDep = Annotated[Settings, Depends(get_settings)]
