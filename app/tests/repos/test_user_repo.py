from uuid import uuid4
from app.error.exceptions import ResourceNotFoundException, ValidationException
from app.repos import user_repo
from app.schemas.user_schemas import UserCreate
import pytest

from app.tests.conftest import UserFactory, session


def test_create_user_works(session):
    new_user = UserCreate(username="test_user", password="test_password")
    user = user_repo.create_user(session, new_user)
    assert user.username == "test_user"

def test_create_existing_user_raises_exception(session):
    UserFactory(username="existing_user")
    new_user = UserCreate(username="existing_user", password="test_password")
    with pytest.raises(ValidationException, match="E008"):
        user_repo.create_user(session=session, user=new_user)

def test_read_user_by_name_works(session):
    user = UserFactory()
    user_read = user_repo.read_user_by_name(session, user.username)
    assert user.username == user_read.username

def test_non_existing_user_raises_exception(session):
    with pytest.raises(ResourceNotFoundException, match="E011"):
        user_repo.read_user_by_name(session, "non_existing_user")