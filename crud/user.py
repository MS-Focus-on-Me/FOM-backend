from sqlalchemy.orm import Session
import models


def get_by_id(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.user_id == user_id).first()


def get_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def create(db: Session, username: str, email: str, password: str):
    new_user = models.User(username=username, email=email, password=password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def update(db: Session, user_id: int, email: str = None, password: str = None):
    user = get_by_id(db, user_id)
    if not user:
        return None
    if email is not None:
        user.email = email
    if password is not None:
        user.password = password
    db.commit()
    return user


def update_reference(db: Session, user_id: int, reference_text: str):
    user = get_by_id(db, user_id)
    if not user:
        return None
    user.reference_text = reference_text
    db.commit()
    return user
