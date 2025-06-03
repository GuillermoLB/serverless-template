from sqlalchemy.orm import Session

from app.models.user_models import User
from app.schemas.user_schemas import UserCreate
from app.error.codes import Errors
from app.error.exceptions import ResourceNotFoundException, ValidationException
from app.utils.authentication import get_password_hash


def create_user(session: Session, user: UserCreate) -> User:
    db_user = session.query(User).filter(
        User.username == user.username).first()
    if db_user:
        raise ValidationException(error=Errors.E008.format(
            username=db_user.username))
    hashed_password = get_password_hash(user.password.get_secret_value())
    db_user = User(
        username=user.username,
        hashed_password=hashed_password)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def read_user_by_name(session: Session, username: str) -> User:
    db_user = session.query(User).filter(User.username == username).first()
    if db_user is None:
        raise ResourceNotFoundException(error=Errors.E011)
    return db_user
