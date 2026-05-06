from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from database import get_db
from schemas.image import ImageData, ImageSettingData
import crud.diary as diary_crud
import crud.image_setting as image_setting_crud
import crud.share_diary as share_diary_crud
from services.dalle_diary import generate_mone_pastel_image

router = APIRouter(prefix="/api", tags=["image"])


@router.put("/diary/image/create")
def create_image(data: ImageData, db: Session = Depends(get_db)):
    diary = diary_crud.get_by_id(db, data.diary_id)
    if not diary:
        raise HTTPException(status_code=404, detail="일기를 찾을 수 없습니다.")

    imgsetting = image_setting_crud.get_by_user_id(db, diary.user_id)
    nation = imgsetting.nation if imgsetting and imgsetting.nation else "대한민국"
    sex = imgsetting.sex if imgsetting and imgsetting.sex else "남"
    age = imgsetting.age if imgsetting and imgsetting.age else 26

    image_url, filename = generate_mone_pastel_image(data.content, nation, sex, age)
    diary_crud.update_photo(db, data.diary_id, image_url)

    return {"message": "기록 성공", "URL": image_url, "FILENAME": filename}


@router.get("/diary/image/read")
async def read_image(user_id: int, selected_date: str, db: Session = Depends(get_db)):
    if len(selected_date) != 12:
        raise HTTPException(status_code=400, detail="날짜 문자열이 올바른 길이가 아닙니다.")
    start_str, end_str = selected_date[:6], selected_date[6:]
    try:
        start_date = datetime.strptime(start_str, "%y%m%d")
        end_date = datetime.strptime(end_str, "%y%m%d")
    except Exception:
        raise HTTPException(status_code=400, detail="날짜 형식이 올바르지 않습니다.")
    if end_date < start_date:
        raise HTTPException(status_code=400, detail="종료 날짜가 시작 날짜보다 이전입니다.")

    diaries = diary_crud.get_with_photo(db, user_id, start_date, end_date + timedelta(days=1))
    return [
        {
            "diary_id": d.diary_id,
            "photo": d.photo,
            "content": d.content,
            "created_at": d.created_at,
            "summary": d.summary,
        }
        for d in diaries
    ]


@router.put("/image/setting")
async def upsert_image_setting(data: ImageSettingData, db: Session = Depends(get_db)):
    setting, created = image_setting_crud.upsert(db, data.user_id, data.nation, data.sex, data.age)
    msg = "새 설정이 저장되었습니다." if created else "설정이 업데이트 되었습니다."
    return {"message": msg, "setting": setting}


@router.put("/image/delete/{diary_id}")
async def delete_image(diary_id: int, db: Session = Depends(get_db)):
    diary = diary_crud.delete_photo(db, diary_id)
    if not diary:
        raise HTTPException(status_code=404, detail="일기를 찾을 수 없음")
    share_diary_crud.delete_by_diary_id(db, diary_id)
    return {"message": "일기 사진 삭제 및 공유 일기 삭제 성공"}
