from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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

# test
# 이제 어떡하죠