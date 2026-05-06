from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class DiaryData(BaseModel):
    user_id: int
    content: str
    created_at: datetime


class UpdateDiary(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None


class QuestionRequest(BaseModel):
    question_text: str
    user_id: int
