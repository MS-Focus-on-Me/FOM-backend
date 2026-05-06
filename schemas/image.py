from pydantic import BaseModel
from datetime import datetime


class ImageData(BaseModel):
    diary_id: int
    content: str
    created_at: datetime


class ImageSettingData(BaseModel):
    user_id: int
    nation: str
    sex: str
    age: int
