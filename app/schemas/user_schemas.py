from typing import Optional
from pydantic import BaseModel, SecretStr


class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    password: SecretStr


class UserRead(UserBase):
    pass


class UserInDBBase(UserBase):
    id: Optional[int] = None
    disabled: Optional[bool] = None

    class Config:
        from_attributes = True


class User(UserInDBBase):
    pass
