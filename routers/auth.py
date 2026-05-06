from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from database import get_db
from schemas.user import SignupData, UserLogin
import crud.user as user_crud

router = APIRouter(prefix="/api", tags=["auth"])


@router.post("/signup")
async def signup(data: SignupData, db: Session = Depends(get_db)):
    if user_crud.get_by_email(db, data.email):
        raise HTTPException(status_code=400, detail="이메일이 이미 사용 중입니다.")
    new_user = user_crud.create(db, data.username, data.email, data.password)
    return {"message": "회원가입 성공!", "user": {"email": new_user.email, "name": new_user.username}}


@router.post("/login")
async def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = user_crud.get_by_email(db, user.email)
    if not db_user:
        return {"success": False, "message": "이메일 또는 비밀번호가 잘못되었습니다.1"}
    if user.password != db_user.password:
        return {"success": False, "message": "이메일 또는 비밀번호가 잘못되었습니다.2"}
    return {"success": True, "message": "로그인 성공!", "user_id": db_user.user_id}
