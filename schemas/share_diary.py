from pydantic import BaseModel
from datetime import datetime


class ShareDiaryData(BaseModel):
    diary_id: int
    created_at: datetime
