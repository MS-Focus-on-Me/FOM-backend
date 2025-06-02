from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from database import SessionLocal
import models, os, uvicorn
from sqlalchemy.orm import Session
from datetime import date, datetime
from sqlalchemy import func
from convert_diary_format import writer_workflow
from summary_diary import summary_workflow
from models import User  # 이미 정의된 User 모델

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# CORS 허용 정책 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],    # 모든 HTTP 메소드 허용
    allow_headers=["*"],    # 모든 헤더 허용
)

# 회원가입 API
class SignupData(BaseModel):
    username: str
    email: str
    password: str

@app.post("/api/signup")
async def signup(data: SignupData, db: Session = Depends(get_db)):
    # 이메일 중복 체크
    existing_user = db.query(models.User).filter(models.User.email == data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="이메일이 이미 사용 중입니다.")
    # 새 회원 등록
    new_user = models.User(
        username=data.username,
        email=data.email,
        password=data.password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "회원가입 성공!", "user": {"email": new_user.email, "name": new_user.username}}

# 로그인 API
class UserLogin(BaseModel):
    email: str
    password: str
    
@app.post("/api/login")
async def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if not db_user:
        return {"success": False, "message": "이메일 또는 비밀번호가 잘못되었습니다.1"}
    if user.password != db_user.password:
        return {"success": False, "message": "이메일 또는 비밀번호가 잘못되었습니다.2"}
    return {"success": True, "message": "로그인 성공!", "user_id": db_user.user_id}

# 기록 생성
class TempDiaryData(BaseModel):
    user_id: int
    title: str
    content: str
    created_at: datetime

@app.post("/api/temp_diary/create")
async def create_temp_diary(data: TempDiaryData, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.user_id == data.user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
    
    # 새로운 temp_diary 생성
    new_temp_diary = models.TempDiary(
        user_id=user.user_id,
        title=data.title,
        content=data.content,
        created_at=data.created_at
    )

    db.add(new_temp_diary)
    db.commit()
    db.refresh(new_temp_diary)
    
    return {"message": "기록 성공", "temp_diary_id": new_temp_diary.temp_diary_id}


# 기록 조회
@app.get("/api/temp_diary/read")
async def read_temp_diary(user_id: int, db: Session = Depends(get_db)):
    
    today = date.today()  # 오늘 날짜 (예: 2025-05-25)
    # 오늘 date와 동일한 날짜의 기록들 쿼리
    diaries_today = db.query(models.TempDiary).filter(
        models.TempDiary.user_id == user_id,
        func.date(models.TempDiary.created_at) == today
    ).all()

    return diaries_today

# 기록 수정
class UpdateTempDiary(BaseModel):
    title: str = None
    content: str = None

@app.put("/api/temp_diary/{temp_diary_id}")
async def update_temp_diary(temp_diary_id: int, data: UpdateTempDiary, db: Session = Depends(get_db)):
    # 수정할 기록 찾기
    temp_diary = db.query(models.TempDiary).filter(models.TempDiary.temp_diary_id == temp_diary_id).first()

    if not temp_diary:
        raise HTTPException(status_code=404, detail="일기를 찾을 수 없습니다.")

    if data.title is not None:
        temp_diary.title = data.title
    if data.content is not None:
        temp_diary.content = data.content
        
    db.commit()

    return {"message": "수정 성공"}

# 기록 삭제
@app.delete("/api/temp_diary/delete")
async def delete_temp_diary(temp_diary_id: int, db: Session = Depends(get_db)):
    # 삭제할 기록 찾기
    temp_diary = db.query(models.TempDiary).filter(models.TempDiary.temp_diary_id == temp_diary_id).first()
    
    if not temp_diary:
        raise HTTPException(status_code=404, detail="일기를 찾을 수 없습니다.")

    # 삭제 수행
    db.delete(temp_diary)
    db.commit()

    return {"message": "기록 삭제 성공"}

# 일기 작성
class DiaryData(BaseModel):
    user_id: int
    content: str
    created_at: datetime

@app.post("/api/diary/create")
async def create_diary(data: DiaryData, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.user_id == data.user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
    
    diary_summary = summary_workflow(data.content)

    # 새로운 diary 생성
    new_diary = models.Diary(
        user_id=user.user_id,
        content=data.content,
        created_at=data.created_at,
        summary=diary_summary
    )

    db.add(new_diary)
    db.commit()
    db.refresh(new_diary)
    
    return {"message": "기록 성공", "diary_id": new_diary.diary_id}

# 일기 삭제
@app.delete("/api/diary/delete")
async def delete_temp_diary(diary_id: int, db: Session = Depends(get_db)):
    # 삭제할 기록 찾기
    diary = db.query(models.Diary).filter(models.Diary.diary_id == diary_id).first()
    
    if not diary:
        raise HTTPException(status_code=404, detail="일기를 찾을 수 없습니다.")

    # 삭제 수행
    db.delete(diary)
    db.commit()

    return {"message": "일기 삭제 성공"}

# 일기 수정
class UpdateDiary(BaseModel):
    title: str = None
    content: str = None

@app.put("/api/diary/{diary_id}")
async def update_diary(diary_id: int, data: UpdateDiary, db: Session = Depends(get_db)):
    # 수정할 기록 찾기
    diary = db.query(models.Diary).filter(models.Diary.diary_id == diary_id).first()

    if not diary:
        raise HTTPException(status_code=404, detail="일기를 찾을 수 없습니다.")

    if data.title is not None:
        diary.title = data.title
    if data.content is not None:
        diary.content = data.content
        
    db.commit()

    return {"message": "수정 성공"}

# 일기형태 변환
class QuestionRequest(BaseModel):
    question_text: str

@app.post("/generate_diary")
async def generate_diary(request: QuestionRequest):
    result = await writer_workflow(request.question_text)
    return {"일기 변환": result}

# 유저정보 수정
class UpdateUserInfo(BaseModel):
    email: str = None
    password: str = None

@app.put("/api/users/{user_id}")
async def update_user(user_id: int, data: UpdateUserInfo, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.user_id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="유저를 찾을 수 없습니다.")
    
    if data.email is not None:
        user.email = data.email
    if data.password is not None:
        user.password = data.password
        
    db.commit()

    return {"message": "유저 정보 수정 성공"}

# 유저정보 조회
@app.get("/api/users/{user_id}")
async def get_user_email(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="유저를 찾을 수 없음")
    return {"email": user.email}

# reference 선택
class ReferenceData(BaseModel):
    reference_text: str = None

@app.put("/api/users/reference/{user_id}")
async def select_reference(user_id: int, data: ReferenceData, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.user_id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="유저를 찾을 수 없습니다.")
    
    if data.reference_text is not None:
        user.reference_text = data.reference_text
    
    db.commit()
    return {"message": "reference 수정 성공"}


########## 테스트 ##########

@app.get("/test")
async def read_root():
    return {"message": "Hello, FastAPI"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app:app", host="0.0.0.0", port=port)


# source venv/bin/activate     
# uvicorn app:app --host 0.0.0.0 --port 8000
