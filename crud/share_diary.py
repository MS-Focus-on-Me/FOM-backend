from sqlalchemy.orm import Session
import models


def get_by_diary_id(db: Session, diary_id: int):
    return db.query(models.ShareDiary).filter(models.ShareDiary.diary_id == diary_id).first()


def create(db: Session, diary_id: int, user_id: int, photo: str, content: str, created_at, flag: bool = True):
    shared = models.ShareDiary(
        diary_id=diary_id,
        user_id=user_id,
        photo=photo,
        content=content,
        created_at=created_at,
        flag=flag
    )
    db.add(shared)
    db.commit()
    db.refresh(shared)
    return shared


def update_flag(db: Session, diary_id: int, flag: bool):
    shared = get_by_diary_id(db, diary_id)
    if not shared:
        return None
    shared.flag = flag
    db.commit()
    db.refresh(shared)
    return shared


def delete_by_diary_id(db: Session, diary_id: int):
    db.query(models.ShareDiary).filter(models.ShareDiary.diary_id == diary_id).delete()
    db.commit()


def get_recent(db: Session, yesterday, end_dt_exclusive):
    return db.query(models.ShareDiary).filter(
        models.ShareDiary.flag == True,
        models.ShareDiary.created_at >= yesterday,
        models.ShareDiary.created_at < end_dt_exclusive
    ).all()
