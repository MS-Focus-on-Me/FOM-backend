from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import datetime
from zoneinfo import ZoneInfo
from database import get_db
from schemas.temp_diary import TempDiaryData, UpdateTempDiary
import crud.temp_diary as temp_diary_crud
import crud.user as user_crud

router = APIRouter(prefix="/api/temp_diary", tags=["temp_diary"])


@router.post("/create")
async def create_temp_diary(data: TempDiaryData, db: Session = Depends(get_db)):
    if not user_crud.get_by_id(db, data.user_id):
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
    new = temp_diary_crud.create(db, data.user_id, data.title, data.content, data.created_at)
    return {"message": "기록 성공", "temp_diary_id": new.temp_diary_id}


@router.get("/read")
async def read_temp_diary(user_id: int, db: Session = Depends(get_db)):
    today = datetime.now(ZoneInfo("Asia/Seoul")).date()
    return temp_diary_crud.get_today(db, user_id, today)


@router.put("/{temp_diary_id}")
async def update_temp_diary(temp_diary_id: int, data: UpdateTempDiary, db: Session = Depends(get_db)):
    temp_diary = temp_diary_crud.update(db, temp_diary_id, title=data.title, content=data.content)
    if not temp_diary:
        raise HTTPException(status_code=404, detail="일기를 찾을 수 없습니다.")
    return {"message": "수정 성공"}


@router.delete("/delete")
async def delete_temp_diary(temp_diary_id: int, db: Session = Depends(get_db)):
    if not temp_diary_crud.delete(db, temp_diary_id):
        raise HTTPException(status_code=404, detail="일기를 찾을 수 없습니다.")
    return {"message": "기록 삭제 성공"}
