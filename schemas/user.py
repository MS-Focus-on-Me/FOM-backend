from pydantic import BaseModel
from typing import Optional


class SignupData(BaseModel):
    username: str
    email: str
    password: str


class UserLogin(BaseModel):
    email: str
    password: str


class UpdateUserInfo(BaseModel):
    email: Optional[str] = None
    password: Optional[str] = None


class ReferenceData(BaseModel):
    reference_text: Optional[str] = None
