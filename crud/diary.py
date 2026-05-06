from sqlalchemy.orm import Session
from sqlalchemy import func, asc
from datetime import datetime
import models


def get_by_id(db: Session, diary_id: int):
    return db.query(models.Diary).filter(models.Diary.diary_id == diary_id).first()


def get_by_date(db: Session, user_id: int, target_date):
    return db.query(models.Diary).filter(
        models.Diary.user_id == user_id,
        func.date(models.Diary.created_at) == target_date
    ).all()


def get_by_date_range(db: Session, user_id: int, start_date, end_date_exclusive):
    return db.query(models.Diary).filter(
        models.Diary.user_id == user_id,
        func.date(models.Diary.created_at) >= start_date,
        func.date(models.Diary.created_at) < end_date_exclusive
    ).order_by(asc(models.Diary.created_at)).all()


def upsert(db: Session, user_id: int, content: str, summary: str, created_date):
    today_start = datetime.combine(created_date, datetime.min.time())
    today_end = datetime.combine(created_date, datetime.max.time())

    existing = db.query(models.Diary).filter(
        models.Diary.user_id == user_id,
        models.Diary.created_at >= today_start,
        models.Diary.created_at <= today_end
    ).first()

    if existing:
        existing.content = content
        existing.created_at = created_date
        existing.summary = summary
        db.commit()
        db.refresh(existing)
        return existing

    new_diary = models.Diary(
        user_id=user_id,
        content=content,
        created_at=created_date,
        summary=summary
    )
    db.add(new_diary)
    db.commit()
    db.refresh(new_diary)
    return new_diary


def update(db: Session, diary_id: int, title: str = None, content: str = None, summary: str = None):
    diary = get_by_id(db, diary_id)
    if not diary:
        return None
    if title is not None:
        diary.title = title
    if content is not None:
        diary.content = content
    if summary is not None:
        diary.summary = summary
    db.commit()
    return diary


def delete(db: Session, diary_id: int):
    diary = get_by_id(db, diary_id)
    if not diary:
        return False
    db.query(models.Emotion).filter(models.Emotion.diary_id == diary_id).delete()
    db.query(models.Psy).filter(models.Psy.diary_id == diary_id).delete()
    db.delete(diary)
    db.commit()
    return True


def update_photo(db: Session, diary_id: int, photo_url: str):
    diary = get_by_id(db, diary_id)
    if not diary:
        return None
    diary.photo = photo_url
    db.commit()
    db.refresh(diary)
    return diary


def delete_photo(db: Session, diary_id: int):
    diary = get_by_id(db, diary_id)
    if not diary:
        return None
    diary.photo = None
    db.commit()
    return diary


def get_with_photo(db: Session, user_id: int, start_date, end_date_exclusive):
    return db.query(models.Diary).filter(
        models.Diary.user_id == user_id,
        models.Diary.created_at >= start_date,
        models.Diary.created_at < end_date_exclusive,
        models.Diary.photo != None,
        models.Diary.photo != ""
    ).all()
