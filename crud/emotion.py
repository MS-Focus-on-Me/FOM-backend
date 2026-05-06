from sqlalchemy.orm import Session
import models


def get_by_id(db: Session, emotion_id: int):
    return db.query(models.Emotion).filter(models.Emotion.emotion_id == emotion_id).first()


def get_by_diary_id(db: Session, diary_id: int):
    return db.query(models.Emotion).filter(models.Emotion.diary_id == diary_id).first()


def get_by_date_range(db: Session, user_id: int, start_date, end_date_exclusive):
    return db.query(models.Emotion).filter(
        models.Emotion.user_id == user_id,
        models.Emotion.created_at >= start_date,
        models.Emotion.created_at < end_date_exclusive
    ).all()


def upsert(db: Session, user_id: int, diary_id: int, emotions: dict, created_date):
    existing = get_by_diary_id(db, diary_id)
    if existing:
        for key, value in emotions.items():
            setattr(existing, key, value)
        existing.created_at = created_date
        db.commit()
        db.refresh(existing)
        return existing

    new_emotion = models.Emotion(
        user_id=user_id,
        diary_id=diary_id,
        created_at=created_date,
        **emotions
    )
    db.add(new_emotion)
    db.commit()
    db.refresh(new_emotion)
    return new_emotion


def create(db: Session, user_id: int, diary_id: int, emotions: dict, created_at):
    new_emotion = models.Emotion(
        user_id=user_id,
        diary_id=diary_id,
        created_at=created_at,
        **emotions
    )
    db.add(new_emotion)
    db.commit()
    db.refresh(new_emotion)
    return new_emotion


def delete(db: Session, emotion_id: int):
    emotion = get_by_id(db, emotion_id)
    if not emotion:
        return False
    db.delete(emotion)
    db.commit()
    return True
