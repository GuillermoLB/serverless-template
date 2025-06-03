from typing import Optional
from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class TokenCreate(BaseModel):
    username: str
    expire_minutes: int
    secret_key: str
    algorithm: str


class TokenVerify(Token):
    secret_key: str
    algorithm: str
