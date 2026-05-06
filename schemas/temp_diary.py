from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class TempDiaryData(BaseModel):
    user_id: int
    title: str
    content: str
    created_at: datetime


class UpdateTempDiary(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
