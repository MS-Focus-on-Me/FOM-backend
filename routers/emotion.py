import os
import mysql.connector
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from database import get_db
from schemas.emotion import EmotionData
import crud.emotion as emotion_crud

router = APIRouter(prefix="/api", tags=["emotion"])


@router.get("/emotion/read")
def get_emotions(user_id: int, selected_date: str, db: Session = Depends(get_db)):
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

    emotions = emotion_crud.get_by_date_range(db, user_id, start_date, end_date + timedelta(days=1))
    if not emotions:
        raise HTTPException(status_code=404, detail="감정들이 없습니다.")

    return [
        {
            "emotion_id": e.emotion_id,
            "user_id": e.user_id,
            "diary_id": e.diary_id,
            "joy": e.joy,
            "sadness": e.sadness,
            "anger": e.anger,
            "fear": e.fear,
            "disgust": e.disgust,
            "anxiety": e.anxiety,
            "envy": e.envy,
            "bewilderment": e.bewilderment,
            "boredom": e.boredom,
            "created_at": e.created_at,
        }
        for e in emotions
    ]


@router.post("/emotion/create")
async def create_emotion(data: EmotionData, db: Session = Depends(get_db)):
    emotions = {
        "joy": data.joy, "sadness": data.sadness, "anger": data.anger,
        "fear": data.fear, "disgust": data.disgust, "anxiety": data.anxiety,
        "envy": data.envy, "bewilderment": data.bewilderment, "boredom": data.boredom,
    }
    new_emotion = emotion_crud.create(db, data.user_id, data.diary_id, emotions, data.created_at)
    return {"message": "감정 데이터가 성공적으로 추가되었습니다.", "emotion_id": new_emotion.emotion_id}


@router.delete("/emotion/delete")
async def delete_emotion(emotion_id: int, db: Session = Depends(get_db)):
    if not emotion_crud.delete(db, emotion_id):
        raise HTTPException(status_code=404, detail="감정을 찾을 수 없습니다.")
    return {"message": "감정 삭제 성공"}


def _get_raw_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_DATABASE"),
    )


@router.get("/feeling/")
async def average_emotions():
    try:
        today = datetime.now()
        yesterday = today - timedelta(days=1)
        yesterday_start = datetime(yesterday.year, yesterday.month, yesterday.day, 0, 0, 0)
        yesterday_end = datetime(yesterday.year, yesterday.month, yesterday.day, 23, 59, 59)

        conn = _get_raw_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT
                CAST(AVG(joy) AS UNSIGNED) AS joy_avg,
                CAST(AVG(sadness) AS UNSIGNED) AS sadness_avg,
                CAST(AVG(anger) AS UNSIGNED) AS anger_avg,
                CAST(AVG(fear) AS UNSIGNED) AS fear_avg,
                CAST(AVG(disgust) AS UNSIGNED) AS disgust_avg,
                CAST(AVG(anxiety) AS UNSIGNED) AS anxiety_avg,
                CAST(AVG(envy) AS UNSIGNED) AS envy_avg,
                CAST(AVG(bewilderment) AS UNSIGNED) AS bewilderment_avg,
                CAST(AVG(boredom) AS UNSIGNED) AS boredom_avg
            FROM EMOTIONS
            WHERE created_at BETWEEN %s AND %s;
            """,
            (yesterday_start, yesterday_end),
        )
        result = cursor.fetchone()
        cursor.close()
        conn.close()

        return {
            "joy": result["joy_avg"] or 0,
            "sadness": result["sadness_avg"] or 0,
            "anger": result["anger_avg"] or 0,
            "fear": result["fear_avg"] or 0,
            "disgust": result["disgust_avg"] or 0,
            "anxiety": result["anxiety_avg"] or 0,
            "envy": result["envy_avg"] or 0,
            "bewilderment": result["bewilderment_avg"] or 0,
            "boredom": result["boredom_avg"] or 0,
        }
    except Exception as e:
        return {"error": str(e)}
