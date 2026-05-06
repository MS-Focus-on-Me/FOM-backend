import json
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from database import get_db
from schemas.diary import DiaryData, UpdateDiary, QuestionRequest
import crud.diary as diary_crud
import crud.user as user_crud
import crud.emotion as emotion_crud
from services.summary_diary import summary_workflow
from services.emotion import request_gpt
from services.convert_diary_format import writer_workflow

router = APIRouter(tags=["diary"])


def _parse_emotions(analysis_result: dict) -> dict:
    try:
        response_text = analysis_result["response"]
        json_str = response_text.strip()
        if json_str.startswith("```json"):
            json_str = json_str[len("```json"):].strip()
        if json_str.endswith("```"):
            json_str = json_str[:-3].strip()
        emotions_raw = json.loads(json_str)[0]["감정"]
        return {
            "joy": emotions_raw.get("기쁨", 0),
            "sadness": emotions_raw.get("슬픔", 0),
            "anger": emotions_raw.get("분노", 0),
            "fear": emotions_raw.get("공포", 0),
            "disgust": emotions_raw.get("혐오", 0),
            "anxiety": emotions_raw.get("불안", 0),
            "envy": emotions_raw.get("부러움", 0),
            "bewilderment": emotions_raw.get("당황", 0),
            "boredom": emotions_raw.get("따분", 0),
        }
    except Exception as e:
        print("파싱 에러:", e)
        return {k: 0 for k in ["joy", "sadness", "anger", "fear", "disgust", "anxiety", "envy", "bewilderment", "boredom"]}


@router.put("/api/diary/create")
async def create_diary(data: DiaryData, db: Session = Depends(get_db)):
    if not user_crud.get_by_id(db, data.user_id):
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")

    diary_summary = await summary_workflow(data.content)
    created_date = data.created_at.date()
    diary = diary_crud.upsert(db, data.user_id, data.content, diary_summary, created_date)

    analysis_result = request_gpt(data.content)
    if not isinstance(analysis_result, dict):
        raise HTTPException(status_code=400, detail="감정 분석 실패 또는 유효하지 않은 결과입니다.")

    emotions = _parse_emotions(analysis_result)
    emotion_crud.upsert(db, data.user_id, diary.diary_id, emotions, created_date)

    return {"message": "일기 기록 및 감정 분석 성공", "diary_id": diary.diary_id}


@router.get("/api/diary/read")
async def read_diary_by_date(user_id: int, selected_date: str, db: Session = Depends(get_db)):
    target_date = datetime.strptime(selected_date, "%Y-%m-%d").date()
    entries = diary_crud.get_by_date(db, user_id, target_date)
    if not entries:
        return {"message": "일기가 없습니다."}
    return entries


@router.get("/api/diary/read_mte")
async def read_diary_by_date_range(user_id: int, selected_date: str, db: Session = Depends(get_db)):
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
    entries = diary_crud.get_by_date_range(db, user_id, start_date, end_date + timedelta(days=1))
    if not entries:
        return {"message": "일기가 없습니다."}
    return entries


@router.delete("/api/diary/delete")
async def delete_diary(diary_id: int, db: Session = Depends(get_db)):
    if not diary_crud.delete(db, diary_id):
        raise HTTPException(status_code=404, detail="일기를 찾을 수 없습니다.")
    return {"message": "일기 삭제 성공"}


@router.put("/api/diary/{diary_id}")
async def update_diary(diary_id: int, data: UpdateDiary, db: Session = Depends(get_db)):
    summary = None
    if data.content is not None:
        summary = await summary_workflow(data.content)
    diary = diary_crud.update(db, diary_id, title=data.title, content=data.content, summary=summary)
    if not diary:
        raise HTTPException(status_code=404, detail="일기를 찾을 수 없습니다.")
    return {"message": "수정 성공"}


@router.post("/generate_diary")
async def generate_diary(request: QuestionRequest, db: Session = Depends(get_db)):
    user = user_crud.get_by_id(db, request.user_id)
    reference = user.reference_text if user and user.reference_text else None
    result = await writer_workflow(request.question_text, reference)
    return {"일기 변환": result}
