from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from database import SessionLocal, engine
import models, os, uvicorn
from sqlalchemy.orm import Session

app = FastAPI()

# CORS 허용 정책 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],    # 모든 HTTP 메소드 허용
    allow_headers=["*"],    # 모든 헤더 허용
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

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



##### 테스트 #####

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

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app:app", host="0.0.0.0", port=port)