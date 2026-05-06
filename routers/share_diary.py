from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import date, timedelta
from database import get_db
from schemas.share_diary import ShareDiaryData
import crud.diary as diary_crud
import crud.share_diary as share_diary_crud
from services.anonymous import request_anonymous

router = APIRouter(prefix="/api", tags=["share_diary"])


@router.post("/share_diary/create")
async def create_share_diary(data: ShareDiaryData, db: Session = Depends(get_db)):
    diary = diary_crud.get_by_id(db, data.diary_id)
    if not diary:
        raise HTTPException(status_code=404, detail="일기를 찾을 수 없음")

    existing = share_diary_crud.get_by_diary_id(db, data.diary_id)
    if existing:
        share_diary_crud.update_flag(db, data.diary_id, True)
        return {"message": "일기가 이미 공유되고 있음"}

    anonymous_text = request_anonymous(diary.summary).get("response", "")
    shared = share_diary_crud.create(
        db, data.diary_id, diary.user_id, diary.photo, anonymous_text, data.created_at
    )
    return {"message": "일기가 성공적으로 공유되었습니다.", "share_diary_id": shared.share_diary_id}


@router.get("/shared_diaries/get")
async def get_shared_diaries(db: Session = Depends(get_db)):
    today = date.today()
    yesterday = today - timedelta(days=1)
    diaries = share_diary_crud.get_recent(db, yesterday, today + timedelta(days=1))
    return [{"diary_id": d.diary_id, "photo": d.photo, "content": d.content} for d in diaries]


@router.put("/share_diary/cancel/{diary_id}")
async def cancel_share(diary_id: int, db: Session = Depends(get_db)):
    shared = share_diary_crud.update_flag(db, diary_id, False)
    if not shared:
        raise HTTPException(status_code=404, detail="공유 일기를 찾을 수 없습니다.")
    return {"message": "공유 취소 완료"}
