from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date
import models


def create(db: Session, user_id: int, title: str, content: str, created_at):
    new = models.TempDiary(user_id=user_id, title=title, content=content, created_at=created_at)
    db.add(new)
    db.commit()
    db.refresh(new)
    return new


def get_by_id(db: Session, temp_diary_id: int):
    return db.query(models.TempDiary).filter(models.TempDiary.temp_diary_id == temp_diary_id).first()


def get_today(db: Session, user_id: int, today: date):
    return db.query(models.TempDiary).filter(
        models.TempDiary.user_id == user_id,
        func.date(models.TempDiary.created_at) == today
    ).all()


def update(db: Session, temp_diary_id: int, title: str = None, content: str = None):
    temp_diary = get_by_id(db, temp_diary_id)
    if not temp_diary:
        return None
    if title is not None:
        temp_diary.title = title
    if content is not None:
        temp_diary.content = content
    db.commit()
    return temp_diary


def delete(db: Session, temp_diary_id: int):
    temp_diary = get_by_id(db, temp_diary_id)
    if not temp_diary:
        return False
    db.delete(temp_diary)
    db.commit()
    return True
