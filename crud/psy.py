from sqlalchemy.orm import Session
import models


def create(db: Session, user_id: int, diary_id: int, comment: str):
    new_psy = models.Psy(user_id=user_id, diary_id=diary_id, comment=comment)
    db.add(new_psy)
    db.commit()
    db.refresh(new_psy)
    return new_psy
