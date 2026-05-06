from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from database import get_db
from schemas.user import UpdateUserInfo, ReferenceData
import crud.user as user_crud
import crud.image_setting as image_setting_crud

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("/{user_id}")
async def get_user(user_id: int, db: Session = Depends(get_db)):
    user = user_crud.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="유저를 찾을 수 없음")

    imgsetting = image_setting_crud.get_by_user_id(db, user_id)
    nation = imgsetting.nation if imgsetting else "대한민국"
    sex = imgsetting.sex if imgsetting else "남"
    age = imgsetting.age if imgsetting else 26

    return {
        "user_id": user.user_id,
        "reference_text": user.reference_text,
        "email": user.email,
        "nation": nation,
        "sex": sex,
        "age": age
    }


@router.put("/reference/{user_id}")
async def update_reference(user_id: int, data: ReferenceData, db: Session = Depends(get_db)):
    user = user_crud.update_reference(db, user_id, data.reference_text)
    if not user:
        raise HTTPException(status_code=404, detail="유저를 찾을 수 없습니다.")
    return {"message": "reference 수정 성공"}


@router.put("/{user_id}")
async def update_user(user_id: int, data: UpdateUserInfo, db: Session = Depends(get_db)):
    user = user_crud.update(db, user_id, email=data.email, password=data.password)
    if not user:
        raise HTTPException(status_code=404, detail="유저를 찾을 수 없습니다.")
    return {"message": "유저 정보 수정 성공"}
