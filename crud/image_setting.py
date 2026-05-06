from sqlalchemy.orm import Session
import models


def get_by_user_id(db: Session, user_id: int):
    return db.query(models.ImageSetting).filter(models.ImageSetting.user_id == user_id).first()


def upsert(db: Session, user_id: int, nation: str, sex: str, age: int):
    existing = get_by_user_id(db, user_id)
    if existing:
        existing.nation = nation
        existing.sex = sex
        existing.age = age
        db.commit()
        db.refresh(existing)
        return existing, False  # False = updated

    new_setting = models.ImageSetting(user_id=user_id, nation=nation, sex=sex, age=age)
    db.add(new_setting)
    db.commit()
    db.refresh(new_setting)
    return new_setting, True  # True = created
