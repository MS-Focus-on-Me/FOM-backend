from pydantic import BaseModel
from datetime import datetime


class EmotionData(BaseModel):
    user_id: int
    diary_id: int
    joy: int = 0
    sadness: int = 0
    anger: int = 0
    fear: int = 0
    disgust: int = 0
    anxiety: int = 0
    envy: int = 0
    bewilderment: int = 0
    boredom: int = 0
    created_at: datetime
