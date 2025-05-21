from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
import models
from database import engine, get_db

# 모델과 DB 연동
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# CORS 허용 정책 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 출처 허용, 특정 출처만 허용하려면 리스트에 URL 넣기
    allow_credentials=True,
    allow_methods=["*"],    # 모든 HTTP 메소드 허용
    allow_headers=["*"],    # 모든 헤더 허용
)


def get_db_session():
    db = get_db()
    try:
        yield db
    finally:
        db.close()

# 회원가입 API 예제
class SignupData(BaseModel):
    email: str
    name: str
    password: str

@app.post("/api/signup")
async def signup(data: SignupData, db: Session = Depends(get_db_session)):
    # 이메일 중복 체크
    existing_user = db.query(models.User).filter(models.User.email == data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="이메일이 이미 사용 중입니다.")
    # 새 회원 등록
    new_user = models.User(
        email=data.email,
        name=data.name,
        password=data.password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "회원가입 성공!", "user": {"email": new_user.email, "name": new_user.name}}

# 로그인 API
class UserLogin(BaseModel):
    email: str
    password: str

@app.post("/api/login")
async def login(user: UserLogin, db: Session = Depends(get_db_session)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user and db_user.password == user.password:
        return {"success": True, "message": "로그인 성공!"}
    else:
        return {"success": False, "message": "이메일 또는 비밀번호가 잘못되었습니다."}

# 일기 저장 API
class DiaryData(BaseModel):
    email: str
    content: str    

@app.post("/api/diary")
async def create_diary(data: DiaryData, db: Session = Depends(get_db)):
    # 사용자 존재 여부 검사 (선택사항, 필요 시)
    user_exists = db.query(models.User).filter(models.User.email == data.email).first()
    if not user_exists:
        raise HTTPException(status_code=404, detail="해당 이메일의 사용자 없음")
    
    # 일기 데이터 저장
    new_diary = models.Diary(
        user_email=data.email,
        content=data.content
    )
    db.add(new_diary)
    db.commit()
    db.refresh(new_diary)
    return {"message": "일기 저장 성공!", "diary_id": new_diary.id}

@app.get("/")
async def read_root():
    return {"message": "Hello, FastAPI"}

@app.post("/name")
async def name():
    return {"message": "Hello, FastAPI"}

class UserLogin(BaseModel):
    email: str
    password: str

@app.post("/api/login")
async def login(user: UserLogin):
    print(user)  # 데이터 잘 도착했는지 출력 확인
    if user.email == "test@test.com" and user.password == "123":
        return {"success": True, "message": "로그인 성공!"}
    else:
        return {"success": False, "message": "로그인 실패: 이메일 또는 비밀번호가 잘못되었습니다."}
    
    

class SignupData(BaseModel):  
    username: str  
    email: str  
    password: str  

@app.post("/api/signup")  
async def signup(data: SignupData):  
    # 간단한 예제: 이메일 중복 확인 로직  
    if data.email == "test@example.com":  
        raise HTTPException(status_code=400, detail="이메일이 이미 사용 중입니다.")  

    # 정상 처리  
    return {"message": "회원가입이 성공적으로 처리되었습니다.", "username": data.username}  