from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from schemas.psy import PsyInput
import crud.psy as psy_crud
from services.diary_psy import request_psy

router = APIRouter(prefix="/api/psy", tags=["psy"])


@router.post("/create")
async def create_psy(data: PsyInput, db: Session = Depends(get_db)):
    result = request_psy(data.diary_text).get("response")
    psy_crud.create(db, data.user_id, data.diary_id, result)
    return {"Fome": result}
