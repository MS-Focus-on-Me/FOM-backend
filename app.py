import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from routers import auth, user, diary, temp_diary, emotion, image, psy, share_diary

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(user.router)
app.include_router(diary.router)
app.include_router(temp_diary.router)
app.include_router(emotion.router)
app.include_router(image.router)
app.include_router(psy.router)
app.include_router(share_diary.router)


@app.get("/test")
async def read_root():
    return {"message": "Hello, FastAPI"}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app:app", host="0.0.0.0", port=port)
