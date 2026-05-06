from pydantic import BaseModel


class PsyInput(BaseModel):
    user_id: int
    diary_id: int
    diary_text: str
