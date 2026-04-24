"""鉴权相关请求/响应模型。"""
from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    is_admin: bool
    username: str


class UserMe(BaseModel):
    username: str
    is_admin: bool
