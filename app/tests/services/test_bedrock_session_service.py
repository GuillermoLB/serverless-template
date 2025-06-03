from typing import Any
from app.schemas.bedrock_session_schemas import BedrockSessionCreate
from app.services.bedrock_session_service import create_session
from sqlalchemy.orm import Session
import pytest

from app.tests.conftest import UserFactory, session


def test_create_bedrock_session_works(session: Session, bedrock: Any):
    bedrock_session_create = BedrockSessionCreate(
        encryption_key_arn="1234"  # TODO: take from a settings fixture
    )

    bedrock_session = create_session(
        bedrock=bedrock,
        bedrock_session_create=bedrock_session_create
    )
    assert bedrock_session.session_id is not None
