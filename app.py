from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# CORS 허용 정책 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # 모든 출처 허용, 특정 출처만 허용하려면 리스트에 URL 넣기
    allow_credentials=True,
    allow_methods=["*"],    # 모든 HTTP 메소드 허용
    allow_headers=["*"],    # 모든 헤더 허용
)

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